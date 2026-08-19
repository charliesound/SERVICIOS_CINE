"""CID Local Media Agent ffprobe metadata extraction.

Read-only metadata extraction using the approved BtbN LGPL ffprobe binary.
No media modification, no network, no database.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "cid.local_media_agent.ffprobe_metadata_extraction.v1"

FFPROBE_ENV_VAR = "CID_FFPROBE_PATH"
FFPROBE_TIMEOUT_SECONDS = 30

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"})
AUDIO_EXTENSIONS = frozenset({".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"})
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf"})


def resolve_ffprobe_path(explicit: str | None = None) -> str:
    if explicit:
        return explicit
    configured = os.environ.get(FFPROBE_ENV_VAR)
    if configured:
        return configured
    packaged = _resolve_packaged_ffprobe()
    if packaged:
        return packaged
    raise RuntimeError(
        "No approved ffprobe binary found. "
        f"Set the {FFPROBE_ENV_VAR} environment variable to the approved BtbN ffprobe path."
    )


def _resolve_packaged_ffprobe() -> str | None:
    """Check for a CID-packaged ffprobe relative to this file's location."""
    here = Path(__file__).resolve().parent
    for depth in (here, here.parent, here.parents[1] if len(here.parents) > 1 else here):
        candidate = depth / "runtime" / "ffmpeg" / "bin" / "ffprobe.exe"
        if candidate.is_file():
            return str(candidate)
        candidate = depth / "runtime" / "bin" / "ffprobe.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def extract_metadata(
    input_root: str | Path,
    scanner_result: dict[str, Any],
    *,
    ffprobe_path: str | None = None,
) -> dict[str, Any]:
    tool = resolve_ffprobe_path(ffprobe_path)
    ext_summary = scanner_result.get("extension_summary", {})
    media_files = _collect_media_files(input_root, ext_summary)

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    start = time.monotonic()

    for item in media_files:
        try:
            meta = _probe_one(tool, Path(item["abs_path"]))
            results.append({
                "relative_path": item["relative_path"],
                "category": item["category"],
                "file_size_bytes": item["file_size"],
                **meta,
            })
        except Exception as exc:
            errors.append({
                "relative_path": item["relative_path"],
                "category": item["category"],
                "error": str(exc)[:200],
            })

    elapsed = time.monotonic() - start

    return {
        "schema_version": SCHEMA_VERSION,
        "input_root_label": "SANITIZED_LOCAL_FOLDER_INPUT",
        "ffprobe_path": _sanitize_tool_path(tool),
        "ffprobe_timeout_seconds": FFPROBE_TIMEOUT_SECONDS,
        "media_attempted": len(media_files),
        "metadata_success_count": len(results),
        "metadata_error_count": len(errors),
        "elapsed_seconds": round(elapsed, 2),
        "results": results,
        "errors": errors,
    }


def _collect_media_files(
    input_root: str | Path,
    ext_summary: dict[str, int],
) -> list[dict[str, Any]]:
    root = Path(input_root)
    media_exts = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | IMAGE_EXTENSIONS
    files: list[dict[str, Any]] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("._"):
            continue
        ext = path.suffix.lower()
        if ext not in media_exts:
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        cat = "video" if ext in VIDEO_EXTENSIONS else ("audio" if ext in AUDIO_EXTENSIONS else "image")
        files.append({
            "abs_path": str(path),
            "relative_path": rel.as_posix(),
            "category": cat,
            "extension": ext,
            "file_size": size,
        })
    return files


def _probe_one(tool: str, path: Path) -> dict[str, Any]:
    cmd = [
        tool,
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=FFPROBE_TIMEOUT_SECONDS,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe exit {proc.returncode}: {proc.stderr[:200]}")

    raw = json.loads(proc.stdout)
    return _parse_ffprobe(raw)


def _parse_ffprobe(data: dict[str, Any]) -> dict[str, Any]:
    fmt = data.get("format", {})
    streams = data.get("streams", [])

    video_streams = [s for s in streams if s.get("codec_type") == "video"]
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    result: dict[str, Any] = {
        "format_name": fmt.get("format_name"),
        "format_long_name": fmt.get("format_long_name"),
        "duration_seconds": _safe_float(fmt.get("duration")),
        "creation_time": _tag_value(fmt, "creation_time"),
        "timecode": _find_timecode(streams, fmt),
    }

    if video_streams:
        vs = video_streams[0]
        result["video"] = {
            "codec": vs.get("codec_name"),
            "codec_long": vs.get("codec_long_name"),
            "width": _safe_int(vs.get("width")),
            "height": _safe_int(vs.get("height")),
            "frame_rate": _parse_frame_rate(vs.get("avg_frame_rate"), vs.get("r_frame_rate")),
            "pixel_format": vs.get("pix_fmt"),
            "bit_depth": _safe_int(vs.get("bits_per_raw_sample")),
            "stream_count": len(video_streams),
        }

    if audio_streams:
        aus = audio_streams[0]
        result["audio"] = {
            "codec": aus.get("codec_name"),
            "codec_long": aus.get("codec_long_name"),
            "sample_rate": _safe_int(aus.get("sample_rate")),
            "channel_count": _safe_int(aus.get("channels")),
            "channel_layout": aus.get("channel_layout"),
            "bit_depth": _safe_int(aus.get("bits_per_raw_sample")),
            "stream_count": len(audio_streams),
        }

    return result


def _parse_frame_rate(avg: str | None, raw: str | None) -> dict[str, Any]:
    avg_val = _frac_to_float(avg)
    raw_val = _frac_to_float(raw)
    if avg_val is not None and raw_val is not None and abs(avg_val - raw_val) > 0.1:
        return {"display": _human_framerate(avg_val), "raw_avg": avg, "raw_frame": raw, "variable": True}
    display = _human_framerate(avg_val or raw_val)
    return {"display": display, "raw_avg": avg, "raw_frame": raw, "variable": False}


def _frac_to_float(frac: str | None) -> float | None:
    if not frac or frac == "0/0":
        return None
    parts = frac.split("/")
    if len(parts) != 2:
        return None
    try:
        num, den = int(parts[0]), int(parts[1])
        if den == 0:
            return None
        return num / den
    except (ValueError, ZeroDivisionError):
        return None


def _human_framerate(val: float | None) -> str | None:
    if val is None:
        return None
    common = {23.976, 24.0, 25.0, 29.97, 30.0, 50.0, 59.94, 60.0}
    for c in common:
        if abs(val - c) < 0.01:
            return str(c) if c != int(c) else str(int(c))
    return f"{val:.2f}"


def _find_timecode(streams: list[dict], fmt: dict) -> str | None:
    for s in streams:
        tags = s.get("tags", {})
        tc = tags.get("timecode")
        if tc:
            return tc
    fmt_tags = fmt.get("tags", {})
    tc = fmt_tags.get("timecode")
    return tc


def _tag_value(container: dict, key: str) -> str | None:
    tags = container.get("tags", {})
    return tags.get(key)


def _safe_int(val: Any) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return round(float(val), 3)
    except (ValueError, TypeError):
        return None


def _sanitize_tool_path(tool: str) -> str:
    if "/" in tool or "\\" in tool:
        return os.path.basename(tool)
    return tool
