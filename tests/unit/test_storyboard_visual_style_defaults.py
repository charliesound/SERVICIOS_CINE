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
    assert "hand-drawn" in positive
    assert "pencil" in positive
    assert "storyboard" in positive


def test_hand_drawn_storyboard_negative_prompt_blocks_photorealism() -> None:
    service = StoryboardService()
    style = service.build_storyboard_visual_style_prompt("hand_drawn_storyboard")
    negative = style["negative_style_prompt"].lower()
    assert "photorealistic" in negative
    assert "raw photo" in negative
    assert "dslr" in negative


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
