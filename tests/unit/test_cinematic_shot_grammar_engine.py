from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

import pytest
from schemas.cinematic_grammar_schema import (
    CinematicFunction,
    CinematicGrammarRequest,
    CinematicShotType,
    EditorialRole,
    SceneType,
    ShotPriority,
)
from services.cinematic_shot_grammar_engine import cinematic_grammar_engine


MARTA_TEXT = (
    "Marta entra con una linterna. "
    "La casa está en silencio. "
    "El suelo cruje. "
    "Marta pregunta si hay alguien. "
    "Una sombra cruza al fondo del pasillo. "
    "Marta se queda quieta."
)


class TestSceneDetection:
    def test_detect_suspense_from_marta(self) -> None:
        scene_type = cinematic_grammar_engine.detect_scene_type(MARTA_TEXT)
        assert scene_type in (SceneType.SUSPENSE, SceneType.INTERIOR_EXPLORATION)

    def test_detect_dialogue_keywords(self) -> None:
        text = "Juan dice hola. María responde adiós."
        scene_type = cinematic_grammar_engine.detect_scene_type(text)
        assert scene_type == SceneType.DIALOGUE

    def test_detect_terror(self) -> None:
        text = "Ella grita de terror. El monstruo aparece."
        scene_type = cinematic_grammar_engine.detect_scene_type(text)
        assert scene_type == SceneType.TERROR

    def test_detect_physical_action(self) -> None:
        text = "Pedro golpea la puerta y salta por la ventana."
        scene_type = cinematic_grammar_engine.detect_scene_type(text)
        assert scene_type == SceneType.PHYSICAL_ACTION

    def test_detect_important_sound(self) -> None:
        text = "El sonido de una campana resuena en todo el valle."
        scene_type = cinematic_grammar_engine.detect_scene_type(text)
        assert scene_type == SceneType.IMPORTANT_SOUND

    def test_detect_scene_type_and_confidence_returns_confidence(self) -> None:
        scene_type, confidence = cinematic_grammar_engine.detect_scene_type_and_confidence(MARTA_TEXT)
        assert scene_type in (SceneType.SUSPENSE, SceneType.INTERIOR_EXPLORATION)
        assert 0.0 <= confidence <= 1.0


class TestCoverageSelection:
    def test_select_coverage_for_suspense(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        assert pattern.value == "suspense_coverage"

    def test_select_coverage_for_dialogue(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.DIALOGUE)
        assert pattern.value == "dialogue_coverage"

    def test_select_coverage_for_discovery(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.DISCOVERY)
        assert pattern.value == "discovery_coverage"


class TestMartaExample:
    def test_marta_plan_generates_minimum_8_shots(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        assert len(plan.shots) >= 8, f"Expected at least 8 shots, got {len(plan.shots)}"

    def test_marta_plan_has_dialogue_shot(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        dialogues = [
            s for s in plan.shots
            if s.shot_type == CinematicShotType.MEDIUM_CLOSE_UP
            and s.dramatic_function == CinematicFunction.DIALOGUE
        ]
        assert len(dialogues) >= 1, "Expected at least one MEDIUM_CLOSE_UP dialogue shot"
        assert dialogues[0].priority == ShotPriority.MUST_HAVE, "Dialogue shot must be MUST_HAVE"

    def test_marta_plan_threat_is_must_have(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        threats = [s for s in plan.shots if s.coverage_role == EditorialRole.THREAT_INDICATOR]
        assert len(threats) >= 1, "Expected at least one threat_indicator"
        assert threats[0].priority == ShotPriority.MUST_HAVE, "Threat indicator must be MUST_HAVE"

    def test_marta_plan_has_at_least_one_insert(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        inserts = [s for s in plan.shots if s.shot_type == CinematicShotType.INSERT]
        assert len(inserts) >= 1, "Expected at least one INSERT shot"

    def test_marta_plan_has_at_least_one_pov(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        povs = [s for s in plan.shots if s.shot_type == CinematicShotType.POV]
        assert len(povs) >= 1, "Expected at least one POV shot"

    def test_marta_plan_has_at_least_one_threat_indicator(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        threats = [s for s in plan.shots if s.coverage_role == EditorialRole.THREAT_INDICATOR]
        assert len(threats) >= 1, "Expected at least one threat_indicator"

    def test_marta_plan_has_at_least_one_reaction(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        reactions = [s for s in plan.shots if s.coverage_role == EditorialRole.REACTION]
        assert len(reactions) >= 1, "Expected at least one REACTION shot"

    def test_marta_plan_has_must_have_priorities(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        must_haves = [s for s in plan.shots if s.priority == ShotPriority.MUST_HAVE]
        assert len(must_haves) >= 1, "Expected at least one MUST_HAVE priority"

    def test_marta_plan_has_continuity_notes_in_reaction(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        reactions = [s for s in plan.shots if s.coverage_role == EditorialRole.REACTION]
        assert len(reactions) >= 1
        reaction = reactions[0]
        assert reaction.continuity_note is not None, "Reaction should have continuity note"

    def test_marta_plan_has_eyeline_note_in_pov(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        povs = [s for s in plan.shots if s.coverage_role == EditorialRole.POV]
        assert len(povs) >= 1
        pov = povs[0]
        assert pov.eyeline_note is not None, "POV shot should have eyeline note"

    def test_marta_plan_has_raccord_note_after_pov(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for i, shot in enumerate(plan.shots):
            if i > 0 and plan.shots[i - 1].coverage_role == EditorialRole.POV:
                assert shot.raccord_note is not None, (
                    f"Shot {shot.shot_number} after POV should have raccord note"
                )
                break

    def test_marta_plan_all_shots_have_shot_type(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.shot_type is not None, f"Shot {shot.shot_number} missing shot_type"

    def test_marta_plan_all_shots_have_coverage_role(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.coverage_role is not None, f"Shot {shot.shot_number} missing coverage_role"

    def test_marta_plan_cinematic_grammar_version_is_v0_1(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.cinematic_grammar_version == "v0.1"
        assert plan.cinematic_grammar_version == "v0.1"

    def test_marta_plan_has_character_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.character_continuity_note is not None, (
                f"Shot {shot.shot_number} missing character_continuity_note"
            )
            assert "Marta" in shot.character_continuity_note

    def test_marta_plan_has_set_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.set_continuity_note is not None
            assert "abandoned house hallway" in shot.set_continuity_note.lower()

    def test_marta_plan_has_prop_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.prop_continuity_note is not None
            assert "flashlight" in shot.prop_continuity_note.lower()

    def test_marta_plan_has_lighting_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.lighting_continuity_note is not None
            assert "flashlight" in shot.lighting_continuity_note.lower()

    def test_marta_plan_has_atmosphere_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.atmosphere_continuity_note is not None
            assert "silent" in shot.atmosphere_continuity_note.lower()

    def test_marta_plan_has_visual_raccord_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.visual_raccord_note is not None
            assert "preserve" in shot.visual_raccord_note.lower()

    def test_marta_plan_has_character_reference_id(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.character_reference_id == "Marta"

    def test_marta_plan_has_location_reference_id(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.location_reference_id is not None

    def test_marta_plan_has_wardrobe_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        for shot in plan.shots:
            assert shot.wardrobe_continuity_note is not None

    def test_marta_plan_has_axis_continuity_note(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        establishing = [s for s in plan.shots if s.coverage_role == EditorialRole.ESTABLISHING]
        if establishing:
            assert establishing[0].axis_continuity_note is not None

    def test_marta_plan_all_shots_share_consistent_visual_raccord(self) -> None:
        pattern = cinematic_grammar_engine.select_coverage_pattern(SceneType.SUSPENSE)
        plan = cinematic_grammar_engine.build_ordered_shot_plan(MARTA_TEXT, pattern)
        first = plan.shots[0]
        for shot in plan.shots:
            assert shot.character_continuity_note == first.character_continuity_note
            assert shot.set_continuity_note == first.set_continuity_note
            assert shot.prop_continuity_note == first.prop_continuity_note
            assert shot.lighting_continuity_note == first.lighting_continuity_note
            assert shot.visual_raccord_note == first.visual_raccord_note


class TestEndToEnd:
    def test_plan_scene_coverage_returns_result(self) -> None:
        request = CinematicGrammarRequest(
            scene_text=MARTA_TEXT,
            character_names=["Marta"],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan is not None
        assert len(result.plan.shots) >= 8
        assert result.detected_scene_type is not None
        assert result.confidence > 0.0
        assert result.cinematic_grammar_version == "v0.1"

    def test_plan_scene_coverage_with_hint(self) -> None:
        request = CinematicGrammarRequest(
            scene_text="Juan y María hablan en un café.",
            scene_type_hint=SceneType.DIALOGUE,
            character_names=["Juan", "María"],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.detected_scene_type == SceneType.DIALOGUE
        assert result.plan.coverage_pattern.value == "dialogue_coverage"
        assert len(result.plan.shots) >= 4

    def test_dialogue_scene_has_ots_shots(self) -> None:
        request = CinematicGrammarRequest(
            scene_text="Ana dice que no. Carlos responde que sí.",
            character_names=["Ana", "Carlos"],
        )
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        ots = [s for s in result.plan.shots if s.shot_type == CinematicShotType.OVER_THE_SHOULDER]
        assert len(ots) >= 1, "Dialogue coverage should have OTS shots"

    def test_continuity_rules_are_set(self) -> None:
        request = CinematicGrammarRequest(scene_text=MARTA_TEXT)
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert len(result.plan.continuity_rules) > 0, "Continuity rules should not be empty"

    def test_empty_text_does_not_crash(self) -> None:
        request = CinematicGrammarRequest(scene_text="")
        result = cinematic_grammar_engine.plan_scene_coverage(request)
        assert result.plan is not None
        assert result.plan.scene_type is not None
