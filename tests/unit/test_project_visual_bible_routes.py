from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")


class _FakeVisualBible:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class _FakeDbExecuteResult:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows or []

    def scalar_one_or_none(self):
        return self._row

    def scalars(self):
        return self

    def first(self):
        return self._row

    def all(self):
        return self._rows


class _FakeDb:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.refreshes = 0
        self._execute_map = {}

    def set_execute(self, key, result):
        self._execute_map[key] = result

    async def execute(self, stmt):
        # Check if it's a Project query or VisualBible query based on the SQL
        sql_str = str(stmt)
        if "projects" in sql_str and "project_visual_bibles" not in sql_str:
            return self._execute_map.get("project", _FakeDbExecuteResult())
        if "project_visual_bibles" in sql_str:
            return self._execute_map.get("vb", _FakeDbExecuteResult())
        return _FakeDbExecuteResult()

    async def commit(self):
        self.commits += 1

    async def refresh(self, obj):
        self.refreshes += 1
        if not hasattr(obj, "id"):
            obj.id = "vb-fake-id-1"

    def add(self, obj):
        self.added.append(obj)


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture(autouse=True)
def _reset_taxonomy_service():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    CinematicTaxonomyService._instance = None


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


class TestGetVisualBibleEndpoint:
    def test_get_returns_visual_bible(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_vb = _FakeVisualBible(
            id="vb-1",
            project_id="proj-1",
            organization_id="org-1",
            active_preset_id=None,
            selected_elements_json={},
            custom_prompt_tags_json=[],
            negative_prompt_tags_json=[],
            director_notes=None,
            prompt_mode="tag_soup",
            target_model="SDXL",
            is_active=True,
            created_by=None,
            created_at=None,
            updated_at=None,
        )
        fake_project = SimpleNamespace(
            id="proj-1", organization_id="org-1", name="Test"
        )
        fake_db.set_execute("project", _FakeDbExecuteResult(row=fake_project))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=fake_vb))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-1", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.get("/api/projects/proj-1/visual-bible")

        test_app.dependency_overrides.clear()
        assert response.status_code == 200
        body = response.json()
        assert body["project_id"] == "proj-1"
        assert body["prompt_mode"] == "tag_soup"

    def test_get_project_not_found(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_db.set_execute("project", _FakeDbExecuteResult(row=None))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=None))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-other", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.get("/api/projects/proj-1/visual-bible")

        test_app.dependency_overrides.clear()
        assert response.status_code == 404


class TestUpdateVisualBibleEndpoint:
    def test_update_active_preset(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_vb = _FakeVisualBible(
            id="vb-1",
            project_id="proj-1",
            organization_id="org-1",
            active_preset_id=None,
            selected_elements_json={},
            custom_prompt_tags_json=[],
            negative_prompt_tags_json=[],
            director_notes=None,
            prompt_mode="tag_soup",
            target_model="SDXL",
            is_active=True,
            created_by=None,
            created_at=None,
            updated_at=None,
        )
        fake_project = SimpleNamespace(
            id="proj-1", organization_id="org-1", name="Test"
        )
        fake_db.set_execute("project", _FakeDbExecuteResult(row=fake_project))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=fake_vb))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-1", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.put(
                "/api/projects/proj-1/visual-bible",
                json={"active_preset_id": "noir_classic"},
            )

        test_app.dependency_overrides.clear()
        assert response.status_code == 200

    def test_update_rejects_fake_preset(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_vb = _FakeVisualBible(
            id="vb-1",
            project_id="proj-1",
            organization_id="org-1",
            active_preset_id=None,
            selected_elements_json={},
            custom_prompt_tags_json=[],
            negative_prompt_tags_json=[],
            director_notes=None,
            prompt_mode="tag_soup",
            target_model="SDXL",
            is_active=True,
            created_by=None,
            created_at=None,
            updated_at=None,
        )
        fake_project = SimpleNamespace(
            id="proj-1", organization_id="org-1", name="Test"
        )
        fake_db.set_execute("project", _FakeDbExecuteResult(row=fake_project))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=fake_vb))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-1", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.put(
                "/api/projects/proj-1/visual-bible",
                json={"active_preset_id": "fake_preset_999"},
            )

        test_app.dependency_overrides.clear()
        assert response.status_code == 400


class TestResetVisualBibleEndpoint:
    def test_reset_clears_config(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_vb = _FakeVisualBible(
            id="vb-1",
            project_id="proj-1",
            organization_id="org-1",
            active_preset_id="noir_classic",
            selected_elements_json={"shot_types": ["cu"]},
            custom_prompt_tags_json=["custom tag"],
            negative_prompt_tags_json=[],
            director_notes="Some notes",
            prompt_mode="semantic_t5",
            target_model="Flux",
            is_active=True,
            created_by=None,
            created_at=None,
            updated_at=None,
        )
        fake_project = SimpleNamespace(
            id="proj-1", organization_id="org-1", name="Test"
        )
        fake_db.set_execute("project", _FakeDbExecuteResult(row=fake_project))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=fake_vb))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-1", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.post("/api/projects/proj-1/visual-bible/reset")

        test_app.dependency_overrides.clear()
        assert response.status_code == 200


class TestPreviewPromptEndpoint:
    def test_preview_returns_enriched_prompt(self, test_app, monkeypatch):
        from database import get_db
        from dependencies.tenant_context import get_tenant_context, TenantContext

        fake_db = _FakeDb()
        fake_vb = _FakeVisualBible(
            id="vb-1",
            project_id="proj-1",
            organization_id="org-1",
            active_preset_id="noir_classic",
            selected_elements_json={},
            custom_prompt_tags_json=[],
            negative_prompt_tags_json=[],
            director_notes=None,
            prompt_mode="tag_soup",
            target_model="SDXL",
            is_active=True,
            created_by=None,
            created_at=None,
            updated_at=None,
        )
        fake_project = SimpleNamespace(
            id="proj-1", organization_id="org-1", name="Test"
        )
        fake_db.set_execute("project", _FakeDbExecuteResult(row=fake_project))
        fake_db.set_execute("vb", _FakeDbExecuteResult(row=fake_vb))

        async def override_db():
            yield fake_db

        def fake_tenant():
            return TenantContext(
                user_id="u1", organization_id="org-1", role="admin", plan="free"
            )

        test_app.dependency_overrides[get_db] = override_db
        test_app.dependency_overrides[get_tenant_context] = fake_tenant

        with TestClient(test_app) as client:
            response = client.post(
                "/api/projects/proj-1/visual-bible/preview-prompt",
                json={"base_prompt": "A detective in the rain"},
            )

        test_app.dependency_overrides.clear()
        assert response.status_code == 200
        body = response.json()
        assert body["base_prompt"] == "A detective in the rain"
        assert body["enriched_prompt"].startswith("A detective in the rain")
        assert body["applied_preset"]["id"] == "noir_classic"
        assert body["visual_bible_id"] == "vb-1"
