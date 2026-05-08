from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.cid_sequence_first_schema import ScriptSequenceMapEntry, SequenceStoryboardPlan  # noqa: E402
from services.sequence_storyboard_planning_service import sequence_storyboard_planning_service  # noqa: E402

ENTRY = ScriptSequenceMapEntry(
    sequence_id="seq_001",
    sequence_number=1,
    title="Revisión en estudio",
    script_excerpt="INT. ESTUDIO - NOCHE\nUn director revisa el storyboard. El equipo observa en silencio.\nDIRECTOR: Esta escena necesita más tensión.\nCAMARÓGRAFO: Podríamos cambiar la luz.\nLa atmósfera es tensa.",
    summary="Revisión del storyboard con el equipo",
    location="ESTUDIO",
    time_of_day="NOCHE",
    characters=["DIRECTOR", "CAMARÓGRAFO"],
    dramatic_function="setup",
    emotional_goal="tension",
    visual_opportunity="high",
    production_complexity="low",
    recommended_for_storyboard=True,
    suggested_shot_count=7,
)


def test_plan_sequence_returns_plan() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    assert isinstance(plan, SequenceStoryboardPlan)


def test_plan_has_shot_progression() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    assert len(plan.shot_plan) >= 5
    shot_types = {s.shot_type for s in plan.shot_plan}
    assert len(shot_types) >= 2


def test_plan_starts_with_wide_or_establishing() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    first = plan.shot_plan[0]
    assert first.shot_type in ("WS", "ESTABLISHING")


def test_dialogue_produces_ots_shots() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    shot_types = [s.shot_type for s in plan.shot_plan]
    assert "OTS" in shot_types


def test_emotional_tension_produces_close_up() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    shot_types = [s.shot_type for s in plan.shot_plan]
    assert "CU" in shot_types


def test_plan_has_continuity_notes() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    assert len(plan.continuity_plan) > 0


def test_plan_has_visual_style_guidance() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    assert plan.visual_style_guidance


def test_each_shot_has_prompt_brief() -> None:
    plan = sequence_storyboard_planning_service.plan_sequence(ENTRY)
    for shot in plan.shot_plan:
        assert shot.prompt_brief
