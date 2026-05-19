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
