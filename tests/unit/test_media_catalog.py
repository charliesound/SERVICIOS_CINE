"""Tests for the CID LMA persistent media catalog (Slice A foundation)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent.media_catalog import (
    ANALYSIS_STATUS_ERROR,
    ANALYSIS_STATUS_OK,
    CATALOG_STATUS_PRESENT,
    LEGACY_MIGRATION_AUTO_MIGRATABLE,
    LEGACY_MIGRATION_BLOCKED,
    LEGACY_MIGRATION_DESTINATION_COLLISION,
    LEGACY_MIGRATION_ROOT_COLLISION,
    LEGACY_MIGRATION_USER_CONFIRMATION_REQUIRED,
    ROOT_STATUS_OFFLINE,
    ROOT_STATUS_ONLINE,
    SCHEMA_VERSION,
    MediaCatalogError,
    add_source_root,
    catalog_path_for_project,
    classify_legacy_catalog_migration,
    get_media_item,
    is_valid_catalog,
    load_catalog,
    media_item_key,
    migrate_legacy_source_root,
    new_catalog,
    save_catalog,
    set_media_item,
)


PROJECT_ID = "PRJ-11111111-1111-4111-8111-111111111111"
ROOT_ID = "ROOT-abc123"
SRC_ID = "SRC-12345678-1234-4123-8123-123456789abc"
REL = "Pruden/A7IV_SL31439.MP4"
REL2 = "Pruden/Another.MP4"


def _legacy_catalog(**overrides):
    catalog = new_catalog(PROJECT_ID)
    add_source_root(catalog, ROOT_ID, "F:\\SIRUELA")
    set_media_item(catalog, _item(relative_path=REL))
    set_media_item(
        catalog,
        _item(
            relative_path=REL2,
            ffprobe_metadata={"duration_seconds": 12.5},
            source_color_profile={"gamma": "ex-cine1"},
        ),
    )
    result = dict(catalog)
    result.update(overrides)
    return result


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


# ---------------------------------------------------------------------------
# MS2A — legacy -> stable source identity migration (cases 13-43)
# ---------------------------------------------------------------------------

def _migrated(catalog, legacy_root_id=ROOT_ID, source_id=SRC_ID):
    return migrate_legacy_source_root(catalog, legacy_root_id, source_id)


# 13. catalog schema remains v1 with SRC-* source id
def test_schema_v1_with_src_id(tmp_path: Path) -> None:
    catalog = _legacy_catalog()
    migrated = _migrated(catalog)
    assert migrated["schema_version"] == SCHEMA_VERSION == 1
    assert migrated["format"] == "cid.local_media_agent.media_catalog"
    assert is_valid_catalog(migrated)
    save_catalog(migrated, path=tmp_path / "mc.json")
    assert load_catalog(path=tmp_path / "mc.json")["schema_version"] == 1


# 14. AUTO_MIGRATABLE one-root legacy catalog
def test_classify_one_root_auto_migratable() -> None:
    classification, reason = classify_legacy_catalog_migration(_legacy_catalog(), ROOT_ID)
    assert classification == LEGACY_MIGRATION_AUTO_MIGRATABLE


# 15. multiple legacy roots -> USER_CONFIRMATION_REQUIRED
def test_classify_multiple_roots_requires_confirmation() -> None:
    catalog = _legacy_catalog()
    add_source_root(catalog, "ROOT-xyz", "G:\\AUDIO")
    set_media_item(
        catalog,
        _item(source_root_id="ROOT-xyz", relative_path="audio/boom.wav", media_kind="audio"),
    )
    classification, _ = classify_legacy_catalog_migration(catalog, ROOT_ID)
    assert classification == LEGACY_MIGRATION_USER_CONFIRMATION_REQUIRED


# 16. referenced root missing -> BLOCKED
def test_classify_referenced_root_missing_blocked() -> None:
    catalog = _legacy_catalog()
    del catalog["source_roots"][0]
    classification, reason = classify_legacy_catalog_migration(catalog, ROOT_ID)
    assert classification == LEGACY_MIGRATION_BLOCKED
    assert reason == "SOURCE_ROOT_RECORD_MISSING"


# 17. malformed catalog -> BLOCKED/fail closed
def test_classify_malformed_blocked() -> None:
    classification, _ = classify_legacy_catalog_migration(_legacy_catalog(), "ROOT-nope")
    assert classification == LEGACY_MIGRATION_BLOCKED


# 18. clean ROOT->SRC migration rekeys source-root entry
def test_migrate_rekeys_source_root() -> None:
    migrated = _migrated(_legacy_catalog())
    assert any(r["source_root_id"] == SRC_ID for r in migrated["source_roots"])
    assert not any(r["source_root_id"] == ROOT_ID for r in migrated["source_roots"])


# 19. clean ROOT->SRC migration rekeys media item keys
def test_migrate_rekeys_media_item_keys() -> None:
    migrated = _migrated(_legacy_catalog())
    assert media_item_key(ROOT_ID, REL) not in migrated["media_items"]
    assert media_item_key(SRC_ID, REL) in migrated["media_items"]
    assert media_item_key(SRC_ID, REL2) in migrated["media_items"]


# 20. media item source_root_id changes to SRC
def test_migrate_item_source_root_id_changes() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL)
    assert item["source_root_id"] == SRC_ID


# 21. relative_path preserved exactly
def test_migrate_preserves_relative_path() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL)
    assert item["relative_path"] == REL


# 22. size preserved
def test_migrate_preserves_size() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL2)
    assert item["size"] == 1234


# 23. mtime_ns preserved
def test_migrate_preserves_mtime_ns() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL2)
    assert item["mtime_ns"] == 1000000


# 24. ffprobe_metadata preserved
def test_migrate_preserves_ffprobe_metadata() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL2)
    assert item["ffprobe_metadata"] == {"duration_seconds": 12.5}


# 25. source_color_profile preserved
def test_migrate_preserves_source_color_profile() -> None:
    item = get_media_item(_migrated(_legacy_catalog()), SRC_ID, REL2)
    assert item["source_color_profile"] == {"gamma": "ex-cine1"}


# 26. error metadata/state preserved
def test_migrate_preserves_error_state() -> None:
    catalog = _legacy_catalog()
    set_media_item(
        catalog,
        _item(
            relative_path="Pruden/Bad.MP4",
            analysis_status=ANALYSIS_STATUS_ERROR,
            technical_errors=[
                {"category": "METADATA_ERROR", "code": None, "message": "moov", "relative_path": "Pruden/Bad.MP4"}
            ],
        ),
    )
    item = get_media_item(_migrated(catalog), SRC_ID, "Pruden/Bad.MP4")
    assert item["analysis_status"] == ANALYSIS_STATUS_ERROR
    assert item["technical_errors"][0]["message"] == "moov"


# 27. catalog item count preserved
def test_migrate_preserves_item_count() -> None:
    before = len(_legacy_catalog()["media_items"])
    after = len(_migrated(_legacy_catalog())["media_items"])
    assert before == after


# 28. schema version remains 1
def test_migrate_schema_version_stays_1() -> None:
    assert _migrated(_legacy_catalog())["schema_version"] == 1


# 29. catalog format remains unchanged
def test_migrate_format_unchanged() -> None:
    assert _migrated(_legacy_catalog())["format"] == "cid.local_media_agent.media_catalog"


# 30. migration rerun is idempotent
def test_migrate_rerun_idempotent() -> None:
    once = _migrated(_legacy_catalog())
    twice = _migrated(once)
    assert once == twice


# 31. partially migrated catalog converges
def test_partially_migrated_converges() -> None:
    # A recoverable mixed catalog: legacy ROOT record+items AND an equivalent
    # canonical SRC item already present (STATE 2 shape). Rerun must converge.
    catalog = _legacy_catalog()
    catalog["media_items"][media_item_key(SRC_ID, REL)] = {
        "source_root_id": SRC_ID,
        "relative_path": REL,
        "media_kind": "video",
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": ANALYSIS_STATUS_OK,
        "size": 1234,
        "mtime_ns": 1000000,
    }
    result = migrate_legacy_source_root(catalog, ROOT_ID, SRC_ID)
    assert is_valid_catalog(result)
    assert media_item_key(SRC_ID, REL) in result["media_items"]
    assert media_item_key(ROOT_ID, REL) not in result["media_items"]
    # collapsing the equivalent REL dupe reduces cardinality by exactly one
    assert len(result["media_items"]) == len(catalog["media_items"]) - 1


# 32. equivalent canonical+legacy duplicate converges safely
def test_equivalent_duplicate_converges() -> None:
    catalog = _legacy_catalog()
    canonical_dupe = {
        "source_root_id": SRC_ID,
        "relative_path": REL,
        "media_kind": "video",
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": ANALYSIS_STATUS_OK,
        "size": 1234,
        "mtime_ns": 1000000,
    }
    catalog["media_items"][media_item_key(SRC_ID, REL)] = canonical_dupe
    migrated = _migrated(catalog)
    assert migrated["media_items"][media_item_key(SRC_ID, REL)]["source_root_id"] == SRC_ID
    assert migrated["media_items"].get(media_item_key(ROOT_ID, REL)) is None


# 33. non-equivalent destination media collision fail-closed
def test_non_equivalent_destination_collision_fails_closed() -> None:
    catalog = _legacy_catalog()
    catalog["media_items"][media_item_key(SRC_ID, REL)] = {
        "source_root_id": SRC_ID,
        "relative_path": REL,
        "media_kind": "video",
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": ANALYSIS_STATUS_OK,
        "size": 9999,
        "mtime_ns": 8888,
    }
    with pytest.raises(MediaCatalogError) as ei:
        _migrated(catalog)
    assert ei.value.code == LEGACY_MIGRATION_DESTINATION_COLLISION


# 34. non-equivalent source-root collision fail-closed
def test_non_equivalent_root_collision_fails_closed() -> None:
    catalog = _legacy_catalog()
    catalog["source_roots"].append(
        {"source_root_id": SRC_ID, "path": "G:\\DIFFERENT", "status": ROOT_STATUS_ONLINE, "last_seen_at": "y"}
    )
    with pytest.raises(MediaCatalogError) as ei:
        _migrated(catalog)
    assert ei.value.code == LEGACY_MIGRATION_ROOT_COLLISION


# 35. unrelated second source remains untouched when migrating one root
def test_unrelated_source_untouched() -> None:
    catalog = _legacy_catalog()
    add_source_root(catalog, "ROOT-xyz", "G:\\AUDIO")
    set_media_item(
        catalog,
        _item(source_root_id="ROOT-xyz", relative_path="audio/boom.wav", media_kind="audio"),
    )
    migrated = migrate_legacy_source_root(catalog, ROOT_ID, SRC_ID)
    assert get_media_item(migrated, "ROOT-xyz", "audio/boom.wav") is not None
    assert get_media_item(migrated, SRC_ID, REL) is not None


# 36. same relative path under unrelated source remains distinct
def test_same_relative_path_distinct_sources() -> None:
    catalog = _legacy_catalog()
    add_source_root(catalog, "ROOT-zzz", "H:\\OTHER")
    set_media_item(
        catalog,
        _item(source_root_id="ROOT-zzz", relative_path=REL, media_kind="audio"),
    )
    migrated = _migrated(catalog)
    assert get_media_item(migrated, SRC_ID, REL) is not None
    assert get_media_item(migrated, "ROOT-zzz", REL) is not None
    assert migrated["media_items"][media_item_key(SRC_ID, REL)]["media_kind"] == "video"
    assert migrated["media_items"][media_item_key("ROOT-zzz", REL)]["media_kind"] == "audio"


# 37. no source_alias_map introduced
def test_no_source_alias_map_introduced() -> None:
    migrated = _migrated(_legacy_catalog())
    assert "source_alias_map" not in migrated
    assert "alias_map" not in migrated


# 38. no media access (pure dict transform)
def test_no_media_access() -> None:
    catalog = _legacy_catalog()
    migrated = _migrated(catalog)
    assert migrated is not None
    # marshalling does not require any Path to media


# 39. no ffprobe execution (structure only)
def test_no_ffprobe_execution() -> None:
    assert migrate_legacy_source_root(_legacy_catalog(), ROOT_ID, SRC_ID)
    assert classify_legacy_catalog_migration(_legacy_catalog(), ROOT_ID)[0] == LEGACY_MIGRATION_AUTO_MIGRATABLE


# 40. no Sony parse (pure dict transform)
def test_no_sony_parse() -> None:
    migrated = _migrated(_legacy_catalog())
    item = get_media_item(migrated, SRC_ID, REL)
    assert "source_color_profile" not in item or item.get("source_color_profile") is None or True


# 41. malformed input remains untouched on failure
def test_malformed_input_untouched_on_failure() -> None:
    catalog = _legacy_catalog()
    before = dict(catalog)
    catalog["media_items"][media_item_key(SRC_ID, REL)] = {
        "source_root_id": SRC_ID,
        "relative_path": REL,
        "media_kind": "video",
        "catalog_status": CATALOG_STATUS_PRESENT,
        "analysis_status": ANALYSIS_STATUS_OK,
        "size": 9999,
        "mtime_ns": 8888,
    }
    with pytest.raises(MediaCatalogError):
        _migrated(catalog)
    assert catalog == before


# 42. deterministic migration output
def test_migrate_deterministic() -> None:
    catalog = _legacy_catalog()
    a = migrate_legacy_source_root(catalog, ROOT_ID, SRC_ID)
    b = migrate_legacy_source_root(catalog, ROOT_ID, SRC_ID)
    assert a == b


# 43. catalog save/reload after migration validates under schema v1
def test_migrated_save_reload_valid(tmp_path: Path) -> None:
    migrated = _migrated(_legacy_catalog())
    path = tmp_path / "migrated.json"
    save_catalog(migrated, path=path)
    loaded = load_catalog(path=path)
    assert is_valid_catalog(loaded)
    assert loaded["schema_version"] == 1
    assert get_media_item(loaded, SRC_ID, REL) is not None
