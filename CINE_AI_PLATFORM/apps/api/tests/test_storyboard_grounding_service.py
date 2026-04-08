from src.services.storyboard_grounding_service import StoryboardGroundingService
from src.services.screenplay_parser_service import ScreenplayParserService
from src.services.cinematic_breakdown_service import CinematicBreakdownService


def _parse_and_breakdown(script: str):
    parser = ScreenplayParserService()
    breakdown_svc = CinematicBreakdownService()
    parsed = parser.parse_script(script)
    return breakdown_svc.build_scene_breakdowns(parsed)


def test_grounding_two_shot_with_two_characters() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. SALON - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="two_shot",
        beat_type="dialogue",
        scene_breakdown=breakdown,
        beat_text="Carlos y Marta dialogan en el salon",
        characters=["Carlos", "Marta"],
        locations=["salon"],
    )

    assert grounding["shot_intent"] == "two_shot"
    assert grounding["visual_focus"] == "spatial_relationship"
    assert "composition_hint" in grounding
    assert "two" in grounding["composition_hint"].lower() or "relationship" in grounding["composition_hint"].lower()
    assert grounding["primary_subjects"]
    assert grounding["location_anchor"]


def test_grounding_over_shoulder_in_dialogue() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. OFICINA - DIA

ANA
Tenemos que hablar.

LUIS
Dime.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="over_shoulder",
        beat_type="dialogue",
        scene_breakdown=breakdown,
        beat_text="Ana habla con Luis",
        characters=["Ana", "Luis"],
        locations=["oficina"],
    )

    assert grounding["shot_intent"] == "over_shoulder"
    assert grounding["visual_focus"] == "conversation_axis"
    assert "over-shoulder" in grounding["composition_hint"].lower() or "speaker" in grounding["composition_hint"].lower()


def test_grounding_insert_with_relevant_prop() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. HABITACION - NOCHE

Una maleta abierta sobre la cama. Documentos esparcidos.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="insert",
        beat_type="insert",
        scene_breakdown=breakdown,
        beat_text="La maleta abierta revela documentos",
        characters=[],
        locations=["habitacion"],
    )

    assert grounding["shot_intent"] == "insert"
    assert grounding["visual_focus"] == "object_dominance"
    assert grounding["prop_focus"]
    assert "isolate" in grounding["composition_hint"].lower() or "object" in grounding["composition_hint"].lower()


def test_grounding_reaction_with_emotional_focus() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. COCINA - NOCHE

Marta escucha la noticia y palidece.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="reaction",
        beat_type="reaction",
        scene_breakdown=breakdown,
        beat_text="Marta reacciona a la noticia",
        characters=["Marta"],
        locations=["cocina"],
    )

    assert grounding["shot_intent"] == "reaction"
    assert grounding["visual_focus"] == "emotional_response"
    assert grounding["emotional_focus"]
    assert "tight" in grounding["composition_hint"].lower() or "face" in grounding["composition_hint"].lower()


def test_grounding_establishing_with_new_location() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. CASA ABANDONADA - DIA

Polvo en el suelo. Ventanas rotas.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="establishing",
        beat_type="exposition",
        scene_breakdown=breakdown,
        beat_text="Plano de establecimiento de la casa abandonada",
        characters=[],
        locations=["casa abandonada"],
    )

    assert grounding["shot_intent"] == "establishing"
    assert grounding["visual_focus"] == "environment"
    assert grounding["location_anchor"]
    assert "wide" in grounding["composition_hint"].lower() or "space" in grounding["composition_hint"].lower()


def test_grounding_does_not_overload_sparse_scene() -> None:
    service = StoryboardGroundingService()

    grounding = service.ground_shot(
        shot_intent="medium",
        beat_type="exposition",
        scene_breakdown=None,
        beat_text="Silencio.",
        characters=[],
        locations=[],
    )

    assert grounding["shot_intent"] == "medium"
    assert grounding["primary_subjects"]
    assert grounding["composition_hint"]
    assert not grounding.get("prop_focus")


def test_grounding_enriches_prompt_base() -> None:
    service = StoryboardGroundingService()
    breakdowns = _parse_and_breakdown(
        """
INT. GARAJE - NOCHE

Carlos abre el coche. Una llave descansa en el asiento.
"""
    )
    breakdown = breakdowns[0] if breakdowns else {}

    grounding = service.ground_shot(
        shot_intent="insert",
        beat_type="insert",
        scene_breakdown=breakdown,
        beat_text="La llave en el asiento del coche",
        characters=["Carlos"],
        locations=["garaje"],
    )

    prompt_base = "cinematic still, extreme close up, la llave en el asiento del coche"
    enriched = service.enrich_prompt_base(prompt_base, grounding)

    assert enriched != prompt_base
    assert "composition_hint" in enriched.lower() or "focus" in enriched.lower() or "featuring" in enriched.lower()
