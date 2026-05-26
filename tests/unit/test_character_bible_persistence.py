from __future__ import annotations

import json
from pathlib import Path

import pytest

from schemas.character_bible_schema import (
    ApprovedAssetType,
    CharacterBibleEntry,
    CharacterBibleEntryCreate,
    LookVariantCreate,
    ReferenceAssetCreate,
)
from services.character_bible_service import CharacterBibleService


class TestPersistence:
    """Verify that CharacterBible data persists to disk and survives reload."""

    @pytest.mark.asyncio
    async def test_save_and_reload_entry(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(
            character_id="char_marta",
            character_name="Marta",
            wardrobe_notes="Jeans oscuros",
        )
        await svc.create_or_update_entry("proj_1", payload)

        svc2 = CharacterBibleService(data_dir=tmp_path)
        loaded = svc2.get_entry("proj_1", "char_marta")
        assert loaded is not None
        assert loaded.character_name == "Marta"
        assert loaded.wardrobe_notes == "Jeans oscuros"
        assert loaded.version == 1

    @pytest.mark.asyncio
    async def test_persist_look_variant(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        await svc.create_or_update_entry("proj_1", payload)
        variant = LookVariantCreate(
            look_id="look_night",
            look_name="Night Look",
            wardrobe_notes="Dark clothes",
        )
        await svc.add_look_variant("proj_1", "c1", variant)

        svc2 = CharacterBibleService(data_dir=tmp_path)
        loaded = svc2.get_entry("proj_1", "c1")
        assert loaded is not None
        assert len(loaded.look_variants) == 1
        assert loaded.look_variants[0].look_id == "look_night"
        assert loaded.look_variants[0].wardrobe_notes == "Dark clothes"

    @pytest.mark.asyncio
    async def test_persist_reference(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        await svc.create_or_update_entry("proj_1", payload)
        ref = ReferenceAssetCreate(
            asset_id="asset_001",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/api/assets/face.png",
            is_primary=True,
        )
        await svc.add_reference("proj_1", "c1", ref)

        svc2 = CharacterBibleService(data_dir=tmp_path)
        loaded = svc2.get_entry("proj_1", "c1")
        assert loaded is not None
        assert len(loaded.approved_references) == 1
        assert loaded.approved_references[0].asset_id == "asset_001"
        assert loaded.approved_references[0].is_primary is True

    @pytest.mark.asyncio
    async def test_persist_update_increments_version(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        await svc.create_or_update_entry("proj_1", payload)
        payload2 = CharacterBibleEntryCreate(character_id="c1", character_name="C1 v2")
        await svc.create_or_update_entry("proj_1", payload2)

        svc2 = CharacterBibleService(data_dir=tmp_path)
        loaded = svc2.get_entry("proj_1", "c1")
        assert loaded is not None
        assert loaded.version == 2
        assert loaded.character_name == "C1 v2"

    @pytest.mark.asyncio
    async def test_project_isolation_across_reload(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        p1 = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        p2 = CharacterBibleEntryCreate(character_id="c1", character_name="C1 Diff")
        await svc.create_or_update_entry("proj_a", p1)
        await svc.create_or_update_entry("proj_b", p2)

        svc2 = CharacterBibleService(data_dir=tmp_path)
        assert svc2.get_entry("proj_a", "c1").character_name == "C1"
        assert svc2.get_entry("proj_b", "c1").character_name == "C1 Diff"

    def test_persistence_files_created(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        # Creating a service with empty dir should not create files yet
        assert list(tmp_path.glob("*.json")) == []

    @pytest.mark.asyncio
    async def test_json_file_is_written(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        await svc.create_or_update_entry("proj_x", payload)

        json_files = list(tmp_path.glob("*.json"))
        assert len(json_files) == 1
        assert json_files[0].name == "proj_x.json"

        raw = json_files[0].read_text("utf-8")
        data = json.loads(raw)
        assert "c1" in data
        assert data["c1"]["character_name"] == "C1"

    @pytest.mark.asyncio
    async def test_multiple_projects_multiple_files(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        await svc.create_or_update_entry("proj_a", CharacterBibleEntryCreate(
            character_id="c1", character_name="A",
        ))
        await svc.create_or_update_entry("proj_b", CharacterBibleEntryCreate(
            character_id="c2", character_name="B",
        ))

        files = {f.name for f in tmp_path.glob("*.json")}
        assert files == {"proj_a.json", "proj_b.json"}

    @pytest.mark.asyncio
    async def test_empty_data_dir_does_not_crash(self, tmp_path):
        empty_dir = tmp_path / "nonexistent"
        svc = CharacterBibleService(data_dir=empty_dir)
        assert svc.list_entries("proj_1") == []

    def test_corrupt_file_does_not_crash(self, tmp_path):
        bad_file = tmp_path / "proj_bad.json"
        bad_file.write_text("{{invalid json}}", "utf-8")
        svc = CharacterBibleService(data_dir=tmp_path)
        assert svc.list_entries("proj_bad") == []
        assert svc.list_entries("proj_good") == []

    @pytest.mark.asyncio
    async def test_atomic_write_leaves_valid_file(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        payload = CharacterBibleEntryCreate(character_id="c1", character_name="C1")
        await svc.create_or_update_entry("proj_1", payload)

        written_file = tmp_path / "proj_1.json"
        raw = written_file.read_text("utf-8")
        data = json.loads(raw)
        assert data["c1"]["character_name"] == "C1"
        # Ensure no .tmp file remains
        assert not (tmp_path / "proj_1.tmp").exists()

    @pytest.mark.asyncio
    async def test_reload_with_no_writes_starts_empty(self, tmp_path):
        svc = CharacterBibleService(data_dir=tmp_path)
        assert svc.list_entries("proj_1") == []

        svc2 = CharacterBibleService(data_dir=tmp_path)
        assert svc2.list_entries("proj_1") == []
