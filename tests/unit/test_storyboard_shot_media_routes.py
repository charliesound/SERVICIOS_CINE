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


class _ScalarResult:
    def __init__(self, row):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _FakeDb:
    def __init__(self, *, shot, asset):
        self.shot = shot
        self.asset = asset

    async def execute(self, stmt):
        sql = str(stmt)
        if "storyboard_shots" in sql:
            return _ScalarResult(self.shot)
        if "media_assets" in sql:
            return _ScalarResult(self.asset)
        return _ScalarResult(None)


@pytest.fixture
def test_app(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> FastAPI:
    image_path = tmp_path / "data" / "output" / "frames" / "shot.png"
    image_path.parent.mkdir(parents=True, exist_ok=True)
    image_path.write_bytes(b"image-bytes")

    thumbnail_path = tmp_path / "data" / "output" / "frames" / "shot_thumb.webp"
    thumbnail_path.write_bytes(b"thumb-bytes")

    shot = SimpleNamespace(
        id="shot-1",
        project_id="proj-1",
        organization_id="org-1",
        asset_id="asset-1",
        is_active=True,
    )
    asset = SimpleNamespace(
        id="asset-1",
        project_id="proj-1",
        organization_id="org-1",
        canonical_path=str(image_path),
        metadata_json={
            "thumbnail_path": str(thumbnail_path),
            "thumbnail_relative_path": "frames/shot_thumb.webp",
        },
        mime_type="image/png",
        file_name="shot.png",
    )
    fake_db = _FakeDb(shot=shot, asset=asset)

    async def override_db():
        yield fake_db

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant
    monkeypatch.setattr(storyboard_service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (tmp_path / "data",))
    return app


def test_storyboard_shot_image_endpoint_returns_200(test_app: FastAPI) -> None:
    with TestClient(test_app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-1/image")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")


def test_storyboard_shot_thumbnail_endpoint_uses_thumbnail_if_available(test_app: FastAPI) -> None:
    with TestClient(test_app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-1/thumbnail")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/webp")


def test_storyboard_shot_image_endpoint_returns_404_when_asset_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    async def override_db():
        yield _FakeDb(shot=None, asset=None)

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant
    monkeypatch.setattr(storyboard_service, "_get_project_for_tenant", fake_get_project_for_tenant)

    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-1/image")

    assert response.status_code == 404


def test_storyboard_shot_image_endpoint_blocks_outside_allowed_roots(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    outside_file = tmp_path / "outside" / "shot.png"
    outside_file.parent.mkdir(parents=True, exist_ok=True)
    outside_file.write_bytes(b"image-bytes")

    shot = SimpleNamespace(
        id="shot-1",
        project_id="proj-1",
        organization_id="org-1",
        asset_id="asset-1",
        is_active=True,
    )
    asset = SimpleNamespace(
        id="asset-1",
        project_id="proj-1",
        organization_id="org-1",
        canonical_path=str(outside_file),
        metadata_json={},
        mime_type="image/png",
        file_name="shot.png",
    )

    async def override_db():
        yield _FakeDb(shot=shot, asset=asset)

    def override_tenant():
        return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_tenant_context] = override_tenant
    app.dependency_overrides[deps_get_tenant_context] = override_tenant
    monkeypatch.setattr(storyboard_service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(storyboard_frame_service, "_ALLOWED_DATA_ROOTS", (tmp_path / "data",))

    with TestClient(app) as client:
        response = client.get("/api/projects/proj-1/storyboard/shots/shot-1/image")

    assert response.status_code == 404
