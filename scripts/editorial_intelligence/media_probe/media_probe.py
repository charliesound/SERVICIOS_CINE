#!/usr/bin/env python3
"""CID Editorial Intelligence - Real Media Metadata Probe V1.

Structured probe of a single local media file's metadata via ffprobe JSON
output. Consumes an ``asset_id`` from the per-file scanner and emits a
privacy-safe, contract-shaped media probe result. Pure parser is subprocess
free so it can be tested without real media or real ffprobe.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.REAL_MEDIA_METADATA_PROBE.V1"
FFPROBE_TIMEOUT_SECONDS = 10

FLOAT_ONLY_ALLOWED = False
CREATION_TIME_TREATED_AS_AUTHORITATIVE_SHOOT_DATE = False

STATE_PROBE_COMPLETED = "PROBE_COMPLETED"
STATE_PROBE_FAILED = "PROBE_FAILED"
STATE_UNSUPPORTED = "UNSUPPORTED"
STATE_NO_AUDIO = "NO_AUDIO"
STATE_NO_VIDEO = "NO_VIDEO"

MEDIA_KIND_PROBE_ERROR = "probe_error"
MEDIA_KIND_UNSUPPORTED = "unsupported"
MEDIA_KIND_VIDEO_WITH_AUDIO = "video_with_audio"
MEDIA_KIND_VIDEO_WITHOUT_AUDIO = "video_without_audio"
MEDIA_KIND_STANDALONE_AUDIO = "standalone_audio"
MEDIA_KIND_MULTIPLE_AUDIO_STREAMS = "multiple_audio_streams"

EMBEDDED_TIMECODE_PRESENT = "present"
EMBEDDED_TIMECODE_ABSENT = "absent"
EMBEDDED_TIMECODE_INVALID = "invalid"


def sanitize_source_label(source_path: str | Path) -> str:
    return Path(source_path).name


def build_ffprobe_command(source_path: str | Path) -> list[str]:
    return [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(Path(source_path)),
    ]


def parse_rational(value: object) -> dict[str, Any] | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    if text == "N/A":
        return {"original": text, "numerator": None, "denominator": None}
    if "/" not in text:
        try:
            return {"original": text, "numerator": int(text), "denominator": 1}
        except ValueError:
            return {"original": text, "numerator": None, "denominator": None}
    raw_numerator, raw_denominator = text.split("/", 1)
    try:
        numerator = int(raw_numerator)
    except ValueError:
        numerator = None
    try:
        denominator = int(raw_denominator)
    except ValueError:
        denominator = None
    return {
        "original": text,
        "numerator": numerator,
        "denominator": denominator,
    }


def effective_fps_from_rational(rational: dict[str, Any] | None) -> float | None:
    if rational is None:
        return None
    numerator = rational.get("numerator")
    denominator = rational.get("denominator")
    if not isinstance(numerator, int) or not isinstance(denominator, int):
        return None
    if denominator == 0:
        return None
    return numerator / denominator


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


def _parse_video_stream(stream: dict[str, Any]) -> dict[str, Any]:
    avg_frame_rate = parse_rational(stream.get("avg_frame_rate"))
    r_frame_rate = parse_rational(stream.get("r_frame_rate"))
    return {
        "stream_index": stream.get("index"),
        "codec_name": stream.get("codec_name"),
        "codec_long_name": stream.get("codec_long_name"),
        "width": _parse_int(stream.get("width")),
        "height": _parse_int(stream.get("height")),
        "pix_fmt": stream.get("pix_fmt"),
        "avg_frame_rate": avg_frame_rate,
        "r_frame_rate": r_frame_rate,
        "effective_fps": effective_fps_from_rational(avg_frame_rate),
        "time_base": stream.get("time_base"),
        "start_pts": _parse_int(stream.get("start_pts")),
        "start_time": _parse_float(stream.get("start_time")),
    }


def _parse_audio_stream(stream: dict[str, Any]) -> dict[str, Any]:
    return {
        "stream_index": stream.get("index"),
        "codec_name": stream.get("codec_name"),
        "sample_rate": _parse_int(stream.get("sample_rate")),
        "channels": _parse_int(stream.get("channels")),
        "channel_layout": stream.get("channel_layout"),
        "sample_fmt": stream.get("sample_fmt"),
        "bit_rate": _parse_int(stream.get("bit_rate")),
    }


def _collect_timecode_candidates(
    format_data: dict[str, Any],
    streams: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    format_tags = format_data.get("tags") or {}
    for key, value in format_tags.items():
        if key.lower() == "timecode" and value:
            candidates.append(
                {
                    "source": "format_tag",
                    "key": key,
                    "value": str(value),
                    "stream_index": None,
                }
            )
    for stream in streams:
        tags = stream.get("tags") or {}
        for key, value in tags.items():
            if key.lower() == "timecode" and value:
                candidates.append(
                    {
                        "source": "stream_tag",
                        "key": key,
                        "value": str(value),
                        "stream_index": stream.get("index"),
                    }
                )
    return candidates


def _select_canonical_timecode(
    candidates: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not candidates:
        return None
    stream_candidates = [candidate for candidate in candidates if candidate["source"] == "stream_tag"]
    if not stream_candidates:
        return candidates[0]
    stream_candidates.sort(key=lambda item: item["stream_index"] or 0)
    return stream_candidates[0]


def _extract_creation_time(
    format_data: dict[str, Any],
    streams: list[dict[str, Any]],
) -> tuple[str | None, str | None]:
    format_tags = format_data.get("tags") or {}
    for key, value in format_tags.items():
        if key.lower() == "creation_time" and value:
            return str(value), "format_tag"
    for stream in streams:
        tags = stream.get("tags") or {}
        for key, value in tags.items():
            if key.lower() == "creation_time" and value:
                return str(value), "stream_tag"
    return None, None


def _normalize_creation_time(value: str | None) -> str | None:
    if not value:
        return None
    try:
        normalized = value.strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc)
        return parsed.isoformat()
    except (TypeError, ValueError):
        return None


def _select_preferred_audio_stream(
    audio_streams: list[dict[str, Any]],
) -> int | None:
    if not audio_streams:
        return None
    qualified = [
        stream
        for stream in audio_streams
        if (_parse_int(stream.get("channels")) or 0) <= 2
        and (_parse_int(stream.get("sample_rate")) or 0) > 0
    ]
    pool = qualified or audio_streams
    pool.sort(
        key=lambda item: (
            -int(_parse_int(item.get("sample_rate")) or 0),
            int(item.get("index") or 0),
        )
    )
    return pool[0].get("index")


def _base_result(asset_id: str, source_path: str | Path) -> dict[str, Any]:
    return {
        "phase": PHASE,
        "asset_id": asset_id,
        "media_probe_state": None,
        "media_kind": None,
        "source_reference": {
            "internal_local_source_reference": str(Path(source_path)),
            "sanitized_external_source_label": sanitize_source_label(source_path),
        },
        "container": {
            "format_name": None,
            "format_long_name": None,
            "duration_seconds": None,
            "start_time_seconds": None,
            "size_bytes": None,
        },
        "video": {
            "has_video": False,
            "video_stream_count": 0,
            "streams": [],
        },
        "audio": {
            "has_audio": False,
            "audio_stream_count": 0,
            "streams": [],
            "multiple_audio_streams": False,
            "preferred_audio_stream_index": None,
        },
        "timecode": {
            "TIMECODE_PRESENT": False,
            "embedded_timecode": None,
            "embedded_timecode_status": EMBEDDED_TIMECODE_ABSENT,
            "embedded_timecode_source": None,
            "embedded_timecode_candidates": [],
        },
        "creation_time": {
            "creation_time_present": False,
            "creation_time_raw": None,
            "creation_time_normalized": None,
            "creation_time_source": None,
        },
        "error": {
            "error_code": None,
            "stage": None,
            "message_sanitized": None,
            "ffprobe_exit_code": None,
            "timed_out": False,
        },
        "warnings": [],
    }


def _state_and_kind(
    has_video: bool,
    has_audio: bool,
    audio_stream_count: int,
) -> tuple[str, str]:
    if has_video and has_audio:
        if audio_stream_count > 1:
            return STATE_PROBE_COMPLETED, MEDIA_KIND_MULTIPLE_AUDIO_STREAMS
        return STATE_PROBE_COMPLETED, MEDIA_KIND_VIDEO_WITH_AUDIO
    if has_video:
        return STATE_NO_AUDIO, MEDIA_KIND_VIDEO_WITHOUT_AUDIO
    if has_audio:
        return STATE_NO_VIDEO, MEDIA_KIND_STANDALONE_AUDIO
    return STATE_UNSUPPORTED, MEDIA_KIND_UNSUPPORTED


def parse_ffprobe_payload(
    asset_id: str,
    source_path: str | Path,
    payload: dict[str, Any],
    size_bytes: int | None = None,
) -> dict[str, Any]:
    format_data = payload.get("format") or {}
    streams = payload.get("streams") or []
    result = _base_result(asset_id, source_path)
    result["container"] = {
        "format_name": format_data.get("format_name"),
        "format_long_name": format_data.get("format_long_name"),
        "duration_seconds": _parse_float(format_data.get("duration")),
        "start_time_seconds": _parse_float(format_data.get("start_time")),
        "size_bytes": size_bytes,
    }

    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]

    result["video"] = {
        "has_video": bool(video_streams),
        "video_stream_count": len(video_streams),
        "streams": [_parse_video_stream(stream) for stream in video_streams],
    }
    result["audio"] = {
        "has_audio": bool(audio_streams),
        "audio_stream_count": len(audio_streams),
        "streams": [_parse_audio_stream(stream) for stream in audio_streams],
        "multiple_audio_streams": len(audio_streams) > 1,
        "preferred_audio_stream_index": _select_preferred_audio_stream(audio_streams),
    }

    candidates = _collect_timecode_candidates(format_data, streams)
    canonical = _select_canonical_timecode(candidates)
    timecode_present = canonical is not None
    result["timecode"] = {
        "TIMECODE_PRESENT": timecode_present,
        "embedded_timecode": canonical["value"] if canonical else None,
        "embedded_timecode_status": (
            EMBEDDED_TIMECODE_PRESENT if canonical else EMBEDDED_TIMECODE_ABSENT
        ),
        "embedded_timecode_source": canonical["source"] if canonical else None,
        "embedded_timecode_candidates": candidates,
    }

    creation_raw, creation_source = _extract_creation_time(format_data, streams)
    result["creation_time"] = {
        "creation_time_present": creation_raw is not None,
        "creation_time_raw": creation_raw,
        "creation_time_normalized": _normalize_creation_time(creation_raw),
        "creation_time_source": creation_source,
    }

    warnings: list[str] = []
    for stream in result["video"]["streams"]:
        for key in ("avg_frame_rate", "r_frame_rate"):
            rational = stream.get(key)
            if rational and rational.get("denominator") == 0:
                warnings.append(f"video stream {stream.get('stream_index')}: {key} invalid 0/0")
    result["warnings"] = warnings

    state, kind = _state_and_kind(
        result["video"]["has_video"],
        result["audio"]["has_audio"],
        result["audio"]["audio_stream_count"],
    )
    result["media_probe_state"] = state
    result["media_kind"] = kind
    return result


def parse_ffprobe_json(
    asset_id: str,
    source_path: str | Path,
    raw_json: str,
    size_bytes: int | None = None,
) -> dict[str, Any]:
    result = _base_result(asset_id, source_path)
    try:
        payload = json.loads(raw_json or "{}")
    except json.JSONDecodeError:
        result["media_probe_state"] = STATE_PROBE_FAILED
        result["media_kind"] = MEDIA_KIND_PROBE_ERROR
        result["error"] = {
            "error_code": "parse_invalid_json",
            "stage": "parse",
            "message_sanitized": "ffprobe returned invalid JSON",
            "ffprobe_exit_code": None,
            "timed_out": False,
        }
        return result
    if not isinstance(payload, dict):
        result["media_probe_state"] = STATE_PROBE_FAILED
        result["media_kind"] = MEDIA_KIND_PROBE_ERROR
        result["error"] = {
            "error_code": "parse_invalid_json",
            "stage": "parse",
            "message_sanitized": "ffprobe JSON payload is not an object",
            "ffprobe_exit_code": None,
            "timed_out": False,
        }
        return result
    return parse_ffprobe_payload(asset_id, source_path, payload, size_bytes=size_bytes)


def probe_media(
    asset_id: str,
    source_path: str | Path,
    size_bytes: int | None = None,
    timeout: int = FFPROBE_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    command = build_ffprobe_command(source_path)
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        result = _base_result(asset_id, source_path)
        result["media_probe_state"] = STATE_PROBE_FAILED
        result["media_kind"] = MEDIA_KIND_PROBE_ERROR
        result["error"] = {
            "error_code": "subprocess_error",
            "stage": "subprocess",
            "message_sanitized": f"ffprobe subprocess failed: {type(exc).__name__}",
            "ffprobe_exit_code": None,
            "timed_out": isinstance(exc, subprocess.TimeoutExpired),
        }
        return result

    if completed.returncode != 0:
        result = _base_result(asset_id, source_path)
        result["media_probe_state"] = STATE_PROBE_FAILED
        result["media_kind"] = MEDIA_KIND_PROBE_ERROR
        result["error"] = {
            "error_code": "ffprobe_nonzero_exit",
            "stage": "subprocess",
            "message_sanitized": "ffprobe exited with a non-zero status",
            "ffprobe_exit_code": completed.returncode,
            "timed_out": False,
        }
        return result

    return parse_ffprobe_json(asset_id, source_path, completed.stdout or "", size_bytes=size_bytes)
