#!/usr/bin/env python3
"""CID Editorial Intelligence - Transcript Segment + Timecode Provenance V1.

Consumes a Transcription V1 result (whose segments already carry
``source_start_seconds`` / ``source_end_seconds`` mapped via
``extracted_audio_start_seconds + stt_relative_seconds``) plus optional Audio
Extraction V1 and Media Probe V1 payloads, and produces deterministic
``TranscriptSegment`` objects with a source-relative provenance chain and a
safe-degradation source-timecode model.

Contract invariants enforced here:

- Source-relative seconds are PRESERVED from Transcription V1. This layer never
  re-applies the extraction anchor on top of already-mapped values (no double
  offset). The anchor, when supplied, is used only for provenance and an
  optional consistency check within a tolerance.
- Media Probe embedded timecode is NOT promoted to a productive source
  timecode in V1: its start semantics are not demonstrable from the probe
  contract, so segments degrade to a structured ``unavailable``/``absent``/
  ``unsupported`` status and remain valid source-relative citations.
- Any frame arithmetic is exact rational (``fractions.Fraction``), never a
  ``seconds * 29.97`` float approximation.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1"

SOURCE_TIMECODE_STATUS_UNAVAILABLE = "unavailable"
SOURCE_TIMECODE_STATUS_ABSENT = "absent"
SOURCE_TIMECODE_STATUS_UNSUPPORTED = "unsupported"

SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS = 1e-6

SEGMENT_START_FRAME_ROUNDING_POLICY = "floor"
SEGMENT_END_FRAME_ROUNDING_POLICY = "ceil"

ERROR_CODE_INVALID_INPUT = "invalid_input"
ERROR_CODE_INVALID_SEGMENT = "invalid_segment"
ERROR_CODE_SEGMENTS_NOT_MONOTONIC = "segments_not_monotonic"

_NDF_TIMECODE_PATTERN = re.compile(r"^(\d{2}):(\d{2}):(\d{2}):(\d{2})$")
_DROP_FRAME_CANDIDATE_PATTERN = re.compile(r"^(\d{2}):(\d{2}):(\d{2});(\d{2})$")

TIMECODE_FORMAT_NDF = "ndf"
TIMECODE_FORMAT_DROP_FRAME_CANDIDATE = "drop_frame_candidate"
TIMECODE_FORMAT_INVALID = "invalid"

EMBEDDED_TIMECODE_PRESENT = "present"
EMBEDDED_TIMECODE_ABSENT = "absent"
EMBEDDED_TIMECODE_INVALID = "invalid"


class TranscriptSegmentError(Exception):
    """Structured validation failure with a sanitized message."""

    def __init__(self, error_code: str, message_sanitized: str) -> None:
        super().__init__(message_sanitized)
        self.error_code = error_code
        self.message_sanitized = message_sanitized


def nominal_frames_per_second(numerator: int, denominator: int) -> int:
    """Nominal integer frame labels per second for an NDF representation.

    Integer rates return their numerator; fractional rates (e.g. 30000/1001)
    return the ceiling, matching the standard NDF nominal label convention
    (29.97 -> 30). Raises ValueError for invalid denominators.
    """
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if numerator <= 0:
        raise ValueError("numerator must be positive")
    return -(-numerator // denominator)


def parse_ndf_timecode(value: str) -> tuple[int, int, int, int]:
    """Parse an HH:MM:SS:FF non-drop timecode into (H, M, S, F)."""
    if not isinstance(value, str):
        raise ValueError("timecode must be a string")
    match = _NDF_TIMECODE_PATTERN.match(value.strip())
    if match is None:
        raise ValueError("invalid non-drop timecode")
    return tuple(int(part) for part in match.groups())


def classify_timecode_format(value: str) -> str:
    """Classify a raw timecode string as ndf, drop_frame_candidate or invalid."""
    if not isinstance(value, str):
        return TIMECODE_FORMAT_INVALID
    text = value.strip()
    if _NDF_TIMECODE_PATTERN.match(text) is not None:
        return TIMECODE_FORMAT_NDF
    if _DROP_FRAME_CANDIDATE_PATTERN.match(text) is not None:
        return TIMECODE_FORMAT_DROP_FRAME_CANDIDATE
    return TIMECODE_FORMAT_INVALID


def timecode_to_frames(value: str, numerator: int, denominator: int) -> int:
    """Map an NDF timecode to a nominal integer frame index (frame-based)."""
    hours, minutes, seconds, frames = parse_ndf_timecode(value)
    nominal = nominal_frames_per_second(numerator, denominator)
    if frames >= nominal:
        raise ValueError("frame field exceeds nominal frames per second")
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return (total_seconds * nominal) + frames


def format_ndf_timecode(frames: int, numerator: int, denominator: int) -> str:
    """Format a non-negative integer frame index as an HH:MM:SS:FF NDF value."""
    if frames < 0:
        raise ValueError("frame index must be non-negative")
    nominal = nominal_frames_per_second(numerator, denominator)
    frame_field = frames % nominal
    total_seconds = frames // nominal
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frame_field:02d}"


def seconds_to_start_frame(seconds: float, numerator: int, denominator: int) -> int:
    """Start frame offset with the SEGMENT_START_FRAME_ROUNDING_POLICY=floor.

    Uses exact rational arithmetic: floor(seconds * numerator / denominator).
    """
    seconds_fraction = Fraction(str(seconds))
    frame_offset = seconds_fraction * Fraction(numerator, denominator)
    return math.floor(frame_offset)


def seconds_to_end_frame(seconds: float, numerator: int, denominator: int) -> int:
    """End frame offset with the SEGMENT_END_FRAME_ROUNDING_POLICY=ceil.

    Uses exact rational arithmetic: ceil(seconds * numerator / denominator).
    """
    seconds_fraction = Fraction(str(seconds))
    frame_offset = seconds_fraction * Fraction(numerator, denominator)
    return math.ceil(frame_offset)


def derive_ndf_timecode(
    source_start_timecode: str,
    offset_frames: int,
    numerator: int,
    denominator: int,
) -> str:
    """Derive an NDF timecode from a safe source start plus an integer offset.

    PURE utility for explicit, safe inputs. This is never called with ambiguous
    Media Probe metadata; the productive path degrades instead.
    """
    start_frames = timecode_to_frames(source_start_timecode, numerator, denominator)
    return format_ndf_timecode(start_frames + offset_frames, numerator, denominator)


def build_source_timecode(
    probe_timecode: dict[str, Any] | None,
) -> dict[str, Any]:
    """Safe-degradation source-timecode model for V1.

    Returns a structured block that is ALWAYS ``available=False`` in V1. An
    embedded Media Probe timecode is never promoted because its start semantics
    (clip start meaning, paired rational FPS, drop-frame indicator) are not
    demonstrable from the probe contract.
    """
    unavailable = {
        "available": False,
        "status": SOURCE_TIMECODE_STATUS_UNAVAILABLE,
        "reason": "no safe embedded timecode semantics demonstrable from probe contract",
        "source_fps": None,
        "source_start_timecode": None,
        "source_end_timecode": None,
    }
    if probe_timecode is None:
        return dict(unavailable)

    embedded = probe_timecode.get("embedded_timecode")
    status_raw = probe_timecode.get("embedded_timecode_status")
    present = bool(probe_timecode.get("TIMECODE_PRESENT"))

    if not present or not embedded or status_raw == EMBEDDED_TIMECODE_ABSENT:
        return {
            "available": False,
            "status": SOURCE_TIMECODE_STATUS_ABSENT,
            "reason": "no embedded timecode present in media probe",
            "source_fps": None,
            "source_start_timecode": None,
            "source_end_timecode": None,
        }

    if status_raw == EMBEDDED_TIMECODE_INVALID:
        return {
            "available": False,
            "status": SOURCE_TIMECODE_STATUS_UNSUPPORTED,
            "reason": "embedded timecode marked invalid by media probe",
            "source_fps": None,
            "source_start_timecode": None,
            "source_end_timecode": None,
        }

    fmt = classify_timecode_format(str(embedded))
    if fmt == TIMECODE_FORMAT_DROP_FRAME_CANDIDATE:
        return {
            "available": False,
            "status": SOURCE_TIMECODE_STATUS_UNSUPPORTED,
            "reason": "drop-frame timecode candidate is not supported in V1",
            "source_fps": None,
            "source_start_timecode": None,
            "source_end_timecode": None,
        }
    if fmt == TIMECODE_FORMAT_INVALID:
        return {
            "available": False,
            "status": SOURCE_TIMECODE_STATUS_UNSUPPORTED,
            "reason": "embedded timecode malformed",
            "source_fps": None,
            "source_start_timecode": None,
            "source_end_timecode": None,
        }

    return {
        "available": False,
        "status": SOURCE_TIMECODE_STATUS_UNSUPPORTED,
        "reason": "embedded timecode semantics not demonstrable from probe contract; not promoted in V1",
        "source_fps": None,
        "source_start_timecode": None,
        "source_end_timecode": None,
    }


@dataclass(frozen=True)
class TranscriptSegment:
    """Deterministic TranscriptSegment V1 contract object."""

    phase: str
    asset_id: str
    source_audio_stream_index: int | None
    segment_index: int
    text: str
    stt_start_seconds: float
    stt_end_seconds: float
    source_start_seconds: float
    source_end_seconds: float
    source_timecode: dict[str, Any]
    provenance: dict[str, Any]
    error: dict[str, Any] | None
    warnings: list[str]

    @property
    def segment_ref(self) -> str:
        return f"{self.asset_id}::{self.source_audio_stream_index}::{self.segment_index}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "asset_id": self.asset_id,
            "source_audio_stream_index": self.source_audio_stream_index,
            "segment_index": self.segment_index,
            "text": self.text,
            "stt_start_seconds": self.stt_start_seconds,
            "stt_end_seconds": self.stt_end_seconds,
            "source_start_seconds": self.source_start_seconds,
            "source_end_seconds": self.source_end_seconds,
            "source_timecode": self.source_timecode,
            "provenance": self.provenance,
            "error": self.error,
            "warnings": self.warnings,
        }


def _extract_source_reference(
    media_probe_payload: dict[str, Any] | None,
    audio_extraction_payload: dict[str, Any] | None,
) -> tuple[str | None, str | None]:
    internal_source_reference: str | None = None
    sanitized_source_label: str | None = None
    for source_payload in (media_probe_payload, audio_extraction_payload):
        if not source_payload:
            continue
        ref = source_payload.get("source_reference") or {}
        if internal_source_reference is None:
            internal_source_reference = ref.get("internal_local_source_reference")
        if sanitized_source_label is None:
            sanitized_source_label = ref.get("sanitized_external_source_label")
    return internal_source_reference, sanitized_source_label


def _build_provenance(
    asset_id: str,
    source_audio_stream_index: int | None,
    segment_index: int,
    stt_start_seconds: float,
    stt_end_seconds: float,
    source_start_seconds: float,
    source_end_seconds: float,
    extraction_anchor_seconds: float,
    audio_duration_seconds: float | None,
    internal_source_reference: str | None,
    sanitized_source_label: str | None,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "source_audio_stream_index": source_audio_stream_index,
        "segment_index": segment_index,
        "stt_relative_interval": {
            "start_seconds": stt_start_seconds,
            "end_seconds": stt_end_seconds,
        },
        "source_relative_interval": {
            "start_seconds": source_start_seconds,
            "end_seconds": source_end_seconds,
        },
        "source_timecode_interval": None,
        "extraction_anchor_seconds": extraction_anchor_seconds,
        "audio_duration_seconds": audio_duration_seconds,
        "source_reference_sanitized": sanitized_source_label,
        "internal_source_reference": internal_source_reference,
    }


def transcription_result_to_transcript_segments(
    transcription_payload: dict[str, Any],
    *,
    audio_extraction_payload: dict[str, Any] | None = None,
    media_probe_payload: dict[str, Any] | None = None,
    extraction_anchor_seconds: float | None = None,
) -> list[TranscriptSegment]:
    """Transform a Transcription V1 result into TranscriptSegment[].

    - Preserves ``source_start_seconds`` / ``source_end_seconds`` verbatim; the
      extraction anchor is used only for provenance and an optional consistency
      check, never to re-shift already-mapped values (no double offset).
    - Enforces segment invariants and monotonic ordering; invalid input raises
      a structured TranscriptSegmentError.
    - Never runs STT, never reads audio, never executes ffmpeg/ffprobe.
    """
    if hasattr(transcription_payload, "to_dict"):
        transcription_payload = transcription_payload.to_dict()

    asset_id = transcription_payload.get("asset_id")
    if not isinstance(asset_id, str) or not asset_id:
        raise TranscriptSegmentError(ERROR_CODE_INVALID_INPUT, "transcription payload missing asset_id")
    source_audio_stream_index = transcription_payload.get("source_audio_stream_index")
    audio_duration_seconds = transcription_payload.get("audio_duration_seconds")
    if audio_duration_seconds is not None and not isinstance(
        audio_duration_seconds, (int, float)
    ):
        raise TranscriptSegmentError(ERROR_CODE_INVALID_INPUT, "invalid audio duration")

    anchor = extraction_anchor_seconds
    if anchor is None and audio_extraction_payload is not None:
        audio_block = audio_extraction_payload.get("audio") or {}
        anchor = audio_block.get("extracted_audio_start_seconds")
    if anchor is None:
        anchor = 0.0
    else:
        anchor = float(anchor)

    internal_source_reference, sanitized_source_label = _extract_source_reference(
        media_probe_payload,
        audio_extraction_payload,
    )

    probe_timecode: dict[str, Any] | None = None
    if media_probe_payload is not None:
        probe_timecode = media_probe_payload.get("timecode")

    segments_raw = transcription_payload.get("segments") or []
    result: list[TranscriptSegment] = []
    previous_stt_start: float | None = None

    for raw in segments_raw:
        seg_index = raw.get("segment_index")
        start = raw.get("start_seconds")
        end = raw.get("end_seconds")
        text = raw.get("text")

        if isinstance(seg_index, bool) or not isinstance(seg_index, int) or seg_index < 0:
            raise TranscriptSegmentError(ERROR_CODE_INVALID_SEGMENT, "invalid segment index")
        if isinstance(start, bool) or not isinstance(start, (int, float)) or start < 0:
            raise TranscriptSegmentError(ERROR_CODE_INVALID_SEGMENT, "invalid segment start")
        if isinstance(end, bool) or not isinstance(end, (int, float)) or end < start:
            raise TranscriptSegmentError(ERROR_CODE_INVALID_SEGMENT, "invalid segment end")
        if not isinstance(text, str):
            raise TranscriptSegmentError(ERROR_CODE_INVALID_SEGMENT, "invalid segment text")

        stt_start_seconds = float(start)
        stt_end_seconds = float(end)
        if previous_stt_start is not None and stt_start_seconds < previous_stt_start:
            raise TranscriptSegmentError(
                ERROR_CODE_SEGMENTS_NOT_MONOTONIC,
                "segment timestamps are not monotonic",
            )
        previous_stt_start = stt_start_seconds

        warnings: list[str] = []
        source_start_seconds = raw.get("source_start_seconds")
        source_end_seconds = raw.get("source_end_seconds")
        if source_start_seconds is None or source_end_seconds is None:
            source_start_seconds = anchor + stt_start_seconds
            source_end_seconds = anchor + stt_end_seconds
            warnings.append(
                "source-relative fields absent in transcription segment; derived once from extraction anchor"
            )
        else:
            source_start_seconds = float(source_start_seconds)
            source_end_seconds = float(source_end_seconds)
            expected_start = anchor + stt_start_seconds
            expected_end = anchor + stt_end_seconds
            if (
                abs(source_start_seconds - expected_start) > SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS
                or abs(source_end_seconds - expected_end) > SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS
            ):
                warnings.append(
                    "source-relative fields do not match extraction anchor within tolerance; transcription values preserved"
                )

        if source_start_seconds < 0 or source_end_seconds < source_start_seconds:
            raise TranscriptSegmentError(ERROR_CODE_INVALID_SEGMENT, "invalid source-relative interval")

        source_timecode = build_source_timecode(probe_timecode)
        provenance = _build_provenance(
            asset_id=asset_id,
            source_audio_stream_index=source_audio_stream_index,
            segment_index=seg_index,
            stt_start_seconds=stt_start_seconds,
            stt_end_seconds=stt_end_seconds,
            source_start_seconds=source_start_seconds,
            source_end_seconds=source_end_seconds,
            extraction_anchor_seconds=anchor,
            audio_duration_seconds=audio_duration_seconds,
            internal_source_reference=internal_source_reference,
            sanitized_source_label=sanitized_source_label,
        )
        result.append(
            TranscriptSegment(
                phase=PHASE,
                asset_id=asset_id,
                source_audio_stream_index=source_audio_stream_index,
                segment_index=seg_index,
                text=text,
                stt_start_seconds=stt_start_seconds,
                stt_end_seconds=stt_end_seconds,
                source_start_seconds=source_start_seconds,
                source_end_seconds=source_end_seconds,
                source_timecode=source_timecode,
                provenance=provenance,
                error=None,
                warnings=warnings,
            )
        )
    return result


def _normalize_excerpt(text: str) -> str:
    return " ".join(str(text).split())


def build_editorial_citation(
    segment: TranscriptSegment,
    text_excerpt: str | None = None,
) -> dict[str, Any]:
    """Future editorial citation representation (minimal V1).

    References the segment by ``segment_ref``; the full text lives in the
    TranscriptSegment. Never exposes the internal source reference nor any raw
    path.
    """
    excerpt = _normalize_excerpt(text_excerpt) if text_excerpt else None
    return {
        "asset_id": segment.asset_id,
        "segment_ref": segment.segment_ref,
        "text_excerpt": excerpt,
        "source_start_seconds": segment.source_start_seconds,
        "source_end_seconds": segment.source_end_seconds,
        "source_start_timecode": segment.source_timecode.get("source_start_timecode"),
        "source_end_timecode": segment.source_timecode.get("source_end_timecode"),
    }
