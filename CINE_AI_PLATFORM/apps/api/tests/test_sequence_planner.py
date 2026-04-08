import pytest
import pydantic
from src.services.sequence_planner_service import SequencePlannerService
from src.schemas.sequence_plan import SequencePlanRequest

@pytest.fixture
def planner():
    return SequencePlannerService()

def test_plan_empty_script(planner):
    """Should raise ValidationError for empty script text."""
    with pytest.raises(pydantic.ValidationError) as excinfo:
        SequencePlanRequest(script_text="   ")
    
    assert "script_text must be a non-empty string" in str(excinfo.value)

def test_plan_basic_flow(planner):
    """Should generate a valid sequence plan for a simple script."""
    script = "EXT. BOSQUE - DIA. El Guerrero camina bajo la lluvia. Se detiene y mira hacia el cielo."
    request = SequencePlanRequest(script_text=script, sequence_id="test_seq")
    
    response = planner.plan_sequence(request)
    
    assert response["ok"] is True
    assert len(response["beats"]) >= 1
    assert len(response["shots"]) >= 1
    assert "test_seq" in response["sequence_summary"]
    # Check that the first shot is an establishing wide by default logic
    assert response["shots"][0]["shot_type"] == "establishing_wide"


def test_plan_exposes_parsed_scenes_for_screenplay_input(planner):
    script = """
INT. CASA - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    request = SequencePlanRequest(script_text=script, sequence_id="seq_parser")

    response = planner.plan_sequence(request)

    assert response["ok"] is True
    assert len(response["parsed_scenes"]) == 1
    assert len(response["scene_breakdowns"]) == 1
    assert response["parsed_scenes"][0]["heading"] == "INT. CASA - NOCHE"
    assert response["scene_breakdowns"][0]["scene_id"] == response["parsed_scenes"][0]["scene_id"]
    assert any(beat.get("beat_type") for beat in response["beats"])
    assert any(beat.get("shot_intent") for beat in response["beats"])


def test_plan_falls_back_when_screenplay_headings_are_missing(planner):
    script = "Carlos entra en la cocina. Marta lo mira con miedo. La lluvia golpea la ventana."
    request = SequencePlanRequest(script_text=script, sequence_id="seq_fallback")

    response = planner.plan_sequence(request)

    assert response["ok"] is True
    assert response["parsed_scenes"] == []
    assert response["scene_breakdowns"] == []
    assert len(response["beats"]) >= 1
    assert len(response["shots"]) >= 1

def test_character_detection(planner):
    """Should detect characters in uppercase or title case."""
    script = "CARLOS entra en la sala. Maria lo mira con sorpresa. EL GUERRERO desenvaina su espada."
    request = SequencePlanRequest(script_text=script)
    
    response = planner.plan_sequence(request)
    
    # "EL" and "GUERRERO" (individually) might be stopped, but usually we detect Title Case
    # Based on the service: re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", script_text)
    # And uppercase: re.findall(r"\b[A-Z]{2,}\b", script_text)
    
    detected = response["characters_detected"]
    assert "Carlos" in detected
    assert "Maria" in detected
    assert "Guerrero" in detected

def test_render_inputs_integrity(planner):
    """Should generate render inputs compatible with RenderJobsService."""
    script = "Un plano de la ciudad al atardecer."
    request = SequencePlanRequest(script_text=script, style_profile="noir")
    
    response = planner.plan_sequence(request)
    
    render_inputs = response["render_inputs"]
    assert render_inputs["target_endpoint"] == "/api/render/jobs"
    assert len(render_inputs["jobs"]) == 1
    
    job = render_inputs["jobs"][0]
    assert "prompt" in job["request_payload"]
    assert "noir" in job["request_payload"]["prompt"]["6"]["inputs"]["text"]

def test_continuity_persistence(planner):
    """Should propagate the first character to render_context if strict mode is active."""
    script = "EL GUERRERO camina solo."
    request = SequencePlanRequest(
        script_text=script, 
        continuity_mode="strict"
    )
    
    response = planner.plan_sequence(request)
    
    job = response["render_inputs"]["jobs"][0]
    assert job["render_context"]["character_id"] == "char_guerrero"
    assert job["render_context"]["use_ipadapter"] is True

def test_intent_detection(planner):
    """Should detect dialogue intent when quotes are present."""
    script = 'Él dijo: "No podemos quedarnos aquí". Ella asintió.'
    request = SequencePlanRequest(script_text=script)
    
    response = planner.plan_sequence(request)
    
    # Find the beat with dialogue
    dialogue_beats = [b for b in response["beats"] if b["intent"] == "dialogue"]
    assert len(dialogue_beats) > 0


def test_planning_v3_exposes_beat_type_and_shot_intent(planner):
    """Should expose beat_type, shot_intent and motivation when parser finds structure."""
    script = """
INT. SALON - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    request = SequencePlanRequest(script_text=script, sequence_id="seq_v3")

    response = planner.plan_sequence(request)

    assert response["ok"] is True
    assert any(b.get("beat_type") for b in response["beats"])
    assert any(b.get("shot_intent") for b in response["beats"])
    assert any(b.get("motivation") for b in response["beats"])
    assert any(b["beat_type"] == "dialogue" for b in response["beats"])


def test_storyboard_grounding_exposes_grounding_in_shots(planner):
    """Should expose grounding information in shots when planning finds structure."""
    script = """
INT. SALON - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    request = SequencePlanRequest(script_text=script, sequence_id="seq_grounding")

    response = planner.plan_sequence(request)

    assert response["ok"] is True
    assert len(response["shots"]) >= 1
    assert any(s.get("grounding") for s in response["shots"])
    grounding = response["shots"][0].get("grounding", {})
    assert "shot_intent" in grounding
    assert "composition_hint" in grounding


def test_continuity_formal_exposes_axis_in_conversational_shots(planner):
    """Should expose continuity_formal for conversational shots."""
    script = """
INT. SALON - NOCHE

CARLOS
No deberiamos estar aqui.

MARTA
Ya es tarde para volver.
"""
    request = SequencePlanRequest(script_text=script, sequence_id="seq_continuity")

    response = planner.plan_sequence(request)

    assert response["ok"] is True
    assert len(response["shots"]) >= 1
    conversational_shots = [
        s for s in response["shots"]
        if s.get("continuity_formal") and isinstance(s.get("continuity_formal"), dict)
    ]
    assert len(conversational_shots) >= 1
    shot = conversational_shots[0]
    cf = shot["continuity_formal"]
    assert "axis_side" in cf
    assert "eyeline_direction" in cf
    assert "screen_position" in cf
