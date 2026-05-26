from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from schemas.cinematic_grammar_schema import (
    CinematicFunction,
    CinematicGrammarRequest,
    CinematicShotType,
    CoveragePattern,
    EditorialRole,
    ReferenceMode,
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
    ShotDirectorNotes,
    VoiceDirectorNoteDraft,
)
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

MARTA_CHARACTER = CharacterDirectorNotes(
    character_id="char_marta",
    character_name="Marta",
    age_range="30-35",
    face_description="Ovalada, ojos oscuros, expresión seria",
    hair="Castaño largo recogido",
    wardrobe="Chaqueta oscura, vaqueros, botas",
    body_language="Tensa, alerta, movimientos calculados",
    emotional_state="Asustada pero decidida",
    continuity_constraints=["Misma chaqueta en toda la escena", "Mismo peinado"],
    forbidden_changes=["No cambiar peinado", "No cambiar chaqueta"],
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

MARTA_LOCATION = LocationDirectorNotes(
    location_id="loc_casa",
    location_name="Casa abandonada",
    period="contemporáneo",
    architecture_style="rural abandonada",
    atmosphere="silencioso, polvoriento, opresivo",
    lighting="Oscuridad total, solo linterna como luz motriz",
    color_palette=["negro", "marrón oscuro", "gris"],
    continuity_constraints=["Misma disposición en todos los planos"],
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

MARTA_FLASHLIGHT = PropDirectorNotes(
    prop_id="prop_linterna",
    prop_name="Linterna",
    description="Linterna metálica negra, haz potente",
    placement="mano derecha de Marta",
    dramatic_importance="alta — luz motriz de la escena",
    continuity_rule="Misma linterna en todos los planos",
    must_appear=True,
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

ECU_SHOT = ShotDirectorNotes(
    shot_number=5,
    sequence_id="seq_001",
    shot_type_override="extreme_close_up",
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)

PATTERN_OVERRIDE_SHOT = ShotDirectorNotes(
    shot_number=1,
    sequence_id="seq_001",
    coverage_pattern_override="emotional_coverage",
    source=DirectorNoteSource.MANUAL,
    override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
    reviewed_by_user=True,
)


def _make_bundle(
    characters: list[CharacterDirectorNotes] | None = None,
    locations: list[LocationDirectorNotes] | None = None,
    props: list[PropDirectorNotes] | None = None,
    shots: list[ShotDirectorNotes] | None = None,
    voice_drafts: list[VoiceDirectorNoteDraft] | None = None,
) -> DirectorNotesBundle:
    return DirectorNotesBundle(
        characters=characters or [],
        locations=locations or [],
        props=props or [],
        shots=shots or [],
        voice_drafts=voice_drafts or [],
    )


def _resolve(
    bundle: DirectorNotesBundle,
    project_id: str = "proj_test",
    sequence_id: str | None = "seq_001",
    shot_number: int | None = None,
) -> DirectorNotesResolveResult:
    return director_notes_resolver.resolve_notes_for_shot(
        project_id=project_id,
        sequence_id=sequence_id,
        shot_number=shot_number,
        bundle=bundle,
    )


class TestDirectorNotesCharacterPropagation:
    def test_character_note_propagates_to_all_shots(self) -> None:
        bundle = _make_bundle(characters=[MARTA_CHARACTER])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.character_continuity_note is not None
            assert "Marta" in shot.character_continuity_note

    def test_wardrobe_note_propagates(self) -> None:
        bundle = _make_bundle(characters=[MARTA_CHARACTER])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.wardrobe_continuity_note is not None
            assert "Chaqueta oscura" in shot.wardrobe_continuity_note

    def test_wardrobe_note_not_overridden_by_heuristic(self) -> None:
        request_no_dn = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
        )
        plan_no = cinematic_grammar_engine.plan_scene_coverage(request_no_dn).plan
        bundle = _make_bundle(characters=[MARTA_CHARACTER])
        result = _resolve(bundle)
        request_dn = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan_dn = cinematic_grammar_engine.plan_scene_coverage(request_dn).plan
        heuristic_wardrobe = plan_no.shots[0].wardrobe_continuity_note
        dn_wardrobe = plan_dn.shots[0].wardrobe_continuity_note
        assert dn_wardrobe != heuristic_wardrobe
        assert "Chaqueta oscura" in dn_wardrobe


class TestDirectorNotesLocationPropagation:
    def test_location_note_propagates_to_all_shots(self) -> None:
        bundle = _make_bundle(locations=[MARTA_LOCATION])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.set_continuity_note is not None
            assert "Casa abandonada" in shot.set_continuity_note

    def test_location_reference_id_propagates(self) -> None:
        bundle = _make_bundle(locations=[MARTA_LOCATION])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.location_reference_id == "casa_abandonada"

    def test_lighting_note_propagates(self) -> None:
        bundle = _make_bundle(locations=[MARTA_LOCATION])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.lighting_continuity_note is not None
            assert "linterna" in shot.lighting_continuity_note.lower()

    def test_atmosphere_note_propagates(self) -> None:
        bundle = _make_bundle(locations=[MARTA_LOCATION])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.atmosphere_continuity_note is not None
            assert "polvoriento" in shot.atmosphere_continuity_note.lower()


class TestDirectorNotesMustAppearProp:
    def test_must_appear_prop_adds_insert(self) -> None:
        bundle = _make_bundle(props=[MARTA_FLASHLIGHT])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text="Una persona camina.",
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        inserts = [s for s in plan.shots if s.shot_type == CinematicShotType.INSERT]
        assert len(inserts) >= 1
        assert inserts[0].priority == ShotPriority.MUST_HAVE
        assert "Linterna" in inserts[0].prompt_intent

    def test_must_appear_prop_elevates_existing_insert(self) -> None:
        bundle = _make_bundle(props=[MARTA_FLASHLIGHT])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        inserts = [s for s in plan.shots if s.shot_type == CinematicShotType.INSERT]
        assert len(inserts) >= 1
        for ins in inserts:
            assert ins.priority == ShotPriority.MUST_HAVE


class TestDirectorNotesExtremeCloseUp:
    def test_ecu_request_adds_shot(self) -> None:
        bundle = _make_bundle(shots=[ECU_SHOT])
        result = _resolve(bundle, shot_number=5)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        ecus = [s for s in plan.shots if s.shot_type == CinematicShotType.EXTREME_CLOSE_UP]
        assert len(ecus) >= 1

    def test_ecu_added_as_must_have_reaction(self) -> None:
        bundle = _make_bundle(shots=[ECU_SHOT])
        result = _resolve(bundle, shot_number=5)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        ecus = [s for s in plan.shots if s.shot_type == CinematicShotType.EXTREME_CLOSE_UP]
        assert len(ecus) >= 1
        ecu = ecus[0]
        assert ecu.priority == ShotPriority.MUST_HAVE
        assert ecu.coverage_role == EditorialRole.REACTION


class TestDirectorNotesCoveragePatternOverride:
    def test_coverage_pattern_overridden(self) -> None:
        bundle = _make_bundle(shots=[PATTERN_OVERRIDE_SHOT])
        result = _resolve(bundle, shot_number=1)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        assert plan.coverage_pattern == CoveragePattern.EMOTIONAL_COVERAGE

    def test_coverage_pattern_default_when_no_override(self) -> None:
        bundle = _make_bundle()
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        assert plan.coverage_pattern == CoveragePattern.SUSPENSE_COVERAGE


class TestDirectorNotesReferenceMode:
    def test_reference_mode_literary_from_director_notes(self) -> None:
        result = DirectorNotesResolveResult(
            project_id="proj_test",
            cinematic_grammar_overrides={"reference_mode": "literary"},
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.reference_mode == ReferenceMode.LITERARY


class TestDirectorNotesVisualRaccord:
    def test_visual_raccord_block_from_prompt_blocks(self) -> None:
        blocks = PromptBlocks(
            visual_raccord_block="Preserve character and lighting continuity per Director Notes.",
        )
        result = DirectorNotesResolveResult(
            project_id="proj_test",
            prompt_blocks=blocks,
        )
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.visual_raccord_note is not None
            assert "Director Notes" in shot.visual_raccord_note


class TestDirectorNotesPriority:
    def test_manual_override_wins_over_heuristic(self) -> None:
        char_auto = CharacterDirectorNotes(
            character_id="c1",
            character_name="Marta",
            wardrobe="Vestido rojo",
            source=DirectorNoteSource.SYSTEM,
            override_priority=DirectorNoteOverrideLevel.AUTOMATIC_HEURISTIC,
            reviewed_by_user=True,
        )
        char_manual = CharacterDirectorNotes(
            character_id="c1",
            character_name="Marta",
            wardrobe="Chaqueta negra de cuero",
            source=DirectorNoteSource.MANUAL,
            override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
            reviewed_by_user=True,
        )
        bundle = _make_bundle(characters=[char_auto, char_manual])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        for shot in plan.shots:
            assert shot.wardrobe_continuity_note is not None
            assert "cuero" in shot.wardrobe_continuity_note


class TestDirectorNotesVoiceDraft:
    def test_unreviewed_voice_draft_does_not_affect_plan(self) -> None:
        draft = VoiceDirectorNoteDraft(
            transcript="Marta lleva una linterna roja",
            transcript_confidence=0.85,
            reviewed_by_user=False,
        )
        bundle = _make_bundle(voice_drafts=[draft])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        assert len(result.voice_drafts_pending_review) == 1
        for shot in plan.shots:
            if shot.prop_continuity_note:
                assert "roja" not in shot.prop_continuity_note.lower()

    def test_reviewed_voice_draft_can_affect_plan(self) -> None:
        prop_from_voice = PropDirectorNotes(
            prop_id="prop_voice_linterna",
            prop_name="Linterna roja",
            must_appear=True,
            source=DirectorNoteSource.VOICE,
            override_priority=DirectorNoteOverrideLevel.OVERRIDE_MANUAL,
            reviewed_by_user=True,
        )
        bundle = _make_bundle(props=[prop_from_voice])
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        inserts = [s for s in plan.shots if s.shot_type == CinematicShotType.INSERT]
        assert len(inserts) >= 1
        assert inserts[0].priority == ShotPriority.MUST_HAVE
        assert "Linterna roja" in inserts[0].prompt_intent


class TestMartaWithDirectorNotes:
    def test_marta_with_director_notes_keeps_minimum_8_shots(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        assert len(plan.shots) >= 8

    def test_marta_with_dn_conserves_threat(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        threats = [s for s in plan.shots if s.coverage_role == EditorialRole.THREAT_INDICATOR]
        assert len(threats) >= 1
        assert threats[0].priority == ShotPriority.MUST_HAVE

    def test_marta_with_dn_conserves_dialogue(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        dialogues = [
            s for s in plan.shots
            if s.shot_type == CinematicShotType.MEDIUM_CLOSE_UP
            and s.dramatic_function == CinematicFunction.DIALOGUE
        ]
        assert len(dialogues) >= 1

    def test_marta_with_dn_conserves_pov(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        povs = [s for s in plan.shots if s.shot_type == CinematicShotType.POV]
        assert len(povs) >= 1

    def test_marta_with_dn_conserves_insert(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        inserts = [s for s in plan.shots if s.shot_type == CinematicShotType.INSERT]
        assert len(inserts) >= 1

    def test_marta_with_dn_conserves_reaction(self) -> None:
        bundle = _make_bundle(
            characters=[MARTA_CHARACTER],
            locations=[MARTA_LOCATION],
            props=[MARTA_FLASHLIGHT],
        )
        result = _resolve(bundle)
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        plan = cinematic_grammar_engine.plan_scene_coverage(request).plan
        reactions = [s for s in plan.shots if s.coverage_role == EditorialRole.REACTION]
        assert len(reactions) >= 1

    def test_marta_no_director_notes_still_works(self) -> None:
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan is not None
        assert len(result.plan.shots) >= 8
        assert result.detected_scene_type is not None


class TestEmptyDirectorNotes:
    def test_none_director_notes_does_not_crash(self) -> None:
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=None,
            director_notes_bundle=None,
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan is not None
        assert len(result.plan.shots) >= 8

    def test_empty_bundle_does_not_change_plan(self) -> None:
        bundle = _make_bundle()
        result = _resolve(bundle)
        request_with = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            director_notes_result=result,
            director_notes_bundle=bundle,
        )
        request_without = CinematicGrammarRequest(scene_text=MARTA_TEXT)
        plan_with = cinematic_grammar_engine.plan_scene_coverage(request_with).plan
        plan_without = cinematic_grammar_engine.plan_scene_coverage(request_without).plan
        assert len(plan_with.shots) == len(plan_without.shots)


class TestBackwardsCompatibility:
    def test_existing_tests_still_pass_structure(self) -> None:
        request = CinematicGrammarRequest(scene_text=MARTA_TEXT, character_names=["Marta"])
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan is not None
        assert len(result.plan.shots) >= 8
        assert result.detected_scene_type is not None
        assert result.confidence > 0.0
        assert result.cinematic_grammar_version == "v0.1"

    def test_director_notes_new_field_has_default_none(self) -> None:
        request = CinematicGrammarRequest(scene_text=MARTA_TEXT)
        assert request.director_notes_result is None
        assert request.director_notes_bundle is None

    def test_plan_scene_coverage_without_director_notes(self) -> None:
        request = CinematicGrammarRequest(
            scene_text="Juan y María hablan en un café.",
            scene_type_hint=SceneType.DIALOGUE,
            character_names=["Juan", "María"],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.detected_scene_type == SceneType.DIALOGUE
        assert result.plan.coverage_pattern.value == "dialogue_coverage"
        assert len(result.plan.shots) >= 4
