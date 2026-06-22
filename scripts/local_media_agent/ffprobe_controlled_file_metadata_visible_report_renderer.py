from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any


PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.V1"
)
NEXT_SAFE_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.QA.GATE.V1"
)
CONTROLLED_INPUT_POLICY = "controlled_fixture_only"
METADATA_COMMAND_KIND = "metadata_json"
SAFE_INPUT_PLACEHOLDER = "<redacted-input>"

SAFE_FLAGS = (
    "media_processing_performed",
    "scanner_executed",
    "real_media_used",
    "ffmpeg_used",
    "audio_extraction_performed",
    "sync_generated",
    "transcription_generated",
    "subtitles_generated",
    "timeline_export_generated",
    "database_write",
    "saas_upload",
    "network_call",
)

BLOCKED_OPERATIONS = (
    "scanner execution: false",
    "media processing: false",
    "audio extraction: false",
    "sync generation: false",
    "transcription generation: false",
    "subtitle generation: false",
    "timeline export: false",
    "SaaS upload: false",
    "DB write: false",
    "installer creation: false",
    "client-facing readiness: false",
    "public demo readiness: false",
    "sales demo readiness: false",
    "production readiness: false",
)

_PATH_MARKERS = (
    "/",
    "\\",
    "..",
    "~",
)


def render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str:
    """Render a deterministic visible report from an already-safe metadata payload.

    The renderer is pure: it does not read files, scan folders, call external
    commands, probe media, process media, write databases, or perform network calls.
    """

    data = payload if isinstance(payload, Mapping) else {}
    input_policy = _safe_inline_text(data.get("input_policy", "missing"))
    command_kind = _safe_inline_text(data.get("ffprobe_command_kind", "missing"))
    filename = _safe_redacted_filename(data.get("input_path_redacted"))
    flags_safe = _safe_flags_are_false(data)
    blocked = (
        input_policy != CONTROLLED_INPUT_POLICY
        or command_kind != METADATA_COMMAND_KIND
        or not flags_safe
    )

    metadata = data.get("metadata") if isinstance(data.get("metadata"), Mapping) else {}
    metadata_format = metadata.get("format")
    raw_streams = metadata.get("streams")
    streams = list(raw_streams) if _is_mapping_sequence(raw_streams) else []
    visible_streams = [] if blocked else streams

    if blocked:
        result = "BLOCKED_UNSAFE_CONTROLLED_METADATA_PAYLOAD"
        format_summary = "blocked before metadata rendering"
    else:
        result = _safe_inline_text(data.get("result", "unknown"))
        format_summary = _format_summary(metadata_format)

    video_streams = [stream for stream in visible_streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in visible_streams if stream.get("codec_type") == "audio"]
    unknown_streams = [
        stream for stream in visible_streams if stream.get("codec_type") not in {"video", "audio"}
    ]

    lines = [
        "# CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
        "",
        f"## Phase\n{PHASE}",
        f"## Input Policy\n{input_policy}",
        f"## Input\n{filename}",
        f"## Preflight Result\n{result}",
        f"## Format Summary\n{format_summary}",
        (
            "## Stream Summary\n"
            f"total={len(visible_streams)}, video={len(video_streams)}, "
            f"audio={len(audio_streams)}, unknown={len(unknown_streams)}"
        ),
        f"## Video Streams\n{_video_summary(video_streams)}",
        f"## Audio Streams\n{_audio_summary(audio_streams)}",
        f"## Unknown Streams\n{_unknown_summary(unknown_streams)}",
        (
            "## Safety Boundary\n"
            "local-only; controlled-fixture-only; pure renderer; no scanner, media "
            "processing, network call, or database write performed"
        ),
        f"## Blocked Operations\n{_blocked_operations_summary()}",
        (
            "## Human Review Required\n"
            "Human review is required before any client-facing or production use."
        ),
        f"## Next Safe Phase\n{NEXT_SAFE_PHASE}",
    ]

    if result != "FFPROBE_METADATA_PREFLIGHT_PASS":
        lines.insert(-1, f"## Failure Note\n{_safe_inline_text(data.get('failure_reason', 'not applicable'))}")

    return "\n\n".join(lines).rstrip() + "\n"


def _safe_flags_are_false(data: Mapping[str, object]) -> bool:
    return all(data.get(flag) is False for flag in SAFE_FLAGS)


def _is_mapping_sequence(value: object) -> bool:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return False
    return all(isinstance(item, Mapping) for item in value)


def _safe_redacted_filename(value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return SAFE_INPUT_PLACEHOLDER
    if re.match(r"^[A-Za-z]:", text):
        return SAFE_INPUT_PLACEHOLDER
    if text.startswith(("//", "\\\\")):
        return SAFE_INPUT_PLACEHOLDER
    if any(marker in text for marker in _PATH_MARKERS):
        return SAFE_INPUT_PLACEHOLDER
    return _safe_inline_text(text)


def _format_summary(metadata_format: object) -> str:
    if not isinstance(metadata_format, Mapping):
        return "format unavailable"
    return "; ".join([
        f"format={_safe_inline_text(metadata_format.get('format_name', 'unknown'))}",
        f"duration={_safe_inline_text(metadata_format.get('duration', 'unknown'))}",
        f"size={_safe_inline_text(metadata_format.get('size', 'unknown'))}",
    ])


def _video_summary(streams: Sequence[Mapping[str, object]]) -> str:
    return "; ".join(
        ", ".join([
            f"index={_safe_inline_text(stream.get('index', 'unknown'))}",
            f"codec={_safe_inline_text(stream.get('codec_name', 'unknown'))}",
            f"size={_safe_inline_text(stream.get('width', 'unknown'))}x{_safe_inline_text(stream.get('height', 'unknown'))}",
            f"duration={_safe_inline_text(stream.get('duration', 'unknown'))}",
        ])
        for stream in streams
    ) or "no video streams reported"


def _audio_summary(streams: Sequence[Mapping[str, object]]) -> str:
    return "; ".join(
        ", ".join([
            f"index={_safe_inline_text(stream.get('index', 'unknown'))}",
            f"codec={_safe_inline_text(stream.get('codec_name', 'unknown'))}",
            f"sample_rate={_safe_inline_text(stream.get('sample_rate', 'unknown'))}",
            f"channels={_safe_inline_text(stream.get('channels', 'unknown'))}",
            f"duration={_safe_inline_text(stream.get('duration', 'unknown'))}",
        ])
        for stream in streams
    ) or "no audio streams reported"


def _unknown_summary(streams: Sequence[Mapping[str, object]]) -> str:
    return "; ".join(
        ", ".join([
            f"index={_safe_inline_text(stream.get('index', 'unknown'))}",
            "type=unknown",
            f"codec={_safe_inline_text(stream.get('codec_name', 'unknown'))}",
        ])
        for stream in streams
    ) or "no unknown streams reported"


def _blocked_operations_summary() -> str:
    return "\n".join(f"- {operation}" for operation in BLOCKED_OPERATIONS)


def _safe_inline_text(value: object) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    if not text:
        return "unknown"
    if text.startswith(("/", "//", "\\\\")) or re.match(r"^[A-Za-z]:", text):
        return SAFE_INPUT_PLACEHOLDER
    if "/tmp/" in text or "/home/" in text or "/mnt/" in text:
        return SAFE_INPUT_PLACEHOLDER
    return text
