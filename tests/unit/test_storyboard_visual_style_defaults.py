from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.storyboard_schema import StoryboardGenerateRequest  # noqa: E402
from services.storyboard_service import StoryboardService  # noqa: E402


def test_schema_default_style_preset_is_hand_drawn_storyboard() -> None:
    req = StoryboardGenerateRequest()
    assert req.style_preset == "hand_drawn_storyboard"


def test_hand_drawn_storyboard_style_prompt_contains_drawing_terms() -> None:
    service = StoryboardService()
    style = service.build_storyboard_visual_style_prompt("hand_drawn_storyboard")
    positive = style["positive_style_prompt"].lower()
    assert "pencil line art" in positive
    assert "unfinished production sketch" in positive
    assert "storyboard" in positive


def test_hand_drawn_storyboard_negative_prompt_blocks_photorealism() -> None:
    service = StoryboardService()
    style = service.build_storyboard_visual_style_prompt("hand_drawn_storyboard")
    negative = style["negative_style_prompt"].lower()
    assert "photograph" in negative
    assert "realistic skin" in negative
    assert "cinematic still" in negative


def test_hand_drawn_storyboard_render_payload_not_using_realistic_preset() -> None:
    service = StoryboardService()
    payload = service._build_render_prompt_payload(
        project=SimpleNamespace(id="proj-1", name="Project", description=""),
        scene={"heading": "INT. CASA - NOCHE", "location": "CASA", "time_of_day": "NOCHE"},
        shot_payload={"shot_type": "MS", "description": "Marta entra", "metadata_json": {}},
        style_preset="hand_drawn_storyboard",
        shot_id="shot-1",
        scene_number=1,
    )
    assert payload["preset_key"] != "storyboard_realistic"
    assert "photorealistic" in payload["negative_prompt"].lower()


def test_render_payload_grounds_visual_context_from_scene() -> None:
    service = StoryboardService()
    payload = service._build_render_prompt_payload(
        project=SimpleNamespace(id="proj-1", name="Project", description=""),
        scene={
            "heading": "INT. CASA ABANDONADA - NOCHE",
            "int_ext": "INT",
            "location": "CASA ABANDONADA",
            "time_of_day": "NOCHE",
            "action_blocks": [
                "MARTA entra con una linterna.",
                "La casa está en silencio.",
                "El suelo cruje bajo sus pies.",
                "Una sombra cruza al fondo del pasillo.",
                "Marta se queda quieta.",
            ],
            "dialogue_blocks": [{"character": "MARTA", "text": "¿Hay alguien ahí?"}],
            "characters_detected": ["MARTA"],
            "props": ["linterna"],
            "visual_anchors": ["abandoned hallway", "flashlight beam"],
            "emotional_tone": "silent tense",
        },
        shot_payload={"shot_type": "MS", "description": "Marta entra con una linterna.", "metadata_json": {"atmosphere": "silent tense", "shot_objective": "advance_story_information"}},
        style_preset="hand_drawn_storyboard",
        shot_id="shot-1",
        scene_number=1,
    )
    prompt = payload["prompt"].lower()
    assert "abandoned" in prompt
    assert "interior at night" in prompt
    assert "marta holding a flashlight" in prompt
    assert "medium shot" in prompt
    assert "silent tense atmosphere" in prompt
    assert "creaking floorboards" in prompt
    assert "shadow crossing" in prompt
    assert "freezes in place" in prompt
    assert "hand drawn storyboard style" in prompt


def test_cinematic_realistic_keeps_legacy_behavior() -> None:
    service = StoryboardService()
    payload = service._build_render_prompt_payload(
        project=SimpleNamespace(id="proj-1", name="Project", description=""),
        scene={"heading": "EXT. CALLE - DIA", "location": "CALLE", "time_of_day": "DIA"},
        shot_payload={"shot_type": "WS", "description": "Ciudad despierta", "metadata_json": {}},
        style_preset="cinematic_realistic",
        shot_id="shot-2",
        scene_number=2,
    )
    assert payload["preset_key"] == "storyboard_realistic"


def test_legacy_request_cinematic_realistic_still_supported() -> None:
    service = StoryboardService()
    style = service.build_storyboard_visual_style_prompt("cinematic_realistic")
    assert style["normalized_style_preset"] == "cinematic_realistic"
    assert style["preset_key"] == "storyboard_realistic"


def test_regeneration_default_style_does_not_inherit_cinematic_realistic() -> None:
    service = StoryboardService()
    style = service.build_storyboard_visual_style_prompt("")
    assert style["normalized_style_preset"] == "hand_drawn_storyboard"
    assert style["preset_key"] == "storyboard_sketch"
