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

# legacy -> stable identity migration classifications (MS2A)
LEGACY_MIGRATION_AUTO_MIGRATABLE = "AUTO_MIGRATABLE"
LEGACY_MIGRATION_USER_CONFIRMATION_REQUIRED = "USER_CONFIRMATION_REQUIRED"
LEGACY_MIGRATION_BLOCKED = "BLOCKED"

# legacy migration error codes
LEGACY_MIGRATION_ERROR = "LEGACY_MIGRATION_ERROR"
LEGACY_MIGRATION_DESTINATION_COLLISION = "LEGACY_MIGRATION_DESTINATION_COLLISION"
LEGACY_MIGRATION_ROOT_COLLISION = "LEGACY_MIGRATION_ROOT_COLLISION"
LEGACY_MIGRATION_AMBIGUOUS = "LEGACY_MIGRATION_AMBIGUOUS"

# canonical stable source id prefix (matches project_sources SRC-<uuid4>)
_CANONICAL_SOURCE_PREFIX = "SRC-"

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


# ---------------------------------------------------------------------------
# MS2A — legacy -> stable source identity migration (pure, read-only where
# noted). Migration is an administrative data transformation only: it never
# imports ffprobe/ffmpeg/Sony sidecar parsing, never stats media, and never
# opens source media. It operates on persisted catalog dictionaries.
# ---------------------------------------------------------------------------

def _distinct_item_roots(catalog: dict[str, Any]) -> set[str]:
    """Return the set of ``source_root_id`` values referenced by media items."""
    roots: set[str] = set()
    for item in catalog.get("media_items", {}).values():
        if isinstance(item, dict):
            rid = item.get("source_root_id")
            if isinstance(rid, str) and rid.strip():
                roots.add(rid)
    return roots


def _source_root_record(catalog: dict[str, Any], source_root_id: str) -> dict[str, Any] | None:
    for record in catalog.get("source_roots", []):
        if isinstance(record, dict) and record.get("source_root_id") == source_root_id:
            return record
    return None


def classify_legacy_catalog_migration(
    catalog: dict[str, Any],
    legacy_root_id: str,
    *,
    source_id: str | None = None,
) -> tuple[str, str]:
    """Determine whether a catalog is safe for automatic single-source identity
    migration of ``legacy_root_id`` -> ``source_id``.

    Returns ``(classification, reason)`` where classification is one of:

    - ``AUTO_MIGRATABLE``: unambiguous, safe to migrate automatically.
    - ``USER_CONFIRMATION_REQUIRED``: ambiguous / multiple roots; do not guess.
    - ``BLOCKED``: fail closed (malformed, missing record, collision).

    This is a pure read-only inspection; the physical location is never
    accessed.
    """
    if not _is_valid_catalog(catalog):
        return (LEGACY_MIGRATION_BLOCKED, "CATALOG_INVALID_V1")
    if not isinstance(legacy_root_id, str) or not legacy_root_id.strip():
        return (LEGACY_MIGRATION_BLOCKED, "LEGACY_ROOT_ID_INVALID")
    if source_id is not None and (not isinstance(source_id, str) or not source_id.strip()):
        return (LEGACY_MIGRATION_BLOCKED, "SOURCE_ID_INVALID")
    if source_id is not None and source_id == legacy_root_id:
        return (LEGACY_MIGRATION_BLOCKED, "SOURCE_ID_EQUALS_LEGACY_ROOT")

    item_roots = _distinct_item_roots(catalog)
    if not item_roots:
        return (LEGACY_MIGRATION_AUTO_MIGRATABLE, "NO_MEDIA_ITEMS_MIGRATE_VACUOUSLY")

    root_record = _source_root_record(catalog, legacy_root_id)
    if root_record is None:
        return (LEGACY_MIGRATION_BLOCKED, "SOURCE_ROOT_RECORD_MISSING")
    stored_path = root_record.get("path")
    if not isinstance(stored_path, str) or not stored_path.strip():
        return (LEGACY_MIGRATION_BLOCKED, "SOURCE_ROOT_PATH_EMPTY")

    for item in catalog.get("media_items", {}).values():
        if not isinstance(item, dict):
            return (LEGACY_MIGRATION_BLOCKED, "MEDIA_ITEM_MALFORMED")
        rid = item.get("source_root_id")
        if not isinstance(rid, str) or not rid.strip():
            return (LEGACY_MIGRATION_BLOCKED, "MEDIA_ITEM_SOURCE_ROOT_ID_INVALID")
        if rid != legacy_root_id:
            return (LEGACY_MIGRATION_USER_CONFIRMATION_REQUIRED, "MULTIPLE_DISTINCT_ROOTS")

    conflicting = _find_conflicting_canonical(catalog, legacy_root_id, source_id)
    if conflicting is not None:
        return (LEGACY_MIGRATION_BLOCKED, conflicting)

    return (LEGACY_MIGRATION_AUTO_MIGRATABLE, "SINGLE_LEGACY_ROOT_UNAMBIGUOUS")


def _find_conflicting_canonical(
    catalog: dict[str, Any], legacy_root_id: str, source_id: str | None
) -> str | None:
    """Return a conflict reason string, or None if no destination collision.

    Only relevant when a canonical ``source_id`` (or a pre-existing canonical
    root) is already present and its record/payload differ from the legacy one
    under identity substitution. Equivalent records are not treated as a
    conflict (they converge); materially different records fail closed.
    """
    if source_id is None:
        canonical_roots = {
            _source_root_record(catalog, rid)
            for rid in _distinct_item_roots(catalog)
            if rid.startswith(_CANONICAL_SOURCE_PREFIX)
        }
        if len(canonical_roots) > 1:
            return "CANONICAL_ROOT_AMBIGUOUS"
        if canonical_roots:
            return "CANONICAL_IDENTITY_ALREADY_PRESENT"
        return None

    existing_root = _source_root_record(catalog, source_id)
    if existing_root is not None:
        legacy_root = _source_root_record(catalog, legacy_root_id)
        if legacy_root is not None and not _equivalent_source_root(legacy_root, existing_root):
            return "SOURCE_ROOT_COLLISION"
        return None

    for item in _items_for_root(catalog, legacy_root_id):
        existing = catalog.get("media_items", {}).get(media_item_key(source_id, item["relative_path"]))
        if existing is None:
            continue
        if not _equivalent_media_item(item, existing, legacy_root_id, source_id):
            return "DESTINATION_COLLISION"
    return None


def _items_for_root(catalog: dict[str, Any], source_root_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in catalog.get("media_items", {}).values():
        if isinstance(item, dict) and item.get("source_root_id") == source_root_id:
            items.append(item)
    return items


def _equivalent_media_item(
    legacy_item: dict[str, Any],
    canonical_item: dict[str, Any],
    legacy_root_id: str,
    source_id: str,
) -> bool:
    """Normalized equality after substituting the legacy identity for the
    canonical SOURCE_ID.

    ``relative_path`` must match; every other material payload field must be
    semantically identical. ``source_root_id`` is permitted to differ (it is
    the identity being migrated).
    """
    if canonical_item.get("relative_path") != legacy_item.get("relative_path"):
        return False
    for key, value in legacy_item.items():
        if key == "source_root_id":
            expected = source_id
            if canonical_item.get(key) != expected:
                return False
            continue
        if key not in canonical_item:
            return False
        if canonical_item[key] != value:
            return False
    for key in canonical_item:
        if key == "source_root_id":
            continue
        if key not in legacy_item:
            return False
        if legacy_item[key] != canonical_item[key]:
            return False
    return True


def _equivalent_source_root(
    legacy_record: dict[str, Any], canonical_record: dict[str, Any]
) -> bool:
    """Source-root records are equivalent when all fields except the identity
    ``source_root_id`` are semantically identical and the identity maps
    legacy -> canonical."""
    for key, value in legacy_record.items():
        if key == "source_root_id":
            continue
        if key not in canonical_record:
            return False
        if canonical_record[key] != value:
            return False
    for key in canonical_record:
        if key == "source_root_id":
            continue
        if key not in legacy_record:
            return False
        if legacy_record[key] != canonical_record[key]:
            return False
    return True


def migrate_legacy_source_root(
    catalog: dict[str, Any],
    legacy_root_id: str,
    source_id: str,
) -> dict[str, Any]:
    """Deterministic re-key of a catalog's source identity in place semantics.

    Returns a NEW catalog dictionary; the input ``catalog`` is not mutated.
    Migrates ``legacy_root_id`` -> ``source_id`` for the matching source-root
    record and every media item that references it, preserving all unrelated
    payload fields verbatim:

    - media item key ``legacy_root_id::<rel>`` -> ``source_id::<rel>``
    - item ``source_root_id`` -> ``source_id``
    - ffprobe_metadata, source_color_profile, size, mtime_ns, fingerprints,
      analysis/error state, warnings, and all unrelated fields preserved.

    Identity-only migration; no reprobe, no media access, no Sony reparse.

    Collision rules:
    - Equivalent legacy+canonical duplicate records collapse to the single
      canonical record (idempotent rerun safe).
    - Materially different destination media / source-root records FAIL CLOSED
      (no overwrite, no silent data loss).

    Leaves unrelated roots (and canonical entries) untouched.
    """
    _require_catalog(catalog)
    if not isinstance(legacy_root_id, str) or not legacy_root_id.strip():
        raise MediaCatalogError("LEGACY_ROOT_ID_INVALID")
    if not isinstance(source_id, str) or not source_id.strip():
        raise MediaCatalogError("SOURCE_ID_INVALID")
    if source_id == legacy_root_id:
        raise MediaCatalogError("SOURCE_ID_EQUALS_LEGACY_ROOT")

    legacy_root = _source_root_record(catalog, legacy_root_id)
    if legacy_root is None:
        if any(
            isinstance(item, dict) and item.get("source_root_id") == legacy_root_id
            for item in catalog.get("media_items", {}).values()
        ):
            raise MediaCatalogError(LEGACY_MIGRATION_ERROR + ":SOURCE_ROOT_RECORD_MISSING")
        return dict(catalog)

    new_catalog_structure: dict[str, Any] = {
        "format": CATALOG_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "project_id": catalog["project_id"],
        "updated_at": catalog["updated_at"],
        "source_roots": [],
        "media_items": {},
        "analysis_state": catalog["analysis_state"],
    }

    existing_canonical_root = _source_root_record(catalog, source_id)
    if existing_canonical_root is not None:
        if not _equivalent_source_root(legacy_root, existing_canonical_root):
            raise MediaCatalogError(LEGACY_MIGRATION_ROOT_COLLISION)
        new_catalog_structure["source_roots"].append(dict(existing_canonical_root))
    else:
        migrated_root = dict(legacy_root)
        migrated_root["source_root_id"] = source_id
        new_catalog_structure["source_roots"].append(migrated_root)

    for record in catalog.get("source_roots", []):
        if not isinstance(record, dict):
            continue
        rid = record.get("source_root_id")
        if rid == legacy_root_id or rid == source_id:
            continue
        new_catalog_structure["source_roots"].append(dict(record))

    for item in catalog.get("media_items", {}).values():
        if not isinstance(item, dict):
            continue
        rid = item.get("source_root_id")
        if rid == legacy_root_id:
            migrated = dict(item)
            migrated["source_root_id"] = source_id
            new_key = media_item_key(source_id, migrated["relative_path"])
            orig_canonical = catalog.get("media_items", {}).get(new_key)
            if orig_canonical is not None:
                if not _equivalent_media_item(migrated, orig_canonical, legacy_root_id, source_id):
                    raise MediaCatalogError(LEGACY_MIGRATION_DESTINATION_COLLISION)
                continue
            new_catalog_structure["media_items"][new_key] = migrated
        elif rid == source_id:
            key = media_item_key(source_id, item["relative_path"])
            if key not in new_catalog_structure["media_items"]:
                new_catalog_structure["media_items"][key] = dict(item)
        else:
            key = media_item_key(rid, item["relative_path"])
            new_catalog_structure["media_items"][key] = dict(item)

    _require_catalog(new_catalog_structure)
    return new_catalog_structure
