from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from models.storyboard import StoryboardShot
from services.job_scheduler import JobScheduler
from services.storyboard_service import StoryboardService


class MockSession:
    def __init__(self, shot):
        self.shot = shot
        self.commit_called = 0

    async def get(self, model_class, id):
        return self.shot

    async def commit(self):
        self.commit_called += 1

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_persist_success_updates_render_status() -> None:
    # Arrange
    scheduler = JobScheduler()
    item = SimpleNamespace(
        job_id="job-123",
        metadata={"storyboard_shot_id": "shot-123"},
        prompt={"style_preset": "cinematic_realistic"},
    )
    client = SimpleNamespace(base_url="http://localhost:8188")
    created_assets = [SimpleNamespace(id="asset-123", asset_type="image")]

    # Mock shot and session stub
    shot = StoryboardShot(
        id="shot-123",
        metadata_json=json.dumps({"render_status": "render_pending"}),
    )
    session = MockSession(shot)

    # Mock persist_scheduler_success_assets to return our mock asset
    with patch(
        "services.job_tracking_service.job_tracking_service.persist_scheduler_success_assets",
        AsyncMock(return_value=created_assets),
    ), patch("database.AsyncSessionLocal", return_value=session):
        # Act
        await scheduler._persist_success_assets(
            item=item,
            client=client,
            prompt_id="prompt-123",
            history_entry={},
        )

    # Assert
    assert shot.asset_id == "asset-123"
    meta = json.loads(shot.metadata_json)
    assert meta["render_status"] == "render_succeeded"
    assert session.commit_called == 1


@pytest.mark.asyncio
async def test_persist_failure_updates_render_status() -> None:
    # Arrange
    scheduler = JobScheduler()
    item = SimpleNamespace(
        job_id="job-123",
        metadata={"storyboard_shot_id": "shot-123"},
    )

    shot = StoryboardShot(
        id="shot-123",
        metadata_json=json.dumps({"render_status": "render_pending"}),
    )
    session = MockSession(shot)

    # Act
    with patch("database.AsyncSessionLocal", return_value=session):
        await scheduler._persist_failure(item, "render_failed", "Mock execution failed")

    # Assert
    meta = json.loads(shot.metadata_json)
    assert meta["render_status"] == "render_failed"
    assert meta["render_error"] == "Mock execution failed"
    assert session.commit_called == 1


@pytest.mark.asyncio
async def test_list_storyboard_shots_populates_dynamic_ui_states() -> None:
    # Arrange
    service = StoryboardService()
    project_id = "project-123"
    tenant = SimpleNamespace(organization_id="org-123", user_id="user-123", role="owner", is_global_admin=False)
    project = SimpleNamespace(organization_id="org-123")

    shot_completed = StoryboardShot(
        id="shot-completed",
        asset_id="asset-123",
        metadata_json=json.dumps({"render_job_id": "job-1", "render_status": "render_succeeded"}),
    )
    shot_pending = StoryboardShot(
        id="shot-pending",
        asset_id=None,
        metadata_json=json.dumps({"render_job_id": "job-2", "render_status": "render_pending"}),
    )
    shot_failed = StoryboardShot(
        id="shot-failed",
        asset_id=None,
        metadata_json=json.dumps({"render_job_id": "job-3", "render_status": "render_failed"}),
    )
    shot_none = StoryboardShot(
        id="shot-none",
        asset_id=None,
        metadata_json=None,
    )

    shots = [shot_completed, shot_pending, shot_failed, shot_none]
    assets_map = {
        "asset-123": SimpleNamespace(id="asset-123", file_name="image.png", mime_type="image/png"),
    }

    # Mock execute results
    db = AsyncMock()
    mock_shots_result = MagicMock()
    mock_shots_result.scalars.return_value.all.return_value = shots
    mock_assets_result = MagicMock()
    mock_assets_result.scalars.return_value.all.return_value = list(assets_map.values())
    db.execute.side_effect = [mock_shots_result, mock_assets_result]

    with patch.object(service, "_get_project_for_tenant", AsyncMock(return_value=project)), \
         patch.object(service, "_get_analysis_payload", AsyncMock(return_value={})), \
         patch.object(service, "_sequence_blocks_from_analysis", MagicMock(return_value=[])):

        # Act
        result_shots, version = await service.list_storyboard_shots(db, project_id=project_id, tenant=tenant)

    # Assert
    # 1. Shot Completed
    assert result_shots[0].render_status == "completed"
    assert result_shots[0].has_image is True
    assert result_shots[0].image_state == "render_succeeded"

    # 2. Shot Pending
    assert result_shots[1].render_status == "render_pending"
    assert result_shots[1].has_image is False
    assert result_shots[1].image_state == "render_pending"

    # 3. Shot Failed
    assert result_shots[2].render_status == "render_failed"
    assert result_shots[2].has_image is False
    assert result_shots[2].image_state == "render_failed"

    # 4. Shot None
    assert result_shots[3].render_status == "no_asset"
    assert result_shots[3].has_image is False
    assert result_shots[3].image_state == "no_asset"
