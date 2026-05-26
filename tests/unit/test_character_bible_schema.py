from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from schemas.character_bible_schema import (
    ApprovedAssetType,
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleResolveRequest,
    CharacterBibleResolveResult,
    CharacterLookVariant,
    ShotCharacterReference,
)


class TestApprovedAssetType:
    def test_has_face_sheet(self) -> None:
        assert ApprovedAssetType.FACE_SHEET.value == "face_sheet"

    def test_has_wardrobe_sheet(self) -> None:
        assert ApprovedAssetType.WARDROBE_SHEET.value == "wardrobe_sheet"

    def test_has_prop_reference(self) -> None:
        assert ApprovedAssetType.PROP_REFERENCE.value == "prop_reference"

    def test_has_expression_sheet(self) -> None:
        assert ApprovedAssetType.EXPRESSION_SHEET.value == "expression_sheet"

    def test_has_full_body(self) -> None:
        assert ApprovedAssetType.FULL_BODY.value == "full_body"

    def test_all_types_defined(self) -> None:
        expected = {
            "face_sheet", "wardrobe_sheet", "full_body", "hair_makeup",
            "prop_reference", "expression_sheet", "pose_sheet",
            "action_still", "mood_board", "concept_art",
        }
        actual = {e.value for e in ApprovedAssetType}
        assert actual == expected


class TestApprovedReferenceAsset:
    def test_minimal(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_marta_face_v2",
            asset_type=ApprovedAssetType.FACE_SHEET,
        )
        assert asset.asset_id == "asset_marta_face_v2"
        assert asset.is_primary is False
        assert asset.sort_order == 0
        assert asset.asset_api_url is None

    def test_full(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_marta_face_v2",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/api/assets/asset_marta_face_v2",
            asset_file_name="marta_face_v2.png",
            reference_id="ref_marta_001",
            description="Rostro de Marta versión aprobada V2",
            is_primary=True,
            sort_order=1,
            approved_by_user_id="user_director",
            approved_at="2026-05-26T10:00:00Z",
            notes="Aprobado por dirección",
        )
        assert asset.is_primary is True
        assert asset.approved_by_user_id == "user_director"
        assert asset.reference_id == "ref_marta_001"
        assert "/api/assets/" in asset.asset_api_url

    def test_does_not_expose_absolute_path(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_marta_face_v2",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/api/assets/asset_marta_face_v2",
            asset_file_name="marta_face_v2.png",
        )
        assert "\\" not in (asset.asset_api_url or "")
        assert "/" not in (asset.asset_file_name or "")
        assert not (asset.asset_api_url or "").startswith(("/opt/", "/home/", "C:"))

    def test_serialize_roundtrip(self) -> None:
        original = ApprovedReferenceAsset(
            asset_id="asset_linterna",
            asset_type=ApprovedAssetType.PROP_REFERENCE,
            is_primary=True,
        )
        data = original.model_dump()
        restored = ApprovedReferenceAsset.model_validate(data)
        assert restored.asset_id == "asset_linterna"
        assert restored.is_primary is True

    def test_secondary_reference(self) -> None:
        primary = ApprovedReferenceAsset(
            asset_id="asset_primary", asset_type=ApprovedAssetType.FACE_SHEET, is_primary=True
        )
        secondary = ApprovedReferenceAsset(
            asset_id="asset_secondary", asset_type=ApprovedAssetType.WARDROBE_SHEET, is_primary=False
        )
        assert primary.is_primary is True
        assert secondary.is_primary is False

    def test_api_url_is_api_endpoint_not_filesystem(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_test",
            asset_type=ApprovedAssetType.FULL_BODY,
            asset_api_url="/api/character-bible/asset/asset_test",
        )
        assert asset.asset_api_url.startswith("/api/")


class TestCharacterLookVariant:
    def test_minimal(self) -> None:
        look = CharacterLookVariant(look_id="look_night", look_name="Noche entrada")
        assert look.narrative_phase is None
        assert len(look.approved_references) == 0

    def test_with_references(self) -> None:
        refs = [
            ApprovedReferenceAsset(
                asset_id="asset_face", asset_type=ApprovedAssetType.FACE_SHEET
            ),
            ApprovedReferenceAsset(
                asset_id="asset_wardrobe", asset_type=ApprovedAssetType.WARDROBE_SHEET
            ),
        ]
        look = CharacterLookVariant(
            look_id="look_night",
            look_name="Noche entrada",
            narrative_phase="primer_acto",
            approved_references=refs,
            wardrobe_notes="Chaqueta oscura, vaqueros, botas",
            hair_makeup_notes="Castaño largo recogido, maquillaje natural",
            key_props=["linterna", "llaves"],
            continuity_rules=["Misma chaqueta en toda la escena"],
            negative_constraints=["No cambiar peinado"],
            scene_ids=["seq_entrada"],
        )
        assert len(look.approved_references) == 2
        assert look.narrative_phase == "primer_acto"
        assert "linterna" in look.key_props

    def test_multiple_variants_same_character(self) -> None:
        night = CharacterLookVariant(
            look_id="look_night", look_name="Noche",
            key_props=["linterna"],
        )
        day = CharacterLookVariant(
            look_id="look_day", look_name="Día",
            key_props=["gafas de sol"],
        )
        assert night.look_id != day.look_id
        assert night.key_props != day.key_props

    def test_negative_constraints(self) -> None:
        look = CharacterLookVariant(
            look_id="look_test",
            look_name="Test",
            negative_constraints=["No cambiar peinado", "No cambiar chaqueta"],
        )
        assert len(look.negative_constraints) == 2
        assert "No cambiar peinado" in look.negative_constraints

    def test_continuity_rules(self) -> None:
        look = CharacterLookVariant(
            look_id="look_test",
            look_name="Test",
            continuity_rules=["Misma chaqueta", "Mismo peinado"],
        )
        assert len(look.continuity_rules) == 2

    def test_scene_assignment(self) -> None:
        look = CharacterLookVariant(
            look_id="look_act1",
            look_name="Acto 1",
            scene_ids=["seq_entrada", "seq_descubrimiento"],
        )
        assert "seq_entrada" in look.scene_ids

    def test_serialize_roundtrip(self) -> None:
        original = CharacterLookVariant(
            look_id="look_night",
            look_name="Noche",
            wardrobe_notes="Chaqueta oscura",
        )
        data = original.model_dump()
        restored = CharacterLookVariant.model_validate(data)
        assert restored.look_id == "look_night"
        assert restored.wardrobe_notes == "Chaqueta oscura"


class TestCharacterBibleEntry:
    def test_minimal(self) -> None:
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
        )
        assert entry.character_name == "Marta"
        assert entry.version == 1
        assert len(entry.look_variants) == 0

    def test_with_approved_reference(self) -> None:
        ref = ApprovedReferenceAsset(
            asset_id="asset_marta_face_v2",
            asset_type=ApprovedAssetType.FACE_SHEET,
            is_primary=True,
        )
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
            approved_reference_asset_id="asset_marta_face_v2",
            approved_references=[ref],
            wardrobe_notes="Chaqueta oscura, vaqueros, botas",
            hair_makeup_notes="Castaño largo recogido",
            key_props=["linterna"],
            continuity_rules=["Misma chaqueta"],
            negative_constraints=["No cambiar peinado"],
        )
        assert entry.approved_reference_asset_id == "asset_marta_face_v2"
        assert len(entry.approved_references) == 1
        assert len(entry.key_props) == 1
        assert "Misma chaqueta" in entry.continuity_rules

    def test_multiple_look_variants(self) -> None:
        night = CharacterLookVariant(
            look_id="look_night", look_name="Noche",
            key_props=["linterna"],
            scene_ids=["seq_entrada"],
        )
        day = CharacterLookVariant(
            look_id="look_day", look_name="Día",
            key_props=["gafas", "mochila"],
            scene_ids=["seq_salida"],
        )
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
            look_variants=[night, day],
            default_look_id="look_night",
        )
        assert len(entry.look_variants) == 2
        assert entry.default_look_id == "look_night"

    def test_secondary_references(self) -> None:
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
            approved_reference_asset_id="asset_primary",
            secondary_reference_asset_ids=["asset_wardrobe", "asset_hair"],
        )
        assert len(entry.secondary_reference_asset_ids) == 2

    def test_serialize_roundtrip(self) -> None:
        original = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
            version=2,
        )
        data = original.model_dump()
        restored = CharacterBibleEntry.model_validate(data)
        assert restored.character_name == "Marta"
        assert restored.version == 2

    def test_with_look_variant_serialization(self) -> None:
        look = CharacterLookVariant(
            look_id="look_night",
            look_name="Noche",
            negative_constraints=["No cambiar peinado"],
        )
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
            look_variants=[look],
        )
        data = entry.model_dump()
        restored = CharacterBibleEntry.model_validate(data)
        assert len(restored.look_variants) == 1
        assert restored.look_variants[0].negative_constraints == ["No cambiar peinado"]

    def test_project_id_default_empty(self) -> None:
        entry = CharacterBibleEntry(
            character_id="char_marta",
            character_name="Marta",
        )
        assert entry.project_id == ""


class TestShotCharacterReference:
    def test_minimal(self) -> None:
        ref = ShotCharacterReference(
            shot_number=1,
            character_id="char_marta",
        )
        assert ref.wardrobe_confirmed is False
        assert ref.hair_makeup_confirmed is False
        assert len(ref.applied_reference_asset_ids) == 0

    def test_with_applied_assets(self) -> None:
        ref = ShotCharacterReference(
            project_id="proj_corto",
            shot_number=3,
            sequence_id="seq_entrada",
            character_id="char_marta",
            applied_look_id="look_night",
            applied_reference_asset_ids=[
                "asset_marta_face_v2",
                "asset_marta_wardrobe_night",
                "asset_linterna_ref",
            ],
            wardrobe_confirmed=True,
            hair_makeup_confirmed=True,
            props_confirmed=True,
            continuity_verified=True,
            tracking_note="Primer plano — verificar linterna en mano",
        )
        assert ref.shot_number == 3
        assert len(ref.applied_reference_asset_ids) == 3
        assert ref.wardrobe_confirmed is True
        assert ref.continuity_verified is True

    def test_tracks_look_variant(self) -> None:
        ref = ShotCharacterReference(
            shot_number=5,
            character_id="char_marta",
            applied_look_id="look_night_entrance",
        )
        assert ref.applied_look_id == "look_night_entrance"

    def test_tracking_note(self) -> None:
        ref = ShotCharacterReference(
            shot_number=1,
            character_id="char_marta",
            tracking_note="Verificar linterna en mano derecha",
        )
        assert "linterna" in ref.tracking_note

    def test_serialize_roundtrip(self) -> None:
        original = ShotCharacterReference(
            shot_number=2,
            character_id="char_marta",
            applied_look_id="look_night",
            applied_reference_asset_ids=["asset_face", "asset_wardrobe"],
        )
        data = original.model_dump()
        restored = ShotCharacterReference.model_validate(data)
        assert restored.shot_number == 2
        assert len(restored.applied_reference_asset_ids) == 2

    def test_project_id_default_empty(self) -> None:
        ref = ShotCharacterReference(shot_number=1, character_id="char_marta")
        assert ref.project_id == ""


class TestCharacterBibleResolveRequest:
    def test_minimal(self) -> None:
        req = CharacterBibleResolveRequest(
            project_id="proj_corto",
            character_id="char_marta",
        )
        assert req.look_id is None
        assert req.narrative_phase is None

    def test_with_all_fields(self) -> None:
        req = CharacterBibleResolveRequest(
            project_id="proj_corto",
            character_id="char_marta",
            look_id="look_night",
            narrative_phase="primer_acto",
            scene_id="seq_entrada",
        )
        assert req.look_id == "look_night"
        assert req.scene_id == "seq_entrada"


class TestCharacterBibleResolveResult:
    def test_minimal(self) -> None:
        result = CharacterBibleResolveResult(
            character_id="char_marta",
            character_name="Marta",
        )
        assert result.resolved_look is None
        assert len(result.applied_reference_ids) == 0

    def test_with_resolved_look(self) -> None:
        look = CharacterLookVariant(
            look_id="look_night",
            look_name="Noche",
            wardrobe_notes="Chaqueta oscura",
        )
        primary = ApprovedReferenceAsset(
            asset_id="asset_face",
            asset_type=ApprovedAssetType.FACE_SHEET,
            is_primary=True,
        )
        secondary = ApprovedReferenceAsset(
            asset_id="asset_wardrobe",
            asset_type=ApprovedAssetType.WARDROBE_SHEET,
        )
        result = CharacterBibleResolveResult(
            project_id="proj_corto",
            character_id="char_marta",
            character_name="Marta",
            resolved_look=look,
            primary_reference=primary,
            secondary_references=[secondary],
            prompt_lock_block="Marta: rostro asset_face, vestuario asset_wardrobe",
            prompt_negative_block="No cambiar peinado, no cambiar chaqueta",
            continuity_block="Misma chaqueta en toda la escena",
            applied_reference_ids=["asset_face", "asset_wardrobe"],
        )
        assert result.resolved_look is not None
        assert result.resolved_look.wardrobe_notes == "Chaqueta oscura"
        assert len(result.applied_reference_ids) == 2

    def test_unresolved_props(self) -> None:
        result = CharacterBibleResolveResult(
            character_id="char_marta",
            character_name="Marta",
            unresolved_props=["linterna", "llaves"],
        )
        assert len(result.unresolved_props) == 2
        assert "linterna" in result.unresolved_props

    def test_serialize_roundtrip(self) -> None:
        original = CharacterBibleResolveResult(
            character_id="char_marta",
            character_name="Marta",
            prompt_lock_block="Character lock: Marta",
        )
        data = original.model_dump()
        restored = CharacterBibleResolveResult.model_validate(data)
        assert restored.character_name == "Marta"
        assert restored.prompt_lock_block == "Character lock: Marta"

    def test_project_id_default_empty(self) -> None:
        result = CharacterBibleResolveResult(
            character_id="char_marta",
            character_name="Marta",
        )
        assert result.project_id == ""


class TestNoAbsolutePaths:
    def test_asset_api_url_is_relative(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_test",
            asset_type=ApprovedAssetType.FACE_SHEET,
            asset_api_url="/api/assets/asset_test",
        )
        assert asset.asset_api_url.startswith("/api/")
        assert not asset.asset_api_url.startswith(("/opt/", "/home/", "/var/", "C:", "D:"))

    def test_approved_by_is_user_id_not_name(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_test",
            asset_type=ApprovedAssetType.FACE_SHEET,
            approved_by_user_id="user_director_42",
        )
        assert "user_" in asset.approved_by_user_id

    def test_reference_id_is_external_not_path(self) -> None:
        asset = ApprovedReferenceAsset(
            asset_id="asset_test",
            asset_type=ApprovedAssetType.FACE_SHEET,
            reference_id="ref_marta_001",
        )
        assert asset.reference_id.startswith("ref_")
