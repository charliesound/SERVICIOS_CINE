"""CID Local Media Agent — persistent, versioned local media catalog.

Operation state for the analysis pipeline. This catalog is the *operational*
record of what has been scanned, fingerprinted and analyzed; it coexists with
the existing technical contract files (``source_video_profiles.json``) rather
than replacing them.

Design goals
------------
- Versioned, JSON, atomically written local persistence (no DB, no SaaS).
- Stable, deterministic media identity from ``source_root_id`` + relative path.
- Cheap fingerprint (``size`` + ``mtime_ns``) so incremental analysis does not
  require hashing large audiovisual files.
- Controlled, non-crashing handling of malformed catalog files.
- Forward-compatible with Slice D multi-source roots.

This module is Slice A scope: it deliberately does NOT modify project/contract
modules. The project directory is resolved by importing the existing
``local_project.project_path`` helper (read-only).
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import time
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
CATALOG_FORMAT = "cid.local_media_agent.media_catalog"
CATALOG_FILE_NAME = "media_catalog.json"

# catalog_status — filesystem presence from the last scan
CATALOG_STATUS_PRESENT = "PRESENT"

# analysis_status — per media item technical analysis lifecycle
ANALYSIS_STATUS_NOT_ANALYZED = "NOT_ANALYZED"
ANALYSIS_STATUS_PENDING = "PENDING"
ANALYSIS_STATUS_OK = "OK"
ANALYSIS_STATUS_ERROR = "ERROR"

# error categories (distinct; never conflated)
ERROR_CATEGORY_SCAN = "SCAN_ERROR"
ERROR_CATEGORY_METADATA = "METADATA_ERROR"
ERROR_CATEGORY_SIDECAR = "SIDECAR_ERROR"
ERROR_CATEGORY_ANALYSIS = "ANALYSIS_ERROR"

# root status — online/offline classification
ROOT_STATUS_ONLINE = "ONLINE"
ROOT_STATUS_OFFLINE = "OFFLINE"

_PROJECT_ID_RE = re.compile(
    r"^PRJ-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_MEDIA_KINDS = frozenset({"video", "audio", "image"})
_ANALYSIS_STATUSES = frozenset(
    {ANALYSIS_STATUS_NOT_ANALYZED, ANALYSIS_STATUS_PENDING, ANALYSIS_STATUS_OK, ANALYSIS_STATUS_ERROR}
)
_TOP_LEVEL_KEYS = frozenset(
    {"format", "schema_version", "project_id", "updated_at", "source_roots", "media_items", "analysis_state"}
)


class MediaCatalogError(ValueError):
    """Controlled media-catalog refusal (malformed input, invalid identity)."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def validate_project_id(project_id: object) -> str:
    if not isinstance(project_id, str) or _PROJECT_ID_RE.fullmatch(project_id) is None:
        raise MediaCatalogError("PROJECT_ID_INVALID")
    return project_id


def media_item_key(source_root_id: str, relative_path: str) -> str:
    """Deterministic media-item primary key.

    Identity is rooted in ``source_root_id`` + relative path, never the drive
    letter alone (forward-compatible with Slice D multi-root/relink).
    """
    if not isinstance(source_root_id, str) or not source_root_id.strip():
        raise MediaCatalogError("SOURCE_ROOT_ID_INVALID")
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise MediaCatalogError("RELATIVE_PATH_INVALID")
    return f"{source_root_id}::{relative_path}"


def new_catalog(
    project_id: str,
    *,
    source_roots: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a fresh, empty V1 catalog."""
    validate_project_id(project_id)
    return {
        "format": CATALOG_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "updated_at": _now_iso(),
        "source_roots": [dict(r) for r in (source_roots or [])],
        "media_items": {},
        "analysis_state": {"scan": "NOT_STARTED", "metadata": "NOT_STARTED", "counters": {}},
    }


def add_source_root(catalog: dict[str, Any], source_root_id: str, path: str) -> None:
    """Register (or update) one source root. V1 supports at least one; schema
    is forward-compatible with multiple roots."""
    _require_catalog(catalog)
    if not isinstance(source_root_id, str) or not source_root_id.strip():
        raise MediaCatalogError("SOURCE_ROOT_ID_INVALID")
    if not isinstance(path, str) or not path.strip():
        raise MediaCatalogError("SOURCE_ROOT_PATH_INVALID")
    roots = catalog["source_roots"]
    for existing in roots:
        if existing.get("source_root_id") == source_root_id:
            existing["path"] = path
            existing.setdefault("status", ROOT_STATUS_ONLINE)
            existing["last_seen_at"] = _now_iso()
            _touch(catalog)
            return
    roots.append(
        {
            "source_root_id": source_root_id,
            "path": path,
            "status": ROOT_STATUS_ONLINE,
            "last_seen_at": _now_iso(),
        }
    )
    _touch(catalog)


def set_media_item(catalog: dict[str, Any], item: dict[str, Any]) -> None:
    """Upsert one media item into the catalog."""
    _require_catalog(catalog)
    source_root_id = item.get("source_root_id")
    relative_path = item.get("relative_path")
    if not isinstance(source_root_id, str) or not source_root_id.strip():
        raise MediaCatalogError("SOURCE_ROOT_ID_INVALID")
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise MediaCatalogError("RELATIVE_PATH_INVALID")
    if relative_path.startswith(("/", "\\")) or relative_path.lstrip().startswith("/") or (
        len(relative_path) > 1 and relative_path[1] == ":"
    ):
        raise MediaCatalogError("RELATIVE_PATH_MUST_BE_RELATIVE")
    kind = item.get("media_kind")
    if kind is not None and kind not in _MEDIA_KINDS:
        raise MediaCatalogError("MEDIA_KIND_INVALID")
    analysis_status = item.get("analysis_status", ANALYSIS_STATUS_NOT_ANALYZED)
    if analysis_status not in _ANALYSIS_STATUSES:
        raise MediaCatalogError("ANALYSIS_STATUS_INVALID")

    normalized: dict[str, Any] = {
        "source_root_id": source_root_id,
        "relative_path": relative_path,
        "media_kind": kind or "video",
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": analysis_status,
    }
    for key in ("size", "mtime_ns"):
        value = item.get(key)
        if value is None:
            normalized[key] = None
        elif isinstance(value, int) and not isinstance(value, bool):
            normalized[key] = value
        else:
            raise MediaCatalogError(f"{key}_INVALID")
    if "last_analyzed_at" in item:
        if item["last_analyzed_at"] is not None and not isinstance(item["last_analyzed_at"], str):
            raise MediaCatalogError("LAST_ANALYZED_AT_INVALID")
        normalized["last_analyzed_at"] = item["last_analyzed_at"]
    for key in ("ffprobe_metadata", "source_color_profile"):
        if key in item and item[key] is not None:
            normalized[key] = item[key]
    if "source_video_profile_ref" in item and item["source_video_profile_ref"] is not None:
        normalized["source_video_profile_ref"] = item["source_video_profile_ref"]
    if "technical_errors" in item and item["technical_errors"]:
        normalized["technical_errors"] = [dict(e) for e in item["technical_errors"]]

    catalog["media_items"][media_item_key(source_root_id, relative_path)] = normalized
    _touch(catalog)


def get_media_item(
    catalog: dict[str, Any], source_root_id: str, relative_path: str
) -> dict[str, Any] | None:
    _require_catalog(catalog)
    from_catalog = catalog["media_items"].get(media_item_key(source_root_id, relative_path))
    return dict(from_catalog) if from_catalog is not None else None


def catalog_path_for_project(
    project_id: str, *, local_appdata: str | Path | None = None
) -> Path:
    """Resolve the catalog file path inside the project directory.

    Imports the existing ``local_project.project_path`` helper read-only so the
    catalog coexists with ``source_video_profiles.json`` under the same project.
    """
    from scripts.local_media_agent.local_project import project_path

    return project_path(project_id, local_appdata=local_appdata) / CATALOG_FILE_NAME


def save_catalog(
    catalog: dict[str, Any],
    *,
    path: str | Path | None = None,
    project_id: str | None = None,
    local_appdata: str | Path | None = None,
) -> Path:
    """Atomically persist the catalog (temp + fsync + ``os.replace``)."""
    _require_catalog(catalog)
    if path is None:
        pid = project_id or catalog.get("project_id")
        if pid is None:
            raise MediaCatalogError("PROJECT_ID_REQUIRED")
        path = catalog_path_for_project(pid, local_appdata=local_appdata)
    destination = Path(path)
    catalog = dict(catalog)
    catalog["updated_at"] = _now_iso()
    encoded = json.dumps(
        catalog, ensure_ascii=False, sort_keys=True, indent=2, separators=(",", ": ")
    ) + "\n"
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return destination


def load_catalog(
    *,
    path: str | Path | None = None,
    project_id: str | None = None,
    local_appdata: str | Path | None = None,
) -> dict[str, Any]:
    """Load a catalog; raise ``MediaCatalogError`` on malformed content.

    Deliberately does not delete or auto-repair a malformed catalog.
    """
    if path is None:
        if project_id is None:
            raise MediaCatalogError("PROJECT_ID_REQUIRED")
        path = catalog_path_for_project(project_id, local_appdata=local_appdata)
    source = Path(path)
    if not source.is_file():
        raise MediaCatalogError("CATALOG_NOT_FOUND")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MediaCatalogError("CATALOG_MALFORMED") from exc
    if not isinstance(payload, dict):
        raise MediaCatalogError("CATALOG_MALFORMED")
    if not _is_valid_catalog(payload):
        raise MediaCatalogError("CATALOG_MALFORMED")
    return payload


def is_valid_catalog(obj: object) -> bool:
    return _is_valid_catalog(obj)


def _is_valid_catalog(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if not _TOP_LEVEL_KEYS.issubset(set(obj)):
        return False
    if obj.get("format") != CATALOG_FORMAT:
        return False
    if obj.get("schema_version") != SCHEMA_VERSION:
        return False
    try:
        validate_project_id(obj.get("project_id"))
    except MediaCatalogError:
        return False
    if not isinstance(obj.get("source_roots"), list):
        return False
    if not isinstance(obj.get("media_items"), dict):
        return False
    for item in obj["media_items"].values():
        if not isinstance(item, dict):
            return False
        if item.get("catalog_status") != CATALOG_STATUS_PRESENT:
            return False
        if item.get("analysis_status") not in _ANALYSIS_STATUSES:
            return False
        source_root_id = item.get("source_root_id")
        relative_path = item.get("relative_path")
        if not isinstance(source_root_id, str) or not isinstance(relative_path, str):
            return False
    return isinstance(obj.get("analysis_state"), dict)


def _require_catalog(catalog: object) -> None:
    if not _is_valid_catalog(catalog):
        raise MediaCatalogError("CATALOG_MALFORMED")


def _touch(catalog: dict[str, Any]) -> None:
    catalog["updated_at"] = _now_iso()
