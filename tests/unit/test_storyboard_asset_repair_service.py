from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from schemas.auth_schema import TenantContext  # noqa: E402
from services.storyboard_asset_repair_service import storyboard_asset_repair_service  # noqa: E402


class _Scalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _Result:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows if rows is not None else ([] if row is None else [row])

    def scalar_one_or_none(self):
        return self._row

    def scalars(self):
        return _Scalars(self._rows)


class _Db:
    def __init__(self, shot, asset):
        self.shot = shot
        self.asset = asset
        self.committed = False

    async def execute(self, stmt):
        sql = str(stmt)
        if "storyboard_shots" in sql:
            return _Result(rows=[self.shot])
        if "media_assets" in sql:
            return _Result(rows=[self.asset])
        return _Result()

    def add(self, _obj):
        return None

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_repair_records_direct_metadata_association() -> None:
    shot = SimpleNamespace(
        id="shot-1",
        project_id="proj-1",
        organization_id="org-1",
        is_active=True,
        asset_id=None,
        metadata_json=json.dumps({"render_job_id": "render-job-1"}),
    )
    asset = SimpleNamespace(
        id="asset-1",
        project_id="proj-1",
        organization_id="org-1",
        asset_type="image",
        file_name="shot.png",
        canonical_path="/opt/SERVICIOS_CINE/private/shot.png",
        relative_path="frames/shot.png",
        job_id="render-job-1",
        metadata_json=json.dumps({"storyboard_shot_id": "shot-1"}),
    )
    db = _Db(shot, asset)
    tenant = TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    result = await storyboard_asset_repair_service.repair_storyboard_shot_asset_links(db, "proj-1", tenant)

    metadata = json.loads(shot.metadata_json)
    association = metadata["asset_association"]
    assert result["repaired_count"] == 1
    assert shot.asset_id == "asset-1"
    assert association["association_method"] == "direct_metadata_link"
    assert association["association_reason"] == "metadata_json.storyboard_shot_id"
    assert association["association_confidence"] == 1.0
    assert association["repaired_at"]
    assert db.committed is True


@pytest.mark.asyncio
async def test_repair_records_heuristic_association() -> None:
    shot = SimpleNamespace(
        id="abcdef12-0000-0000-0000-000000000000",
        project_id="proj-1",
        organization_id="org-1",
        is_active=True,
        asset_id=None,
        metadata_json="{}",
    )
    asset = SimpleNamespace(
        id="asset-2",
        project_id="proj-1",
        organization_id="org-1",
        asset_type="image",
        file_name="abcdef12_frame.png",
        canonical_path="/opt/SERVICIOS_CINE/private/abcdef12_frame.png",
        relative_path="frames/abcdef12_frame.png",
        job_id=None,
        metadata_json="{}",
    )
    db = _Db(shot, asset)
    tenant = TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    result = await storyboard_asset_repair_service.repair_storyboard_shot_asset_links(db, "proj-1", tenant)

    association = json.loads(shot.metadata_json)["asset_association"]
    assert result["repaired_count"] == 1
    assert association["association_method"] == "repair_service"
    assert association["association_reason"] == "shot_id_segment_in_path"
    assert 0 < association["association_confidence"] < 1
