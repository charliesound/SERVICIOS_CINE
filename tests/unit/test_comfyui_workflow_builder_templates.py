from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.workflow_builder import builder  # noqa: E402


TEMPLATE_DIR = ROOT / "data" / "workflows" / "comfyui"
CORE_NODES = {
    "CheckpointLoaderSimple",
    "CLIPTextEncode",
    "EmptyLatentImage",
    "KSampler",
    "VAEDecode",
    "SaveImage",
}


def _load_template(name: str) -> dict:
    return json.loads((TEMPLATE_DIR / name).read_text(encoding="utf-8"))


def test_smoke_light_template_uses_only_core_nodes() -> None:
    template = _load_template("smoke_light.json")
    classes = {node["class_type"] for node in template["prompt_template"].values()}
    assert classes == CORE_NODES


def test_storyboard_safe_template_uses_only_core_nodes() -> None:
    template = _load_template("storyboard_safe.json")
    classes = {node["class_type"] for node in template["prompt_template"].values()}
    assert classes == CORE_NODES


def test_production_storyboard_cinematic_template_uses_only_core_nodes() -> None:
    template = _load_template("production_storyboard_cinematic_v1.json")
    classes = {node["class_type"] for node in template["prompt_template"].values()}
    assert classes == CORE_NODES


def test_still_storyboard_frame_remains_supported() -> None:
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
    assert runtime["1"]["class_type"] == "CheckpointLoaderSimple"
    assert runtime["7"]["class_type"] == "SaveImage"


def test_builder_can_build_profile_template_with_safety_net() -> None:
    runtime, workflow_key, fallback_report, executed_profile = builder.build_runtime_prompt_with_profile(
        "still_text_to_image_pro",
        {"prompt": "defensive prompt", "workflow_profile_requested": "storyboard_safe"},
        requested_profile="storyboard_safe",
        available_nodes=CORE_NODES,
    )

    assert isinstance(runtime, dict)
    assert workflow_key == "storyboard_safe"
    assert executed_profile == "storyboard_safe"
    assert fallback_report is None


def test_realistic_client_review_prompt_enrichment_in_runtime_builder() -> None:
    runtime = builder.build_runtime_prompt(
        "still_storyboard_frame",
        {
            "preset_key": "storyboard_realistic",
            "style_preset": "realistic_client_review",
            "prompt": "A founder presents a pitch deck to the client",
            "negative_prompt": "blurry",
        },
    )

    prompt = runtime["2"]["inputs"]["text"].lower()
    negative = runtime["3"]["inputs"]["text"].lower()
    assert "client-facing commercial or film pitch" in prompt
    assert "clean professional visual style" in prompt
    assert "consistent characters" in prompt
    assert "messy composition" in negative
    assert "distorted faces" in negative
