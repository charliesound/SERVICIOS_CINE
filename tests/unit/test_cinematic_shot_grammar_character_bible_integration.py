from __future__ import annotations

from schemas.character_bible_schema import (
    ApprovedAssetType,
    ApprovedReferenceAsset,
    CharacterBibleEntry,
    CharacterBibleResolveResult,
    CharacterLookVariant,
)
from schemas.cinematic_grammar_schema import (
    CinematicGrammarRequest,
    CinematicShotType,
    CoveragePattern,
    EditorialRole,
    SceneType,
    ShotPriority,
)
from schemas.director_notes_schema import (
    CharacterDirectorNotes,
    DirectorNoteOverrideLevel,
    DirectorNoteSource,
    DirectorNotesBundle,
    DirectorNotesResolveResult,
    LocationDirectorNotes,
    PromptBlocks,
    PropDirectorNotes,
)
from services.character_bible_resolver_service import CharacterBibleResolver
from services.cinematic_shot_grammar_engine import cinematic_grammar_engine
from services.director_notes_resolver_service import director_notes_resolver


MARTA_TEXT = (
    "Marta entra con una linterna. "
    "La casa está en silencio. "
    "El suelo cruje. "
    "Marta pregunta si hay alguien. "
    "Una sombra cruza al fondo del pasillo. "
    "Marta se queda quieta."
)

face_ref = ApprovedReferenceAsset(
    asset_id="asset_marta_face_v2",
    asset_type=ApprovedAssetType.FACE_SHEET,
    asset_api_url="/api/assets/marta_face_v2.png",
    reference_id="ref_marta_face_v2",
    description="Marta face sheet v2 - determined expression",
    is_primary=True,
    sort_order=0,
)

body_ref = ApprovedReferenceAsset(
    asset_id="asset_marta_full_body",
    asset_type=ApprovedAssetType.FULL_BODY,
    asset_api_url="/api/assets/marta_full_body.png",
    reference_id="ref_marta_full_body",
    description="Marta full body reference",
    is_primary=False,
    sort_order=1,
)

wardrobe_ref = ApprovedReferenceAsset(
    asset_id="asset_marta_wardrobe_night",
    asset_type=ApprovedAssetType.WARDROBE_SHEET,
    asset_api_url="/api/assets/marta_wardrobe_night.png",
    reference_id="ref_marta_wardrobe_night",
    description="Marta nighttime wardrobe",
    is_primary=False,
    sort_order=2,
)

night_look = CharacterLookVariant(
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

marta_bible_entry = CharacterBibleEntry(
    character_id="char_marta",
    project_id="proj_test_01",
    character_name="Marta",
    approved_reference_asset_id="asset_marta_face_v2",
    secondary_reference_asset_ids=["asset_marta_full_body", "asset_marta_wardrobe_night"],
    approved_references=[face_ref, body_ref, wardrobe_ref],
    look_variants=[night_look],
    default_look_id="look_night_entrance",
    wardrobe_notes="Vestuario casual, tonos oscuros predominan",
    hair_makeup_notes="Pelo castaño, estilo natural",
    key_props=["flashlight", "notebook"],
    continuity_rules=["Continuidad de vestuario entre secuencias"],
    negative_constraints=["No cambios extremos de look entre escenas"],
    version=2,
)

resolver = CharacterBibleResolver()

marta_cb_results = resolver.resolve_character_references_for_shot(
    bible_entries=[marta_bible_entry],
    shot_number=1,
    sequence_id="seq_night_01",
    character_ids_in_shot=["char_marta"],
)


class TestCharacterBibleIntegration:
    def test_approved_reference_propagates_to_all_shots(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            assert shot.approved_reference_asset_ids is not None
            if shot.approved_reference_asset_ids:
                assert "asset_marta_face_v2" in shot.approved_reference_asset_ids

    def test_look_variant_appears_in_shot_metadata(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.look_variant_applied:
                assert shot.look_variant_applied == "look_night_entrance"
                break
        else:
            shots_with = [s for s in result.plan.shots if s.look_variant_applied]
            assert len(shots_with) > 0, "No shot has look_variant_applied"

    def test_character_lock_applied_true_when_approved_reference(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            assert shot.character_lock_applied is not None

    def test_approved_reference_asset_ids_in_shot_metadata(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.approved_reference_asset_ids:
                assert "asset_marta_face_v2" in shot.approved_reference_asset_ids
                break

    def test_negative_constraints_preserved(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.character_negative_constraints:
                assert "No cambiar a ropa clara" in shot.character_negative_constraints
                break

    def test_unresolved_characters_do_not_break_plan(self):
        unknown_result = CharacterBibleResolveResult(
            character_id="char_unknown",
            character_name="",
            trace_metadata={"unresolved": True, "confidence": 0.0},
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=[unknown_result],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 3
        assert "unresolved_characters" in result.character_bible_metadata

    def test_marta_plan_generates_at_least_8_shots(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 8

    def test_marta_plan_includes_threat_coverage(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan.coverage_pattern == CoveragePattern.SUSPENSE_COVERAGE

    def test_marta_plan_includes_pov_shot(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        roles = [s.coverage_role for s in result.plan.shots]
        assert EditorialRole.POV in roles

    def test_marta_plan_includes_insert_shot(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        roles = [s.coverage_role for s in result.plan.shots]
        assert EditorialRole.SOUND_DETAIL in roles or EditorialRole.INSERT in roles

    def test_marta_plan_includes_reaction_shot(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        roles = [s.coverage_role for s in result.plan.shots]
        assert EditorialRole.REACTION in roles

    def test_character_bible_metadata_in_result(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.character_bible_metadata.get("character_bible_active") is True
        assert result.character_bible_metadata.get("character_count") == 1

    def test_character_bible_metadata_includes_resolved_characters(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert "char_marta" in result.character_bible_metadata.get("resolved_characters", [])

    def test_character_bible_empty_results_does_not_break(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=[],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 3

    def test_character_bible_none_results_does_not_break(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=None,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 3

    def test_character_continuity_note_includes_bible_data(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.character_continuity_note:
                assert "Personaje:" in shot.character_continuity_note
                break

    def test_character_reference_id_set_from_bible(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.character_reference_id:
                assert shot.character_reference_id == "Marta"
                break


class TestCharacterBibleAndDirectorNotesInteraction:
    @classmethod
    def setup_class(cls):
        cls.dn_bundle = DirectorNotesBundle(
            characters=[
                CharacterDirectorNotes(
                    character_id="char_marta",
                    character_name="Marta",
                    face_description="Ovalada, ojos grandes, gesto serio",
                    hair="Corto y oscuro",
                    wardrobe="Gabardina beige",
                    body_language="Tensa",
                    emotional_state="Alerta",
                    continuity_constraints=["Gabardina en toda la escena"],
                    forbidden_changes=["No quitar gabardina"],
                    source=DirectorNoteSource.MANUAL,
                    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
                    reviewed_by_user=True,
                )
            ],
            locations=[
                LocationDirectorNotes(
                    location_id="loc_casa",
                    location_name="Casa abandonada",
                    atmosphere="silencioso, polvoriento",
                    lighting="Oscuridad total, linterna",
                    source=DirectorNoteSource.MANUAL,
                    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
                    reviewed_by_user=True,
                )
            ],
            props=[
                PropDirectorNotes(
                    prop_id="prop_linterna",
                    prop_name="Linterna",
                    must_appear=True,
                    source=DirectorNoteSource.MANUAL,
                    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
                    reviewed_by_user=True,
                )
            ],
        )

    def test_director_notes_overrides_character_bible(self):
        dn_result = director_notes_resolver.resolve_notes_for_shot(
            project_id="proj_test_01",
            sequence_id="seq_001",
            shot_number=1,
            bundle=self.dn_bundle,
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=dn_result,
            director_notes_bundle=self.dn_bundle,
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.wardrobe_continuity_note:
                assert "Gabardina" in shot.wardrobe_continuity_note
                break

    def test_character_bible_fills_gaps_director_notes_miss(self):
        dn_result = director_notes_resolver.resolve_notes_for_shot(
            project_id="proj_test_01",
            sequence_id="seq_001",
            shot_number=1,
            bundle=self.dn_bundle,
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=dn_result,
            director_notes_bundle=self.dn_bundle,
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.approved_reference_asset_ids:
                assert "asset_marta_face_v2" in shot.approved_reference_asset_ids
                break

    def test_character_lock_applied_reflects_winner(self):
        dn_result = director_notes_resolver.resolve_notes_for_shot(
            project_id="proj_test_01",
            sequence_id="seq_001",
            shot_number=1,
            bundle=self.dn_bundle,
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=dn_result,
            director_notes_bundle=self.dn_bundle,
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.character_lock_applied:
                assert shot.character_lock_applied == "director_notes"
                break


class TestNoAbsolutePaths:
    def test_no_opt_in_bible_fields(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        dumped = result.model_dump_json()
        assert "/opt/" not in dumped
        assert "/mnt/" not in dumped
        assert "C:" not in dumped

    def test_asset_api_url_is_relative_in_shots(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.character_continuity_note:
                assert "/opt/" not in shot.character_continuity_note
                assert "C:" not in shot.character_continuity_note
                assert "/mnt/" not in shot.character_continuity_note

    def test_no_storage_path_in_output(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        dumped = result.model_dump_json()
        assert "storage_path" not in dumped
        assert "canonical_path" not in dumped


class TestMultipleCharacters:
    def test_two_characters_resolved(self):
        body_ref2 = ApprovedReferenceAsset(
            asset_id="asset_juan_face",
            asset_type=ApprovedAssetType.FACE_SHEET,
            reference_id="ref_juan_face",
            is_primary=True,
        )
        juan_entry = CharacterBibleEntry(
            character_id="char_juan",
            character_name="Juan",
            project_id="proj_test_01",
            approved_references=[body_ref2],
        )
        juan_results = resolver.resolve_character_references_for_shot(
            bible_entries=[juan_entry],
            shot_number=1,
            character_ids_in_shot=["char_juan"],
        )
        all_results = marta_cb_results + juan_results
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta", "Juan"],
            character_bible_results=all_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            if shot.approved_reference_asset_ids:
                assert len(shot.approved_reference_asset_ids) >= 1
                break

    def test_mixed_resolved_and_unresolved(self):
        unknown_result = CharacterBibleResolveResult(
            character_id="char_unknown",
            character_name="",
            trace_metadata={"unresolved": True, "confidence": 0.0},
        )
        all_results = marta_cb_results + [unknown_result]
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta", "Unknown"],
            character_bible_results=all_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 8
        assert "char_unknown" in result.character_bible_metadata.get("unresolved_characters", [])
        assert "char_marta" in result.character_bible_metadata.get("resolved_characters", [])

    def test_look_variants_in_metadata(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert "look_night_entrance" in result.character_bible_metadata.get("look_variants_applied", [])


class TestCharacterBibleWithPriority:
    def test_bible_with_priority_maintained(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        priorities = [s.priority for s in result.plan.shots]
        assert ShotPriority.MUST_HAVE in priorities
        assert ShotPriority.HIGH in priorities

    def test_bible_does_not_change_shot_types(self):
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=marta_cb_results,
        )
        result_with = cinematic_grammar_engine.plan_scene_coverage(request)
        request_no = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
        )
        result_without = cinematic_grammar_engine.plan_scene_coverage(request_no)
        assert len(result_with.plan.shots) == len(result_without.plan.shots)


class TestEdgeCases:
    def test_bible_with_no_approved_references(self):
        empty_result = CharacterBibleResolveResult(
            project_id="proj_test_01",
            character_id="char_no_ref",
            character_name="NoRef",
            trace_metadata={
                "look_variant_applied": None,
                "confidence": 0.0,
            },
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=[empty_result],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.shots) >= 8
        assert result.character_bible_metadata.get("character_bible_active") is True

    def test_look_variant_applied_none_when_no_look(self):
        no_look_result = CharacterBibleResolveResult(
            project_id="proj_test_01",
            character_id="char_no_look",
            character_name="NoLook",
            trace_metadata={
                "look_variant_applied": None,
                "confidence": 0.3,
            },
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            character_bible_results=[no_look_result],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        for shot in result.plan.shots:
            assert shot.look_variant_applied is None
