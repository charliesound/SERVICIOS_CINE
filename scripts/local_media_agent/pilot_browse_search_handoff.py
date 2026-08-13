"""Adapt an in-memory pilot-flow result to transcript browse/search."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from scripts.local_media_agent.transcript_browse import (
    TranscriptBrowseInputError,
    TranscriptBrowseResult,
    _segment_from_dict,
    browse_transcript,
    search_transcript,
)


def handoff_pilot_transcript_segments(
    pilot_result: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    operation: str,
    *,
    query: str | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> list[TranscriptBrowseResult]:
    """Convert an in-memory pilot result through the canonical browse path."""
    if isinstance(pilot_result, Mapping):
        raw_segments = pilot_result.get("transcript_segments")
    elif isinstance(pilot_result, Sequence) and not isinstance(pilot_result, (str, bytes)):
        raw_segments = pilot_result
    else:
        raise TranscriptBrowseInputError("PILOT_RESULT_INVALID")
    if not isinstance(raw_segments, list):
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENTS_REQUIRED")
    try:
        segments = [_segment_from_dict(value) for value in raw_segments]
    except TranscriptBrowseInputError:
        raise
    except (TypeError, ValueError) as exc:
        raise TranscriptBrowseInputError("TRANSCRIPT_SEGMENT_INVALID") from exc

    if operation == "browse":
        return browse_transcript(segments, offset=offset, limit=20 if limit is None else limit)
    if operation == "search":
        if query is None:
            raise TranscriptBrowseInputError("SEARCH_QUERY_REQUIRED")
        return search_transcript(segments, query, limit=20 if limit is None else limit)
    raise TranscriptBrowseInputError("PILOT_OPERATION_INVALID")


__all__ = ["handoff_pilot_transcript_segments"]
