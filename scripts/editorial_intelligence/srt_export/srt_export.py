"""Standard SubRip rendering for TranscriptSegment V1.

The renderer uses source-relative seconds exclusively. It does not inspect media,
reapply extraction anchors, interpret SMPTE, or require FPS metadata.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from typing import Any, Sequence

from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment

SRT_COMPLETED = "SRT_COMPLETED"
SRT_INVALID_INPUT = "SRT_INVALID_INPUT"
SRT_MIXED_ASSET_INPUT = "SRT_MIXED_ASSET_INPUT"
SRT_INVALID_TIME_RANGE = "SRT_INVALID_TIME_RANGE"
SRT_SERIALIZATION_FAILED = "SRT_SERIALIZATION_FAILED"

SRT_START_MILLISECOND_ROUNDING_POLICY = "FLOOR"
SRT_END_MILLISECOND_ROUNDING_POLICY = "CEIL"
SRT_MINIMUM_CUE_DURATION_POLICY = "ENFORCE_MINIMUM_1MS_WITH_WARNING"
SRT_MULTI_ASSET_POLICY = "REJECT_MIXED_ASSETS"
SRT_MULTI_AUDIO_STREAM_POLICY = "REQUIRE_SINGLE_SOURCE_AUDIO_STREAM"
SRT_EMPTY_TEXT_POLICY = "SKIP_WITH_WARNING"
SRT_ENCODING = "UTF-8"
SRT_OUTPUT_NEWLINE = "LF"
SRT_FINAL_NEWLINE_REQUIRED = True
SRT_USES_SOURCE_RELATIVE_SECONDS = True
SRT_USES_STT_RELATIVE_SECONDS_AS_PRIMARY_TIMELINE = False

_INCOMPATIBLE_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class SrtExportError(ValueError):
    """Sanitized SRT input or serialization failure."""

    def __init__(self, error_code: str, message_sanitized: str) -> None:
        super().__init__(message_sanitized)
        self.error_code = error_code
        self.message_sanitized = message_sanitized


@dataclass(frozen=True)
class SrtExportResult:
    status: str
    asset_id: str | None
    cue_count: int
    srt_text: str
    warnings: tuple[str, ...]
    error: dict[str, str] | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "asset_id": self.asset_id,
            "cue_count": self.cue_count,
            "srt_text": self.srt_text,
            "warnings": list(self.warnings),
            "error": self.error,
        }


def _decimal_seconds(value: Any, *, field: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise SrtExportError(SRT_INVALID_TIME_RANGE, f"invalid {field}")
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise SrtExportError(SRT_INVALID_TIME_RANGE, f"invalid {field}") from None
    if not decimal_value.is_finite():
        raise SrtExportError(SRT_INVALID_TIME_RANGE, f"invalid {field}")
    return decimal_value


def _milliseconds(seconds: Any, *, rounding: str, field: str) -> int:
    decimal_value = _decimal_seconds(seconds, field=field)
    if decimal_value < 0:
        raise SrtExportError(SRT_INVALID_TIME_RANGE, f"invalid {field}")
    scaled = decimal_value * Decimal(1000)
    mode = ROUND_FLOOR if rounding == SRT_START_MILLISECOND_ROUNDING_POLICY else ROUND_CEILING
    return int(scaled.to_integral_value(rounding=mode))


def _format_timestamp(milliseconds: int) -> str:
    if milliseconds < 0:
        raise SrtExportError(SRT_INVALID_TIME_RANGE, "negative timestamp")
    total_seconds, millis = divmod(milliseconds, 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def _normalize_text(text: Any) -> str:
    if not isinstance(text, str):
        raise SrtExportError(SRT_INVALID_INPUT, "text must be a string")
    if _INCOMPATIBLE_CONTROL_RE.search(text):
        raise SrtExportError(SRT_INVALID_INPUT, "text contains incompatible control characters")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _validate_segment(segment: TranscriptSegment) -> tuple[int, int, str]:
    if not isinstance(segment, TranscriptSegment):
        raise SrtExportError(SRT_INVALID_INPUT, "input must contain TranscriptSegment objects")
    start_ms = _milliseconds(
        segment.source_start_seconds,
        rounding=SRT_START_MILLISECOND_ROUNDING_POLICY,
        field="source_start_seconds",
    )
    end_ms = _milliseconds(
        segment.source_end_seconds,
        rounding=SRT_END_MILLISECOND_ROUNDING_POLICY,
        field="source_end_seconds",
    )
    if end_ms < start_ms:
        raise SrtExportError(SRT_INVALID_TIME_RANGE, "end precedes start")
    text = _normalize_text(segment.text)
    return start_ms, end_ms, text


def render_srt(segments: Sequence[TranscriptSegment]) -> SrtExportResult:
    """Render validated TranscriptSegment objects as canonical UTF-8 SubRip text."""
    if isinstance(segments, (str, bytes)):
        raise SrtExportError(SRT_INVALID_INPUT, "segments must be a collection")
    try:
        materialized = list(segments)
    except TypeError:
        raise SrtExportError(SRT_INVALID_INPUT, "segments must be a collection") from None

    if not materialized:
        return SrtExportResult(SRT_COMPLETED, None, 0, "", (), None)

    asset_ids = {segment.asset_id for segment in materialized if isinstance(segment, TranscriptSegment)}
    if len(asset_ids) > 1:
        raise SrtExportError(SRT_MIXED_ASSET_INPUT, "segments contain multiple assets")
    streams = {
        segment.source_audio_stream_index
        for segment in materialized
        if isinstance(segment, TranscriptSegment)
    }
    if len(streams) > 1:
        raise SrtExportError(SRT_INVALID_INPUT, "segments contain multiple source audio streams")

    cues: list[str] = []
    warnings: list[str] = []
    previous_start: int | None = None
    for segment in materialized:
        start_ms, end_ms, text = _validate_segment(segment)
        if previous_start is not None and start_ms < previous_start:
            raise SrtExportError(SRT_INVALID_TIME_RANGE, "segments are not monotonic")
        previous_start = start_ms
        if not text.strip():
            warnings.append(f"segment {segment.segment_index}: empty text skipped")
            continue
        if end_ms <= start_ms:
            end_ms = start_ms + 1
            warnings.append(f"segment {segment.segment_index}: minimum cue duration applied")
        cue_number = len(cues) + 1
        cues.append(
            "\n".join(
                (
                    str(cue_number),
                    f"{_format_timestamp(start_ms)} --> {_format_timestamp(end_ms)}",
                    text,
                    "",
                )
            )
        )

    srt_text = "\n".join(cues)
    if cues and SRT_FINAL_NEWLINE_REQUIRED and not srt_text.endswith("\n"):
        srt_text += "\n"
    return SrtExportResult(
        status=SRT_COMPLETED,
        asset_id=next(iter(asset_ids)) if asset_ids else None,
        cue_count=len(cues),
        srt_text=srt_text,
        warnings=tuple(warnings),
        error=None,
    )


def transcript_segments_to_srt(segments: Sequence[TranscriptSegment]) -> SrtExportResult:
    """Named product entrypoint for rendering a TranscriptSegment collection."""
    return render_srt(segments)
