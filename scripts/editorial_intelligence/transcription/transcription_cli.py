#!/usr/bin/env python3
"""CID Editorial Intelligence - Transcription CLI.

Thin wrapper around the transcription core. Consumes an Audio Extraction V1 JSON
result (from the committed audio extraction CLI) and emits a structured JSON
transcription result. Never auto-downloads models, never runs STT with network,
and only exposes the V1 surface: model path, device, language hint, timeout.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.editorial_intelligence.transcription.transcription import (
    FasterWhisperTranscriptionBackend,
    TranscriptionRequest,
    transcribe,
)

CLI_NAME = "cid-editorial-transcribe"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe an Audio Extraction V1 PCM WAV derivative."
    )
    parser.add_argument(
        "--extract-json",
        required=True,
        help="Path to an Audio Extraction V1 result JSON file.",
    )
    parser.add_argument(
        "--model-local-path",
        required=True,
        help="Explicit local directory with a CTranslate2/faster-whisper model.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Inference device (default: cpu).",
    )
    parser.add_argument(
        "--language-hint",
        default=None,
        help="Optional language hint forwarded to the backend.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Optional timeout hint in seconds (carried for traceability).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    with open(Path(args.extract_json), encoding="utf-8") as handle:
        extract_result = json.load(handle)

    audio = extract_result.get("audio") or {}
    request = TranscriptionRequest(
        asset_id=extract_result.get("asset_id"),
        temporary_audio_path=audio.get("extracted_audio_temp_ref"),
        source_audio_stream_index=audio.get("source_audio_stream_index"),
        extracted_audio_start_seconds=audio.get("extracted_audio_start_seconds"),
        audio_duration_seconds=audio.get("duration_seconds"),
        language_hint=args.language_hint,
        model_local_path=args.model_local_path,
        device=args.device,
        timeout_seconds=args.timeout,
    )
    backend = FasterWhisperTranscriptionBackend(
        request.model_local_path,
        device=request.device,
    )
    result = transcribe(request, backend)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
