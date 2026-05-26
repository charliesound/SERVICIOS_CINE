from __future__ import annotations

import pytest

from schemas.character_bible_schema import (
    ApprovedAssetType,
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleEntryCreate,
    CharacterBibleEntryUpdate,
    CharacterBibleResolveRequest,
    CharacterLookVariant,
    LookVariantCreate,
    ReferenceAssetCreate,
)
from services.character_bible_service import CharacterBibleService


@pytest.fixture
def service() -> CharacterBibleService:
    return CharacterBibleService()


class TestCreateEntry:
    def test_create_entry(self, service):
        payload = CharacterBibleEntryCreate(
            character_id="char_marta",
            character_name="Marta",
            wardrobe_notes="Jeans oscuros",
        )
        entry = service.create_or_update_entry("proj_1", payload)
        assert entry.character_id == "char_marta"
        assert entry.project_id == "proj_1"
        assert entry.version == 1
        assert entry.created_at is not None
        assert entry.updated_at is not None

    def test_update_existing_entry(self, service):
        payload = CharacterBibleEntryCreate(
            character_id="char_marta",
            character_name="Marta",
            wardrobe_notes="Jeans oscuros",
        )
        service.create_or_update_entry("proj_1", payload)
        payload2 = CharacterBibleEntryCreate(
            character_id="char_marta",
            character_name="Marta Updated",
            wardrobe_notes="Jeans claros",
        )
        entry = service.create_or_update_entry("proj_1", payload2)
        assert entry.version == 2
        assert entry.wardrobe_notes == "Jeans claros"
        assert entry.character_name == "Marta Updated"


class TestUpdateEntry:
    def test_partial_update(self, service):
        payload = CharacterBibleEntryCreate(
            character_id="char_marta",
            character_name="Marta",
            wardrobe_notes="Jeans oscuros",
            key_props=["flashlight"],
        )
        service.create_or_update_entry("proj_1", payload)
        update = CharacterBibleEntryUpdate(wardrobe_notes="Jeans claros")
        entry = service.update_entry("proj_1", "char_marta", update)
        assert entry is not None
        assert entry.wardrobe_notes == "Jeans claros"
        assert entry.key_props == ["flashlight"]
        assert entry.version == 2

    def test_update_nonexistent_returns_none(self, service):
        update = CharacterBibleEntryUpdate(character_name="Ghost")
        assert service.update_entry("proj_1", "char_ghost", update) is None


class TestListEntries:
    def test_list_empty(self, service):
        entries = service.list_entries("proj_empty")
        assert entries == []

    def test_list_entries(self, service):
        p1 = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        p2 = CharacterBibleEntryCreate(character_id="c2", character_name="C2")
        service.create_or_update_entry("proj_1", p1)
        service.create_or_update_entry("proj_1", p2)
        entries = service.list_entries("proj_1")
        assert len(entries) == 2

    def test_list_project_isolation(self, service):
        p = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_a", p)
        assert service.list_entries("proj_b") == []


class TestGetEntry:
    def test_get_existing(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        entry = service.get_entry("proj_1", "c1")
        assert entry is not None
        assert entry.character_name == "C1"

    def test_get_nonexistent(self, service):
        assert service.get_entry("proj_1", "ghost") is None


class TestAddLookVariant:
    def test_add_variant(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        variant = LookVariantCreate(
            look_id="look_night",
            look_name="Night Look",
            wardrobe_notes="Dark clothes",
            key_props=["flashlight"],
        )
        result = service.add_look_variant("proj_1", "c1", variant)
        assert result is not None
        assert result.look_id == "look_night"
        entry = service.get_entry("proj_1", "c1")
        assert entry is not None
        assert len(entry.look_variants) == 1

    def test_add_variant_nonexistent_character(self, service):
        variant = LookVariantCreate(look_id="l1", look_name="L1")
        assert service.add_look_variant("proj_1", "ghost", variant) is None

    def test_duplicate_look_id_returns_existing(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        v1 = LookVariantCreate(look_id="look_night", look_name="Night")
        v2 = LookVariantCreate(look_id="look_night", look_name="Night Dup")
        result1 = service.add_look_variant("proj_1", "c1", v1)
        result2 = service.add_look_variant("proj_1", "c1", v2)
        assert result1 is not None
        assert result2 is not None
        assert result2.look_name == "Night"


class TestAddReference:
    def test_add_reference(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        ref = ReferenceAssetCreate(
            asset_id="asset_001",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/api/assets/face.png",
            description="Face reference",
            is_primary=True,
        )
        result = service.add_reference("proj_1", "c1", ref)
        assert result is not None
        assert result.asset_id == "asset_001"
        assert result.is_primary is True
        entry = service.get_entry("proj_1", "c1")
        assert entry is not None
        assert len(entry.approved_references) == 1

    def test_add_reference_sanitizes_absolute_path(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        ref = ReferenceAssetCreate(
            asset_id="asset_bad",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/opt/storage/face.png",
        )
        result = service.add_reference("proj_1", "c1", ref)
        assert result is not None
        assert result.asset_api_url is None

    def test_add_reference_nonexistent_character(self, service):
        ref = ReferenceAssetCreate(
            asset_id="asset_001",
            asset_type=ApprovedAssetType.FACE_SHEET,
        )
        assert service.add_reference("proj_1", "ghost", ref) is None


class TestResolve:
    def test_resolve_existing(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        req = CharacterBibleResolveRequest(project_id="proj_1", character_id="c1")
        result = service.resolve("proj_1", "c1", req)
        assert result is not None
        assert result.character_id == "c1"

    def test_resolve_nonexistent(self, service):
        req = CharacterBibleResolveRequest(project_id="proj_1", character_id="ghost")
        assert service.resolve("proj_1", "ghost", req) is None


class TestTrace:
    def test_get_trace(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        trace = service.get_trace("proj_1", "c1")
        assert trace is not None
        assert trace["character_id"] == "c1"
        assert "trace_metadata" in trace

    def test_trace_nonexistent(self, service):
        assert service.get_trace("proj_1", "ghost") is None


class TestSanitizeAssetUrl:
    def test_sanitize_blocks_opt_path(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("/opt/storage/file.png") is None

    def test_sanitize_blocks_mnt_path(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("/mnt/data/file.png") is None

    def test_sanitize_blocks_windows_path(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("C:\\Users\\file.png") is None

    def test_sanitize_blocks_storage_path(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("storage_path/media/file.png") is None

    def test_sanitize_blocks_canonical_path(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("canonical_path/file.png") is None

    def test_sanitize_allows_api_url(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url("/api/assets/face.png") == "/api/assets/face.png"

    def test_sanitize_returns_none_for_none(self, service):
        from services.character_bible_service import _sanitize_asset_url
        assert _sanitize_asset_url(None) is None


class TestProjectIsolation:
    def test_entries_isolated_by_project(self, service):
        p1 = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        p2 = CharacterBibleEntryCreate(character_id="c1", character_name="C1 Diff")
        service.create_or_update_entry("proj_a", p1)
        service.create_or_update_entry("proj_b", p2)
        assert service.get_entry("proj_a", "c1").character_name == "C1"
        assert service.get_entry("proj_b", "c1").character_name == "C1 Diff"


class TestNoAbsolutePathsInEntry:
    def test_entry_no_absolute_paths(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        entry = service.create_or_update_entry("proj_1", payload)
        dumped = entry.model_dump_json()
        assert "/opt/" not in dumped
        assert "/mnt/" not in dumped
        assert "C:" not in dumped

    def test_trace_no_absolute_paths(self, service):
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        service.create_or_update_entry("proj_1", payload)
        trace = service.get_trace("proj_1", "c1")
        assert trace is not None
        dumped = str(trace)
        assert "/opt/" not in dumped
        assert "/mnt/" not in dumped
        assert "C:" not in dumped
