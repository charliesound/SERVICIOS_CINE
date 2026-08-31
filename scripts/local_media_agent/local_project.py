"""CID local project identity and project-scoped storage authority."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

PROJECT_FORMAT = "CID_PROJECT"
PROJECT_VERSION = 1

CID_ACTIVE_PROJECT_REQUIRED = "CID_ACTIVE_PROJECT_REQUIRED"
CID_ACTIVE_PROJECT_INVALID = "CID_ACTIVE_PROJECT_INVALID"
CID_ACTIVE_PROJECT_NOT_FOUND = "CID_ACTIVE_PROJECT_NOT_FOUND"
CID_PROJECT_MANIFEST_INVALID = "CID_PROJECT_MANIFEST_INVALID"

_PROJECT_ID_RE = re.compile(
    r"^PRJ-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class LocalProjectError(ValueError):
    """Controlled local-project refusal."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def cid_data_root(local_appdata: str | Path | None = None) -> Path:
    base = local_appdata if local_appdata is not None else os.environ.get("LOCALAPPDATA")
    if base is None or not str(base).strip():
        raise LocalProjectError(CID_ACTIVE_PROJECT_REQUIRED)
    return Path(base) / "CID"


def validate_project_id(project_id: object) -> str:
    if not isinstance(project_id, str) or _PROJECT_ID_RE.fullmatch(project_id) is None:
        raise LocalProjectError(CID_ACTIVE_PROJECT_INVALID)
    try:
        parsed = UUID(project_id[4:])
    except ValueError as exc:
        raise LocalProjectError(CID_ACTIVE_PROJECT_INVALID) from exc
    if parsed.version != 4 or str(parsed) != project_id[4:]:
        raise LocalProjectError(CID_ACTIVE_PROJECT_INVALID)
    return project_id


def projects_path(local_appdata: str | Path | None = None) -> Path:
    return cid_data_root(local_appdata) / "projects"


def active_project_path(local_appdata: str | Path | None = None) -> Path:
    return cid_data_root(local_appdata) / "active_project.json"


def project_path(project_id: str, local_appdata: str | Path | None = None) -> Path:
    return projects_path(local_appdata) / validate_project_id(project_id)


def project_manifest_path(project_id: str, local_appdata: str | Path | None = None) -> Path:
    return project_path(project_id, local_appdata) / "project.json"


def project_video_profile_path(
    project_id: str, local_appdata: str | Path | None = None
) -> Path:
    return project_path(project_id, local_appdata) / "project_video_profile.json"


def source_video_profiles_path(
    project_id: str, local_appdata: str | Path | None = None
) -> Path:
    return project_path(project_id, local_appdata) / "source_video_profiles.json"


def project_selection_store_path(
    project_id: str, local_appdata: str | Path | None = None
) -> Path:
    return project_path(project_id, local_appdata) / "editorial_selections"


def create_project(
    project_name: str,
    *,
    local_appdata: str | Path | None = None,
    project_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create one project without implicitly activating it."""
    name = _validate_project_name(project_name)
    identifier = validate_project_id(project_id) if project_id else f"PRJ-{uuid4()}"
    timestamp = _timestamp(now)
    directory = project_path(identifier, local_appdata)
    try:
        directory.mkdir(parents=True, exist_ok=False)
        project_selection_store_path(identifier, local_appdata).mkdir()
    except OSError as exc:
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID) from exc
    manifest = {
        "format": PROJECT_FORMAT,
        "version": PROJECT_VERSION,
        "project_id": identifier,
        "project_name": name,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    try:
        atomic_write_json(project_manifest_path(identifier, local_appdata), manifest)
    except Exception:
        try:
            project_selection_store_path(identifier, local_appdata).rmdir()
            directory.rmdir()
        except OSError:
            pass
        raise
    return manifest


def select_project(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, str]:
    manifest = load_project(project_id, local_appdata=local_appdata)
    pointer = {"project_id": manifest["project_id"]}
    atomic_write_json(active_project_path(local_appdata), pointer)
    return pointer


def load_project(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    identifier = validate_project_id(project_id)
    path = project_manifest_path(identifier, local_appdata)
    if not path.is_file():
        raise LocalProjectError(CID_ACTIVE_PROJECT_NOT_FOUND)
    manifest = _read_object(path, CID_PROJECT_MANIFEST_INVALID)
    expected = {
        "format", "version", "project_id", "project_name", "created_at", "updated_at"
    }
    if set(manifest) != expected:
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    try:
        valid_id = validate_project_id(manifest.get("project_id"))
        _validate_project_name(manifest.get("project_name"))
    except LocalProjectError as exc:
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID) from exc
    if (
        manifest.get("format") != PROJECT_FORMAT
        or manifest.get("version") != PROJECT_VERSION
        or valid_id != identifier
        or not _valid_timestamp(manifest.get("created_at"))
        or not _valid_timestamp(manifest.get("updated_at"))
    ):
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    return manifest


def load_active_project(
    *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    path = active_project_path(local_appdata)
    if not path.is_file():
        raise LocalProjectError(CID_ACTIVE_PROJECT_REQUIRED)
    pointer = _read_object(path, CID_ACTIVE_PROJECT_INVALID)
    if set(pointer) != {"project_id"}:
        raise LocalProjectError(CID_ACTIVE_PROJECT_INVALID)
    try:
        identifier = validate_project_id(pointer.get("project_id"))
    except LocalProjectError as exc:
        raise LocalProjectError(CID_ACTIVE_PROJECT_INVALID) from exc
    try:
        return load_project(identifier, local_appdata=local_appdata)
    except LocalProjectError as exc:
        if exc.code == CID_ACTIVE_PROJECT_NOT_FOUND:
            raise
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID) from exc


def list_projects(*, local_appdata: str | Path | None = None) -> list[dict[str, Any]]:
    root = projects_path(local_appdata)
    if not root.exists():
        return []
    result: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_dir() and not child.is_symlink() and _PROJECT_ID_RE.fullmatch(child.name):
            result.append(load_project(child.name, local_appdata=local_appdata))
    return result


def active_project_selection_store(
    *, local_appdata: str | Path | None = None
) -> tuple[dict[str, Any], Path]:
    project = load_active_project(local_appdata=local_appdata)
    store = project_selection_store_path(project["project_id"], local_appdata)
    if not store.is_dir():
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    return project, store


def atomic_write_json(path: str | Path, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
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


def _read_object(path: Path, code: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LocalProjectError(code) from exc
    if not isinstance(payload, dict):
        raise LocalProjectError(code)
    return payload


def _validate_project_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    if len(value) > 200 or any(ord(character) < 32 for character in value):
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    return value


def _timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise LocalProjectError(CID_PROJECT_MANIFEST_INVALID)
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True
