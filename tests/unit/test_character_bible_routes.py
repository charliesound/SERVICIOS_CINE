from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")

from dependencies.tenant_context import get_tenant_context, TenantContext
from routes.character_bible_routes import router as character_bible_router


def _get_db_dependency():
    """Lazy import to avoid triggering database model loading at import time."""
    from database import get_db
    return get_db


TEST_TENANT = TenantContext(
    user_id="user_test",
    organization_id="org_test",
    plan="enterprise",
    role="admin",
    is_admin=True,
    auth_method="test",
)


class _FakeResult:
    def __init__(self, row=None):
        self._row = row

    def scalar_one_or_none(self):
        return self._row


class _FakeDb:
    def __init__(self, project_exists: bool = True):
        self.project_exists = project_exists

    async def execute(self, stmt):
        sql_str = str(stmt)
        if "projects" in sql_str and self.project_exists:
            return _FakeResult(row=object())
        return _FakeResult(row=None)


async def override_db():
    yield _FakeDb(project_exists=True)


async def override_db_no_project():
    yield _FakeDb(project_exists=False)


async def override_tenant() -> TenantContext:
    return TEST_TENANT


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI()
    application.dependency_overrides[get_tenant_context] = override_tenant
    application.include_router(character_bible_router)
    return application


get_db = _get_db_dependency()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestCharacterBibleRoutes:
    def test_list_empty(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.get("/api/projects/proj_test_01/character-bible")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["entries"] == []

    def test_create_entry(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={
                "character_id": "char_marta",
                "character_name": "Marta",
                "wardrobe_notes": "Jeans oscuros",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char_marta"
        assert data["project_id"] == "proj_test_01"
        assert data["character_name"] == "Marta"
        assert data["version"] == 1

    def test_create_and_get_entry(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.get(
            "/api/projects/proj_test_01/character-bible/char_marta"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["character_name"] == "Marta"

    def test_get_nonexistent_entry(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.get(
            "/api/projects/proj_test_01/character-bible/char_ghost"
        )
        assert response.status_code == 404

    def test_list_after_create(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.get("/api/projects/proj_test_01/character-bible")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1

    def test_add_look_variant(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/look-variants",
            json={
                "look_id": "look_night",
                "look_name": "Night Entrance",
                "wardrobe_notes": "Dark clothes",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["look_id"] == "look_night"

    def test_add_look_variant_nonexistent_character(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_ghost/look-variants",
            json={"look_id": "l1", "look_name": "L1"},
        )
        assert response.status_code == 404

    def test_add_reference(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/references",
            json={
                "asset_id": "asset_face_v2",
                "asset_type": "face_sheet",
                "asset_api_url": "/api/assets/face_v2.png",
                "is_primary": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["asset_id"] == "asset_face_v2"

    def test_add_reference_empty_asset_id(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/references",
            json={"asset_id": "", "asset_type": "face_sheet"},
        )
        assert response.status_code == 400

    def test_add_reference_invalid_path_in_asset_id(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/references",
            json={"asset_id": "../etc/passwd", "asset_type": "face_sheet"},
        )
        assert response.status_code == 400

    def test_resolve_character(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/resolve",
            json={"project_id": "proj_test_01", "character_id": "char_marta"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char_marta"

    def test_resolve_nonexistent(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_ghost/resolve",
            json={"project_id": "proj_test_01", "character_id": "char_ghost"},
        )
        assert response.status_code == 404

    def test_resolve_mismatched_project_id(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.post(
            "/api/projects/proj_test_01/character-bible/char_marta/resolve",
            json={"project_id": "wrong_project", "character_id": "char_marta"},
        )
        assert response.status_code == 400

    def test_get_trace(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.get(
            "/api/projects/proj_test_01/character-bible/char_marta/trace"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["character_id"] == "char_marta"
        assert "trace_metadata" in data

    def test_trace_nonexistent(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        response = client.get(
            "/api/projects/proj_test_01/character-bible/char_ghost/trace"
        )
        assert response.status_code == 404

    def test_project_not_found(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db_no_project
        response = client.get(
            "/api/projects/proj_nonexistent/character-bible"
        )
        assert response.status_code == 404

    def test_no_absolute_paths_in_response(self, client):
        app = client.app
        app.dependency_overrides[get_db] = override_db
        client.put(
            "/api/projects/proj_test_01/character-bible/char_marta",
            json={"character_id": "char_marta", "character_name": "Marta"},
        )
        response = client.get(
            "/api/projects/proj_test_01/character-bible/char_marta"
        )
        text = response.text
        assert "/opt/" not in text
        assert "/mnt/" not in text
        assert "C:" not in text



