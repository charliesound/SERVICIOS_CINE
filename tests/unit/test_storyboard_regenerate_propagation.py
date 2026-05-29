from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.storyboard_schema import StoryboardGenerateRequest  # noqa: E402
from services.storyboard_workflow_preset_service import storyboard_workflow_preset_service  # noqa: E402
from services.job_tracking_service import JobTrackingService  # noqa: E402


def test_generate_request_schema_includes_reference_mode() -> None:
    fields = StoryboardGenerateRequest.model_fields
    assert "reference_mode" in fields
    assert fields["reference_mode"].annotation == str | None


def test_generate_request_schema_stores_reference_mode() -> None:
    req = StoryboardGenerateRequest(style_preset="realistic_client_review", reference_mode="ipadapter_flux")
    assert req.reference_mode == "ipadapter_flux"


def test_generate_request_schema_stores_workflow_profile() -> None:
    req = StoryboardGenerateRequest(
        style_preset="realistic_client_review",
        workflow_profile="production_storyboard_cinematic_reference",
        character_reference_images=["ref.png"],
        ipadapter_model="instantx_flux1_dev_ip_adapter_bf16.safetensors",
    )
    assert req.workflow_profile == "production_storyboard_cinematic_reference"
    assert req.character_reference_images == ["ref.png"]
    assert req.ipadapter_model == "instantx_flux1_dev_ip_adapter_bf16.safetensors"


def test_extract_render_metadata_preserves_ipadapter_flux_reference_mode() -> None:
    source_metadata = {
        "reference_mode": "ipadapter_flux",
        "character_reference_images": ["character_reference_smoke_2b2.png"],
        "reference_strength": 0.85,
        "ipadapter_weight": 0.85,
        "ipadapter_model": "instantx_flux1_dev_ip_adapter_bf16.safetensors",
        "clip_vision_model": "google/siglip-so400m-patch14-384",
        "start_at": 0.0,
        "end_at": 1.0,
    }

    render_meta = JobTrackingService._extract_render_prompt_metadata(source_metadata)

    assert render_meta["reference_mode"] == "ipadapter_flux"
    assert render_meta["character_reference_images"] == ["character_reference_smoke_2b2.png"]
    assert render_meta["reference_strength"] == 0.85
    assert render_meta["ipadapter_model"] == "instantx_flux1_dev_ip_adapter_bf16.safetensors"


def test_resolve_profile_with_reference_mode_default_none() -> None:
    resolved = storyboard_workflow_preset_service.resolve_profile(
        sheet_template=None,
        requested_profile="production_storyboard_cinematic_reference",
    )

    assert resolved["workflow_profile_requested"] == "production_storyboard_cinematic_reference"
    assert resolved["fallback_applied"] is False


def test_workflow_profile_requested_matches_expected_values() -> None:
    req = StoryboardGenerateRequest(
        style_preset="realistic_client_review",
        workflow_profile="production_storyboard_cinematic_reference",
        character_reference_images=["test.png"],
        reference_mode="ipadapter_flux",
        provider="cuda",
        ipadapter_weight=0.85,
        ipadapter_model="instantx_flux1_dev_ip_adapter_bf16.safetensors",
        clip_vision_model="google/siglip-so400m-patch14-384",
    )

    assert req.workflow_profile == "production_storyboard_cinematic_reference"
    assert req.character_reference_images == ["test.png"]
    assert req.reference_mode == "ipadapter_flux"
    assert req.ipadapter_weight == 0.85
    assert req.ipadapter_model == "instantx_flux1_dev_ip_adapter_bf16.safetensors"
    assert req.clip_vision_model == "google/siglip-so400m-patch14-384"


def test_generate_request_schema_includes_provider() -> None:
    fields = StoryboardGenerateRequest.model_fields
    assert "provider" in fields


def test_generate_request_schema_stores_provider() -> None:
    req = StoryboardGenerateRequest(provider="cuda")
    assert req.provider == "cuda"
