from __future__ import annotations

import pytest

from schemas.character_bible_schema import (
    ApprovedAssetType,
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleResolveRequest,
    CharacterBibleResolveResult,
    CharacterLookVariant,
)
from schemas.director_notes_schema import (
    DirectorNoteOverrideLevel,
    DirectorNoteSource,
    DirectorNotesBundle,
    DirectorNotesResolveResult,
    PromptBlocks,
)
from services.character_bible_resolver_service import CharacterBibleResolver


@pytest.fixture
def face_ref() -> ApprovedReferenceAsset:
    return ApprovedReferenceAsset(
        asset_id="asset_marta_face_v2",
        asset_type=ApprovedAssetType.FACE_SHEET,
        asset_api_url="/api/assets/marta_face_v2.png",
        reference_id="ref_marta_face_v2",
        description="Marta face sheet v2 - determined expression",
        is_primary=True,
        sort_order=0,
    )


@pytest.fixture
def body_ref() -> ApprovedReferenceAsset:
    return ApprovedReferenceAsset(
        asset_id="asset_marta_full_body",
        asset_type=ApprovedAssetType.FULL_BODY,
        asset_api_url="/api/assets/marta_full_body.png",
        reference_id="ref_marta_full_body",
        description="Marta full body reference",
        is_primary=False,
        sort_order=1,
    )


@pytest.fixture
def wardrobe_ref() -> ApprovedReferenceAsset:
    return ApprovedReferenceAsset(
        asset_id="asset_marta_wardrobe_night",
        asset_type=ApprovedAssetType.WARDROBE_SHEET,
        asset_api_url="/api/assets/marta_wardrobe_night.png",
        reference_id="ref_marta_wardrobe_night",
        description="Marta nighttime wardrobe",
        is_primary=False,
        sort_order=2,
    )


@pytest.fixture
def prop_ref() -> ApprovedReferenceAsset:
    return ApprovedReferenceAsset(
        asset_id="asset_flashlight_prop",
        asset_type=ApprovedAssetType.PROP_REFERENCE,
        asset_api_url="/api/assets/flashlight_prop.png",
        reference_id="ref_flashlight",
        description="Flashlight prop reference",
        is_primary=False,
        sort_order=0,
    )


@pytest.fixture
def night_look(face_ref, body_ref, wardrobe_ref) -> CharacterLookVariant:
    return CharacterLookVariant(
        look_id="look_night_entrance",
        look_name="Night Entrance",
        narrative_phase="night_entrance",
        approved_references=[face_ref, body_ref, wardrobe_ref],
        wardrobe_notes="Jeans oscuros, camiseta negra, chaqueta vaquera",
        hair_makeup_notes="Pelo recogido, maquillaje mínimo, ojeras marcadas",
        key_props=["flashlight"],
        continuity_rules=[
            "Misma ropa en toda la secuencia nocturna",
            "Flashlight siempre en mano derecha",
        ],
        negative_constraints=[
            "No cambiar a ropa clara",
            "No pelo suelto",
        ],
        scene_ids=["seq_night_01"],
    )


@pytest.fixture
def day_look(face_ref) -> CharacterLookVariant:
    return CharacterLookVariant(
        look_id="look_day_investigation",
        look_name="Day Investigation",
        narrative_phase="day_investigation",
        approved_references=[face_ref],
        wardrobe_notes="Vaqueros claros, camisa azul, chaqueta ligera",
        hair_makeup_notes="Pelo suelto, maquillaje natural",
        key_props=["notebook", "phone"],
        continuity_rules=[
            "Misma ropa en toda la secuencia diurna",
        ],
        negative_constraints=[
            "No chaqueta vaquera",
        ],
        scene_ids=["seq_day_01"],
    )


@pytest.fixture
def marta_bible_entry(face_ref, body_ref, wardrobe_ref, night_look, day_look) -> CharacterBibleEntry:
    return CharacterBibleEntry(
        character_id="char_marta",
        project_id="proj_test_01",
        character_name="Marta",
        approved_reference_asset_id="asset_marta_face_v2",
        secondary_reference_asset_ids=["asset_marta_full_body", "asset_marta_wardrobe_night"],
        approved_references=[face_ref, body_ref, wardrobe_ref],
        look_variants=[night_look, day_look],
        default_look_id="look_night_entrance",
        wardrobe_notes="Vestuario casual, tonos oscuros predominan",
        hair_makeup_notes="Pelo castaño, estilo natural",
        key_props=["flashlight", "notebook"],
        continuity_rules=["Continuidad de vestuario entre secuencias"],
        negative_constraints=["No cambios extremos de look entre escenas"],
        version=2,
    )


@pytest.fixture
def resolver() -> CharacterBibleResolver:
    return CharacterBibleResolver()


# --- Resolve approved reference ---


class TestResolveApprovedReference:
    def test_resolve_primary_reference(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
        )
        result = resolver._resolve_single(marta_bible_entry, request)
        assert result.character_id == "char_marta"
        assert result.character_name == "Marta"
        assert result.primary_reference is not None
        assert result.primary_reference.asset_id == "asset_marta_face_v2"
        assert result.primary_reference.is_primary is True

    def test_resolve_secondary_references(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
        )
        result = resolver._resolve_single(marta_bible_entry, request)
        assert len(result.secondary_references) >= 1

    def test_resolve_no_primary_flag_fallback_to_first_sorted(self, resolver):
        ref_a = ApprovedReferenceAsset(
            asset_id="asset_a", asset_type=ApprovedAssetType.FACE_SHEET,
            sort_order=1, is_primary=False,
        )
        ref_b = ApprovedReferenceAsset(
            asset_id="asset_b", asset_type=ApprovedAssetType.FULL_BODY,
            sort_order=2, is_primary=False,
        )
        entry = CharacterBibleEntry(
            character_id="char_x", character_name="X",
            approved_references=[ref_a, ref_b],
        )
        request = CharacterBibleResolveRequest(project_id="p", character_id="char_x")
        result = resolver._resolve_single(entry, request)
        assert result.primary_reference is not None
        assert result.primary_reference.asset_id == "asset_a"


# --- Look variant selection ---


class TestSelectLookVariant:
    def test_select_by_look_id(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
            look_id="look_night_entrance",
        )
        look = resolver.select_look_variant(marta_bible_entry, request)
        assert look is not None
        assert look.look_id == "look_night_entrance"

    def test_select_by_narrative_phase(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
            narrative_phase="day_investigation",
        )
        look = resolver.select_look_variant(marta_bible_entry, request)
        assert look is not None
        assert look.look_id == "look_day_investigation"

    def test_select_by_scene_id(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
            scene_id="seq_night_01",
        )
        look = resolver.select_look_variant(marta_bible_entry, request)
        assert look is not None
        assert look.look_id == "look_night_entrance"

    def test_select_default_look(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
        )
        look = resolver.select_look_variant(marta_bible_entry, request)
        assert look is not None
        assert look.look_id == "look_night_entrance"

    def test_no_variants_returns_none(self, resolver):
        entry = CharacterBibleEntry(
            character_id="char_no_look", character_name="No Look",
        )
        request = CharacterBibleResolveRequest(project_id="p", character_id="char_no_look")
        look = resolver.select_look_variant(entry, request)
        assert look is None


# --- Fallback to base look ---


class TestFallbackToBaseLook:
    def test_no_exact_phase_uses_default(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(
            project_id="proj_test_01",
            character_id="char_marta",
            narrative_phase="unknown_phase",
        )
        look = resolver.select_look_variant(marta_bible_entry, request)
        assert look is not None
        assert look.look_id == "look_night_entrance"

    def test_first_variant_if_no_default(self, resolver, face_ref, body_ref):
        v1 = CharacterLookVariant(look_id="v1", look_name="V1")
        v2 = CharacterLookVariant(look_id="v2", look_name="V2")
        entry = CharacterBibleEntry(
            character_id="char_x", character_name="X",
            look_variants=[v1, v2],
        )
        request = CharacterBibleResolveRequest(project_id="p", character_id="char_x")
        look = resolver.select_look_variant(entry, request)
        assert look is not None
        assert look.look_id == "v1"


# --- Character without reference unresolved ---


class TestUnresolvedCharacter:
    def test_unknown_character_returns_unresolved(self, resolver):
        results = resolver.resolve_character_references_for_shot(
            bible_entries=[],
            shot_number=1,
            character_ids_in_shot=["char_unknown"],
        )
        assert len(results) == 1
        assert results[0].character_id == "char_unknown"
        assert results[0].trace_metadata.get("unresolved") is True
        assert results[0].trace_metadata.get("confidence") == 0.0

    def test_multiple_with_one_missing(self, resolver, marta_bible_entry):
        results = resolver.resolve_character_references_for_shot(
            bible_entries=[marta_bible_entry],
            shot_number=1,
            character_ids_in_shot=["char_marta", "char_unknown"],
        )
        assert len(results) == 2
        marta = [r for r in results if r.character_id == "char_marta"][0]
        unknown = [r for r in results if r.character_id == "char_unknown"][0]
        assert marta.primary_reference is not None
        assert unknown.trace_metadata.get("unresolved") is True


# --- Character lock block ---


class TestCharacterLockBlock:
    def test_lock_block_includes_face_and_wardrobe_and_hair(self, resolver, marta_bible_entry, night_look):
        entry = marta_bible_entry
        primary, secondary = resolver.select_approved_reference(entry, night_look)
        block = resolver.build_character_lock_block(entry, night_look, primary, secondary)
        assert block is not None
        assert "Marta" in block
        assert "referencia_principal" in block
        assert "/api/assets/" in block
        assert "vestuario" in block
        assert "pelo_maquillaje" in block
        assert "props_clave" in block
        assert "flashlight" in block

    def test_lock_block_without_look_uses_entry_defaults(self, resolver, marta_bible_entry):
        entry = marta_bible_entry
        primary, secondary = resolver.select_approved_reference(entry, None)
        block = resolver.build_character_lock_block(entry, None, primary, secondary)
        assert block is not None
        assert "Marta" in block
        assert "vestuario" in block

    def test_lock_block_no_absolute_paths(self, resolver, marta_bible_entry, night_look):
        entry = marta_bible_entry
        primary, secondary = resolver.select_approved_reference(entry, night_look)
        block = resolver.build_character_lock_block(entry, night_look, primary, secondary)
        assert block is not None
        assert "/opt/" not in block
        assert "/mnt/" not in block
        assert "C:" not in block
        assert "storage_path" not in block
        assert "canonical_path" not in block


# --- Negative constraints ---


class TestNegativeConstraints:
    def test_negative_constraints_from_look(self, resolver, marta_bible_entry, night_look):
        block = resolver.build_negative_constraints(marta_bible_entry, night_look)
        assert block is not None
        assert "Marta" in block
        assert "No cambiar a ropa clara" in block
        assert "No pelo suelto" in block

    def test_negative_constraints_from_entry(self, resolver, marta_bible_entry):
        block = resolver.build_negative_constraints(marta_bible_entry, None)
        assert block is not None
        assert "No cambios extremos" in block

    def test_no_constraints_returns_none(self, resolver):
        entry = CharacterBibleEntry(character_id="c", character_name="C")
        block = resolver.build_negative_constraints(entry, None)
        assert block is None


# --- Continuity block ---


class TestContinuityBlock:
    def test_continuity_block_includes_rules_and_wardrobe(self, resolver, marta_bible_entry, night_look):
        block = resolver._build_continuity_block(marta_bible_entry, night_look)
        assert block is not None
        assert "Misma ropa en toda la secuencia nocturna" in block
        assert "Flashlight siempre en mano derecha" in block
        assert "Continuidad de vestuario entre secuencias" in block
        assert "Vestuario consistente" in block
        assert "Pelo/maquillaje consistente" in block


# --- Trace metadata ---


class TestTraceMetadata:
    def test_trace_includes_approved_reference_asset_ids(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        trace = result.trace_metadata
        assert "approved_reference_asset_ids" in trace
        assert "asset_marta_face_v2" in trace["approved_reference_asset_ids"]

    def test_trace_includes_character_reference_ids_used(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        trace = result.trace_metadata
        assert "character_reference_ids_used" in trace
        ids = trace["character_reference_ids_used"]
        assert any("ref_marta_face_v2" in i for i in ids)

    def test_trace_includes_look_variant_applied(self, resolver, marta_bible_entry, night_look):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        assert result.trace_metadata["look_variant_applied"] == "look_night_entrance"
        assert result.trace_metadata["look_variant_name"] == "Night Entrance"

    def test_trace_includes_confidence(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        assert result.trace_metadata["confidence"] > 0.0

    def test_trace_includes_bible_version(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        assert result.trace_metadata["bible_version"] == 2

    def test_trace_no_absolute_paths(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        serialized = str(result.trace_metadata)
        assert "/opt/" not in serialized
        assert "/mnt/" not in serialized
        assert "C:" not in serialized
        assert "storage_path" not in serialized
        assert "canonical_path" not in serialized


# --- Resolve for shot ---


class TestResolveForShot:
    def test_resolve_single_character_in_shot(self, resolver, marta_bible_entry):
        results = resolver.resolve_character_references_for_shot(
            bible_entries=[marta_bible_entry],
            shot_number=1,
            sequence_id="seq_night_01",
            character_ids_in_shot=["char_marta"],
        )
        assert len(results) == 1
        assert results[0].character_id == "char_marta"
        assert results[0].primary_reference is not None

    def test_resolve_multiple_characters(self, resolver, marta_bible_entry):
        char2 = CharacterBibleEntry(
            character_id="char_juan", character_name="Juan",
            project_id="proj_test_01",
        )
        results = resolver.resolve_character_references_for_shot(
            bible_entries=[marta_bible_entry, char2],
            shot_number=1,
            character_ids_in_shot=["char_marta", "char_juan"],
        )
        assert len(results) == 2

    def test_resolve_empty_bible(self, resolver):
        results = resolver.resolve_character_references_for_shot(
            bible_entries=[], shot_number=1,
        )
        assert results == []


class TestResolveForSequence:
    def test_resolve_sequence_characters(self, resolver, marta_bible_entry):
        results = resolver.resolve_character_references_for_sequence(
            bible_entries=[marta_bible_entry],
            sequence_id="seq_night_01",
            character_ids_in_sequence=["char_marta"],
        )
        assert len(results) == 1
        assert results[0].character_id == "char_marta"

    def test_resolve_sequence_no_characters(self, resolver):
        results = resolver.resolve_character_references_for_sequence(
            bible_entries=[], sequence_id="seq_x",
        )
        assert results == []


# --- Resolution result fields ---


class TestResolutionResultFields:
    def test_applied_reference_ids_in_result(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        assert len(result.applied_reference_ids) > 0

    def test_unresolved_props_in_result(self, resolver, marta_bible_entry, night_look):
        entry = marta_bible_entry
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(entry, request)
        assert isinstance(result.unresolved_props, list)

    def test_confidence_calculation_full(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        assert result.trace_metadata["confidence"] >= 0.8

    def test_confidence_low_when_minimal(self, resolver):
        entry = CharacterBibleEntry(character_id="c", character_name="C")
        request = CharacterBibleResolveRequest(project_id="p", character_id="c")
        result = resolver._resolve_single(entry, request)
        assert result.trace_metadata["confidence"] == 0.0


# --- Select approved reference ---


class TestSelectApprovedReference:
    def test_primary_from_approved_refs(self, resolver, face_ref, body_ref):
        entry = CharacterBibleEntry(
            character_id="c", character_name="C",
            approved_references=[body_ref, face_ref],
        )
        primary, secondary = resolver.select_approved_reference(entry, None)
        assert primary is not None
        assert primary.asset_id == face_ref.asset_id

    def test_primary_from_look_variant(self, resolver, night_look, face_ref):
        entry = CharacterBibleEntry(
            character_id="c", character_name="C",
            approved_references=[],
        )
        primary, secondary = resolver.select_approved_reference(entry, night_look)
        assert primary is not None
        assert primary.asset_id == face_ref.asset_id

    def test_no_references_returns_none(self, resolver):
        entry = CharacterBibleEntry(character_id="c", character_name="C")
        primary, secondary = resolver.select_approved_reference(entry, None)
        assert primary is None
        assert secondary == []


# --- Director Notes override ---


class TestDirectorNotesOverride:
    @pytest.fixture
    def dn_result(self) -> DirectorNotesResolveResult:
        pb = PromptBlocks(
            character_lock_block="Director override: Marta looks determined, hair tied back, dark jacket",
            prompt_negative_constraints=["No poncho", "No sombrero"],
            continuity_prompt_block="Director override: maintain tense atmosphere across all shots",
        )
        return DirectorNotesResolveResult(
            project_id="proj_test_01",
            prompt_blocks=pb,
        )

    def test_director_notes_overrides_character_lock(self, resolver, marta_bible_entry, dn_result):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request, dn_result)
        assert result.prompt_lock_block is not None
        assert "Director override" in result.prompt_lock_block

    def test_trace_records_director_notes_override(self, resolver, marta_bible_entry, dn_result):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request, dn_result)
        assert result.trace_metadata["director_notes_override_applied"] is True
        assert "character_lock_block" in result.trace_metadata["director_notes_overridden_fields"]

    def test_director_notes_no_notice_when_not_present(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request, None)
        assert result.trace_metadata["director_notes_override_applied"] is False

    def test_director_notes_negative_merged(self, resolver, marta_bible_entry, dn_result):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request, dn_result)
        assert result.prompt_negative_block is not None
        assert "Director Notes" in result.prompt_negative_block
        assert "No poncho" in result.prompt_negative_block


# --- No absolute paths ---


class TestNoAbsolutePaths:
    def test_no_absolute_paths_in_lock_block(self, resolver, marta_bible_entry, night_look):
        entry = marta_bible_entry
        primary, secondary = resolver.select_approved_reference(entry, night_look)
        block = resolver.build_character_lock_block(entry, night_look, primary, secondary)
        assert block is not None
        assert "/opt/" not in block
        assert "/mnt/" not in block
        assert "C:" not in block

    def test_no_absolute_paths_in_negative_block(self, resolver, marta_bible_entry, night_look):
        block = resolver.build_negative_constraints(marta_bible_entry, night_look)
        assert block is not None
        assert "/opt/" not in block
        assert "/mnt/" not in block

    def test_no_absolute_paths_in_continuity_block(self, resolver, marta_bible_entry, night_look):
        block = resolver._build_continuity_block(marta_bible_entry, night_look)
        assert block is not None
        assert "/opt/" not in block

    def test_no_absolute_paths_in_full_result(self, resolver, marta_bible_entry):
        request = CharacterBibleResolveRequest(project_id="proj_test_01", character_id="char_marta")
        result = resolver._resolve_single(marta_bible_entry, request)
        dumped = result.model_dump_json()
        assert "/opt/" not in dumped
        assert "/mnt/" not in dumped
        assert "C:" not in dumped

    def test_asset_api_url_is_safe_relative(self, resolver, marta_bible_entry):
        for ref in marta_bible_entry.approved_references:
            if ref.asset_api_url:
                assert ref.asset_api_url.startswith("/api/")
                assert ".." not in ref.asset_api_url
