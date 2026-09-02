"""Tests for the CID LMA persistent media catalog (Slice A foundation)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent.media_catalog import (
    ANALYSIS_STATUS_ERROR,
    ANALYSIS_STATUS_OK,
    CATALOG_STATUS_PRESENT,
    SCHEMA_VERSION,
    MediaCatalogError,
    add_source_root,
    catalog_path_for_project,
    get_media_item,
    load_catalog,
    media_item_key,
    new_catalog,
    save_catalog,
    set_media_item,
)


PROJECT_ID = "PRJ-11111111-1111-4111-8111-111111111111"
ROOT_ID = "ROOT-abc123"
REL = "Pruden/A7IV_SL31439.MP4"


def _item(**overrides):
    base = {
        "source_root_id": ROOT_ID,
        "relative_path": REL,
        "media_kind": "video",
        "size": 1234,
        "mtime_ns": 1000000,
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": ANALYSIS_STATUS_OK,
    }
    base.update(overrides)
    return base


def test_new_catalog() -> None:
    catalog = new_catalog(PROJECT_ID)
    assert catalog["format"] == "cid.local_media_agent.media_catalog"
    assert catalog["schema_version"] == SCHEMA_VERSION == 1
    assert catalog["project_id"] == PROJECT_ID
    assert catalog["media_items"] == {}
    assert isinstance(catalog["source_roots"], list)


def test_save_load_roundtrip(tmp_path: Path) -> None:
    catalog = new_catalog(PROJECT_ID)
    add_source_root(catalog, ROOT_ID, "F:\\SIRUELA")
    set_media_item(catalog, _item(ffprobe_metadata={"duration_seconds": 10.5}))
    path = tmp_path / "media_catalog.json"
    save_catalog(catalog, path=path)
    loaded = load_catalog(path=path)
    assert loaded["schema_version"] == SCHEMA_VERSION
    assert loaded["project_id"] == PROJECT_ID
    item = get_media_item(loaded, ROOT_ID, REL)
    assert item is not None
    assert item["ffprobe_metadata"]["duration_seconds"] == 10.5


def test_atomic_save_creates_file_without_temp_leftover(tmp_path: Path) -> None:
    catalog = new_catalog(PROJECT_ID)
    set_media_item(catalog, _item())
    path = tmp_path / "media_catalog.json"
    save_catalog(catalog, path=path)
    assert path.is_file()
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".")]
    assert leftovers == []


def test_malformed_catalog_handled_safely(tmp_path: Path) -> None:
    path = tmp_path / "media_catalog.json"
    path.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(MediaCatalogError) as ei:
        load_catalog(path=path)
    assert ei.value.code == "CATALOG_MALFORMED"
    # malformed catalog is NOT deleted
    assert path.is_file()


def test_wrong_schema_version_rejected(tmp_path: Path) -> None:
    path = tmp_path / "media_catalog.json"
    payload = dict(new_catalog(PROJECT_ID))
    payload["schema_version"] = 999
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(MediaCatalogError) as ei:
        load_catalog(path=path)
    assert ei.value.code == "CATALOG_MALFORMED"


def test_relative_paths_preserved() -> None:
    catalog = new_catalog(PROJECT_ID)
    set_media_item(catalog, _item(relative_path="a/b/c.MP4"))
    item = get_media_item(catalog, ROOT_ID, "a/b/c.MP4")
    assert item["relative_path"] == "a/b/c.MP4"


def test_absolute_source_media_path_rejected() -> None:
    catalog = new_catalog(PROJECT_ID)
    with pytest.raises(MediaCatalogError):
        set_media_item(catalog, _item(relative_path="F:\\SIRUELA\\clip.MP4".replace("\\", "/")))
    with pytest.raises(MediaCatalogError):
        set_media_item(catalog, _item(relative_path="/abs/path.MP4"))


def test_media_item_key_deterministic() -> None:
    assert media_item_key(ROOT_ID, REL) == media_item_key(ROOT_ID, REL)
    assert media_item_key("a", "x").startswith("a::")


def test_error_item_valid_in_catalog(tmp_path: Path) -> None:
    catalog = new_catalog(PROJECT_ID)
    item = _item(
        analysis_status=ANALYSIS_STATUS_ERROR,
        technical_errors=[{"category": "METADATA_ERROR", "code": None, "message": "moov atom not found", "relative_path": REL}],
        source_color_profile={"gamma": "ex-cine1"},
    )
    set_media_item(catalog, item)
    path = tmp_path / "media_catalog.json"
    save_catalog(catalog, path=path)
    loaded = load_catalog(path=path)
    stored = get_media_item(loaded, ROOT_ID, REL)
    assert stored["analysis_status"] == ANALYSIS_STATUS_ERROR
    assert stored["technical_errors"][0]["message"] == "moov atom not found"
    assert stored["source_color_profile"]["gamma"] == "ex-cine1"


def test_catalog_path_for_project(tmp_path: Path) -> None:
    path = catalog_path_for_project(PROJECT_ID, local_appdata=tmp_path)
    assert path.name == "media_catalog.json"
    assert "projects" in path.parts
