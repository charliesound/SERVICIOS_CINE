from src.services.cinematic_planning_service import CinematicPlanningService
from src.services.screenplay_parser_service import ScreenplayParserService
from src.services.cinematic_breakdown_service import CinematicBreakdownService


def _parse_and_breakdown(script: str):
    parser = ScreenplayParserService()
    breakdown_svc = CinematicBreakdownService()
    parsed = parser.parse_script(script)
    return breakdown_svc.build_scene_breakdowns(parsed)


def test_planning_dialogue_between_two_characters() -> None:
    planning = CinematicPlanningService()
    breakdowns = _parse_and_breakdown(
        """
INT. SALON - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    )

    beats = planning.plan_beats(breakdowns)

    assert len(beats) >= 2
    assert any(b["beat_type"] == "dialogue" for b in beats)
    assert any(b["shot_intent"] in ("two_shot", "over_shoulder") for b in beats)


def test_planning_action_scene_with_spatial_orientation() -> None:
    planning = CinematicPlanningService()
    breakdowns = _parse_and_breakdown(
        """
EXT. CALLE - NOCHE

Carlos corre hacia el coche. El coche frena de golpe.
"""
    )

    beats = planning.plan_beats(breakdowns)

    assert len(beats) >= 1
    assert any(b["beat_type"] == "action" for b in beats)
    assert any(b["shot_intent"] in ("wide", "establishing", "medium") for b in beats)


def test_planning_scene_with_relevant_prop() -> None:
    planning = CinematicPlanningService()
    breakdowns = _parse_and_breakdown(
        """
INT. OFICINA - DIA

Una carpeta descansa sobre la mesa.
"""
    )

    beats = planning.plan_beats(breakdowns)

    assert any(b["beat_type"] == "insert" for b in beats)
    assert any(b["shot_intent"] in ("detail", "insert") for b in beats)


def test_planning_new_location_establishing() -> None:
    planning = CinematicPlanningService()
    breakdowns = _parse_and_breakdown(
        """
INT. CASA ABANDONADA - DIA

Silencio. Polvo en el suelo.
"""
    )

    beats = planning.plan_beats(breakdowns)

    assert len(beats) >= 1
    assert any(b["shot_intent"] in ("establishing", "wide", "medium") for b in beats)


def test_planning_does_not_invent_too_much_in_sparse_scene() -> None:
    planning = CinematicPlanningService()
    breakdowns = _parse_and_breakdown(
        """
INT. PASILLO - DIA

Nada.
"""
    )

    beats = planning.plan_beats(breakdowns)

    assert len(beats) >= 1
    assert all(b["motivation"] for b in beats)
    assert all(b["beat_type"] for b in beats)


def test_planning_integration_with_fallback() -> None:
    planning = CinematicPlanningService()

    planned = planning.plan_beats([], fallback_beats=[
        {"beat_id": "fallback_001", "index": 1, "summary": "Fallback", "text": "Fallback text", "intent": "action"}
    ])

    assert len(planned) == 1
    assert planned[0]["beat_id"] == "fallback_001"
