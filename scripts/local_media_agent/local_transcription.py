"""CID Local Media Agent local transcription.

Minimal audio extraction + transcription integration for the LMA operator.
Uses approved BtbN ffmpeg for audio extraction and existing CID transcription
pipeline for STT. No backend, no database, no network (after model load).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any


TRANSCRIPTION_SCHEMA_VERSION = "cid.local_media_agent.local_transcription.v1"
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNEL_COUNT = 1
AUDIO_CODEC = "pcm_s16le"
AUDIO_CONTAINER = "wav"
FFMPEG_TIMEOUT_SECONDS = 120

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"})
AUDIO_EXTENSIONS = frozenset({".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"})


def _resolve_ffmpeg_path() -> str:
    configured = os.environ.get("CID_FFMPEG_PATH")
    if configured:
        return configured
    packaged = _resolve_packaged_ffmpeg()
    if packaged:
        return packaged
    raise RuntimeError(
        "No approved ffmpeg binary found. "
        "Set the CID_FFMPEG_PATH environment variable to the approved BtbN ffmpeg path."
    )


def _resolve_packaged_ffmpeg() -> str | None:
    """Check for a CID-packaged ffmpeg relative to this file's location."""
    here = Path(__file__).resolve().parent
    for depth in (here, here.parent, here.parents[1] if len(here.parents) > 1 else here):
        candidate = depth / "runtime" / "ffmpeg" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
        candidate = depth / "runtime" / "bin" / "ffmpeg.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def extract_audio_to_wav(
    source_path: str | Path,
    *,
    ffmpeg_path: str | None = None,
    temp_dir: str | Path | None = None,
) -> Path:
    """Extract audio from a media file to PCM WAV mono 16kHz s16le.

    Returns the path to the temporary WAV file. Caller is responsible for cleanup.
    """
    tool = ffmpeg_path or _resolve_ffmpeg_path()
    source = Path(source_path)
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")

    td = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
    td.mkdir(parents=True, exist_ok=True)
    out_name = f"cid_audio_{uuid.uuid4().hex[:12]}.{AUDIO_CONTAINER}"
    output_path = td / out_name

    cmd = [
        tool,
        "-v", "error",
        "-y",
        "-i", str(source),
        "-vn",
        "-ac", str(AUDIO_CHANNEL_COUNT),
        "-ar", str(AUDIO_SAMPLE_RATE),
        "-c:a", AUDIO_CODEC,
        str(output_path),
    ]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=FFMPEG_TIMEOUT_SECONDS,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg exit {proc.returncode}: {proc.stderr[:300]}")
    if not output_path.is_file():
        raise RuntimeError("ffmpeg produced no output file")

    return output_path


def _get_audio_duration(wav_path: Path) -> float | None:
    """Read duration from a WAV file header (bytes 28-31, little-endian uint32)."""
    try:
        with open(wav_path, "rb") as f:
            f.seek(22)
            num_channels = int.from_bytes(f.read(2), "little")
            sample_rate = int.from_bytes(f.read(4), "little")
            f.seek(4)
            chunk_size = int.from_bytes(f.read(4), "little")
            data_size = chunk_size - 36
            bytes_per_sample = 2
            duration = data_size / (sample_rate * num_channels * bytes_per_sample)
            return round(duration, 3)
    except Exception:
        return None


def transcribe_media_file(
    media_path: str | Path,
    model_local_path: str | Path,
    *,
    asset_id: str | None = None,
    language_hint: str | None = None,
    device: str = "cpu",
    compute_type: str = "float32",
    ffmpeg_path: str | None = None,
    temp_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Extract audio and transcribe a single media file.

    Returns a structured dict with transcription results.
    """
    source = Path(media_path)
    if not source.is_file():
        return {
            "schema_version": TRANSCRIPTION_SCHEMA_VERSION,
            "status": "FILE_NOT_FOUND",
            "relative_path": str(media_path),
            "error": {"message": f"File not found: {media_path}"},
        }

    asset = asset_id or source.stem
    start_time = time.monotonic()

    # Extract audio
    wav_path = None
    try:
        wav_path = extract_audio_to_wav(source, ffmpeg_path=ffmpeg_path, temp_dir=temp_dir)
        duration = _get_audio_duration(wav_path)

        # Transcribe using existing CID pipeline
        from scripts.editorial_intelligence.transcription.transcription import (
            FasterWhisperTranscriptionBackend,
            TranscriptionRequest,
            transcribe,
        )

        backend = FasterWhisperTranscriptionBackend(
            model_local_path=model_local_path,
            device=device,
            compute_type=compute_type,
        )
        request = TranscriptionRequest(
            asset_id=asset,
            temporary_audio_path=str(wav_path),
            audio_duration_seconds=duration,
            language_hint=language_hint,
            model_local_path=model_local_path,
            device=device,
        )

        result = transcribe(request, backend)
        payload = result.to_dict()
        elapsed = time.monotonic() - start_time

        return {
            "schema_version": TRANSCRIPTION_SCHEMA_VERSION,
            "status": payload.get("status"),
            "relative_path": source.name,
            "asset_id": asset,
            "detected_language": payload.get("detected_language"),
            "language_probability": payload.get("language_probability"),
            "audio_duration_seconds": duration,
            "processing_seconds": round(elapsed, 2),
            "model_identifier": backend.model_identifier_sanitized,
            "engine": "faster-whisper",
            "ctranslate2_compute_type": compute_type,
            "device": device,
            "segments": payload.get("segments", []),
            "error": payload.get("error"),
            "warnings": payload.get("warnings", []),
        }

    except Exception as exc:
        elapsed = time.monotonic() - start_time
        return {
            "schema_version": TRANSCRIPTION_SCHEMA_VERSION,
            "status": "TRANSCRIPTION_FAILED",
            "relative_path": source.name,
            "asset_id": asset,
            "processing_seconds": round(elapsed, 2),
            "error": {"message": str(exc)[:300]},
        }
    finally:
        if wav_path and wav_path.is_file():
            try:
                wav_path.unlink()
            except OSError:
                pass


def select_transcription_samples(
    metadata_results: list[dict[str, Any]],
    *,
    max_video: int = 1,
    max_audio: int = 2,
) -> list[dict[str, Any]]:
    """Select representative sample files for transcription from metadata results.

    Prefers shorter durations. Skips images and AppleDouble files.
    """
    video_candidates = []
    audio_candidates = []

    for r in metadata_results:
        cat = r.get("category", "")
        rel = r.get("relative_path", "")
        if rel.startswith("._"):
            continue
        if cat == "video":
            video_candidates.append(r)
        elif cat == "audio":
            audio_candidates.append(r)

    video_candidates.sort(key=lambda x: x.get("duration_seconds") or 99999)
    audio_candidates.sort(key=lambda x: x.get("duration_seconds") or 99999)

    selected = video_candidates[:max_video] + audio_candidates[:max_audio]
    return selected
