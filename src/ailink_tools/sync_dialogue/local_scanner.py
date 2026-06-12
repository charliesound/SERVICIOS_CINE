from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMediaFile,
    SyncDialogueMediaKind,
    SyncDialogueScanResult,
)

VIDEO_EXTENSIONS = frozenset({".mov", ".mp4", ".mxf"})
AUDIO_EXTENSIONS = frozenset({".wav", ".bwf", ".mp3"})
TEMP_SUFFIXES = (".tmp", ".temp", ".part", ".crdownload")
TEMP_PREFIXES = ("~$",)
FFPROBE_TIMEOUT_SECONDS = 30


def scan_folder(root_path: str | Path, *, probe: bool = True) -> SyncDialogueScanResult:
    root = Path(root_path).expanduser().resolve()
    if not root.exists():
        raise ValueError("input path does not exist")
    if not root.is_dir():
        raise ValueError("input path must be a directory")

    ffprobe_path = shutil.which("ffprobe") if probe else None
    media_files: list[SyncDialogueMediaFile] = []
    unsupported_count = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_path = path.relative_to(root)
        if _is_ignored_path(relative_path):
            continue

        kind = _classify_extension(path.suffix)
        if kind == "other":
            unsupported_count += 1
            continue

        media_files.append(
            _build_media_file(
                path=path,
                root=root,
                kind=kind,
                probe=probe,
                ffprobe_path=ffprobe_path,
            )
        )

    video_count = sum(1 for media_file in media_files if media_file.kind == "video")
    audio_count = sum(1 for media_file in media_files if media_file.kind == "audio")
    return SyncDialogueScanResult(
        root_path=str(root),
        total_files=video_count + audio_count + unsupported_count,
        video_count=video_count,
        audio_count=audio_count,
        unsupported_count=unsupported_count,
        media_files=media_files,
    )


def _is_ignored_path(relative_path: Path) -> bool:
    parts = relative_path.parts
    if any(part.startswith(".") for part in parts):
        return True
    filename = relative_path.name
    lower_name = filename.lower()
    if filename.startswith(TEMP_PREFIXES):
        return True
    return lower_name.endswith(TEMP_SUFFIXES)


def _classify_extension(extension: str) -> SyncDialogueMediaKind:
    normalized = extension.lower()
    if normalized in VIDEO_EXTENSIONS:
        return "video"
    if normalized in AUDIO_EXTENSIONS:
        return "audio"
    return "other"


def _build_media_file(
    *,
    path: Path,
    root: Path,
    kind: SyncDialogueMediaKind,
    probe: bool,
    ffprobe_path: str | None,
) -> SyncDialogueMediaFile:
    relative_path = path.relative_to(root).as_posix()
    base = {
        "path": str(path),
        "relative_path": relative_path,
        "filename": path.name,
        "extension": path.suffix.lower(),
        "kind": kind,
        "size_bytes": path.stat().st_size,
    }
    if not probe:
        return SyncDialogueMediaFile(**base, probe_status="not_run")
    if not ffprobe_path:
        return SyncDialogueMediaFile(**base, probe_status="ffprobe_missing")

    probe_result = _run_ffprobe(ffprobe_path, path)
    if probe_result["status"] == "failed":
        return SyncDialogueMediaFile(
            **base,
            probe_status="failed",
            error_message=probe_result["error_message"],
        )

    metadata = _parse_ffprobe_metadata(probe_result["payload"])
    return SyncDialogueMediaFile(**base, probe_status="ok", **metadata)


def _run_ffprobe(ffprobe_path: str, path: Path) -> dict[str, Any]:
    command = [
        ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=FFPROBE_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        return {"status": "failed", "error_message": _sanitize_error(str(exc))}

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "ffprobe failed"
        return {"status": "failed", "error_message": _sanitize_error(message)}
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return {"status": "failed", "error_message": "ffprobe returned invalid JSON"}
    return {"status": "ok", "payload": payload}


def _parse_ffprobe_metadata(payload: dict[str, Any]) -> dict[str, object]:
    streams = payload.get("streams") or []
    format_data = payload.get("format") or {}
    first_video_stream = _first_stream(streams, "video")
    first_audio_stream = _first_stream(streams, "audio")
    primary_stream = first_video_stream or first_audio_stream or (streams[0] if streams else {})

    return {
        "duration_seconds": _parse_float(
            primary_stream.get("duration") or format_data.get("duration")
        ),
        "timecode": _extract_timecode(primary_stream, format_data),
        "fps": _parse_frame_rate(
            primary_stream.get("avg_frame_rate") or primary_stream.get("r_frame_rate")
        ),
        "audio_channels": _parse_int(first_audio_stream.get("channels"))
        if first_audio_stream
        else None,
        "codec_name": primary_stream.get("codec_name"),
        "format_name": format_data.get("format_name"),
        "error_message": None,
    }


def _first_stream(streams: list[dict[str, Any]], codec_type: str) -> dict[str, Any]:
    for stream in streams:
        if stream.get("codec_type") == codec_type:
            return stream
    return {}


def _extract_timecode(stream: dict[str, Any], format_data: dict[str, Any]) -> str | None:
    for source in (stream, format_data):
        tags = source.get("tags") or {}
        for key, value in tags.items():
            if key.lower() == "timecode" and value:
                return str(value)
    return None


def _parse_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: object) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_frame_rate(value: object) -> float | None:
    if not value or value == "0/0":
        return None
    text = str(value)
    if "/" not in text:
        return _parse_float(text)
    numerator, denominator = text.split("/", 1)
    try:
        denominator_value = float(denominator)
        if denominator_value == 0:
            return None
        return float(numerator) / denominator_value
    except ValueError:
        return None


def _sanitize_error(message: str) -> str:
    sanitized = message.replace("\n", " ").replace("\r", " ").strip()
    return sanitized[:300] if sanitized else "ffprobe failed"
