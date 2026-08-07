#!/usr/bin/env python3
"""CID Editorial Intelligence - Audio Extraction V1.

Consumes a committed Media Probe V1 result (``scripts/editorial_intelligence/
media_probe/media_probe.py`` output shape) and produces a temporary, STT-ready
PCM WAV mono 16 kHz s16le derivative via a single ffmpeg subprocess. The pure
decision helpers are subprocess-free so they can be tested with mocked
``subprocess.run`` and no real media or real ffmpeg.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.AUDIO_EXTRACTION.V1"

STATE_AUDIO_EXTRACTION_COMPLETED = "AUDIO_EXTRACTION_COMPLETED"
STATE_AUDIO_EXTRACTION_FAILED = "AUDIO_EXTRACTION_FAILED"
STATE_AUDIO_EXTRACTION_NOT_APPLICABLE = "AUDIO_EXTRACTION_NOT_APPLICABLE"
STATE_AUDIO_EXTRACTION_TIMED_OUT = "AUDIO_EXTRACTION_TIMED_OUT"

AUDIO_STREAM_SELECTION_POLICY = "REUSE_MEDIA_PROBE_PREFERRED_AUDIO_STREAM_INDEX"

TRANSCRIPTION_AUDIO_CANONICAL_FORMAT = "PCM_WAV_MONO_16000_S16LE"
TRANSCRIPTION_AUDIO_SAMPLE_RATE = 16000
TRANSCRIPTION_AUDIO_CHANNEL_COUNT = 1
TRANSCRIPTION_AUDIO_SAMPLE_FORMAT = "s16"
OUTPUT_CONTAINER = "wav"

FFMPEG_BINARY_ENV_VAR = "CID_FFMPEG_PATH"
FFMPEG_DEFAULT_BINARY = "ffmpeg"

AUDIO_EXTRACTION_TIMEOUT_FACTOR = 2.0
AUDIO_EXTRACTION_TIMEOUT_FIXED_OVERHEAD_SECONDS = 30.0
AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS = 60.0
AUDIO_EXTRACTION_TIMEOUT_ABSOLUTE_MAX_SECONDS = 24 * 60 * 60

TEMP_FILENAME_PREFIX = "cid_audio_extract_"
TEMP_FILENAME_SUFFIX = ".wav"


def sanitize_asset_id_for_filename(asset_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(asset_id))


def resolve_ffmpeg_path(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    configured = os.environ.get(FFMPEG_BINARY_ENV_VAR)
    if configured:
        return configured
    found = shutil.which("ffmpeg")
    return found or FFMPEG_DEFAULT_BINARY


def select_audio_stream_index(
    audio: dict[str, Any],
    override: int | None = None,
) -> int | None:
    if override is not None:
        return override
    preferred = audio.get("preferred_audio_stream_index")
    if preferred is not None:
        return int(preferred)
    streams = audio.get("streams") or []
    for stream in streams:
        index = stream.get("stream_index")
        if index is not None:
            return int(index)
    return None


def compute_extraction_timeout(duration_seconds: object) -> float:
    if isinstance(duration_seconds, bool):
        return AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS
    if not isinstance(duration_seconds, (int, float)) or duration_seconds is None:
        return AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS
    if duration_seconds <= 0:
        return AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS
    candidate = float(duration_seconds) * AUDIO_EXTRACTION_TIMEOUT_FACTOR
    candidate += AUDIO_EXTRACTION_TIMEOUT_FIXED_OVERHEAD_SECONDS
    bounded = max(candidate, AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS)
    return min(bounded, AUDIO_EXTRACTION_TIMEOUT_ABSOLUTE_MAX_SECONDS)


def build_temp_audio_path(
    asset_id: str,
    stream_index: int | None,
    temp_dir: str | Path | None = None,
) -> Path:
    root = Path(temp_dir) if temp_dir is not None else Path(tempfile.gettempdir())
    safe_asset = sanitize_asset_id_for_filename(asset_id)
    suffix = uuid.uuid4().hex[:8]
    name = f"{TEMP_FILENAME_PREFIX}{safe_asset}_stream{stream_index}_{suffix}{TEMP_FILENAME_SUFFIX}"
    return root / name


def build_ffmpeg_command(
    source_path: str | Path,
    stream_index: int,
    output_path: str | Path,
    ffmpeg_path: str | None = None,
) -> list[str]:
    binary = resolve_ffmpeg_path(ffmpeg_path)
    return [
        binary,
        "-v",
        "error",
        "-y",
        "-i",
        str(Path(source_path)),
        "-map",
        f"0:{stream_index}",
        "-vn",
        "-ac",
        str(TRANSCRIPTION_AUDIO_CHANNEL_COUNT),
        "-ar",
        str(TRANSCRIPTION_AUDIO_SAMPLE_RATE),
        "-c:a",
        "pcm_s16le",
        str(Path(output_path)),
    ]


def _safe_remove(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError:
        return


def _base_result(
    asset_id: str,
    source_reference: dict[str, Any],
) -> dict[str, Any]:
    return {
        "phase": PHASE,
        "state": None,
        "asset_id": asset_id,
        "source_reference": {
            "internal_local_source_reference": source_reference.get(
                "internal_local_source_reference"
            ),
            "sanitized_external_source_label": source_reference.get(
                "sanitized_external_source_label"
            ),
        },
        "audio": {
            "source_audio_stream_index": None,
            "extracted_audio_temp_ref": None,
            "extracted_audio_start_seconds": None,
            "source_stream_start_seconds": None,
            "duration_seconds": None,
            "channels_derived_from_source": None,
        },
        "extraction_parameters": {
            "sample_rate": TRANSCRIPTION_AUDIO_SAMPLE_RATE,
            "channels": TRANSCRIPTION_AUDIO_CHANNEL_COUNT,
            "sample_format": TRANSCRIPTION_AUDIO_SAMPLE_FORMAT,
            "output_container": OUTPUT_CONTAINER,
            "stream_selection_policy": AUDIO_STREAM_SELECTION_POLICY,
        },
        "error": {
            "error_code": None,
            "stage": None,
            "message_sanitized": None,
            "ffmpeg_exit_code": None,
            "timed_out": False,
        },
        "warnings": [],
    }


def _audio_stream_channels(
    audio: dict[str, Any],
    stream_index: int,
) -> int | None:
    for stream in audio.get("streams") or []:
        if stream.get("stream_index") == stream_index:
            channels = stream.get("channels")
            if isinstance(channels, int):
                return channels
            if isinstance(channels, str) and channels.isdigit():
                return int(channels)
            return None
    return None


class ExtractedAudioResult:
    """Result of an audio extraction; usable as a context-manager handle.

    The derivative temp file exists only while inside ``with``; it is removed on
    normal exit and on exception paths (never leaves orphan temp files).
    """

    def __init__(self, payload: dict[str, Any], temp_path: Path | None = None) -> None:
        self._payload = payload
        self.temp_path = temp_path

    def to_dict(self) -> dict[str, Any]:
        return dict(self._payload)

    @property
    def state(self) -> str | None:
        return self._payload.get("state")

    @property
    def path(self) -> Path | None:
        return self.temp_path

    def __enter__(self) -> "ExtractedAudioResult":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        self._payload["error"]["cleanup_error"] = None
        if self.temp_path is not None:
            try:
                self.temp_path.unlink(missing_ok=True)
            except OSError:
                self._payload["error"]["cleanup_error"] = "cleanup_failed"
                return False
            self.temp_path = None
            self._payload["audio"]["extracted_audio_temp_ref"] = None
        return False


def extract_audio(
    probe_result: dict[str, Any],
    *,
    timeout_seconds: float | None = None,
    ffmpeg_path: str | None = None,
    temp_dir: str | Path | None = None,
    stream_override: int | None = None,
) -> ExtractedAudioResult:
    asset_id = probe_result.get("asset_id")
    source_reference = probe_result.get("source_reference") or {}
    audio = probe_result.get("audio") or {}
    container = probe_result.get("container") or {}

    result = _base_result(asset_id, source_reference)
    result["audio"]["source_stream_start_seconds"] = container.get("start_time_seconds")
    result["audio"]["duration_seconds"] = container.get("duration_seconds")
    result["audio"]["extracted_audio_start_seconds"] = container.get("start_time_seconds") or 0.0

    if not audio.get("has_audio"):
        result["state"] = STATE_AUDIO_EXTRACTION_NOT_APPLICABLE
        result["audio"]["extracted_audio_start_seconds"] = None
        return ExtractedAudioResult(result)

    stream_index = select_audio_stream_index(audio, override=stream_override)
    if stream_index is None:
        result["state"] = STATE_AUDIO_EXTRACTION_FAILED
        result["error"] = {
            "error_code": "audio_stream_selection_failed",
            "stage": "validation",
            "message_sanitized": "no audio stream index could be selected",
            "ffmpeg_exit_code": None,
            "timed_out": False,
        }
        return ExtractedAudioResult(result)

    source_path = source_reference.get("internal_local_source_reference")
    if not source_path:
        result["state"] = STATE_AUDIO_EXTRACTION_FAILED
        result["error"] = {
            "error_code": "missing_source_reference",
            "stage": "validation",
            "message_sanitized": "probe result has no internal source reference",
            "ffmpeg_exit_code": None,
            "timed_out": False,
        }
        return ExtractedAudioResult(result)

    timeout = (
        timeout_seconds
        if timeout_seconds is not None
        else compute_extraction_timeout(container.get("duration_seconds"))
    )
    temp_path = build_temp_audio_path(asset_id, stream_index, temp_dir=temp_dir)
    command = build_ffmpeg_command(source_path, stream_index, temp_path, ffmpeg_path=ffmpeg_path)

    result["audio"]["source_audio_stream_index"] = stream_index
    result["audio"]["channels_derived_from_source"] = _audio_stream_channels(audio, stream_index)
    result["extraction_parameters"]["timeout_seconds"] = float(timeout)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        _safe_remove(temp_path)
        timed_out = isinstance(exc, subprocess.TimeoutExpired)
        result["state"] = (
            STATE_AUDIO_EXTRACTION_TIMED_OUT if timed_out else STATE_AUDIO_EXTRACTION_FAILED
        )
        result["error"] = {
            "error_code": "subprocess_error",
            "stage": "subprocess",
            "message_sanitized": (
                "ffmpeg timed out" if timed_out else "ffmpeg subprocess failed"
            ),
            "ffmpeg_exit_code": None,
            "timed_out": timed_out,
        }
        return ExtractedAudioResult(result)

    if completed.returncode != 0:
        _safe_remove(temp_path)
        result["state"] = STATE_AUDIO_EXTRACTION_FAILED
        result["error"] = {
            "error_code": "ffmpeg_nonzero_exit",
            "stage": "subprocess",
            "message_sanitized": "ffmpeg exited with a non-zero status",
            "ffmpeg_exit_code": completed.returncode,
            "timed_out": False,
        }
        return ExtractedAudioResult(result)

    result["state"] = STATE_AUDIO_EXTRACTION_COMPLETED
    result["audio"]["extracted_audio_temp_ref"] = str(temp_path)
    return ExtractedAudioResult(result, temp_path=temp_path)
