from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.comfyui_workflow_schema import WorkflowFallbackReport  # noqa: E402
from services import comfyui_workflow_selector_service as selector  # noqa: E402


CORE_NODES = {
    "CheckpointLoaderSimple",
    "CLIPTextEncode",
    "EmptyLatentImage",
    "KSampler",
    "VAEDecode",
    "SaveImage",
}

CONTROLNET_NODES = {
    *CORE_NODES,
    "LoadImage",
    "ControlNetLoader",
    "ControlNetApplyAdvanced",
    "DWPreprocessor",
}


def test_selector_downgrades_legacy_production_quality_to_new_cinematic_profile() -> None:
    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="production_quality",
        inputs={"prompt": "test prompt"},
        available_nodes=CORE_NODES,
    )

    assert isinstance(prompt, dict)
    assert workflow_key == "production_storyboard_cinematic"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is not None
    assert fallback_report.fallback_applied is True
    assert fallback_report.reason == "profile_not_implemented"


def test_selector_supports_production_storyboard_cinematic_profile_directly() -> None:
    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="production_storyboard_cinematic",
        inputs={"prompt": "test prompt"},
        available_nodes=CORE_NODES,
    )

    assert isinstance(prompt, dict)
    assert workflow_key == "production_storyboard_cinematic"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is None


def test_selector_supports_production_storyboard_cinematic_controlnet_profile_directly() -> None:
    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="production_storyboard_cinematic_controlnet",
        inputs={
            "prompt": "test prompt",
            "pose_reference_image": "pose_reference.png",
            "controlnet_model": "flux_dev_openpose_controlnetl.safetensors",
        },
        available_nodes=CONTROLNET_NODES,
    )

    assert isinstance(prompt, dict)
    assert workflow_key == "production_storyboard_cinematic_controlnet"
    assert executed_profile == "production_storyboard_cinematic_controlnet"
    assert fallback_report is None


def test_selector_controlnet_profile_falls_back_to_production_cinematic_when_controlnet_nodes_missing() -> None:
    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="production_storyboard_cinematic_controlnet",
        inputs={"prompt": "test prompt"},
        available_nodes=CORE_NODES,
    )

    assert isinstance(prompt, dict)
    assert workflow_key == "production_storyboard_cinematic"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_nodes"


def test_selector_downgrades_storyboard_safe_to_smoke_light_when_missing_node(monkeypatch) -> None:
    original_load_template = selector.load_template
    template = original_load_template(selector.WorkflowProfile.storyboard_safe)
    assert template is not None
    template = dict(template)
    prompt_template = dict(template["prompt_template"])
    prompt_template["8"] = {"class_type": "NonExistingNode", "inputs": {}}
    template["prompt_template"] = prompt_template

    def fake_load_template(profile):
        if profile == selector.WorkflowProfile.storyboard_safe:
            return template
        return original_load_template(profile)

    monkeypatch.setattr(selector, "load_template", fake_load_template)

    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="storyboard_safe",
        inputs={"prompt": "test prompt"},
        available_nodes=CORE_NODES,
    )

    assert isinstance(prompt, dict)
    assert workflow_key == "smoke_light"
    assert executed_profile == "smoke_light"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_nodes"
    assert fallback_report.missing_nodes == ["NonExistingNode"]


def test_selector_fails_if_smoke_light_missing_core_node() -> None:
    prompt, workflow_key, fallback_report, executed_profile = selector.select_workflow(
        workflow_key="still_text_to_image_pro",
        requested_profile="smoke_light",
        inputs={"prompt": "test prompt"},
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
        },
    )

    assert prompt is None
    assert workflow_key == ""
    assert executed_profile == "none"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_nodes"
    assert fallback_report.missing_nodes == ["SaveImage"]


def test_workflow_fallback_report_serializes() -> None:
    report = WorkflowFallbackReport(
        requested_profile="production_quality",
        executed_profile="storyboard_safe",
        fallback_applied=True,
        reason="profile_not_implemented",
        missing_nodes=["NodeA"],
        missing_models=["ModelA"],
    )

    payload = report.model_dump()

    assert payload["fallback_applied"] is True
    assert payload["reason"] == "profile_not_implemented"
    assert payload["missing_nodes"] == ["NodeA"]
