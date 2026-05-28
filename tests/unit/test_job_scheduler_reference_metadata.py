from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.job_scheduler import (  # noqa: E402
    _history_entry_completed,
    _history_outputs_count,
    _merge_storyboard_runtime_metadata,
)


def test_merge_storyboard_runtime_metadata_keeps_ipadapter_reference_fields() -> None:
    merged = _merge_storyboard_runtime_metadata(
        {},
        {
            "workflow_profile_requested": "production_storyboard_cinematic_reference",
            "workflow_profile_executed": "production_storyboard_cinematic_reference",
            "workflow_template": "production_storyboard_cinematic_reference_v1.json",
            "reference_mode": "ipadapter",
            "references_used": {"character_reference_images": True},
            "character_reference_images": ["pose_reference_smoke_2b1.png"],
            "ipadapter_model": "FLUX/instantx_flux1_dev_ip_adapter_bf16.safetensors",
            "clip_vision_model": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors",
            "ipadapter_weight": 0.85,
            "reference_strength": 0.85,
            "start_at": 0.0,
            "end_at": 1.0,
            "fallback_applied": False,
            "fallback_reason": "none",
        },
        render_status="render_pending",
    )

    assert merged["reference_mode"] == "ipadapter"
    assert merged["references_used"] == {"character_reference_images": True}
    assert merged["character_reference_images"] == ["pose_reference_smoke_2b1.png"]
    assert merged["ipadapter_model"] == "FLUX/instantx_flux1_dev_ip_adapter_bf16.safetensors"
    assert merged["clip_vision_model"] == "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"
    assert merged["ipadapter_weight"] == 0.85
    assert merged["reference_strength"] == 0.85
    assert merged["start_at"] == 0.0
    assert merged["end_at"] == 1.0
    assert merged["render_status"] == "render_pending"


def test_history_entry_completed_true_when_status_completed_true() -> None:
    assert _history_entry_completed({"status": {"completed": True}}) is True


def test_history_entry_completed_false_when_not_completed_and_no_outputs() -> None:
    assert _history_entry_completed({"status": {"completed": False}}) is False


def test_history_outputs_count_counts_image_entries() -> None:
    history_entry = {
        "outputs": {
            "11": {
                "images": [
                    {"filename": "a.png", "subfolder": "", "type": "output"},
                    {"filename": "b.png", "subfolder": "", "type": "output"},
                ]
            }
        }
    }
    assert _history_outputs_count(history_entry) == 2
