#!/usr/bin/env python3
"""CID Editorial Intelligence - Transcript Provenance CLI.

Thin wrapper around the transcript provenance core. Consumes a Transcription V1
JSON result (and optionally Audio Extraction V1 / Media Probe V1 JSON payloads)
and emits deterministic TranscriptSegment JSON. No media, no STT, no model, no
ffmpeg/ffprobe, no DB, no network.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    PHASE,
    TranscriptSegmentError,
    transcription_result_to_transcript_segments,
)

CLI_NAME = "cid-editorial-transcript-provenance"


def _load_json(path: str) -> dict[str, Any]:
    with open(Path(path), encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("JSON payload must be an object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build TranscriptSegment provenance from a Transcription V1 result."
    )
    parser.add_argument(
        "--transcript-json",
        required=True,
        help="Path to a Transcription V1 result JSON file.",
    )
    parser.add_argument(
        "--extract-json",
        default=None,
        help="Optional Audio Extraction V1 result JSON (anchor + source reference).",
    )
    parser.add_argument(
        "--probe-json",
        default=None,
        help="Optional Media Probe V1 result JSON (source reference + timecode metadata).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    transcription_payload = _load_json(args.transcript_json)
    audio_extraction_payload = (
        _load_json(args.extract_json) if args.extract_json else None
    )
    media_probe_payload = _load_json(args.probe_json) if args.probe_json else None

    try:
        segments = transcription_result_to_transcript_segments(
            transcription_payload,
            audio_extraction_payload=audio_extraction_payload,
            media_probe_payload=media_probe_payload,
        )
    except (TranscriptSegmentError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "phase": PHASE,
                    "error": {
                        "error_code": getattr(exc, "error_code", "invalid_input"),
                        "message_sanitized": str(exc),
                    },
                    "segments": [],
                },
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 2

    output = {
        "phase": PHASE,
        "segments": [segment.to_dict() for segment in segments],
    }
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
