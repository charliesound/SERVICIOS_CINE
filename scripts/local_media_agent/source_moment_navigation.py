"""Build deterministic, local source-moment navigation metadata."""

from __future__ import annotations

from typing import Any

from scripts.local_media_agent.transcript_browse import TranscriptBrowseResult


def build_source_moment_navigation(result: TranscriptBrowseResult) -> dict[str, Any]:
    """Return an additive source-moment block without changing result data."""
    timecode = dict(result.source_timecode)
    status = timecode.get("status")
    if not isinstance(status, str) or not status:
        status = "unavailable"

    source_moment: dict[str, Any] = {
        "asset_id": result.asset_id,
        "segment_ref": result.segment_ref,
        "segment_index": result.segment_index,
        "source_start_seconds": result.source_start_seconds,
        "source_end_seconds": result.source_end_seconds,
        "source_timecode_status": status,
        "navigation_descriptor": (
            f"asset_id={result.asset_id}; segment_ref={result.segment_ref}; "
            f"interval={result.source_start_seconds}-{result.source_end_seconds}s; "
            f"timecode_status={status}"
        ),
    }
    for field in ("source_start_timecode", "source_end_timecode", "source_fps"):
        if timecode.get(field) is not None:
            source_moment[field] = timecode[field]
    return source_moment


__all__ = ["build_source_moment_navigation"]
