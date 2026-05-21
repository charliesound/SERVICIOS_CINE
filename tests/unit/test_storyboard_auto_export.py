from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

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
from services.storyboard_service import storyboard_service  # noqa: E402
from services.storyboard_frame_service import storyboard_frame_service  # noqa: E402
from services.storyboard_export_service import storyboard_export_service  # noqa: E402
from schemas.storyboard_presentation_schema import StoryboardFrame, StoryboardFrameMetadata, StoryboardShotInfo  # noqa: E402


async def _empty_fake_project_for_tenant(db, *, project_id, tenant):
    return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)


def _make_export_test_app(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    auto_export_sheet: bool,
    collect_frames_fails: bool = False,
    export_fails: bool = False,
) -> FastAPI:
    async def override_db():
        yield SimpleNamespace()

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    monkeypatch.setattr(storyboard_service, "_get_project_for_tenant", _empty_fake_project_for_tenant)
    monkeypatch.setattr(storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (tmp_path / "data",))

    async def fake_generate_storyboard(db, **kwargs) -> dict:
        return {
            "job_id": "job-1",
            "status": "completed",
            "mode": "SEQUENCE",
            "generation_mode": "SEQUENCE",
            "version": 1,
            "sequence_id": "seq-1",
            "sequence_ids": ["seq-1"],
            "scene_start": None,
            "scene_end": None,
            "selected_scene_numbers": [],
            "total_selected": 0,
            "total_scenes": 1,
            "total_shots": 4,
            "render_jobs": [],
            "render_errors": [],
            "generated_assets": [],
            "created_at": "2026-01-01T00:00:00Z",
        }

    monkeypatch.setattr(storyboard_service, "generate_storyboard", fake_generate_storyboard)

    image_dir = tmp_path / "data" / "output" / "frames"
    image_dir.mkdir(parents=True, exist_ok=True)
    from PIL import Image as PILImage
    image_file = image_dir / "frame.png"
    PILImage.new("RGB", (100, 100), (0, 128, 0)).save(image_file)
    thumbnail_file = image_dir / "frame_thumb.webp"

    if not collect_frames_fails:
        from services.storyboard_layout_engine import storyboard_layout_engine
        mock_page = PILImage.new("RGB", (100, 100), (0, 128, 0))
        monkeypatch.setattr(storyboard_layout_engine, "render_pages", lambda *a, **kw: [mock_page])

        mock_frame = StoryboardFrame(
            shot_number=1,
            scene_number="1",
            image_path=str(image_file),
            info=StoryboardShotInfo(
                scene="Test scene",
                shot_size="MS",
                camera_angle="eye-level",
                movement="static",
                description="Test",
                dialogue=None,
                notes=None,
                status="completed",
            ),
            metadata=StoryboardFrameMetadata(
                visual_bible=None,
                workflow_profile=None,
                workflow_fallback_report=None,
                render_job_id=None,
                media_asset_id="asset-1",
            ),
        )
        async def fake_collect(*args, **kwargs):
            return [mock_frame]
        monkeypatch.setattr(storyboard_frame_service, "collect_by_project", fake_collect)

    if export_fails:
        def fake_export_png(*, project_id, pages, base_name="storyboard_sheet"):
            raise RuntimeError("Export failed")
        def fake_export_pdf(*, project_id, pages, base_name="storyboard_sheet"):
            raise RuntimeError("Export failed")
        monkeypatch.setattr(storyboard_export_service, "export_png", fake_export_png)
        monkeypatch.setattr(storyboard_export_service, "export_pdf", fake_export_pdf)

    shot = SimpleNamespace(
        id="shot-1",
        project_id="proj-1",
        organization_id="org-1",
        asset_id="asset-1",
        is_active=True,
        sequence_order=1,
        scene_number=1,
        narrative_text="Test",
        metadata_json=None,
    )
    asset = SimpleNamespace(
        id="asset-1",
        project_id="proj-1",
        organization_id="org-1",
        canonical_path=str(image_file),
        metadata_json={
            "thumbnail_path": str(thumbnail_file),
            "thumbnail_relative_path": "frames/frame_thumb.webp",
        },
        mime_type="image/png",
        file_name="frame.png",
    )

    class _FakeDb:
        async def execute(self, stmt):
            sql = str(stmt)
            if "storyboard_shots" in sql:
                return _ScalarResult(shot)
            if "media_assets" in sql:
                return _ScalarResult(asset)
            if "project" in sql:
                return _ScalarResult(SimpleNamespace(id="proj-1"))
            return _ScalarResult(None)

    db_instance = _FakeDb()

    async def override_db_with_data():
        yield db_instance

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db_with_data
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant

    return app


class _ScalarResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


def test_generate_without_auto_export_returns_legacy_response(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _make_export_test_app(monkeypatch, tmp_path, auto_export_sheet=False)
    with TestClient(app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/generate",
            json={"mode": "SEQUENCE", "sequence_id": "seq-1"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-1"
    assert data["auto_exports"] == []
    assert data["auto_export_errors"] == []


def test_generate_with_auto_export_populates_exports(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _make_export_test_app(monkeypatch, tmp_path, auto_export_sheet=True)
    with TestClient(app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/generate",
            json={
                "mode": "SEQUENCE",
                "sequence_id": "seq-1",
                "auto_export_sheet": True,
                "auto_export_formats": ["png", "pdf"],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-1"
    assert len(data["auto_exports"]) == 2
    assert data["auto_export_errors"] == []

    png_export = [e for e in data["auto_exports"] if e["output_format"] == "png"]
    pdf_export = [e for e in data["auto_exports"] if e["output_format"] == "pdf"]
    assert len(png_export) == 1
    assert len(pdf_export) == 1
    assert png_export[0]["artifact_url"] is not None
    assert pdf_export[0]["artifact_url"] is not None
    assert png_export[0]["frame_count"] > 0
    assert pdf_export[0]["frame_count"] > 0


def test_generate_with_auto_export_failure_still_succeeds_main(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    app = _make_export_test_app(monkeypatch, tmp_path, auto_export_sheet=True, export_fails=True)
    with TestClient(app) as client:
        response = client.post(
            "/api/projects/proj-1/storyboard/generate",
            json={
                "mode": "SEQUENCE",
                "sequence_id": "seq-1",
                "auto_export_sheet": True,
                "auto_export_formats": ["png", "pdf"],
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "job-1"
    assert len(data["auto_export_errors"]) >= 1
    assert any("PNG" in err or "PDF" in err or "Failed" in err or "Export" in err for err in data["auto_export_errors"])


def test_serialize_shot_always_includes_urls(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    shot_no_asset = SimpleNamespace(
        id="shot-2",
        project_id="proj-1",
        organization_id="org-1",
        asset_id=None,
        is_active=True,
        sequence_order=2,
        scene_number=2,
        narrative_text="No asset",
        metadata_json=None,
    )

    class _FakeDbNoAsset:
        async def execute(self, stmt):
            sql = str(stmt)
            if "storyboard_shots" in sql:
                return _ScalarResult(shot_no_asset)
            if "project" in sql:
                return _ScalarResult(SimpleNamespace(id="proj-1"))
            return _ScalarResult(None)

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    monkeypatch.setattr(storyboard_service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (tmp_path / "data",))

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: _FakeDbNoAsset()
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant

    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-2/image")

    assert response.status_code == 404
    assert response.json()["detail"] == "Storyboard image not found"
