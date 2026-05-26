from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from database import get_db  # noqa: E402
from dependencies.tenant_context import get_tenant_context as deps_get_tenant_context  # noqa: E402
from routes.auth_routes import get_tenant_context  # noqa: E402
from routes.storyboard_routes import router  # noqa: E402
from schemas.auth_schema import TenantContext  # noqa: E402
from schemas.storyboard_trace_schema import (  # noqa: E402
    AssetTrace,
    ModelTrace,
    PromptTrace,
    StoryboardTraceRecord,
    StoryboardTraceSummary,
    VersionTrace,
    WorkflowTrace,
)


def _app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    async def override_db():
        yield object()

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    async def fake_shot_trace(db, project_id, shot_id, tenant):
        return StoryboardTraceRecord(
            project_id=project_id,
            organization_id=tenant.organization_id,
            shot_id=shot_id,
            sequence_id="seq-1",
            render_job_id="render-job-1",
            prompt_trace=PromptTrace(positive_prompt_enriched="prompt"),
            workflow_trace=WorkflowTrace(workflow_key="still_storyboard_frame"),
            model_trace=ModelTrace(model_family="sdxl"),
            asset_trace=AssetTrace(media_asset_id="asset-1", image_url=f"/api/projects/{project_id}/storyboard/shots/{shot_id}/image"),
            version_trace=VersionTrace(current_version=1, total_versions=1),
        )

    async def fake_summary(db, project_id, tenant):
        return StoryboardTraceSummary(
            project_id=project_id,
            organization_id=tenant.organization_id,
            total_shots=1,
            traced_shots=1,
            workflow_keys=["still_storyboard_frame"],
        )

    async def fake_asset_trace(db, project_id, asset_id, tenant):
        return StoryboardTraceRecord(
            project_id=project_id,
            organization_id=tenant.organization_id,
            shot_id="shot-1",
            asset_trace=AssetTrace(media_asset_id=asset_id, thumbnail_url=f"/api/projects/{project_id}/storyboard/shots/shot-1/thumbnail"),
        )

    monkeypatch.setattr("routes.storyboard_routes.storyboard_trace_service.get_shot_trace", fake_shot_trace)
    monkeypatch.setattr("routes.storyboard_routes.storyboard_trace_service.get_project_trace_summary", fake_summary)
    monkeypatch.setattr("routes.storyboard_routes.storyboard_trace_service.get_asset_trace", fake_asset_trace)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant
    return app


def test_shot_trace_route(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch)
    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-1/trace")

    assert response.status_code == 200
    data = response.json()
    assert data["shot_id"] == "shot-1"
    assert data["prompt_trace"]["positive_prompt_enriched"] == "prompt"
    assert data["workflow_trace"]["workflow_key"] == "still_storyboard_frame"


def test_project_trace_summary_route(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch)
    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/trace")

    assert response.status_code == 200
    data = response.json()
    assert data["total_shots"] == 1
    assert data["workflow_keys"] == ["still_storyboard_frame"]


def test_asset_trace_route(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _app(monkeypatch)
    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/assets/asset-1/trace")

    assert response.status_code == 200
    data = response.json()
    assert data["shot_id"] == "shot-1"
    assert data["asset_trace"]["media_asset_id"] == "asset-1"
    assert "/api/projects/proj-1/storyboard/shots/shot-1/thumbnail" == data["asset_trace"]["thumbnail_url"]
