from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.storyboard import StoryboardShot  # noqa: E402
from routes.shot_routes import _serialize_shot  # noqa: E402


NOW = datetime.now(timezone.utc)


class _ScalarResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


def test_serialize_shot_render_succeeded_with_asset() -> None:
    shot = StoryboardShot(
        id="shot-a",
        project_id="proj-1",
        organization_id="org-1",
        sequence_order=1,
        asset_id="asset-1",
        metadata_json=json.dumps({"render_status": "render_succeeded", "render_job_id": "job-1"}),
        created_at=NOW,
        updated_at=NOW,
    )
    db = AsyncMock()
    db.execute.return_value = _ScalarResult(SimpleNamespace(file_name="img.png", mime_type="image/png"))

    response = asyncio.run(_serialize_shot(db, "proj-1", shot))

    assert response.render_status == "render_succeeded"
    assert response.image_state == "render_succeeded"
    assert response.has_image is True
    assert response.render_job_id == "job-1"


def test_serialize_shot_render_pending_overrides_existing_asset() -> None:
    shot = StoryboardShot(
        id="shot-b",
        project_id="proj-1",
        organization_id="org-1",
        sequence_order=1,
        asset_id="asset-1",
        metadata_json=json.dumps({"render_status": "render_pending", "render_job_id": "job-2"}),
        created_at=NOW,
        updated_at=NOW,
    )
    db = AsyncMock()
    db.execute.return_value = _ScalarResult(SimpleNamespace(file_name="old.png", mime_type="image/png"))

    response = asyncio.run(_serialize_shot(db, "proj-1", shot))

    assert response.render_status == "render_pending"
    assert response.image_state == "render_pending"
    assert response.has_image is False
    assert response.render_job_id == "job-2"


def test_serialize_shot_render_failed_without_asset() -> None:
    shot = StoryboardShot(
        id="shot-c",
        project_id="proj-1",
        organization_id="org-1",
        sequence_order=1,
        asset_id=None,
        metadata_json=json.dumps({"render_status": "render_failed", "render_error": "boom", "render_job_id": "job-3"}),
        created_at=NOW,
        updated_at=NOW,
    )
    db = AsyncMock()

    response = asyncio.run(_serialize_shot(db, "proj-1", shot))

    assert response.render_status == "render_failed"
    assert response.image_state == "render_failed"
    assert response.has_image is False
    assert response.render_job_id == "job-3"


def test_serialize_shot_asset_with_empty_metadata_defaults_to_succeeded() -> None:
    shot = StoryboardShot(
        id="shot-d",
        project_id="proj-1",
        organization_id="org-1",
        sequence_order=1,
        asset_id="asset-9",
        metadata_json=None,
        created_at=NOW,
        updated_at=NOW,
    )
    db = AsyncMock()
    db.execute.return_value = _ScalarResult(SimpleNamespace(file_name="img2.png", mime_type="image/png"))

    response = asyncio.run(_serialize_shot(db, "proj-1", shot))

    assert response.render_status == "render_succeeded"
    assert response.image_state == "render_succeeded"
    assert response.has_image is True
