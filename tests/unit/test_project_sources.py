"""Focused MS1 tests for the CID project source registry (project_sources.py).

Covers the 30 mandated MS1 scenarios using tmp_path only (no real media, no
scanning, no ffprobe, no grouping).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import (
    create_project,
    load_project,
    project_path,
    project_sources_path,
)
from scripts.local_media_agent.project_sources import (
    CID_SOURCE_CROSS_PROJECT_CONFLICT,
    CID_SOURCE_DUPLICATE_ID,
    CID_SOURCE_DUPLICATE_LOCATION,
    CID_SOURCE_ID_INVALID,
    CID_SOURCE_LEGACY_ALIAS_CONFLICT,
    CID_SOURCE_LEGACY_ALIAS_INVALID,
    CID_SOURCE_NOT_FOUND,
    CID_SOURCE_OVERLAPPING_LOCATION,
    CID_SOURCE_PROJECT_MISMATCH,
    CID_SOURCE_RECONNECT_CONFIRMATION_REQUIRED,
    CID_SOURCE_REGISTRY_INVALID,
    CID_SOURCE_STATE_INVALID,
    PROJECT_SOURCES_FORMAT,
    PROJECT_SOURCES_SCHEMA_VERSION,
    STATE_OFFLINE,
    STATE_ONLINE,
    SourceRegistryError,
    _online_source_root_map_from_sources,
    add_legacy_project_source,
    add_project_source,
    build_online_source_root_map,
    detect_cross_project_location_use,
    detect_project_location_conflicts,
    empty_registry,
    find_source_by_id,
    is_location_ancestor_of,
    is_valid_registry,
    list_project_sources,
    load_project_sources,
    locations_equal,
    reconnect_source,
    resolve_legacy_source_id,
    resolve_legacy_source_id_from_registry,
    save_project_sources,
    update_source_state,
    validate_legacy_alias,
    validate_source_id,
)


P1 = "PRJ-11111111-1111-4111-8111-111111111111"
P2 = "PRJ-22222222-2222-4222-8222-222222222222"
P3 = "PRJ-33333333-3333-4333-8333-333333333333"

SRC_ID_RE = re.compile(
    r"^SRC-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

NOW = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


def _write_raw_registry(project_id: str, payload: object, tmp_path: Path, *, valid_ids: bool = True) -> Path:
    path = project_sources_path(project_id, tmp_path)
    project_path(project_id, tmp_path).mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _make_src(source_id: str, location: str, *, label: str = "Cam", state: str = STATE_ONLINE) -> dict:
    return {
        "source_id": source_id,
        "display_label": label,
        "current_location": location,
        "state": state,
        "added_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "legacy_source_root_id_alias": None,
    }


# 1. missing registry -> valid empty in-memory registry, no file created
def test_missing_registry_returns_empty_and_does_not_create_file(tmp_path: Path) -> None:
    registry = load_project_sources(P1, local_appdata=tmp_path)
    assert is_valid_registry(registry, P1)
    assert registry["format"] == PROJECT_SOURCES_FORMAT
    assert registry["schema_version"] == PROJECT_SOURCES_SCHEMA_VERSION
    assert registry["project_id"] == P1
    assert registry["sources"] == []
    assert list_project_sources(P1, local_appdata=tmp_path) == []
    assert not project_sources_path(P1, tmp_path).exists()


# 2. save/reload empty registry
def test_save_reload_empty_registry(tmp_path: Path) -> None:
    save_project_sources(empty_registry(P1), local_appdata=tmp_path)
    path = project_sources_path(P1, tmp_path)
    assert path.is_file()
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert loaded["sources"] == []
    assert loaded["project_id"] == P1


# 3. add source creates a SRC-uuid identity
def test_add_source_creates_src_uuid(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    assert SRC_ID_RE.fullmatch(record["source_id"])
    assert record["state"] == STATE_ONLINE
    assert record["current_location"] == "F:\\SIRUELA"


# 4. add/reload preserves source_id
def test_add_reload_preserves_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    found = find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)
    assert found is not None
    assert found["source_id"] == record["source_id"]
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert [s["source_id"] for s in loaded["sources"]] == [record["source_id"]]


# 5. same project exact duplicate location blocked
def test_same_project_exact_duplicate_blocked(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P1, "F:\\SIRUELA", "Cam2", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_DUPLICATE_LOCATION


# 6. same project descendant source blocked
def test_same_project_descendant_blocked(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P1, "F:\\SIRUELA\\Audio", "Ext", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_OVERLAPPING_LOCATION


# 7. same project ancestor source blocked
def test_same_project_ancestor_blocked(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA\\Audio", "Ext", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_OVERLAPPING_LOCATION


# 8. sibling locations allowed
def test_sibling_source_locations_allowed(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    add_project_source(P1, "F:\\OTHER_FILM", "Cam2", local_appdata=tmp_path, now=NOW)
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 2


# 9. Windows same location case-insensitive
def test_windows_same_location_case_insensitive(tmp_path: Path) -> None:
    assert locations_equal("F:\\SIRUELA", "f:\\siruEla")
    add_project_source(P1, "f:\\siruEla", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P1, "F:\\SIRUELA", "Cam2", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_DUPLICATE_LOCATION


# 10. Windows trailing separator normalized for comparison
def test_windows_trailing_separator_normalized(tmp_path: Path) -> None:
    assert locations_equal("F:\\SIRUELA", "F:\\SIRUELA\\")
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P1, "F:\\SIRUELA\\", "Cam2", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_DUPLICATE_LOCATION


# 11. separator-safe containment: F:\FILM is not ancestor of F:\FILM2
def test_separator_safe_no_prefix_containment(tmp_path: Path) -> None:
    assert is_location_ancestor_of("F:\\FILM", "F:\\FILM2") is False
    assert is_location_ancestor_of("F:\\FILM", "F:\\FILM\\Sub") is True
    add_project_source(P1, "F:\\FILM", "Cam1", local_appdata=tmp_path, now=NOW)
    add_project_source(P1, "F:\\FILM2", "Cam2", local_appdata=tmp_path, now=NOW)
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 2


# 12. same location linked to second project without confirmation blocked
def test_cross_project_shared_without_confirmation_blocked(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P2, "F:\\SIRUELA", "CamB", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_CROSS_PROJECT_CONFLICT


# 13. same location linked to second project with explicit confirmation allowed
def test_cross_project_shared_with_confirmation_allowed(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    record = add_project_source(
        P2, "F:\\SIRUELA", "CamB", local_appdata=tmp_path, allow_shared_location=True, now=NOW
    )
    assert record["current_location"] == "F:\\SIRUELA"
    assert len(list_project_sources(P2, local_appdata=tmp_path)) == 1


# 14. cross-project shared bindings get DIFFERENT source_ids
def test_cross_project_shared_ids_distinct(tmp_path: Path) -> None:
    a = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(
        P2, "F:\\SIRUELA", "CamB", local_appdata=tmp_path, allow_shared_location=True, now=NOW
    )
    assert a["source_id"] != b["source_id"]


# 15. cross-project nested overlap requires explicit confirmation
def test_cross_project_nested_overlap_requires_confirmation(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        add_project_source(P2, "F:\\SIRUELA\\Audio", "ExtB", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_CROSS_PROJECT_CONFLICT
    rec = add_project_source(
        P2, "F:\\SIRUELA\\Audio", "ExtB",
        local_appdata=tmp_path, allow_shared_location=True, now=NOW,
    )
    assert rec["current_location"] == "F:\\SIRUELA\\Audio"


# 16. location update/reconnect preserves source_id
def test_reconnect_preserves_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    src_id = record["source_id"]
    updated = reconnect_source(
        P1, src_id, "J:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["source_id"] == src_id
    assert updated["current_location"] == "J:\\SIRUELA"
    assert updated["state"] == STATE_ONLINE
    assert find_source_by_id(P1, src_id, local_appdata=tmp_path)["current_location"] == "J:\\SIRUELA"


# 17. location update that overlaps another source in same project blocked
def test_reconnect_overlapping_another_source_blocked(tmp_path: Path) -> None:
    a = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "F:\\OTHER", "Cam2", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, b["source_id"], "F:\\SIRUELA\\Audio",
            local_appdata=tmp_path, confirmation=True, now=NOW,
        )
    assert ei.value.code == CID_SOURCE_OVERLAPPING_LOCATION
    assert find_source_by_id(P1, a["source_id"], local_appdata=tmp_path) is not None


# 18. state ONLINE -> OFFLINE preserves identity
def test_state_online_to_offline_preserves_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    updated = update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    assert updated["source_id"] == record["source_id"]
    assert updated["state"] == STATE_OFFLINE
    assert updated["current_location"] == "F:\\SIRUELA"


# 19. state OFFLINE -> ONLINE preserves identity
def test_state_offline_to_online_preserves_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    offline = update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    online = update_source_state(P1, record["source_id"], STATE_ONLINE, local_appdata=tmp_path, now=NOW)
    assert offline["source_id"] == online["source_id"] == record["source_id"]
    assert online["state"] == STATE_ONLINE


# 20. invalid state rejected
def test_invalid_state_rejected(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        update_source_state(P1, record["source_id"], "RECONNECTED", local_appdata=tmp_path, now=NOW)
    assert ei.value.code == CID_SOURCE_STATE_INVALID


# 21. duplicate source_id registry rejected (fail closed on load)
def test_duplicate_source_id_registry_rejected(tmp_path: Path) -> None:
    dup_id = "SRC-12345678-1234-4123-8123-123456789abc"
    registry = empty_registry(P2)
    registry["sources"] = [
        _make_src(dup_id, "F:\\A"),
        _make_src(dup_id, "F:\\B"),
    ]
    _write_raw_registry(P2, registry, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        load_project_sources(P2, local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_DUPLICATE_ID
    # original file untouched
    assert project_sources_path(P2, tmp_path).is_file()


# 22. project_id mismatch rejected
def test_project_id_mismatch_rejected(tmp_path: Path) -> None:
    registry = dict(empty_registry(P2))
    registry["project_id"] = P3
    _write_raw_registry(P2, registry, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        load_project_sources(P2, local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_PROJECT_MISMATCH


# 23. malformed JSON fail-closed and untouched
def test_malformed_json_fail_closed_and_untouched(tmp_path: Path) -> None:
    path = _write_raw_registry(P1, None, tmp_path)
    path.write_text("{ not valid json", encoding="utf-8")
    with pytest.raises(SourceRegistryError) as ei:
        load_project_sources(P1, local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_REGISTRY_INVALID
    assert path.read_text(encoding="utf-8") == "{ not valid json"
    assert not is_valid_registry(None, P1)


# 24. invalid schema/version rejected
def test_invalid_schema_version_rejected(tmp_path: Path) -> None:
    registry = dict(empty_registry(P1))
    registry["schema_version"] = 999
    _write_raw_registry(P1, registry, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        load_project_sources(P1, local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_REGISTRY_INVALID


# 25. legacy_source_root_id_alias persists/reloads
def test_legacy_alias_persists_and_reloads(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    registry = load_project_sources(P1, local_appdata=tmp_path)
    registry["sources"][0]["legacy_source_root_id_alias"] = "ROOT-abc123"
    save_project_sources(registry, local_appdata=tmp_path)
    reloaded = load_project_sources(P1, local_appdata=tmp_path)
    assert reloaded["sources"][0]["legacy_source_root_id_alias"] == "ROOT-abc123"


# 26. deterministic repeated serialization/reload
def test_deterministic_serialization_reload(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    path = project_sources_path(P1, tmp_path)
    first = path.read_text(encoding="utf-8")
    reg = load_project_sources(P1, local_appdata=tmp_path)
    save_project_sources(reg, local_appdata=tmp_path)
    second = path.read_text(encoding="utf-8")
    assert first == second


# 27. atomic save leaves no temp/partial file
def test_atomic_save_no_temp_leftover(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    project_dir = project_path(P1, tmp_path)
    leftovers = [p.name for p in project_dir.iterdir() if p.name.startswith(".")]
    assert leftovers == []
    assert not any(p.name.endswith(".tmp") for p in project_dir.iterdir())


# 28. cross-project detection fails closed if another registry malformed
def test_cross_project_fail_closed_on_malformed(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    malformed = project_sources_path(P3, tmp_path)
    project_path(P3, tmp_path).mkdir(parents=True, exist_ok=True)
    malformed.write_text("{ broken", encoding="utf-8")
    with pytest.raises(SourceRegistryError) as ei:
        detect_cross_project_location_use("F:\\SIRUELA", local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_REGISTRY_INVALID
    assert malformed.read_text(encoding="utf-8") == "{ broken"


# 29. location comparison is lexical only — no filesystem/media access
def test_location_comparison_is_lexical_only(tmp_path: Path) -> None:
    nonexistent = "F:\\DOES\\NOT\\EXIST_ANYWHERE"
    assert locations_equal(nonexistent, "f:\\does\\not\\exist_anywhere\\")
    assert is_location_ancestor_of("F:\\ROOT", "F:\\ROOT\\Sub")
    assert not is_location_ancestor_of("F:\\ROOT", "F:\\ROOTS")
    # POSIX remains case-sensitive
    assert not locations_equal("/media/Film", "/media/film")
    assert is_location_ancestor_of("/data/x", "/data/x/y")
    # conflict detection on a pure lexical (non-existent) location works without
    # any filesystem/media access
    add_project_source(P1, "F:\\VIRTUAL", "V1", local_appdata=tmp_path, now=NOW)
    category, _ = detect_project_location_conflicts(
        P1, "F:\\VIRTUAL\\Sub", local_appdata=tmp_path
    )
    assert category == "OVERLAPPING_LOCATION"


# 30. existing local_project manifest behavior unchanged
def test_local_project_manifest_unchanged(tmp_path: Path) -> None:
    pid = "PRJ-123e4567-e89b-42d3-a456-426614174000"
    create_project("Manifest", local_appdata=tmp_path, project_id=pid)
    loaded = load_project(pid, local_appdata=tmp_path)
    assert set(loaded) == {
        "format", "version", "project_id", "project_name", "created_at", "updated_at"
    }
    assert "sources" not in loaded
    assert "source_ids" not in loaded
    assert "locations" not in loaded


# ---------------------------------------------------------------------------
# MS2A — legacy migration binding (cases 31-42)
# ---------------------------------------------------------------------------

# 31. explicit legacy alias accepted
def test_legacy_alias_accepted(tmp_path: Path) -> None:
    record = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    assert SRC_ID_RE.fullmatch(record["source_id"])
    assert record["legacy_source_root_id_alias"] == "ROOT-abc123"


# 32. legacy alias persists/reloads via binding API
def test_legacy_binding_persists_reloads(tmp_path: Path) -> None:
    record = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert loaded["sources"][0]["legacy_source_root_id_alias"] == "ROOT-abc123"
    assert loaded["sources"][0]["source_id"] == record["source_id"]


# 33. legacy alias maps to stable SRC source
def test_legacy_alias_maps_to_stable_src(tmp_path: Path) -> None:
    record = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    resolved = resolve_legacy_source_id(P1, "ROOT-abc123", local_appdata=tmp_path)
    assert resolved is not None
    assert resolved["source_id"] == record["source_id"]
    assert resolved["legacy_source_root_id_alias"] == "ROOT-abc123"


# 34. rerun/request same alias reuses same source_id (idempotent)
def test_legacy_alias_idempotent_reuse(tmp_path: Path) -> None:
    first = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    second = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    assert second["source_id"] == first["source_id"]
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 1


# 35. same alias cannot map to two sources in one project
def test_legacy_alias_unique_per_project(tmp_path: Path) -> None:
    add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    add_project_source(P1, "F:\\OTHER_FILM", "Cam2", local_appdata=tmp_path, now=NOW)
    registry = load_project_sources(P1, local_appdata=tmp_path)
    registry["sources"][1]["legacy_source_root_id_alias"] = "ROOT-abc123"
    _write_raw_registry(P1, registry, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        load_project_sources(P1, local_appdata=tmp_path)
    assert ei.value.code == CID_SOURCE_LEGACY_ALIAS_CONFLICT


# 36. conflicting alias registry fail-closed (pure resolution)
def test_conflicting_alias_registry_fail_closed(tmp_path: Path) -> None:
    add_legacy_project_source(
        P1, "ROOT-a", "F:\\SIRUELA", "A", local_appdata=tmp_path, now=NOW
    )
    registry = load_project_sources(P1, local_appdata=tmp_path)
    second = {
        "source_id": "SRC-12345678-1234-4123-8123-123456789abc",
        "display_label": "B",
        "current_location": "F:\\OTHER",
        "state": STATE_OFFLINE,
        "added_at": "2024-01-02T03:04:05Z",
        "updated_at": "2024-01-02T03:04:05Z",
        "legacy_source_root_id_alias": "ROOT-a",
    }
    registry["sources"].append(second)
    with pytest.raises(SourceRegistryError) as ei:
        resolve_legacy_source_id_from_registry(registry, "ROOT-a")
    assert ei.value.code == CID_SOURCE_LEGACY_ALIAS_CONFLICT


# 37. creating legacy migration binding requires no filesystem access on media
def test_legacy_binding_no_filesystem_access(tmp_path: Path) -> None:
    nonexistent = "F:\\DOES\\NOT\\EXIST_ANYWHERE_LEGACY"
    record = add_legacy_project_source(
        P1, "ROOT-virtual", nonexistent, "V", local_appdata=tmp_path, now=NOW
    )
    assert record["legacy_source_root_id_alias"] == "ROOT-virtual"
    assert record["current_location"] == nonexistent


# 38. migration-created binding defaults OFFLINE
def test_legacy_binding_defaults_offline(tmp_path: Path) -> None:
    record = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
    )
    assert record["state"] == STATE_OFFLINE
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert loaded["sources"][0]["state"] == STATE_OFFLINE


# 39. explicit valid ONLINE state can be persisted when caller provides it
def test_legacy_binding_explicit_online_state(tmp_path: Path) -> None:
    record = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\SIRUELA", "Legacy Cam",
        local_appdata=tmp_path, state=STATE_ONLINE, now=NOW,
    )
    assert record["state"] == STATE_ONLINE


# 40. invalid legacy alias rejected
def test_invalid_legacy_alias_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceRegistryError) as ei:
        validate_legacy_alias("   ")
    assert ei.value.code == CID_SOURCE_LEGACY_ALIAS_INVALID


# 41. empty alias rejected
def test_empty_legacy_alias_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceRegistryError) as ei:
        add_legacy_project_source(
            P1, "", "F:\\SIRUELA", "Legacy Cam", local_appdata=tmp_path, now=NOW
        )
    assert ei.value.code == CID_SOURCE_LEGACY_ALIAS_INVALID


# 42. existing normal MS1 source with alias=None remains valid
def test_existing_source_alias_none_remains_valid(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    assert record["legacy_source_root_id_alias"] is None
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert is_valid_registry(loaded, P1)
    assert loaded["sources"][0]["legacy_source_root_id_alias"] is None


# ---------------------------------------------------------------------------
# MS2D — offline/reconnect orchestration primitives (existing MS1 API hardened)
# ---------------------------------------------------------------------------

def _registry_bytes(project_id: str, tmp_path: Path) -> bytes:
    return project_sources_path(project_id, tmp_path).read_bytes()


def test_offline_preserves_source_id_location_and_metadata(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    src_id = record["source_id"]
    offline = update_source_state(P1, src_id, STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    assert offline["source_id"] == src_id
    assert offline["current_location"] == "F:\\SIRUELA"
    assert offline["display_label"] == "Cam1"
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert [s["source_id"] for s in loaded["sources"]] == [src_id]
    assert loaded["sources"][0]["state"] == STATE_OFFLINE
    assert loaded["sources"][0]["current_location"] == "F:\\SIRUELA"
    assert loaded["sources"][0]["display_label"] == "Cam1"


def test_offline_does_not_delete_source_record(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 1


def test_only_online_offline_are_allowed_persistent_states(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    for bad in ("RECONNECTED", "RELOCATED", "MISSING", "DETACHED", "UNLINKED"):
        with pytest.raises(SourceRegistryError) as ei:
            update_source_state(P1, record["source_id"], bad, local_appdata=tmp_path, now=NOW)
        assert ei.value.code == CID_SOURCE_STATE_INVALID
    assert find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)["state"] == STATE_ONLINE


def test_reconnect_offline_source_to_new_location_preserves_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    src_id = record["source_id"]
    update_source_state(P1, src_id, STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, src_id, "E:\\ARCHIVE", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["source_id"] == src_id
    assert updated["current_location"] == "E:\\ARCHIVE"
    assert updated["state"] == STATE_ONLINE
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert len(loaded["sources"]) == 1
    assert loaded["sources"][0]["current_location"] == "E:\\ARCHIVE"
    assert loaded["sources"][0]["state"] == STATE_ONLINE


def test_reconnect_does_not_create_third_persistent_state(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, record["source_id"], "E:\\ARCHIVE", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["state"] == STATE_ONLINE
    assert updated["state"] in (STATE_ONLINE, STATE_OFFLINE)
    with pytest.raises(SourceRegistryError):
        update_source_state(P1, record["source_id"], "RECONNECTED", local_appdata=tmp_path, now=NOW)


def test_reconnect_unknown_source_fails_and_does_not_create(tmp_path: Path) -> None:
    unknown = "SRC-12345678-1234-4123-8123-123456789abc"
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, unknown, "F:\\NEW", local_appdata=tmp_path, confirmation=True, now=NOW
        )
    assert ei.value.code == CID_SOURCE_NOT_FOUND
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    assert loaded["sources"] == []
    assert find_source_by_id(P1, unknown, local_appdata=tmp_path) is None


def test_reconnect_requires_explicit_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    with pytest.raises(TypeError):
        reconnect_source(P1, "D:\\MOVED", local_appdata=tmp_path)  # type: ignore[call-arg]
    assert find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)["current_location"] == "F:\\SIRUELA"


def test_same_location_reconnect_preserves_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, record["source_id"], "F:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["source_id"] == record["source_id"]
    assert updated["current_location"] == "F:\\SIRUELA"
    assert updated["state"] == STATE_ONLINE
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 1


def test_online_source_relocate_preserves_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, record["source_id"], "G:\\NEWHOME", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["source_id"] == record["source_id"]
    assert updated["current_location"] == "G:\\NEWHOME"
    assert updated["state"] == STATE_ONLINE


def test_reconnect_exact_overlap_to_other_source_rejected_and_registry_unchanged(tmp_path: Path) -> None:
    a = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "F:\\OTHER", "Cam2", local_appdata=tmp_path, now=NOW)
    before = _registry_bytes(P1, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, b["source_id"], "F:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
        )
    assert ei.value.code == CID_SOURCE_DUPLICATE_LOCATION
    assert _registry_bytes(P1, tmp_path) == before
    assert find_source_by_id(P1, a["source_id"], local_appdata=tmp_path)["current_location"] == "F:\\SIRUELA"
    assert find_source_by_id(P1, b["source_id"], local_appdata=tmp_path)["current_location"] == "F:\\OTHER"


def test_reconnect_parent_overlap_new_root_contains_another_source(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA\\Inner", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "F:\\OTHER", "Cam2", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, b["source_id"], "F:\\SIRUELA",
            local_appdata=tmp_path, confirmation=True, now=NOW,
        )
    assert ei.value.code == CID_SOURCE_OVERLAPPING_LOCATION


def test_reconnect_child_overlap_new_root_inside_another_source(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "F:\\OTHER", "Cam2", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, b["source_id"], "F:\\SIRUELA\\Inner",
            local_appdata=tmp_path, confirmation=True, now=NOW,
        )
    assert ei.value.code == CID_SOURCE_OVERLAPPING_LOCATION


def test_reconnect_self_location_excluded_from_overlap_check(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA\\Sub", "Cam1", local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, record["source_id"], "F:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["current_location"] == "F:\\SIRUELA"
    assert updated["state"] == STATE_ONLINE


def test_reconnect_to_cross_project_shared_location_requires_confirmation(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    rec = add_project_source(P2, "F:\\OTHER", "CamB", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P2, rec["source_id"], "F:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
        )
    assert ei.value.code == CID_SOURCE_CROSS_PROJECT_CONFLICT
    allowed = reconnect_source(
        P2, rec["source_id"], "F:\\SIRUELA",
        local_appdata=tmp_path, confirmation=True, allow_shared_location=True, now=NOW,
    )
    assert allowed["current_location"] == "F:\\SIRUELA"
    assert allowed["state"] == STATE_ONLINE


def test_reconnect_without_confirmation_rejected_and_registry_unchanged(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    before = _registry_bytes(P1, tmp_path)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, record["source_id"], "F:\\MOVED", local_appdata=tmp_path, confirmation=False, now=NOW
        )
    assert ei.value.code == CID_SOURCE_RECONNECT_CONFIRMATION_REQUIRED
    assert _registry_bytes(P1, tmp_path) == before
    assert find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)["current_location"] == "F:\\SIRUELA"


def test_alias_never_acts_as_reconnect_identity(tmp_path: Path) -> None:
    bound = add_legacy_project_source(
        P1, "ROOT-abc123", "F:\\A", "Legacy", local_appdata=tmp_path, now=NOW
    )
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, "ROOT-abc123", "F:\\B", local_appdata=tmp_path, confirmation=True, now=NOW
        )
    assert ei.value.code == CID_SOURCE_ID_INVALID
    assert find_source_by_id(P1, bound["source_id"], local_appdata=tmp_path)["current_location"] == "F:\\A"


# ---------------------------------------------------------------------------
# MS2D — online source root map (build_online_source_root_map)
# ---------------------------------------------------------------------------

def test_root_map_includes_online_source(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD_A", "Cam1", local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path) == {
        record["source_id"]: "D:\\CARD_A"
    }


def test_root_map_omits_offline_source(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD_A", "Cam1", local_appdata=tmp_path, now=NOW)
    update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path) == {}


def test_root_map_includes_multiple_online_sources(tmp_path: Path) -> None:
    a = add_project_source(P1, "D:\\CARD_A", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "E:\\RECORDER", "Cam2", local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {
        a["source_id"]: "D:\\CARD_A",
        b["source_id"]: "E:\\RECORDER",
    }
    assert list(root_map.keys()) == [a["source_id"], b["source_id"]]


def test_root_map_keys_are_exactly_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD_A", "Cam1", local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert set(root_map.keys()) == {record["source_id"]}
    assert "Cam1" not in root_map
    assert "D:\\CARD_A" not in root_map


def test_root_map_values_are_exactly_current_location(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD_A", "Cam1", local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map[record["source_id"]] == "D:\\CARD_A"


def test_root_map_alias_not_used_as_key(tmp_path: Path) -> None:
    bound = add_legacy_project_source(
        P1, "ROOT-abc123", "D:\\CARD_A", "Legacy", local_appdata=tmp_path, now=NOW,
        state=STATE_ONLINE,
    )
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {bound["source_id"]: "D:\\CARD_A"}
    assert "ROOT-abc123" not in root_map


def test_root_map_mixed_online_offline_returns_only_online(tmp_path: Path) -> None:
    a = add_project_source(P1, "D:\\A", "A", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "E:\\B", "B", local_appdata=tmp_path, now=NOW)
    update_source_state(P1, b["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {a["source_id"]: "D:\\A"}
    assert b["source_id"] not in root_map


def test_root_map_construction_does_not_mutate_registry(tmp_path: Path) -> None:
    a = add_project_source(P1, "D:\\A", "A", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "E:\\B", "B", local_appdata=tmp_path, now=NOW)
    update_source_state(P1, b["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    loaded = load_project_sources(P1, local_appdata=tmp_path)
    original = json.dumps(loaded, sort_keys=True)
    build_online_source_root_map(P1, local_appdata=tmp_path)
    build_online_source_root_map(P1, local_appdata=tmp_path)
    after = json.dumps(load_project_sources(P1, local_appdata=tmp_path), sort_keys=True)
    assert after == original
    assert find_source_by_id(P1, b["source_id"], local_appdata=tmp_path)["state"] == STATE_OFFLINE


def test_root_map_construction_does_not_change_updated_at(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\A", "A", local_appdata=tmp_path, now=NOW)
    before = find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)["updated_at"]
    build_online_source_root_map(P1, local_appdata=tmp_path)
    after = find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)["updated_at"]
    assert after == before


def test_root_map_construction_does_not_persist(tmp_path: Path) -> None:
    add_project_source(P1, "D:\\A", "A", local_appdata=tmp_path, now=NOW)
    path = project_sources_path(P1, tmp_path)
    before = path.read_bytes()
    for _ in range(3):
        build_online_source_root_map(P1, local_appdata=tmp_path)
    assert project_sources_path(P1, tmp_path).read_bytes() == before
    project_dir = project_path(P1, tmp_path)
    assert not any(p.name.startswith(".") for p in project_dir.iterdir())


def test_root_map_does_not_probe_filesystem(tmp_path: Path) -> None:
    add_project_source(P1, "F:\\DOES\\NOT\\EXIST\\ANYWHERE", "A", local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map and list(root_map.values())[0] == "F:\\DOES\\NOT\\EXIST\\ANYWHERE"


def test_root_map_windows_location_preserved_faithfully(tmp_path: Path) -> None:
    record = add_project_source(P1, "F:\\SIRUELA\\Audio", "A", local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path)[record["source_id"]] == "F:\\SIRUELA\\Audio"


def test_root_map_posix_location_preserved_faithfully(tmp_path: Path) -> None:
    record = add_project_source(P1, "/media/Archive/Film", "A", local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path)[record["source_id"]] == "/media/Archive/Film"


def test_root_map_output_deterministic(tmp_path: Path) -> None:
    add_project_source(P1, "D:\\A", "A", local_appdata=tmp_path, now=NOW)
    add_project_source(P1, "E:\\B", "B", local_appdata=tmp_path, now=NOW)
    first = build_online_source_root_map(P1, local_appdata=tmp_path)
    second = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert first == second
    assert list(first.keys()) == list(second.keys())


def test_root_map_reflects_reconnect_under_same_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    reconnect_source(
        P1, record["source_id"], "E:\\ARCHIVE", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {record["source_id"]: "E:\\ARCHIVE"}


def test_mark_offline_after_reconnect_removes_from_map_not_registry(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    reconnect_source(
        P1, record["source_id"], "E:\\ARCHIVE", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {}
    kept = find_source_by_id(P1, record["source_id"], local_appdata=tmp_path)
    assert kept is not None
    assert kept["current_location"] == "E:\\ARCHIVE"
    assert kept["state"] == STATE_OFFLINE


def test_mark_online_restores_inclusion_in_map(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    update_source_state(P1, record["source_id"], STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path) == {}
    update_source_state(P1, record["source_id"], STATE_ONLINE, local_appdata=tmp_path, now=NOW)
    assert build_online_source_root_map(P1, local_appdata=tmp_path) == {
        record["source_id"]: "D:\\CARD"
    }


def test_root_map_empty_registry_returns_empty(tmp_path: Path) -> None:
    assert build_online_source_root_map(P1, local_appdata=tmp_path) == {}


def test_pure_projection_does_not_mutate_input(tmp_path: Path) -> None:
    sources = [
        _make_src("SRC-a1", "D:\\A", state=STATE_ONLINE),
        _make_src("SRC-b1", "E:\\B", state=STATE_OFFLINE),
    ]
    snapshot = json.dumps(sources, sort_keys=True)
    result = _online_source_root_map_from_sources(sources)
    assert result == {"SRC-a1": "D:\\A"}
    assert json.dumps(sources, sort_keys=True) == snapshot


def test_root_map_value_type_is_str(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert isinstance(root_map[record["source_id"]], str)


# ---------------------------------------------------------------------------
# MS2D — identity / no rekey
# ---------------------------------------------------------------------------

def test_reconnect_never_changes_source_id(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    for location in ("E:\\A", "F:\\B", "G:\\C"):
        updated = reconnect_source(
            P1, record["source_id"], location, local_appdata=tmp_path, confirmation=True, now=NOW
        )
        assert updated["source_id"] == record["source_id"]
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 1


def test_alias_change_does_not_become_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    registry = load_project_sources(P1, local_appdata=tmp_path)
    registry["sources"][0]["display_label"] = "Renamed"
    registry["sources"][0]["legacy_source_root_id_alias"] = "ROOT-zzz"
    save_project_sources(registry, local_appdata=tmp_path)
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map == {record["source_id"]: "D:\\CARD"}


def test_same_physical_location_concept_does_not_replace_source_id(tmp_path: Path) -> None:
    a = add_project_source(P1, "F:\\SIRUELA", "Cam1", local_appdata=tmp_path, now=NOW)
    b = add_project_source(P1, "E:\\OTHER", "Cam2", local_appdata=tmp_path, now=NOW)
    with pytest.raises(SourceRegistryError) as ei:
        reconnect_source(
            P1, b["source_id"], "F:\\SIRUELA", local_appdata=tmp_path, confirmation=True, now=NOW
        )
    assert ei.value.code == CID_SOURCE_DUPLICATE_LOCATION
    assert a["source_id"] != b["source_id"]
    root_map = build_online_source_root_map(P1, local_appdata=tmp_path)
    assert root_map[a["source_id"]] == "F:\\SIRUELA"
    assert root_map[b["source_id"]] == "E:\\OTHER"
    assert a["source_id"] in root_map and b["source_id"] in root_map


def test_content_irrelevant_to_reconnect_identity(tmp_path: Path) -> None:
    record = add_project_source(P1, "D:\\CARD", "Cam1", local_appdata=tmp_path, now=NOW)
    src_id = record["source_id"]
    update_source_state(P1, src_id, STATE_OFFLINE, local_appdata=tmp_path, now=NOW)
    updated = reconnect_source(
        P1, src_id, "E:\\ARCHIVE", local_appdata=tmp_path, confirmation=True, now=NOW
    )
    assert updated["source_id"] == src_id
    assert len(list_project_sources(P1, local_appdata=tmp_path)) == 1
    assert find_source_by_id(P1, src_id, local_appdata=tmp_path)["current_location"] == "E:\\ARCHIVE"
