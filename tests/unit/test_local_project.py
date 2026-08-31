from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import (
    CID_ACTIVE_PROJECT_INVALID,
    CID_ACTIVE_PROJECT_NOT_FOUND,
    CID_ACTIVE_PROJECT_REQUIRED,
    LocalProjectError,
    active_project_path,
    create_project,
    list_projects,
    load_active_project,
    project_manifest_path,
    project_selection_store_path,
    select_project,
    source_video_profiles_path,
    validate_project_id,
)

PROJECT_ID = "PRJ-123e4567-e89b-42d3-a456-426614174000"


def test_create_select_switch_and_exact_storage(tmp_path: Path) -> None:
    first = create_project("Uno", local_appdata=tmp_path, project_id=PROJECT_ID)
    second = create_project("Dos", local_appdata=tmp_path)
    assert first["format"] == "CID_PROJECT"
    assert first["project_name"] == "Uno"
    assert project_selection_store_path(PROJECT_ID, tmp_path).is_dir()
    assert source_video_profiles_path(PROJECT_ID, tmp_path).name == "source_video_profiles.json"
    assert not active_project_path(tmp_path).exists()

    select_project(PROJECT_ID, local_appdata=tmp_path)
    assert load_active_project(local_appdata=tmp_path)["project_id"] == PROJECT_ID
    select_project(second["project_id"], local_appdata=tmp_path)
    assert load_active_project(local_appdata=tmp_path)["project_id"] == second["project_id"]
    listed = list_projects(local_appdata=tmp_path)
    assert [item["project_id"] for item in listed] == sorted(
        [first["project_id"], second["project_id"]]
    )
    assert {item["project_name"] for item in listed} == {"Uno", "Dos"}


def test_active_pointer_contains_exactly_project_id(tmp_path: Path) -> None:
    create_project("Proyecto", local_appdata=tmp_path, project_id=PROJECT_ID)
    select_project(PROJECT_ID, local_appdata=tmp_path)
    assert json.loads(active_project_path(tmp_path).read_text(encoding="utf-8")) == {
        "project_id": PROJECT_ID
    }


def test_missing_malformed_and_stale_active_project_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(LocalProjectError, match=CID_ACTIVE_PROJECT_REQUIRED):
        load_active_project(local_appdata=tmp_path)
    active_project_path(tmp_path).parent.mkdir(parents=True)
    active_project_path(tmp_path).write_text('{"project_id":"../escape"}', encoding="utf-8")
    with pytest.raises(LocalProjectError, match=CID_ACTIVE_PROJECT_INVALID):
        load_active_project(local_appdata=tmp_path)
    active_project_path(tmp_path).write_text(
        json.dumps({"project_id": PROJECT_ID}), encoding="utf-8"
    )
    with pytest.raises(LocalProjectError, match=CID_ACTIVE_PROJECT_NOT_FOUND):
        load_active_project(local_appdata=tmp_path)


@pytest.mark.parametrize("value", ["../x", "PRJ-../../x", PROJECT_ID + "/x", PROJECT_ID.upper()])
def test_project_id_traversal_and_noncanonical_values_refused(value: str) -> None:
    with pytest.raises(LocalProjectError, match=CID_ACTIVE_PROJECT_INVALID):
        validate_project_id(value)


def test_project_writes_are_atomic_utf8_and_no_scan_creates_project(tmp_path: Path) -> None:
    assert list_projects(local_appdata=tmp_path) == []
    create_project("Película", local_appdata=tmp_path, project_id=PROJECT_ID)
    raw = project_manifest_path(PROJECT_ID, tmp_path).read_text(encoding="utf-8")
    assert "Película" in raw
    assert not list(project_manifest_path(PROJECT_ID, tmp_path).parent.glob("*.tmp"))
    assert not active_project_path(tmp_path).exists()
