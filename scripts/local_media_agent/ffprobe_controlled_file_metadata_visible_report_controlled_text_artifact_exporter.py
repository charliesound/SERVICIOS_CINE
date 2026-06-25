"""Controlled text artifact descriptor builder for CID Local Media Agent.

This module is intentionally pure and local-only.

It builds an in-memory descriptor for already-safe controlled visible report
text. It does not write files, create filesystem artifacts, execute tools,
scan folders, process media, access networks, or touch SaaS/database systems.
"""

from __future__ import annotations

import hashlib
import re
from copy import deepcopy
from typing import Any


ARTIFACT_FORMAT = "text/plain; charset=utf-8"

SOURCE_BOUNDARY = "already_safe_controlled_visible_report_text"

_SUGGESTED_FILENAME_SUFFIX = ".controlled_visible_report.txt"

_SAFETY_FLAGS: dict[str, bool] = {
    "no_real_media": True,
    "no_arbitrary_folders": True,
    "no_scanner_execution": True,
    "no_ffprobe_execution": True,
    "no_ffmpeg_execution": True,
    "no_subprocess_execution": True,
    "no_process_execution": True,
    "no_audio_extraction": True,
    "no_sync": True,
    "no_transcription": True,
    "no_subtitles": True,
    "no_timeline_export": True,
    "no_network_access": True,
    "no_saas_db_access": True,
    "no_installer_behavior": True,
    "no_public_demo_behavior": True,
    "no_client_demo_behavior": True,
    "no_sales_demo_behavior": True,
    "no_production_behavior": True,
}


def _ensure_non_empty_string(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")

    return value


def _safe_filename_stem(controlled_source_id: str) -> str:
    raw_value = _ensure_non_empty_string(
        controlled_source_id,
        "controlled_source_id",
    ).strip()

    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_value)
    normalized = normalized.strip("._-")

    if not normalized:
        normalized = "controlled_visible_report"

    return normalized[:96]


def build_controlled_text_artifact_descriptor(
    *,
    visible_report_text: str,
    controlled_source_id: str = "controlled_visible_report",
) -> dict[str, Any]:
    """Return an in-memory descriptor for controlled visible report text.

    The input must already be safe controlled visible report text. This function
    does not read or write files and does not perform any media operation.
    """

    safe_text = _ensure_non_empty_string(
        visible_report_text,
        "visible_report_text",
    )

    content_bytes = safe_text.encode("utf-8")
    filename_stem = _safe_filename_stem(controlled_source_id)

    return {
        "artifact_format": ARTIFACT_FORMAT,
        "suggested_filename": f"{filename_stem}{_SUGGESTED_FILENAME_SUFFIX}",
        "content_text": safe_text,
        "line_count": len(safe_text.splitlines()),
        "byte_count": len(content_bytes),
        "content_sha256": hashlib.sha256(content_bytes).hexdigest(),
        "safety_flags": deepcopy(_SAFETY_FLAGS),
        "source_boundary": SOURCE_BOUNDARY,
        "write_performed": False,
        "artifact_created_on_disk": False,
    }


__all__ = [
    "ARTIFACT_FORMAT",
    "SOURCE_BOUNDARY",
    "build_controlled_text_artifact_descriptor",
]
