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

os.environ.setdefault('AUTH_SECRET_KEY', 'a' * 32)
os.environ.setdefault('APP_SECRET_KEY', 'a' * 32)
os.environ.setdefault('AUTH_DISABLED', 'true')


class _FakeDb:
    def __init__(self):
        self.commits = 0
        self.refreshes = 0

    async def commit(self):
        self.commits += 1

    async def refresh(self, _project):
        self.refreshes += 1


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv('AUTH_DISABLED', 'true')
    monkeypatch.setenv('APP_ENV', 'development')
    from core.config import reload_settings
    reload_settings()


@pytest.fixture
def test_app():
    from core.app_factory import create_app
    return create_app()


def test_script_upload_endpoint_saves_script_text(test_app, monkeypatch: pytest.MonkeyPatch):
    from database import get_db
    from dependencies.tenant_context import get_tenant_context, TenantContext

    fake_db = _FakeDb()
    project = SimpleNamespace(id='proj-1', script_text=None)

    async def fake_get_project(*args, **kwargs):
        return project

    def fake_tenant():
        return TenantContext(user_id='u1', organization_id='org-1', role='admin', plan='free')

    async def override_db():
        yield fake_db

    monkeypatch.setattr('routes.project_routes._get_project_for_tenant_or_404', fake_get_project)

    test_app.dependency_overrides[get_db] = override_db
    test_app.dependency_overrides[get_tenant_context] = fake_tenant

    with TestClient(test_app) as client:
        response = client.post(
            '/api/projects/proj-1/script/upload',
            files={'file': ('script.txt', b'59 EXT/INT. PARKING/COCHE. DIA.\nMANU corre.\n', 'text/plain')},
        )

    test_app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body['project_id'] == 'proj-1'
    assert body['source_format'] == 'txt'
    assert body['ready_for_analysis'] is True
    assert project.script_text and '59 EXT/INT. PARKING/COCHE. DIA.' in project.script_text
    assert fake_db.commits == 1


def test_script_upload_endpoint_rejects_doc(test_app, monkeypatch: pytest.MonkeyPatch):
    from database import get_db
    from dependencies.tenant_context import get_tenant_context, TenantContext

    fake_db = _FakeDb()
    project = SimpleNamespace(id='proj-1', script_text=None)

    async def fake_get_project(*args, **kwargs):
        return project

    def fake_tenant():
        return TenantContext(user_id='u1', organization_id='org-1', role='admin', plan='free')

    async def override_db():
        yield fake_db

    monkeypatch.setattr('routes.project_routes._get_project_for_tenant_or_404', fake_get_project)

    test_app.dependency_overrides[get_db] = override_db
    test_app.dependency_overrides[get_tenant_context] = fake_tenant

    with TestClient(test_app) as client:
        response = client.post(
            '/api/projects/proj-1/script/upload',
            files={'file': ('script.doc', b'legacy', 'application/msword')},
        )

    test_app.dependency_overrides.clear()
    assert response.status_code == 400
    assert 'DOCX' in str(response.json()) and 'PDF' in str(response.json())
