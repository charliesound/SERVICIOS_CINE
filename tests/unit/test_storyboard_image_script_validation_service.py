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

from services.storyboard_image_script_validation_service import (  # noqa: E402
    StoryboardImageScriptValidationService,
)


def _payload() -> dict:
    service = StoryboardImageScriptValidationService()
    return service.build_validation_payload(
        script_excerpt_used="Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
        positive_prompt="MS shot. Marta enters the abandoned house with a flashlight. dark suspense atmosphere.",
        scene_heading="INT. CASA ABANDONADA - NOCHE",
        shot_type="MS",
        characters=["Marta"],
        location="casa abandonada",
        visual_constraints=["stable identity", "no text"],
        atmosphere="suspense oscuro",
    )


def test_validates_marta_flashlight_abandoned_house() -> None:
    service = StoryboardImageScriptValidationService()
    result = service.validate_shot(
        validation_payload=_payload(),
        observed_visual_text="MS shot of Marta in an abandoned house corridor, holding a flashlight, dark suspense mood.",
    )
    assert result["overall_match_score"] >= 0.72
    assert result["regeneration_recommendation"] == "keep_current_render"


def test_detects_missing_key_object() -> None:
    service = StoryboardImageScriptValidationService()
    result = service.validate_shot(
        validation_payload=_payload(),
        observed_visual_text="MS shot of Marta inside an abandoned house corridor, tense mood.",
    )
    assert "key_object" in result["missing_elements"]


def test_detects_incorrect_location() -> None:
    service = StoryboardImageScriptValidationService()
    result = service.validate_shot(
        validation_payload=_payload(),
        observed_visual_text="MS shot of Marta in a sunny beach resort, carrying a flashlight.",
    )
    assert "location" in result["missing_elements"] or "possible_wrong_location" in result["incorrect_elements"]


def test_detects_shot_type_mismatch() -> None:
    service = StoryboardImageScriptValidationService()
    result = service.validate_shot(
        validation_payload=_payload(),
        observed_visual_text="CU portrait of Marta in abandoned house with flashlight, suspense mood.",
    )
    assert result["shot_type_match"] == 0.0


def test_generates_regeneration_suggestion_for_low_score() -> None:
    service = StoryboardImageScriptValidationService()
    result = service.validate_shot(
        validation_payload=_payload(),
        observed_visual_text="random city crowd at noon.",
    )
    assert result["overall_match_score"] < 0.72
    assert result["suggested_regeneration_prompt"]
    assert result["regeneration_recommendation"] == "regenerate_with_stricter_constraints"
