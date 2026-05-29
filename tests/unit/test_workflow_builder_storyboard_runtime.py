from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.workflow_builder import STORYBOARD_RUNTIME_PRESETS, builder  # noqa: E402


def test_storyboard_sketch_runtime_preset_exists() -> None:
    assert "storyboard_sketch" in STORYBOARD_RUNTIME_PRESETS
    assert STORYBOARD_RUNTIME_PRESETS["storyboard_sketch"]["checkpoint"] != "Realistic_Vision_V2.0.safetensors"


def test_hand_drawn_storyboard_uses_sketch_checkpoint_not_realistic_vision() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "preset_key": "storyboard_sketch",
            "style_preset": "hand_drawn_storyboard",
            "prompt": "hand-drawn storyboard frame",
            "negative_prompt": "photorealistic, dslr, raw photo",
        },
    )
    assert isinstance(runtime, dict)
    checkpoint = runtime["1"]["inputs"]["ckpt_name"]
    assert checkpoint != "Realistic_Vision_V2.0.safetensors"
    assert checkpoint == STORYBOARD_RUNTIME_PRESETS["storyboard_sketch"]["checkpoint"]


def test_cinematic_realistic_keeps_realistic_vision_runtime_checkpoint() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "preset_key": "storyboard_realistic",
            "style_preset": "cinematic_realistic",
            "prompt": "cinematic realistic storyboard frame",
            "negative_prompt": "blurry",
        },
    )
    assert isinstance(runtime, dict)
    assert runtime["1"]["inputs"]["ckpt_name"] == "Realistic_Vision_V2.0.safetensors"


def test_unknown_storyboard_preset_falls_back_to_storyboard_sketch() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "preset_key": "does_not_exist",
            "style_preset": "hand_drawn_storyboard",
            "prompt": "storyboard sketch",
            "negative_prompt": "photorealistic",
        },
    )
    assert isinstance(runtime, dict)
    assert runtime["1"]["inputs"]["ckpt_name"] == STORYBOARD_RUNTIME_PRESETS["storyboard_sketch"]["checkpoint"]


def test_still_storyboard_frame_supports_production_storyboard_cinematic_profile() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "A detective enters a neon-lit alley",
            "source_scene_heading": "EXT. ALLEY - NIGHT",
            "source_action_summary": "The detective enters the alley and scans the shadows.",
            "shot_objective": "establish visual tension",
            "location": "ALLEY",
            "time_of_day": "NIGHT",
            "continuity_seed": "proj-1:seq-1:shot-1",
        },
        requested_profile="production_storyboard_cinematic",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is None
    assert runtime["1"]["inputs"]["ckpt_name"] == STORYBOARD_RUNTIME_PRESETS["production_storyboard_cinematic"]["checkpoint"]
    assert runtime["5"]["inputs"]["steps"] == 8
    assert runtime["5"]["inputs"]["cfg"] == 2.5
    assert runtime["5"]["inputs"]["scheduler"] == "normal"


def test_storyboard_seed_is_deterministic_without_explicit_seed() -> None:
    runtime_a = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "style_preset": "hand_drawn_storyboard",
            "prompt": "Storyboard frame",
            "continuity_seed": "proj-1:seq-1:shot-1",
        },
    )
    runtime_b = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "style_preset": "hand_drawn_storyboard",
            "prompt": "Storyboard frame",
            "continuity_seed": "proj-1:seq-1:shot-1",
        },
    )

    assert runtime_a["5"]["inputs"]["seed"] == runtime_b["5"]["inputs"]["seed"]
    assert runtime_a["5"]["inputs"]["seed"] > 0


def test_explicit_seed_is_preserved() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "style_preset": "hand_drawn_storyboard",
            "prompt": "Storyboard frame",
            "seed": 12345,
        },
    )

    assert runtime["5"]["inputs"]["seed"] == 12345


def test_runtime_prompt_metadata_extracts_real_values() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Client-ready cinematic storyboard frame",
            "workflow_profile_requested": "production_storyboard_cinematic",
            "continuity_seed": "proj-1:seq-1:shot-2",
        },
    )

    metadata = builder.extract_runtime_prompt_metadata(runtime)

    assert metadata["checkpoint"]
    assert metadata["seed"]
    assert metadata["steps"]
    assert metadata["cfg"]
    assert metadata["sampler_name"]
    assert metadata["scheduler"]
    assert metadata["checkpoint"] == "FLUX/flux1-schnell-fp8.safetensors"


def test_still_storyboard_frame_falls_back_to_storyboard_safe_when_production_profile_missing_nodes(monkeypatch) -> None:
    from services import comfyui_workflow_selector_service as selector

    original_load_template = selector.load_template
    template = original_load_template(selector.WorkflowProfile.production_storyboard_cinematic)
    assert template is not None
    template = dict(template)
    prompt_template = dict(template["prompt_template"])
    prompt_template["8"] = {"class_type": "NonExistingNode", "inputs": {}}
    template["prompt_template"] = prompt_template

    def fake_load_template(profile):
        if profile == selector.WorkflowProfile.production_storyboard_cinematic:
            return template
        return original_load_template(profile)

    monkeypatch.setattr(selector, "load_template", fake_load_template)

    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Client-ready cinematic storyboard frame",
            "continuity_seed": "proj-1:seq-1:shot-3",
        },
        requested_profile="production_storyboard_cinematic",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "storyboard_safe"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_nodes"


def test_controlnet_profile_without_reference_falls_back_to_production_cinematic() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "A detective enters a neon-lit alley",
            "source_scene_heading": "EXT. ALLEY - NIGHT",
            "source_action_summary": "The detective enters the alley and scans the shadows.",
            "shot_objective": "establish visual tension",
            "location": "ALLEY",
            "time_of_day": "NIGHT",
            "continuity_seed": "proj-1:seq-1:shot-4",
        },
        requested_profile="production_storyboard_cinematic_controlnet",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_controlnet_reference"


def test_controlnet_profile_with_pose_reference_uses_controlnet_template() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "A detective enters a neon-lit alley",
            "pose_reference_image": "pose_reference.png",
            "controlnet_model": "flux_dev_openpose_controlnetl.safetensors",
            "controlnet_strength": 0.8,
        },
        requested_profile="production_storyboard_cinematic_controlnet",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
            "LoadImage",
            "ControlNetLoader",
            "ControlNetApplyAdvanced",
            "DWPreprocessor",
        },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "production_storyboard_cinematic_controlnet"
    assert fallback_report is None
    assert runtime["2"]["inputs"]["image"] == "pose_reference.png"
    assert runtime["3"]["inputs"]["control_net_name"] == "flux_dev_openpose_controlnetl.safetensors"
    assert runtime["7"]["inputs"]["strength"] == 0.8


def test_controlnet_profile_overrides_legacy_dimensions_and_checkpoint() -> None:
    runtime, _workflow_key, _fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Controlnet production frame",
            "pose_reference_image": "pose_reference.png",
            "checkpoint": "Realistic_Vision_V2.0.safetensors",
            "width": 1024,
            "height": 576,
        },
        requested_profile="production_storyboard_cinematic_controlnet",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
            "LoadImage",
            "ControlNetLoader",
            "ControlNetApplyAdvanced",
            "DWPreprocessor",
        },
    )

    assert isinstance(runtime, dict)
    assert executed_profile == "production_storyboard_cinematic_controlnet"
    assert runtime["1"]["inputs"]["ckpt_name"] == "FLUX/flux1-dev-fp8.safetensors"
    assert runtime["8"]["inputs"]["width"] == 1344
    assert runtime["8"]["inputs"]["height"] == 768


def test_controlnet_runtime_metadata_reads_nodes_by_class_type() -> None:
    runtime, _workflow_key, _fallback_report, _executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Metadata extraction test",
            "pose_reference_image": "pose_reference.png",
        },
        requested_profile="production_storyboard_cinematic_controlnet",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
            "LoadImage",
            "ControlNetLoader",
            "ControlNetApplyAdvanced",
            "DWPreprocessor",
        },
    )

    metadata = builder.extract_runtime_prompt_metadata(runtime)

    assert metadata["checkpoint"] == "FLUX/flux1-dev-fp8.safetensors"
    assert metadata["width"] == 1344
    assert metadata["height"] == 768
    assert metadata["steps"] == 20


def test_reference_profile_without_character_reference_falls_back_to_production_cinematic() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Reference profile without reference",
        },
        requested_profile="production_storyboard_cinematic_reference",
        available_nodes={
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "production_storyboard_cinematic"
    assert fallback_report is not None
    assert fallback_report.reason == "missing_character_reference"


def test_reference_profile_with_character_reference_uses_ipadapter_template() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_storyboard_frame",
        {
            "style_preset": "realistic_client_review",
            "prompt": "Reference profile with image",
            "character_reference_images": ["pose_reference_smoke_2b1.png"],
            "ipadapter_weight": 0.72,
            "start_at": 0.1,
            "end_at": 0.9,
        },
        requested_profile="production_storyboard_cinematic_reference",
            available_nodes={
                "CheckpointLoaderSimple",
                "CLIPTextEncode",
                "EmptyLatentImage",
                "KSampler",
                "VAEDecode",
                "SaveImage",
                "LoadImage",
                "IPAdapterFluxLoader",
                "ApplyIPAdapterFlux",
            },
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "still_storyboard_frame"
    assert executed_profile == "production_storyboard_cinematic_reference"
    assert fallback_report is None
    assert runtime["1"]["inputs"]["ckpt_name"] == "FLUX/flux1-dev-fp8.safetensors"
    assert runtime["2"]["inputs"]["image"] == "pose_reference_smoke_2b1.png"
    assert runtime["3"]["inputs"]["ipadapter"] == "FLUX/instantx_flux1_dev_ip_adapter_bf16.safetensors"
    assert runtime["3"]["inputs"]["clip_vision"] == "google/siglip-so400m-patch14-384"
    assert runtime["3"]["inputs"]["provider"] == "cuda"
    assert runtime["4"]["inputs"]["weight"] == 0.72
    assert runtime["4"]["inputs"]["start_at"] == 0.1
    assert runtime["4"]["inputs"]["end_at"] == 0.9
