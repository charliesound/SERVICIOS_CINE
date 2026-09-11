"""CID project analysis Material display summary (cold-start restore authority).

Persists the latest successfully completed Material analysis execution scope
and scan/incident tallies for GUI cold-start hydration. Does not represent the
full historical media catalog. Groups are out of scope.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from scripts.local_media_agent.local_project import (
    LocalProjectError,
    atomic_write_json,
    project_path,
    validate_project_id,
)

DISPLAY_SUMMARY_FORMAT = "CID_PROJECT_ANALYSIS_DISPLAY_SUMMARY"
DISPLAY_SUMMARY_SCHEMA_VERSION = 1
DISPLAY_SUMMARY_FILENAME = "project_analysis_display_summary.json"

CID_DISPLAY_SUMMARY_REQUIRED = "CID_DISPLAY_SUMMARY_REQUIRED"
CID_DISPLAY_SUMMARY_INVALID = "CID_DISPLAY_SUMMARY_INVALID"
CID_DISPLAY_SUMMARY_PROJECT_MISMATCH = "CID_DISPLAY_SUMMARY_PROJECT_MISMATCH"
CID_DISPLAY_SUMMARY_UNSUPPORTED_VERSION = "CID_DISPLAY_SUMMARY_UNSUPPORTED_VERSION"

_TOP_LEVEL_KEYS = frozenset(
    {
        "format",
        "schema_version",
        "project_id",
        "generated_at",
        "analysis_run_id",
        "analyzed_sources",
        "scan",
        "metadata",
    }
)
_SCAN_KEYS = frozenset(
    {
        "total_files",
        "media_files",
        "video",
        "audio",
        "images",
        "other",
        "errors",
        "warnings",
    }
)


class ProjectAnalysisDisplaySummaryError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def project_analysis_display_summary_path(
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> Path:
    return project_path(project_id, local_appdata) / DISPLAY_SUMMARY_FILENAME


def build_project_analysis_display_summary(
    project_id: str,
    *,
    analyzed_sources: Sequence[Mapping[str, Any]],
    scan: Mapping[str, Any],
    incident_count: int,
    analysis_run_id: str | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a validated schema-v1 Material display summary (in memory)."""
    identifier = validate_project_id(project_id)
    payload = {
        "format": DISPLAY_SUMMARY_FORMAT,
        "schema_version": DISPLAY_SUMMARY_SCHEMA_VERSION,
        "project_id": identifier,
        "generated_at": _timestamp(generated_at),
        "analysis_run_id": _analysis_run_id(analysis_run_id),
        "analyzed_sources": _normalize_analyzed_sources(analyzed_sources),
        "scan": _normalize_scan(scan),
        "metadata": {"incident_count": _non_negative_int(incident_count, "incident_count")},
    }
    _validate_summary(payload, expected_project_id=identifier)
    return payload


def save_project_analysis_display_summary(
    summary: Mapping[str, Any],
    *,
    local_appdata: str | Path | None = None,
) -> Path:
    """Atomically persist a validated Material display summary."""
    payload = dict(summary)
    _validate_summary(payload)
    project_id = payload["project_id"]
    destination = project_analysis_display_summary_path(
        project_id, local_appdata=local_appdata
    )
    atomic_write_json(destination, payload)
    return destination


def load_project_analysis_display_summary(
    project_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> dict[str, Any] | None:
    """Load a validated summary, or ``None`` when the artifact is absent.

    Malformed / unsupported / mismatched payloads raise
    :class:`ProjectAnalysisDisplaySummaryError` (fail closed). Missing file is
    not an error (legacy projects predating this schema).
    """
    identifier = validate_project_id(project_id)
    path = project_analysis_display_summary_path(
        identifier, local_appdata=local_appdata
    )
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID) from exc
    if not isinstance(payload, dict):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    _validate_summary(payload, expected_project_id=identifier)
    return payload


def is_displayable_summary(
    summary: Mapping[str, Any],
    *,
    project_id: str,
    project_sources: Sequence[Mapping[str, Any]],
    online_source_ids: set[str] | frozenset[str],
) -> bool:
    """Return True when persisted analysis scope still matches project state.

    Rules:
    1. summary.project_id equals active project
    2. every analyzed source still exists with the same source_id
    3. every analyzed source retains the same current_location
    4. current ONLINE source-id set equals persisted analyzed source-id set
    """
    try:
        identifier = validate_project_id(project_id)
    except LocalProjectError:
        return False
    if summary.get("project_id") != identifier:
        return False
    try:
        analyzed = _normalize_analyzed_sources(summary.get("analyzed_sources") or [])
    except ProjectAnalysisDisplaySummaryError:
        return False
    by_id = {
        source.get("source_id"): source
        for source in project_sources
        if isinstance(source, Mapping) and isinstance(source.get("source_id"), str)
    }
    analyzed_ids = {entry["source_id"] for entry in analyzed}
    if set(online_source_ids) != analyzed_ids:
        return False
    for entry in analyzed:
        source = by_id.get(entry["source_id"])
        if source is None:
            return False
        location = source.get("current_location")
        if not isinstance(location, str) or location != entry["current_location"]:
            return False
    return True


def material_counts_from_summary(summary: Mapping[str, Any]) -> dict[str, int]:
    """Map persisted scan tallies into GUI Material count keys."""
    scan = summary["scan"]
    return {
        "video": int(scan["video"]),
        "audio": int(scan["audio"]),
        "images": int(scan["images"]),
        "other": int(scan["other"]),
    }


def incident_count_from_summary(summary: Mapping[str, Any]) -> int:
    return int(summary["metadata"]["incident_count"])


def _normalize_analyzed_sources(
    analyzed_sources: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    if not isinstance(analyzed_sources, Sequence) or isinstance(
        analyzed_sources, (str, bytes)
    ):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    if not analyzed_sources:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for entry in analyzed_sources:
        if not isinstance(entry, Mapping):
            raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
        source_id = entry.get("source_id")
        location = entry.get("current_location")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
        if not isinstance(location, str) or not location.strip():
            raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
        if source_id in seen:
            raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
        seen.add(source_id)
        normalized.append(
            {"source_id": source_id, "current_location": location}
        )
    normalized.sort(key=lambda item: item["source_id"])
    return normalized


def _normalize_scan(scan: Mapping[str, Any]) -> dict[str, int]:
    if not isinstance(scan, Mapping):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    if not _SCAN_KEYS.issubset(set(scan)):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    result = {key: _non_negative_int(scan[key], key) for key in sorted(_SCAN_KEYS)}
    media = result["video"] + result["audio"] + result["images"]
    if result["media_files"] != media:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    if result["total_files"] != media + result["other"]:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    return result


def _validate_summary(
    summary: Mapping[str, Any],
    *,
    expected_project_id: str | None = None,
) -> None:
    if not isinstance(summary, Mapping):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    if not _TOP_LEVEL_KEYS.issubset(set(summary)):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    if summary.get("format") != DISPLAY_SUMMARY_FORMAT:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    version = summary.get("schema_version")
    if version != DISPLAY_SUMMARY_SCHEMA_VERSION:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_UNSUPPORTED_VERSION)
    try:
        project_id = validate_project_id(summary.get("project_id"))
    except LocalProjectError as exc:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID) from exc
    if expected_project_id is not None and project_id != expected_project_id:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_PROJECT_MISMATCH)
    if not _valid_timestamp(summary.get("generated_at")):
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    run_id = summary.get("analysis_run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    _normalize_analyzed_sources(summary.get("analyzed_sources") or [])
    _normalize_scan(summary.get("scan") or {})
    metadata = summary.get("metadata")
    if not isinstance(metadata, Mapping) or "incident_count" not in metadata:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    _non_negative_int(metadata.get("incident_count"), "incident_count")


def _non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    return value


def _analysis_run_id(value: str | None) -> str:
    if value is None:
        return str(uuid.uuid4())
    if not isinstance(value, str) or not value.strip():
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    return value.strip()


def _timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ProjectAnalysisDisplaySummaryError(CID_DISPLAY_SUMMARY_INVALID)
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True
