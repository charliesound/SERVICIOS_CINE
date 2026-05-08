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

from schemas.cid_script_to_prompt_schema import ScriptScene  # noqa: E402
from services.cinematic_intent_service import cinematic_intent_service  # noqa: E402
from services.montage_intelligence_service import montage_intelligence_service  # noqa: E402


def _scene(**overrides) -> ScriptScene:
    payload = {
        "scene_id": "scene_201",
        "scene_number": 201,
        "heading": "INT. SALA DE REUNIONES. NOCHE.",
        "int_ext": "INT",
        "location": "SALA DE REUNIONES",
        "time_of_day": "NOCHE",
        "raw_text": "Una directora revisa un storyboard y el productor espera una decision.",
        "action_summary": "Una directora revisa un storyboard y el productor espera una decision.",
        "dialogue_summary": "DIRECTORA: Necesito otra version.",
        "characters": ["DIRECTORA", "PRODUCTOR"],
        "props": ["storyboard"],
        "production_needs": ["cast:2"],
        "dramatic_objective": "decision_and_review",
        "conflict": "latent_tension_or_decision_pressure",
        "emotional_tone": "tension",
        "visual_anchors": ["location:sala de reuniones", "time_of_day:noche"],
        "forbidden_elements": ["generic_futuristic_interface"],
    }
    payload.update(overrides)
    return ScriptScene(**payload)


def test_loads_profiles_from_yaml() -> None:
    profiles = montage_intelligence_service.list_profiles()
    assert profiles
    assert any(profile.get("profile_id") == "adaptive_montage" for profile in profiles)


def test_adaptive_montage_returns_valid_profile() -> None:
    profile_id = montage_intelligence_service.choose_montage_profile(_scene())
    valid_ids = {profile.get("profile_id") for profile in montage_intelligence_service.list_profiles()}
    assert profile_id in valid_ids


def test_dialogue_scene_prefers_rhythmic_dialogue_pressure() -> None:
    profile_id = montage_intelligence_service.choose_montage_profile(_scene())
    assert profile_id == "rhythmic_dialogue_pressure"


def test_suspense_scene_prefers_suspense_information_control() -> None:
    scene = _scene(action_summary="Una mujer abre una puerta mientras escucha un ruido que no puede ubicar.", dialogue_summary=None, dramatic_objective="hidden_threat")
    profile_id = montage_intelligence_service.choose_montage_profile(scene)
    assert profile_id == "suspense_information_control"


def test_contemplative_scene_prefers_contemplative_long_take() -> None:
    scene = _scene(action_summary="Un hombre permanece solo en silencio mirando el agua durante largos segundos.", dialogue_summary=None, emotional_tone="duelo", dramatic_objective="grief_observation")
    profile_id = montage_intelligence_service.choose_montage_profile(scene)
    assert profile_id == "contemplative_long_take"


def test_build_editorial_beats_returns_at_least_one_beat() -> None:
    beats = montage_intelligence_service.build_editorial_beats(_scene())
    assert beats
    assert beats[0].beat_id


def test_build_montage_intent_contains_core_fields() -> None:
    scene = _scene()
    intent = cinematic_intent_service.build_intent(scene, "storyboard_frame", continuity_anchors=scene.visual_anchors)
    montage_intent = montage_intelligence_service.build_montage_intent(scene, intent, intent.directorial_intent)
    assert montage_intent.rhythm
    assert montage_intent.cutting_pattern
    assert montage_intent.coverage_requirements


def test_build_shot_editorial_purpose_has_cut_reason() -> None:
    scene = _scene()
    intent = cinematic_intent_service.build_intent(scene, "storyboard_frame", continuity_anchors=scene.visual_anchors)
    montage_intent = montage_intelligence_service.build_montage_intent(scene, intent, intent.directorial_intent)
    purpose = montage_intelligence_service.build_shot_editorial_purpose(scene, 1, "medium_shot", montage_intent)
    assert purpose.cut_reason
