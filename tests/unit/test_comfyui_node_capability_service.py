from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.comfyui_node_capability_service import (  # noqa: E402
    build_capability_snapshot,
    extract_workflow_node_classes,
    validate_workflow_nodes,
)


def test_extract_workflow_node_classes() -> None:
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {}},
        "3": {"class_type": "SaveImage", "inputs": {}},
    }

    assert extract_workflow_node_classes(workflow) == {
        "CheckpointLoaderSimple",
        "CLIPTextEncode",
        "SaveImage",
    }


def test_validate_workflow_nodes_detects_missing() -> None:
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {}},
        "2": {"class_type": "KSampler", "inputs": {}},
        "3": {"class_type": "SaveImage", "inputs": {}},
    }

    missing = validate_workflow_nodes(workflow, {"CheckpointLoaderSimple", "SaveImage"})

    assert missing == ["KSampler"]


def test_build_capability_snapshot_counts_nodes() -> None:
    snapshot = build_capability_snapshot(
        "still",
        "http://127.0.0.1:8188",
        {
            "CheckpointLoaderSimple": {},
            "CLIPTextEncode": {},
            "KSampler": {},
        },
    )

    assert snapshot.backend == "still"
    assert snapshot.base_url == "http://127.0.0.1:8188"
    assert snapshot.total_nodes == 3
    assert snapshot.available_nodes == ["CLIPTextEncode", "CheckpointLoaderSimple", "KSampler"]
    assert snapshot.object_info_snapshot_at is not None
