"""Bounded, deterministic browsing and text search for TranscriptSegment data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    PHASE as TRANSCRIPT_SEGMENT_PHASE,
    TranscriptSegment,
)


MAX_BROWSE_RESULTS = 100
DEFAULT_BROWSE_LIMIT = 20
MAX_SEARCH_RESULTS = 100
DEFAULT_SEARCH_LIMIT = 20
SEARCH_TYPE = "DETERMINISTIC_CASE_INSENSITIVE_SUBSTRING"


class TranscriptBrowseInputError(ValueError):
    """Sanitized validation failure for bounded transcript operations."""


@dataclass(frozen=True, slots=True)
class TranscriptBrowseResult:
    """Immutable projection of one authoritative transcript segment."""

    asset_id: str
    segment_ref: str
    segment_index: int
    text: str
    source_start_seconds: float
    source_end_seconds: float
    source_timecode: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "segment_ref": self.segment_ref,
            "segment_index": self.segment_index,
            "text": self.text,
            "source_start_seconds": self.source_start_seconds,
            "source_end_seconds": self.source_end_seconds,
            "source_timecode": dict(self.source_timecode),
        }


def browse_transcript(
    segments: Sequence[TranscriptSegment],
    *,
    offset: int = 0,
    limit: int = DEFAULT_BROWSE_LIMIT,
) -> list[TranscriptBrowseResult]:
    """Return a bounded ordered slice without changing input segments."""
    _validate_segments(segments)
    _validate_window(offset, limit, MAX_BROWSE_RESULTS)
    return [_result_for(segment) for segment in segments[offset : offset + limit]]


def search_transcript(
    segments: Sequence[TranscriptSegment],
    query: str,
    *,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[TranscriptBrowseResult]:
    """Find query substrings within individual segments in source order."""
    _validate_segments(segments)
    if not isinstance(query, str) or not query.strip():
        raise TranscriptBrowseInputError("SEARCH_QUERY_REQUIRED")
    _validate_window(0, limit, MAX_SEARCH_RESULTS)
    normalized_query = query.casefold()
    matches = (segment for segment in segments if normalized_query in segment.text.casefold())
    return [_result_for(segment) for segment in _take(matches, limit)]


def load_transcript_segments(path: str | Path) -> list[TranscriptSegment]:
    """Load explicitly selected serialized TranscriptSegment data."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        raise TranscriptBrowseInputError("TRANSCRIPT_INPUT_INVALID") from exc

    raw_segments = value if isinstance(value, list) else value.get("transcript_segments") if isinstance(value, dict) else None
    if not isinstance(raw_segments, list):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENTS_REQUIRED")
    return [_segment_from_dict(raw) for raw in raw_segments]


def _segment_from_dict(value: Any) -> TranscriptSegment:
    if not isinstance(value, dict):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENT_INVALID")
    required = (
        "asset_id",
        "segment_index",
        "text",
        "source_start_seconds",
        "source_end_seconds",
    )
    if any(field not in value for field in required):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENT_FIELDS_REQUIRED")
    try:
        return TranscriptSegment(
            phase=value.get("phase", TRANSCRIPT_SEGMENT_PHASE),
            asset_id=value["asset_id"],
            source_audio_stream_index=value.get("source_audio_stream_index"),
            segment_index=value["segment_index"],
            text=value["text"],
            stt_start_seconds=float(value.get("stt_start_seconds", value["source_start_seconds"])),
            stt_end_seconds=float(value.get("stt_end_seconds", value["source_end_seconds"])),
            source_start_seconds=float(value["source_start_seconds"]),
            source_end_seconds=float(value["source_end_seconds"]),
            source_timecode=dict(value.get("source_timecode") or {}),
            provenance=dict(value.get("provenance") or {}),
            error=value.get("error"),
            warnings=list(value.get("warnings") or []),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENT_INVALID") from exc


def _result_for(segment: TranscriptSegment) -> TranscriptBrowseResult:
    return TranscriptBrowseResult(
        asset_id=segment.asset_id,
        segment_ref=segment.segment_ref,
        segment_index=segment.segment_index,
        text=segment.text,
        source_start_seconds=segment.source_start_seconds,
        source_end_seconds=segment.source_end_seconds,
        source_timecode=dict(segment.source_timecode),
    )


def _take(items: Any, limit: int) -> list[TranscriptSegment]:
    result: list[TranscriptSegment] = []
    for item in items:
        if len(result) >= limit:
            break
        result.append(item)
    return result


def _validate_segments(segments: Sequence[TranscriptSegment]) -> None:
    if not isinstance(segments, Sequence) or isinstance(segments, (str, bytes)):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENTS_INVALID")
    if not all(isinstance(segment, TranscriptSegment) for segment in segments):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENTS_INVALID")


def _validate_window(offset: int, limit: int, maximum: int) -> None:
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise TranscriptBrowseInputError("BROWSE_OFFSET_INVALID")
    if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
        raise TranscriptBrowseInputError("RESULT_LIMIT_INVALID")
    if limit > maximum:
        raise TranscriptBrowseInputError("RESULT_LIMIT_EXCEEDED")


__all__ = [
    "DEFAULT_BROWSE_LIMIT",
    "DEFAULT_SEARCH_LIMIT",
    "MAX_BROWSE_RESULTS",
    "MAX_SEARCH_RESULTS",
    "SEARCH_TYPE",
    "TranscriptBrowseInputError",
    "TranscriptBrowseResult",
    "browse_transcript",
    "load_transcript_segments",
    "search_transcript",
]
