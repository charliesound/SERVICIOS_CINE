#!/usr/bin/env python3
"""Minimal JSON TranscriptSegment input to SubRip stdout CLI."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from scripts.editorial_intelligence.srt_export.srt_export import (
    SrtExportError,
    render_srt,
)
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


def _segment_from_dict(value: dict[str, Any]) -> TranscriptSegment:
    allowed = {
        "phase",
        "asset_id",
        "source_audio_stream_index",
        "segment_index",
        "text",
        "stt_start_seconds",
        "stt_end_seconds",
        "source_start_seconds",
        "source_end_seconds",
        "source_timecode",
        "provenance",
        "error",
        "warnings",
    }
    return TranscriptSegment(**{key: value[key] for key in allowed if key in value})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render TranscriptSegment JSON as SubRip")
    parser.add_argument("--segments-json", required=True, help="JSON array or {segments: [...]} object")
    args = parser.parse_args(argv)
    try:
        with open(args.segments_json, encoding="utf-8") as handle:
            payload = json.load(handle)
        values = payload.get("segments") if isinstance(payload, dict) else payload
        if not isinstance(values, list):
            raise SrtExportError("SRT_INVALID_INPUT", "segments JSON must be an array")
        result = render_srt([_segment_from_dict(value) for value in values])
        sys.stdout.write(result.srt_text)
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError, SrtExportError) as exc:
        message = getattr(exc, "message_sanitized", str(exc))
        sys.stderr.write(f"SRT_INVALID_INPUT: {message}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
