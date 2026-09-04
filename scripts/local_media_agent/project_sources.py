"""CID Local Media Agent — project-scoped source registry (MS1).

Introduces a stable, project-scoped ``SOURCE_ID`` and a versioned, project-local
source registry stored at::

    <CID_DATA_ROOT>/projects/<project_id>/project_sources.json

Purpose
-------
A CID project may contain multiple physical media sources. Each source is an
explicit binding between this project and a physical location. The binding is
identified by a stable ``SRC-<uuid4>`` that is:

- project-scoped (it names *this binding inside this project*);
- stable across location changes (``current_location`` is mutable, ``source_id``
  is not);
- never a global physical-disk identity.

This module is MS1 scope. It deliberately does NOT scan media, call ffprobe,
touch grouping, migrate catalogs, or read real user media. Location comparison
is lexical/path only (no filesystem access, no stat, no existence checks).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

from scripts.local_media_agent.local_project import (
    atomic_write_json,
    project_sources_path,
    projects_path,
    validate_project_id,
)

PROJECT_SOURCES_FORMAT = "CID_PROJECT_SOURCES"
PROJECT_SOURCES_SCHEMA_VERSION = 1

STATE_ONLINE = "ONLINE"
STATE_OFFLINE = "OFFLINE"
_SOURCE_STATES = frozenset({STATE_ONLINE, STATE_OFFLINE})

ErrorCode = str
CID_SOURCE_REGISTRY_INVALID = "CID_SOURCE_REGISTRY_INVALID"
CID_SOURCE_ID_INVALID = "CID_SOURCE_ID_INVALID"
CID_SOURCE_LABEL_INVALID = "CID_SOURCE_LABEL_INVALID"
CID_SOURCE_LOCATION_INVALID = "CID_SOURCE_LOCATION_INVALID"
CID_SOURCE_STATE_INVALID = "CID_SOURCE_STATE_INVALID"
CID_SOURCE_DUPLICATE_ID = "CID_SOURCE_DUPLICATE_ID"
CID_SOURCE_PROJECT_MISMATCH = "CID_SOURCE_PROJECT_MISMATCH"
CID_SOURCE_DUPLICATE_LOCATION = "CID_SOURCE_DUPLICATE_LOCATION"
CID_SOURCE_OVERLAPPING_LOCATION = "CID_SOURCE_OVERLAPPING_LOCATION"
CID_SOURCE_CROSS_PROJECT_CONFLICT = "CID_SOURCE_CROSS_PROJECT_CONFLICT"
CID_SOURCE_NOT_FOUND = "CID_SOURCE_NOT_FOUND"
CID_SOURCE_RECONNECT_CONFIRMATION_REQUIRED = "CID_SOURCE_RECONNECT_CONFIRMATION_REQUIRED"
CID_SOURCE_TIMESTAMP_INVALID = "CID_SOURCE_TIMESTAMP_INVALID"
CID_SOURCE_LEGACY_ALIAS_INVALID = "CID_SOURCE_LEGACY_ALIAS_INVALID"
CID_SOURCE_LEGACY_ALIAS_CONFLICT = "CID_SOURCE_LEGACY_ALIAS_CONFLICT"
CID_SOURCE_MIGRATION_BINDING_INVALID = "CID_SOURCE_MIGRATION_BINDING_INVALID"
CID_SOURCE_MIGRATION_TARGET_CONFLICT = "CID_SOURCE_MIGRATION_TARGET_CONFLICT"

# Mirrors local_project's project-id shape; used only to recognize project
# directories when scanning other projects for shared-location detection.
_PROJECT_ID_RE = re.compile(
    r"^PRJ-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_SOURCE_ID_RE = re.compile(
    r"^SRC-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_TOP_LEVEL_KEYS = frozenset({"format", "schema_version", "project_id", "sources"})
_SOURCE_KEYS = frozenset(
    {
        "source_id",
        "display_label",
        "current_location",
        "state",
        "added_at",
        "updated_at",
        "legacy_source_root_id_alias",
    }
)
_SOURCE_KEYS_WITHOUT_LEGACY = _SOURCE_KEYS - {"legacy_source_root_id_alias"}
_SOURCE_REQUIRED_KEYS = frozenset(
    {"source_id", "display_label", "current_location", "state", "added_at", "updated_at"}
)


class SourceRegistryError(ValueError):
    """Controlled project-source registry refusal."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


# ---------------------------------------------------------------------------
# Location comparison (lexical only — no filesystem access)
# ---------------------------------------------------------------------------

def normalize_location(value: object) -> str:
    """Normalize a location for comparison: separators and trailing slashes.

    Converts backslashes to forward slashes and strips trailing separators.
    Drive roots (``F:``) are left intact. Performs no filesystem access.
    """
    raw = str(value).replace("\\", "/")
    while len(raw) > 1 and raw.endswith("/"):
        raw = raw[:-1]
    return raw


def _is_windows_like(value: object) -> bool:
    raw = str(value).replace("\\", "/")
    return bool(re.match(r"^[A-Za-z]:", raw))


def _location_parts(value: object) -> tuple[list[str], bool]:
    """Return (lowercased-if-windows parts, is_windows). Separator-safe."""
    raw = normalize_location(value)
    win = _is_windows_like(raw)
    parts = raw.split("/")
    if win:
        parts = [part.lower() for part in parts]
    return parts, win


def locations_equal(a: object, b: object) -> bool:
    """Lexical equality, case-insensitive for Windows drive paths, ignoring
    trailing separators. ``F:\\SIRUELA`` == ``f:\\siruela\\``."""
    return _location_parts(a) == _location_parts(b)


def is_location_ancestor_of(ancestor: object, descendant: object) -> bool:
    """Separator-safe ancestor/descendant containment.

    ``F:\\SIRUELA`` is an ancestor of ``F:\\SIRUELA\\Audio`` but ``F:\\FILM`` is
    NOT an ancestor of ``F:\\FILM2`` (never a bare string prefix).
    """
    a_parts, a_win = _location_parts(ancestor)
    d_parts, d_win = _location_parts(descendant)
    if a_win != d_win:
        return False
    if len(d_parts) <= len(a_parts):
        return False
    return d_parts[: len(a_parts)] == a_parts


def locations_overlap(a: object, b: object) -> bool:
    """True when two locations are the same or one contains the other."""
    return locations_equal(a, b) or is_location_ancestor_of(a, b) or is_location_ancestor_of(b, a)


# ---------------------------------------------------------------------------
# Identity validation
# ---------------------------------------------------------------------------

def validate_source_id(source_id: object) -> str:
    if not isinstance(source_id, str) or _SOURCE_ID_RE.fullmatch(source_id) is None:
        raise SourceRegistryError(CID_SOURCE_ID_INVALID)
    return source_id


def _new_source_id() -> str:
    return f"SRC-{uuid4()}"


# ---------------------------------------------------------------------------
# Timestamp conventions (tz-aware UTC, trailing "Z"), mirroring local_project
# ---------------------------------------------------------------------------

def _timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise SourceRegistryError(CID_SOURCE_TIMESTAMP_INVALID)
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


# ---------------------------------------------------------------------------
# Field-level validation
# ---------------------------------------------------------------------------

def _validate_label(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise SourceRegistryError(CID_SOURCE_LABEL_INVALID)
    if len(value) > 200 or any(ord(character) < 32 for character in value):
        raise SourceRegistryError(CID_SOURCE_LABEL_INVALID)
    return value


def _validate_location(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SourceRegistryError(CID_SOURCE_LOCATION_INVALID)
    if "\x00" in value:
        raise SourceRegistryError(CID_SOURCE_LOCATION_INVALID)
    return value


def _normalize_location_record(value: object) -> str:
    """Stored location is a non-empty, NUL-free string."""
    return _validate_location(value)


# ---------------------------------------------------------------------------
# Registry construction / load / save
# ---------------------------------------------------------------------------

def empty_registry(project_id: str) -> dict[str, Any]:
    """Return a valid, empty in-memory registry for a project."""
    validate_project_id(project_id)
    return {
        "format": PROJECT_SOURCES_FORMAT,
        "schema_version": PROJECT_SOURCES_SCHEMA_VERSION,
        "project_id": project_id,
        "sources": [],
    }


def load_project_sources(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    """Read the source registry for a project.

    If ``project_sources.json`` does not exist, returns a valid empty in-memory
    registry and does NOT create the file (legacy/absent projects are left
    untouched). A malformed file raises ``SourceRegistryError`` (fail closed)
    and is never deleted/repaired.
    """
    identifier = validate_project_id(project_id)
    path = project_sources_path(identifier, local_appdata)
    if not path.is_file():
        return empty_registry(identifier)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID) from exc
    if not isinstance(payload, dict):
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    _validate_registry(payload, identifier)
    return payload


def is_valid_registry(obj: object, project_id: str | None = None) -> bool:
    """Return whether ``obj`` is a structurally valid registry."""
    try:
        _validate_registry(obj, project_id if project_id is not None else "")
    except (SourceRegistryError, ValueError):
        return False
    return True


def _validate_registry(registry: Any, project_id: str) -> None:
    if not isinstance(registry, dict):
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    if set(registry) != _TOP_LEVEL_KEYS:
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    if registry.get("format") != PROJECT_SOURCES_FORMAT:
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    if registry.get("schema_version") != PROJECT_SOURCES_SCHEMA_VERSION:
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    try:
        registered_project_id = validate_project_id(registry.get("project_id"))
    except (ValueError, TypeError) as exc:
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID) from exc
    if registered_project_id != project_id:
        raise SourceRegistryError(CID_SOURCE_PROJECT_MISMATCH)
    if not isinstance(registry.get("sources"), list):
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)

    seen_ids: set[str] = set()
    seen_aliases: set[str] = set()
    for source in registry["sources"]:
        if not isinstance(source, dict):
            raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
        keys = set(source)
        if keys not in (_SOURCE_KEYS, _SOURCE_KEYS_WITHOUT_LEGACY):
            raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
        if not _SOURCE_REQUIRED_KEYS.issubset(keys):
            raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
        source_id = validate_source_id(source.get("source_id"))
        if source_id in seen_ids:
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_ID)
        seen_ids.add(source_id)
        _validate_label(source.get("display_label"))
        _validate_location(source.get("current_location"))
        state = source.get("state")
        if state not in _SOURCE_STATES:
            raise SourceRegistryError(CID_SOURCE_STATE_INVALID)
        if not _valid_timestamp(source.get("added_at")) or not _valid_timestamp(
            source.get("updated_at")
        ):
            raise SourceRegistryError(CID_SOURCE_TIMESTAMP_INVALID)
        legacy = source.get("legacy_source_root_id_alias")
        if legacy is not None and (
            not isinstance(legacy, str) or not legacy.strip()
        ):
            raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
        if legacy is not None:
            if legacy in seen_aliases:
                raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_CONFLICT)
            seen_aliases.add(legacy)


def save_project_sources(
    registry: dict[str, Any], *, local_appdata: str | Path | None = None
) -> None:
    """Atomically persist a source registry (temp + fsync + ``os.replace``).

    The registry is validated before writing; a malformed registry is refused
    rather than partially written.
    """
    if not isinstance(registry, dict):
        raise SourceRegistryError(CID_SOURCE_REGISTRY_INVALID)
    project_id = validate_project_id(registry.get("project_id") or "")
    _validate_registry(registry, project_id)
    atomic_write_json(project_sources_path(project_id, local_appdata), registry)


# ---------------------------------------------------------------------------
# Public service API
# ---------------------------------------------------------------------------

def list_project_sources(
    project_id: str, *, local_appdata: str | Path | None = None
) -> list[dict[str, Any]]:
    """Return the ordered source bindings for a project (empty if none)."""
    registry = load_project_sources(project_id, local_appdata=local_appdata)
    return list(registry["sources"])


def find_source_by_id(
    project_id: str,
    source_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> dict[str, Any] | None:
    """Return a source record by stable ``source_id``, or None."""
    validate_source_id(source_id)
    for source in list_project_sources(project_id, local_appdata=local_appdata):
        if source["source_id"] == source_id:
            return dict(source)
    return None


def _online_source_root_map_from_sources(
    sources: Iterable[dict[str, Any]],
) -> dict[str, str]:
    """Pure projection of validated source records into ``source_id`` -> ``current_location``.

    Includes a record iff its persistent ``state == ONLINE`` and it carries a
    non-empty ``current_location`` string. Never mutates the input collection
    and performs no filesystem access. Result order follows source order, so
    the projection is deterministic for a given registry.
    """
    result: dict[str, str] = {}
    for source in sources:
        if not isinstance(source, dict):
            continue
        if source.get("state") != STATE_ONLINE:
            continue
        source_id = source.get("source_id")
        location = source.get("current_location")
        if not isinstance(source_id, str) or not source_id:
            continue
        if not isinstance(location, str) or not location:
            continue
        result[source_id] = location
    return result


def build_online_source_root_map(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, str]:
    """Return the online-source root map: ``source_id`` -> ``current_location``.

    A read-only projection of the currently registered ONLINE sources. OFFLINE
    sources are omitted (never deleted, never mutated). It only reads the
    validated ``project_sources.json`` registry: no writes, no ``updated_at``
    change, no state mutation, and no filesystem existence probe. A missing or
    empty registry yields an empty map.
    """
    identifier = validate_project_id(project_id)
    registry = load_project_sources(identifier, local_appdata=local_appdata)
    return _online_source_root_map_from_sources(registry["sources"])


def add_project_source(
    project_id: str,
    current_location: str,
    display_label: str,
    *,
    local_appdata: str | Path | None = None,
    allow_shared_location: bool = False,
    source_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Add one explicit source binding to a project.

    Creates a new stable ``SRC-<uuid4>`` and atomically persists the registry.
    Same-project exact/overlapping locations are blocked. A location already
    used (exactly or overlapping) by another project requires explicit
    confirmation via ``allow_shared_location=True``; a new distinct source_id
    is created (never the other project's id).
    """
    identifier = validate_project_id(project_id)
    location = _validate_location(current_location)
    label = _validate_label(display_label)
    timestamp = _timestamp(now)
    new_id = validate_source_id(source_id) if source_id is not None else _new_source_id()

    registry = load_project_sources(identifier, local_appdata=local_appdata)

    conflict, conflicting_cid = _same_project_conflict(registry, location)
    if conflict is not None:
        if conflict == "DUPLICATE_LOCATION":
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_LOCATION)
        raise SourceRegistryError(CID_SOURCE_OVERLAPPING_LOCATION)

    cross_use = detect_cross_project_location_use(
        location, local_appdata=local_appdata, exclude_project_id=identifier
    )
    if cross_use and not allow_shared_location:
        raise SourceRegistryError(CID_SOURCE_CROSS_PROJECT_CONFLICT)

    for source in registry["sources"]:
        if source["source_id"] == new_id:
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_ID)

    record: dict[str, Any] = {
        "source_id": new_id,
        "display_label": label,
        "current_location": location,
        "state": STATE_ONLINE,
        "added_at": timestamp,
        "updated_at": timestamp,
        "legacy_source_root_id_alias": None,
    }
    registry["sources"].append(record)
    save_project_sources(registry, local_appdata=local_appdata)
    return dict(record)


def update_source_state(
    project_id: str,
    source_id: str,
    state: str,
    *,
    local_appdata: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Set a source's persistent state ONLINE/OFFLINE (identity preserved).

    State is never inferred from the filesystem in MS1.
    """
    identifier = validate_project_id(project_id)
    validate_source_id(source_id)
    if state not in _SOURCE_STATES:
        raise SourceRegistryError(CID_SOURCE_STATE_INVALID)
    timestamp = _timestamp(now)

    registry = load_project_sources(identifier, local_appdata=local_appdata)
    target = next(
        (s for s in registry["sources"] if s["source_id"] == source_id), None
    )
    if target is None:
        raise SourceRegistryError(CID_SOURCE_NOT_FOUND)
    target["state"] = state
    target["updated_at"] = timestamp
    save_project_sources(registry, local_appdata=local_appdata)
    return dict(target)


def reconnect_source(
    project_id: str,
    source_id: str,
    new_current_location: str,
    *,
    local_appdata: str | Path | None = None,
    confirmation: bool = True,
    allow_shared_location: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Update ``current_location`` for a source with EXPLICIT confirmation.

    MS1 reconnect is manual + explicit only. It does NOT decide whether the new
    location truly matches the old one (no fingerprints / catalog anchors); it
    only persists the new mutable location, keeps the stable ``source_id``, and
    sets state ONLINE. Requires ``confirmation=True`` and fails otherwise.
    """
    identifier = validate_project_id(project_id)
    validate_source_id(source_id)
    if not confirmation:
        raise SourceRegistryError(CID_SOURCE_RECONNECT_CONFIRMATION_REQUIRED)
    new_location = _validate_location(new_current_location)
    timestamp = _timestamp(now)

    registry = load_project_sources(identifier, local_appdata=local_appdata)
    target = next(
        (s for s in registry["sources"] if s["source_id"] == source_id), None
    )
    if target is None:
        raise SourceRegistryError(CID_SOURCE_NOT_FOUND)

    conflict, _ = _same_project_conflict(
        registry, new_location, ignore_source_id=source_id
    )
    if conflict is not None:
        if conflict == "DUPLICATE_LOCATION":
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_LOCATION)
        raise SourceRegistryError(CID_SOURCE_OVERLAPPING_LOCATION)

    cross_use = detect_cross_project_location_use(
        new_location, local_appdata=local_appdata, exclude_project_id=identifier
    )
    if cross_use and not allow_shared_location:
        raise SourceRegistryError(CID_SOURCE_CROSS_PROJECT_CONFLICT)

    target["current_location"] = new_location
    target["state"] = STATE_ONLINE
    target["updated_at"] = timestamp
    save_project_sources(registry, local_appdata=local_appdata)
    return dict(target)


# ---------------------------------------------------------------------------
# Conflict detection (same-project and cross-project, no DB)
# ---------------------------------------------------------------------------

def detect_project_location_conflicts(
    project_id: str,
    candidate_location: str,
    *,
    local_appdata: str | Path | None = None,
    ignore_source_id: str | None = None,
) -> tuple[str | None, str | None]:
    """Return (category, conflicting_source_id) for a candidate location within
    the same project, or (None, None) when no exact/overlapping conflict exists.

    Categories: ``DUPLICATE_LOCATION`` (exact) and ``OVERLAPPING_LOCATION``.
    """
    registry = load_project_sources(project_id, local_appdata=local_appdata)
    return _same_project_conflict(registry, candidate_location, ignore_source_id=ignore_source_id)


def detect_cross_project_location_use(
    current_location: str,
    *,
    local_appdata: str | Path | None = None,
    exclude_project_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return bindings in OTHER projects whose location is the same or overlaps.

    Read-only inspection of ``projects/*/project_sources.json``; no DB, no
    mutable global index. If another project's registry is malformed this FAILS
    CLOSED (raises) rather than silently skipping it.
    """
    location = _validate_location(current_location)
    root = projects_path(local_appdata)
    if not root.exists():
        return []

    results: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink():
            continue
        if _PROJECT_ID_RE.fullmatch(child.name) is None:
            continue
        other_project_id = child.name
        if exclude_project_id is not None and other_project_id == exclude_project_id:
            continue
        other_registry = load_project_sources(other_project_id, local_appdata=local_appdata)
        for source in other_registry["sources"]:
            other_location = source.get("current_location")
            if not isinstance(other_location, str) or not other_location.strip():
                continue
            if locations_overlap(location, other_location):
                results.append(
                    {
                        "project_id": other_project_id,
                        "source_id": source["source_id"],
                        "current_location": other_location,
                    }
                )
    return results


def _same_project_conflict(
    registry: dict[str, Any],
    candidate_location: str,
    ignore_source_id: str | None = None,
) -> tuple[str | None, str | None]:
    location = _validate_location(candidate_location)
    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        if ignore_source_id is not None and source.get("source_id") == ignore_source_id:
            continue
        other = source.get("current_location")
        if not isinstance(other, str) or not other.strip():
            continue
        if locations_equal(other, location):
            return ("DUPLICATE_LOCATION", source.get("source_id"))
        if is_location_ancestor_of(other, location) or is_location_ancestor_of(location, other):
            return ("OVERLAPPING_LOCATION", source.get("source_id"))
    return (None, None)


# ---------------------------------------------------------------------------
# MS2A — legacy source binding (stable identity + legacy alias)
#
# These helpers operate on persisted data / explicit arguments only. They
# never stat the filesystem, resolve drives, scan folders, probe media, or
# test whether a disk is connected. The legacy alias authority lives solely in
# project_sources.json: no second alias structure exists anywhere.
# ---------------------------------------------------------------------------

def validate_legacy_alias(value: object) -> str:
    """Validate a legacy ``source_root_id`` alias: non-empty, NUL-free string."""
    if not isinstance(value, str) or not value.strip():
        raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_INVALID)
    if "\x00" in value:
        raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_INVALID)
    return value


def resolve_legacy_source_id(
    project_id: str,
    legacy_root_id: str,
    *,
    local_appdata: str | Path | None = None,
) -> dict[str, Any] | None:
    """Resolve a legacy root id to its stable binding, if any.

    Looks up ``project_sources.json`` for a source whose
    ``legacy_source_root_id_alias == legacy_root_id``.

    - If exactly one source holds that alias: return it (idempotent reuse).
    - If no source holds it: return None.
    - If more than one source holds the same alias (structurally impossible
      after registry validation, but guarded anyway): FAIL CLOSED.

    No filesystem / media access is performed.
    """
    identifier = validate_project_id(project_id)
    legacy_root_id = validate_legacy_alias(legacy_root_id)
    registry = load_project_sources(identifier, local_appdata=local_appdata)
    matches = resolve_legacy_source_id_from_registry(registry, legacy_root_id)
    if len(matches) == 1:
        return dict(matches[0])
    if len(matches) > 1:
        raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_CONFLICT)
    return None


def resolve_legacy_source_id_from_registry(
    registry: dict[str, Any], legacy_root_id: str
) -> list[dict[str, Any]]:
    """Pure lookup of sources whose alias equals ``legacy_root_id``.

    Returns all matching records (0..1 in practice). Raises
    ``CID_SOURCE_LEGACY_ALIAS_CONFLICT`` if more than one record maps to the
    requested alias.
    """
    legacy_root_id = validate_legacy_alias(legacy_root_id)
    matches = [
        dict(source)
        for source in registry.get("sources", [])
        if isinstance(source, dict)
        and source.get("legacy_source_root_id_alias") == legacy_root_id
    ]
    if len(matches) > 1:
        raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_CONFLICT)
    return matches


def add_legacy_project_source(
    project_id: str,
    legacy_root_id: str,
    current_location: str,
    display_label: str,
    *,
    local_appdata: str | Path | None = None,
    state: str | None = None,
    allow_shared_location: bool = False,
    source_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create/ensure a legacy migration binding for a project and return it.

    This is the idempotent legacy-binding entry point for MS2A:

    - If the registry already holds exactly one source whose
      ``legacy_source_root_id_alias == legacy_root_id``, that stable source is
      returned (no new SRC-<uuid4> is generated).
    - Otherwise a new stable ``SRC-<uuid4>`` binding is created with the given
      explicit alias, and atomically persisted.

    Guard rails:
    - Alias must be a non-empty, NUL-free string.
    - Alias must be unique within the project: a second source may not claim
      the same legacy alias, so the helper never silently reuses a different
      source.
    - Conflicting alias registries fail closed.
    - ``project_sources.json`` schema remains v1.
    - Default state is OFFLINE for automatic/administrative legacy migration
      (``OFFLINE_IS_NOT_MISSING=True``); an explicit validated allowed state
      may be supplied by the caller. No filesystem check is performed.
    """
    identifier = validate_project_id(project_id)
    legacy_root_id = validate_legacy_alias(legacy_root_id)
    location = _validate_location(current_location)
    label = _validate_label(display_label)
    if state is None:
        state = STATE_OFFLINE
    if state not in _SOURCE_STATES:
        raise SourceRegistryError(CID_SOURCE_STATE_INVALID)
    if source_id is not None:
        validate_source_id(source_id)
    timestamp = _timestamp(now)

    registry = load_project_sources(identifier, local_appdata=local_appdata)

    existing = resolve_legacy_source_id_from_registry(registry, legacy_root_id)
    if len(existing) > 1:
        raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_CONFLICT)
    if len(existing) == 1:
        return dict(existing[0])

    for source in registry.get("sources", []):
        if not isinstance(source, dict):
            continue
        other_alias = source.get("legacy_source_root_id_alias")
        if other_alias is not None and other_alias == legacy_root_id:
            raise SourceRegistryError(CID_SOURCE_LEGACY_ALIAS_CONFLICT)

    conflict, _ = _same_project_conflict(registry, location)
    if conflict is not None:
        if conflict == "DUPLICATE_LOCATION":
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_LOCATION)
        raise SourceRegistryError(CID_SOURCE_OVERLAPPING_LOCATION)

    cross_use = detect_cross_project_location_use(
        location, local_appdata=local_appdata, exclude_project_id=identifier
    )
    if cross_use and not allow_shared_location:
        raise SourceRegistryError(CID_SOURCE_CROSS_PROJECT_CONFLICT)

    new_id = validate_source_id(source_id) if source_id is not None else _new_source_id()
    for source in registry.get("sources", []):
        if source["source_id"] == new_id:
            raise SourceRegistryError(CID_SOURCE_DUPLICATE_ID)

    record: dict[str, Any] = {
        "source_id": new_id,
        "display_label": label,
        "current_location": location,
        "state": state,
        "added_at": timestamp,
        "updated_at": timestamp,
        "legacy_source_root_id_alias": legacy_root_id,
    }
    registry["sources"].append(record)
    save_project_sources(registry, local_appdata=local_appdata)
    return dict(record)


__all__ = [
    "PROJECT_SOURCES_FORMAT",
    "PROJECT_SOURCES_SCHEMA_VERSION",
    "STATE_ONLINE",
    "STATE_OFFLINE",
    "SourceRegistryError",
    "normalize_location",
    "locations_equal",
    "is_location_ancestor_of",
    "locations_overlap",
    "validate_source_id",
    "empty_registry",
    "load_project_sources",
    "is_valid_registry",
    "save_project_sources",
    "list_project_sources",
    "find_source_by_id",
    "build_online_source_root_map",
    "add_project_source",
    "update_source_state",
    "reconnect_source",
    "detect_project_location_conflicts",
    "detect_cross_project_location_use",
    "validate_legacy_alias",
    "resolve_legacy_source_id",
    "resolve_legacy_source_id_from_registry",
    "add_legacy_project_source",
]
