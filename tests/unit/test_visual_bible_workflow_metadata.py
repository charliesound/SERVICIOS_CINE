from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.comfyui_workflow_schema import WorkflowFallbackReport  # noqa: E402
from services.job_tracking_service import JobTrackingService  # noqa: E402
from services.comfyui_workflow_selector_service import build_metadata_workflow_profile  # noqa: E402


def test_workflow_metadata_preserves_visual_bible() -> None:
    source_metadata = {
        "visual_bible_enabled": True,
        "visual_bible_applied": True,
        "visual_bible_id": "vb-123",
        "visual_bible_preset": "noir_classic",
        **build_metadata_workflow_profile(
            requested_profile="storyboard_safe",
            executed_profile="storyboard_safe",
            fallback_report=None,
            available_node_count=3664,
        ),
        "workflow_key": "still_storyboard_frame",
    }

    vb_meta = JobTrackingService._extract_visual_bible_metadata(source_metadata)
    workflow_meta = JobTrackingService._extract_workflow_profile_metadata(source_metadata)

    assert vb_meta["visual_bible"]["enabled"] is True
    assert vb_meta["visual_bible"]["applied"] is True
    assert vb_meta["visual_bible"]["visual_bible_id"] == "vb-123"
    assert vb_meta["visual_bible"]["source"] == "render_job_metadata"
    assert workflow_meta["workflow_profile"]["requested"] == "storyboard_safe"
    assert workflow_meta["workflow_profile"]["executed"] == "storyboard_safe"
    assert workflow_meta["workflow_key"] == "still_storyboard_frame"
    assert workflow_meta["available_node_count"] == 3664
    assert workflow_meta["workflow_fallback_report"]["fallback_applied"] is False


def test_workflow_metadata_with_fallback_keeps_visual_bible_applied_true() -> None:
    fallback = WorkflowFallbackReport(
        requested_profile="production_quality",
        executed_profile="storyboard_safe",
        fallback_applied=True,
        reason="profile_not_implemented",
        missing_nodes=[],
        missing_models=[],
    )
    source_metadata = {
        "visual_bible_enabled": True,
        "visual_bible_applied": True,
        "visual_bible_id": "vb-456",
        "visual_bible_preset": "noir_classic",
        **build_metadata_workflow_profile(
            requested_profile="production_quality",
            executed_profile="storyboard_safe",
            fallback_report=fallback,
            available_node_count=3664,
        ),
        "workflow_key": "still_storyboard_frame",
    }

    vb_meta = JobTrackingService._extract_visual_bible_metadata(source_metadata)
    workflow_meta = JobTrackingService._extract_workflow_profile_metadata(source_metadata)

    assert vb_meta["visual_bible"]["applied"] is True
    assert vb_meta["visual_bible"]["visual_bible_preset"] == "noir_classic"
    assert workflow_meta["workflow_profile"] == {
        "requested": "production_quality",
        "executed": "storyboard_safe",
    }
    assert workflow_meta["workflow_fallback_report"]["fallback_applied"] is True
    assert workflow_meta["workflow_fallback_report"]["reason"] == "profile_not_implemented"


def test_visual_bible_and_realistic_client_review_coexist() -> None:
    source_metadata = {
        "visual_bible_enabled": True,
        "visual_bible_applied": True,
        "visual_bible_id": "vb-789",
        "visual_bible_preset": "noir_classic",
        "storyboard_style_preset": "realistic_client_review",
        **build_metadata_workflow_profile(
            requested_profile="storyboard_safe",
            executed_profile="storyboard_safe",
            fallback_report=None,
            available_node_count=3664,
        ),
        "workflow_key": "still_storyboard_frame",
    }

    vb_meta = JobTrackingService._extract_visual_bible_metadata(source_metadata)
    workflow_meta = JobTrackingService._extract_workflow_profile_metadata(source_metadata)

    assert vb_meta["visual_bible"]["applied"] is True
    assert vb_meta["visual_bible"]["visual_bible_preset"] == "noir_classic"
    assert workflow_meta["workflow_profile"]["style_preset"] == "realistic_client_review"
    assert workflow_meta["workflow_profile"]["requested"] == "storyboard_safe"
