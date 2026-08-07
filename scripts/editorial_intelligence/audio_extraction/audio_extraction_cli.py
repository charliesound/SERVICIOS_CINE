#!/usr/bin/env python3
"""CID Editorial Intelligence - Audio Extraction CLI.

Thin wrapper around the audio extraction core. Consumes a Media Probe V1 JSON
result (from the committed media probe CLI) and emits a structured JSON
extraction result. Never re-runs ffprobe and never rescans folders.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.editorial_intelligence.audio_extraction.audio_extraction import (
    extract_audio,
)

CLI_NAME = "cid-editorial-audio-extract"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract an STT-ready PCM WAV mono 16 kHz derivative from a Media Probe result."
    )
    parser.add_argument(
        "--probe-json",
        required=True,
        help="Path to a Media Probe V1 result JSON file.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional explicit ffmpeg subprocess timeout in seconds.",
    )
    parser.add_argument(
        "--ffmpeg",
        default=None,
        help="Optional explicit ffmpeg executable path.",
    )
    parser.add_argument(
        "--temp-dir",
        default=None,
        help="Optional temp directory for the derivative (defaults to OS temp dir).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    with open(Path(args.probe_json), encoding="utf-8") as handle:
        probe_result = json.load(handle)
    with extract_audio(
        probe_result,
        timeout_seconds=args.timeout,
        ffmpeg_path=args.ffmpeg,
        temp_dir=args.temp_dir,
    ) as extracted:
        print(json.dumps(extracted.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
