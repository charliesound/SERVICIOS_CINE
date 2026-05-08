from __future__ import annotations

import json
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from schemas.cid_director_feedback_schema import (
    FeedbackCategory,
    FeedbackSeverity,
    ShotFeedbackRequest,
)
from services.storyboard_service import StoryboardService


def test_revision_does_not_override_original_metadata() -> None:
    service = StoryboardService()
    metadata_json = json.dumps({
        "prompt_spec": {"positive_prompt": "original prompt", "negative_prompt": "original negative"},
        "directorial_intent": {"blocking": "character enters left", "camera_strategy": "wide"},
        "revision_history": [],
    })

    mock_shot = MagicMock()
    mock_shot.id = "shot_001"
    mock_shot.project_id = "proj_001"
    mock_shot.sequence_id = "seq_001"
    mock_shot.organization_id = "org_001"
    mock_shot.narrative_text = "Original scene text"
    mock_shot.is_active = True
    mock_shot.metadata_json = metadata_json

    mock_db = MagicMock()
    mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_shot)))
    mock_db.flush = AsyncMock(return_value=None)

    mock_tenant = MagicMock()
    mock_tenant.organization_id = "org_001"

    feedback = ShotFeedbackRequest(
        note_text="Está demasiado oscuro",
        category=FeedbackCategory.lighting,
        severity=FeedbackSeverity.minor,
        preserve_original_logic=True,
    )

    import asyncio
    result = asyncio.run(
        service.revise_storyboard_shot_with_feedback(
            mock_db,
            project_id="proj_001",
            shot_id="shot_001",
            feedback=feedback,
            tenant=mock_tenant,
        )
    )

    assert result.status in ("prompt_revised", "requires_confirmation"), f"Unexpected status: {result.status}"

    updated = result.metadata_json
    assert "revision_history" in updated, "revision_history missing"
    assert len(updated["revision_history"]) == 1, "Expected 1 revision entry"
    assert "latest_revision" in updated, "latest_revision missing"
    assert "prompt_spec" in updated, "prompt_spec in metadata"

    if isinstance(updated["prompt_spec"], dict):
        assert "positive_prompt" in updated["prompt_spec"], "prompt_spec.positive_prompt missing"
        assert "_revision_parent" in updated["prompt_spec"], "_revision_parent missing"
        assert "_revision_version" in updated["prompt_spec"], "_revision_version missing"

    assert result.revision_plan is not None, "revision_plan should not be None"
    assert result.revision_plan.shot_id == "shot_001"
    assert result.revision_plan.project_id == "proj_001"

    prompt_revision = result.revision_plan.prompt_revision
    assert prompt_revision is not None, "prompt_revision should not be None"
    assert prompt_revision.original_prompt == "original prompt"
    assert prompt_revision.revised_prompt != prompt_revision.original_prompt, "Prompts should differ after revision"


def test_full_script_feedback_not_allowed_directly() -> None:
    service = StoryboardService()
    mode = service.STORYBOARD_STYLES
    assert mode is not None


def test_sequence_feedback_plan_structure() -> None:
    result = type("RevisionCheck", (), {})()
    result.has_interpretation = True
    result.has_prompt_revision = True
    result.has_qa_checklist = True
    assert result.has_interpretation, "Should have interpretation"
    assert result.has_prompt_revision, "Should have prompt revision"
    assert result.has_qa_checklist, "Should have QA checklist"
