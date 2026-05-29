from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.storyboard_workflow_preset_service import storyboard_workflow_preset_service  # noqa: E402


def test_resolve_profile_with_valid_requested_profile() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template="clean_4_panel_pitch",
        requested_profile="storyboard_flux_fast",
    )

    assert resolved["workflow_profile_requested"] == "storyboard_flux_fast"
    assert resolved["source"] == "explicit"
    assert resolved["fallback_applied"] is False


def test_resolve_profile_with_invalid_requested_profile_falls_back() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="unknown_profile",
    )

    assert resolved["workflow_profile_requested"] == "storyboard_safe"
    assert resolved["fallback_applied"] is True
    assert resolved["reason"] == "unknown_requested_profile:unknown_profile"


def test_resolve_profile_maps_clean_4_panel_pitch() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template="clean_4_panel_pitch",
        requested_profile=None,
    )

    assert resolved["workflow_profile_requested"] == "storyboard_cinematic_pitch"
    assert resolved["source"] == "sheet_template"


def test_resolve_profile_maps_clean_6_panel_review() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template="clean_6_panel_review",
        requested_profile=None,
    )

    assert resolved["workflow_profile_requested"] == "storyboard_clean_review"


def test_resolve_profile_maps_production_12_panel_vertical() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template="production_12_panel_vertical",
        requested_profile=None,
    )

    assert resolved["workflow_profile_requested"] == "storyboard_technical"


def test_resolve_profile_without_data_uses_storyboard_safe() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile=None,
    )

    assert resolved == {
        "workflow_profile_requested": "storyboard_safe",
        "source": "default",
        "sheet_template": None,
        "requested_profile": None,
        "fallback_applied": False,
        "reason": "default_storyboard_safe",
    }


def test_resolve_profile_accepts_production_storyboard_cinematic() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="production_storyboard_cinematic",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic"
    assert resolved["fallback_applied"] is False


def test_resolve_profile_accepts_production_storyboard_cinematic_controlnet() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="production_storyboard_cinematic_controlnet",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic_controlnet"
    assert resolved["fallback_applied"] is False


def test_resolve_profile_accepts_production_storyboard_cinematic_reference() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="production_storyboard_cinematic_reference",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic_reference"
    assert resolved["fallback_applied"] is False


def test_resolve_profile_promotes_realistic_client_review_style() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile=None,
        style_preset="realistic_client_review",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic"
    assert resolved["source"] == "style_preset"


def test_resolve_profile_explicit_reference_wins_over_style_preset() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="production_storyboard_cinematic_reference",
        style_preset="realistic_client_review",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic_reference"
    assert resolved["source"] == "explicit"
    assert resolved["fallback_applied"] is False
    assert resolved["reason"] == "explicit_profile_accepted"
