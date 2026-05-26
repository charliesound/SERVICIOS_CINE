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
    BeatType,
    CinematicFunction,
    CinematicGrammarRequest,
    CinematicGrammarResult,
    CinematicShotSpec,
    CinematicShotType,
    ContinuityRule,
    CoveragePattern,
    EditorialRole,
    OrderedShotPlan,
    ReferenceMode,
    SceneType,
    ShotPriority,
)


def test_cinematic_shot_type_enum_has_expected_values() -> None:
    assert CinematicShotType.LONG_SHOT.value == "long_shot"
    assert CinematicShotType.CLOSE_UP.value == "close_up"
    assert CinematicShotType.POV.value == "pov"
    assert CinematicShotType.INSERT.value == "insert"
    assert CinematicShotType.EXTREME_CLOSE_UP.value == "extreme_close_up"
    assert len(CinematicShotType) >= 14


def test_coverage_pattern_enum_has_all_patterns() -> None:
    assert CoveragePattern.CLASSIC_COVERAGE.value == "classic_coverage"
    assert CoveragePattern.SUSPENSE_COVERAGE.value == "suspense_coverage"
    assert CoveragePattern.EXPLORATION_COVERAGE.value == "exploration_coverage"
    assert CoveragePattern.DIALOGUE_COVERAGE.value == "dialogue_coverage"
    assert len(CoveragePattern) >= 9


def test_continuity_rule_enum_has_eyeline_match() -> None:
    assert ContinuityRule.EYELINE_MATCH.value == "eyeline_match"
    assert ContinuityRule.AXIS_OF_ACTION.value == "axis_of_action"


def test_editorial_role_enum_has_all_roles() -> None:
    assert EditorialRole.ESTABLISHING.value == "establishing"
    assert EditorialRole.REACTION.value == "reaction"
    assert EditorialRole.POV.value == "pov"
    assert EditorialRole.SOUND_DETAIL.value == "sound_detail"
    assert EditorialRole.THREAT_INDICATOR.value == "threat_indicator"
    assert EditorialRole.CLOSING.value == "closing"
    assert len(EditorialRole) >= 10


def test_shot_priority_enum() -> None:
    assert ShotPriority.MUST_HAVE.value == "must_have"
    assert ShotPriority.OPTIONAL.value == "optional"


def test_cinematic_function_enum() -> None:
    assert CinematicFunction.REVEAL_THREAT.value == "reveal_threat"
    assert CinematicFunction.SOUND_FOCUS.value == "sound_focus"
    assert CinematicFunction.REACTION.value == "reaction"


def test_scene_type_enum() -> None:
    assert SceneType.SUSPENSE.value == "suspense"
    assert SceneType.TERROR.value == "terror"
    assert SceneType.DIALOGUE.value == "dialogue"
    assert SceneType.IMPORTANT_SOUND.value == "important_sound"
    assert len(SceneType) >= 10


def test_reference_mode_enum() -> None:
    assert ReferenceMode.FILMIC.value == "filmic"
    assert ReferenceMode.LITERARY.value == "literary"


def test_beat_type_enum() -> None:
    assert BeatType.ACTION.value == "action"
    assert BeatType.DIALOGUE.value == "dialogue"
    assert BeatType.REVEAL.value == "reveal"


def test_cinematic_shot_spec_serializes_correctly() -> None:
    spec = CinematicShotSpec(
        shot_number=1,
        coverage_pattern=CoveragePattern.SUSPENSE_COVERAGE,
        shot_type=CinematicShotType.LONG_SHOT,
        coverage_role=EditorialRole.ESTABLISHING,
        beat_type=BeatType.DESCRIPTION,
        dramatic_function=CinematicFunction.ESTABLISH_CONTEXT,
        priority=ShotPriority.MUST_HAVE,
    )
    data = spec.model_dump()
    assert data["shot_number"] == 1
    assert data["coverage_pattern"] == "suspense_coverage"
    assert data["shot_type"] == "long_shot"
    assert data["coverage_role"] == "establishing"
    assert data["priority"] == "must_have"
    assert data["cinematic_grammar_version"] == "v0.1"
    assert data["continuity_note"] is None


def test_cinematic_shot_spec_defaults() -> None:
    spec = CinematicShotSpec(
        shot_number=1,
        coverage_pattern=CoveragePattern.CLASSIC_COVERAGE,
        shot_type=CinematicShotType.MEDIUM_SHOT,
        coverage_role=EditorialRole.MASTER,
    )
    assert spec.reference_mode == ReferenceMode.FILMIC
    assert spec.priority == ShotPriority.MEDIUM
    assert spec.cinematic_grammar_version == "v0.1"


def test_ordered_shot_plan_serializes() -> None:
    shot = CinematicShotSpec(
        shot_number=1,
        coverage_pattern=CoveragePattern.CLASSIC_COVERAGE,
        shot_type=CinematicShotType.LONG_SHOT,
        coverage_role=EditorialRole.ESTABLISHING,
    )
    plan = OrderedShotPlan(
        scene_type=SceneType.DIALOGUE,
        coverage_pattern=CoveragePattern.DIALOGUE_COVERAGE,
        shots=[shot],
        continuity_rules=[ContinuityRule.AXIS_OF_ACTION],
    )
    data = plan.model_dump()
    assert data["scene_type"] == "dialogue"
    assert len(data["shots"]) == 1
    assert data["shots"][0]["shot_type"] == "long_shot"


def test_cinematic_grammar_request_serializes() -> None:
    req = CinematicGrammarRequest(
        scene_text="Marta entra en la casa.",
        character_names=["Marta"],
    )
    data = req.model_dump()
    assert data["scene_text"] == "Marta entra en la casa."
    assert data["character_names"] == ["Marta"]
    assert data["reference_mode"] == "filmic"


def test_cinematic_grammar_result_serializes() -> None:
    shot = CinematicShotSpec(
        shot_number=1,
        coverage_pattern=CoveragePattern.CLASSIC_COVERAGE,
        shot_type=CinematicShotType.LONG_SHOT,
        coverage_role=EditorialRole.ESTABLISHING,
    )
    plan = OrderedShotPlan(
        scene_type=SceneType.SUSPENSE,
        coverage_pattern=CoveragePattern.SUSPENSE_COVERAGE,
        shots=[shot],
    )
    result = CinematicGrammarResult(
        plan=plan,
        scene_text="Test",
        detected_scene_type=SceneType.SUSPENSE,
        confidence=0.85,
    )
    data = result.model_dump()
    assert data["detected_scene_type"] == "suspense"
    assert data["confidence"] == 0.85
    assert data["cinematic_grammar_version"] == "v0.1"
