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
from services.director_lens_service import director_lens_service  # noqa: E402


def _sample_scene(**overrides) -> ScriptScene:
    payload = {
        "scene_id": "scene_101",
        "scene_number": 101,
        "heading": "INT. HOTEL. NOCHE.",
        "int_ext": "INT",
        "location": "HOTEL",
        "time_of_day": "NOCHE",
        "raw_text": "Un politico agotado espera en silencio dentro de una habitacion de hotel demasiado ordenada.",
        "action_summary": "Un politico agotado espera en silencio dentro de una habitacion de hotel demasiado ordenada.",
        "dialogue_summary": "ASESOR: Debe tomar una decision ahora.",
        "characters": ["POLITICO", "ASESOR"],
        "props": ["telefono"],
        "production_needs": ["cast:2"],
        "dramatic_objective": "decision_and_review",
        "conflict": "latent_tension_or_decision_pressure",
        "emotional_tone": "tension",
        "visual_anchors": ["location:hotel", "time_of_day:noche"],
        "forbidden_elements": ["generic_futuristic_interface"],
    }
    payload.update(overrides)
    return ScriptScene(**payload)


def test_loads_profiles_from_yaml() -> None:
    profiles = director_lens_service.list_profiles()
    assert profiles
    assert any(profile.lens_id == "adaptive_auteur_fusion" for profile in profiles)


def test_adaptive_auteur_fusion_chooses_valid_lens() -> None:
    decision = director_lens_service.choose_lens_for_scene(_sample_scene(), "adaptive_auteur_fusion")
    profile_ids = {profile.lens_id for profile in director_lens_service.list_profiles()}
    assert decision.selected_lens_id in profile_ids


def test_unknown_lens_raises_value_error() -> None:
    try:
        director_lens_service.get_profile("nonexistent_lens")
    except ValueError:
        return
    raise AssertionError("Expected ValueError for nonexistent lens")


def test_int_hotel_night_tension_prefers_expected_lens_family() -> None:
    decision = director_lens_service.choose_lens_for_scene(_sample_scene(), "adaptive_auteur_fusion")
    assert decision.selected_lens_id in {
        "suspense_geometric_control",
        "formal_symmetry_control",
        "dream_identity_fragment",
        "urban_moral_energy",
    }


def test_profiles_have_forbidden_cliches() -> None:
    profiles = director_lens_service.list_profiles()
    assert all(profile.forbidden_cliches for profile in profiles)
