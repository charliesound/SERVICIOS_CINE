from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")

from database import get_db  # noqa: E402
from dependencies.tenant_context import get_tenant_context as dependency_tenant_context  # noqa: E402
from routes.auth_routes import get_tenant_context as route_tenant_context  # noqa: E402
from routes.storyboard_presentation_routes import router  # noqa: E402
from schemas.auth_schema import TenantContext  # noqa: E402
from schemas.storyboard_presentation_schema import StoryboardFrame  # noqa: E402
from services.storyboard_export_service import storyboard_export_service  # noqa: E402
from services.storyboard_frame_service import storyboard_frame_service  # noqa: E402
from services.storyboard_layout_engine import storyboard_layout_engine  # noqa: E402


class _FakeExecuteResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _FakeDb:
    def __init__(self, project_id: str, organization_id: str):
        self.project_id = project_id
        self.organization_id = organization_id

    async def execute(self, _stmt):
        return _FakeExecuteResult(self.project_id)


@pytest.fixture
def test_app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> FastAPI:
    fake_db = _FakeDb(project_id="proj-1", organization_id="org-1")

    async def override_db():
        yield fake_db

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise")

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[route_tenant_context] = override_tenant
    app.dependency_overrides[dependency_tenant_context] = override_tenant
    monkeypatch.setattr(storyboard_export_service, "_repo_root", tmp_path)
    return app


def _frame(index: int) -> StoryboardFrame:
    return StoryboardFrame(
        shot_number=index,
        scene_number=str(index),
        image_path=f"/tmp/frame_{index}.png",
    )


def test_generate_sheet_template_clean_4_panel_pitch_defaults_to_four_frames(test_app: FastAPI, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_collect(*_args, **_kwargs):
        return [_frame(index) for index in range(1, 11)]

    monkeypatch.setattr(storyboard_frame_service, "collect_by_project", fake_collect)
    monkeypatch.setattr(storyboard_layout_engine, "render_pages", lambda frames, _config: [Image.new("RGB", (200, 300), color=(255, 255, 255))])

    with TestClient(test_app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/sheet",
            json={
                "project_id": "proj-1",
                "layout": {"layout": "grid_2x2", "preset": "realistic_client_review"},
                "sheet_template": "clean_4_panel_pitch",
                "output_format": "png",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["frame_count"] == 4
    assert body["artifact_url"] is not None
    assert "clean_4_panel_pitch" in body["artifact_path"]
    assert "4f" in body["artifact_path"]
    assert body["metadata"]["template"] == {
        "sheet_template": "clean_4_panel_pitch",
        "effective_layout": "grid_2x2",
        "effective_preset": "cinematic_pitch",
        "effective_max_frames": 4,
        "orientation": "portrait",
    }


def test_generate_sheet_explicit_max_frames_overrides_template_default(test_app: FastAPI, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_collect(*_args, **_kwargs):
        return [_frame(index) for index in range(1, 11)]

    monkeypatch.setattr(storyboard_frame_service, "collect_by_project", fake_collect)
    monkeypatch.setattr(storyboard_layout_engine, "render_pages", lambda frames, _config: [Image.new("RGB", (300, 200), color=(255, 255, 255))])

    with TestClient(test_app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/sheet",
            json={
                "project_id": "proj-1",
                "layout": {"layout": "grid_2x2", "preset": "realistic_client_review"},
                "sheet_template": "clean_4_panel_pitch",
                "max_frames": 8,
                "output_format": "pdf",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["frame_count"] == 8
    assert body["metadata"]["template"]["effective_max_frames"] == 8
    assert body["metadata"]["credit_estimate"]["estimated_credits"] == 8


def test_generate_sheet_template_clean_6_panel_review_defaults_to_six_frames(test_app: FastAPI, monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_collect(*_args, **_kwargs):
        return [_frame(index) for index in range(1, 11)]

    monkeypatch.setattr(storyboard_frame_service, "collect_by_project", fake_collect)
    monkeypatch.setattr(storyboard_layout_engine, "render_pages", lambda frames, _config: [Image.new("RGB", (200, 300), color=(255, 255, 255))])

    with TestClient(test_app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/sheet",
            json={
                "project_id": "proj-1",
                "layout": {"layout": "grid_2x2", "preset": "realistic_client_review"},
                "sheet_template": "clean_6_panel_review",
                "output_format": "png",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["frame_count"] == 6
    assert body["metadata"]["template"]["effective_layout"] == "grid_2x3"
    assert body["metadata"]["template"]["effective_max_frames"] == 6


def test_download_storyboard_artifact_returns_file(test_app: FastAPI) -> None:
    export_dir = storyboard_export_service.get_export_dir("proj-1")
    artifact = export_dir / "sheet.png"
    artifact.write_bytes(b"fake-image")

    with TestClient(test_app) as client:
        response = client.get("/api/projects/proj-1/storyboard/sheet/artifacts/sheet.png")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")


def test_download_storyboard_artifact_blocks_path_traversal(test_app: FastAPI) -> None:
    with TestClient(test_app) as client:
        response = client.get("/api/projects/proj-1/storyboard/sheet/artifacts/../secret.txt")

    assert response.status_code == 404


def test_download_storyboard_artifact_returns_404_when_missing(test_app: FastAPI) -> None:
    with TestClient(test_app) as client:
        response = client.get("/api/projects/proj-1/storyboard/sheet/artifacts/missing.pdf")

    assert response.status_code == 404
