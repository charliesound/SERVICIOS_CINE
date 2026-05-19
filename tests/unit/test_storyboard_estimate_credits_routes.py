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
    pass


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


def test_estimate_credits_counts_coverage_and_filters_sequence_ids(test_app, monkeypatch: pytest.MonkeyPatch):
    from database import get_db
    from routes.auth_routes import get_tenant_context
    from schemas.auth_schema import TenantContext

    async def fake_get_project(*args, **kwargs):
        return SimpleNamespace(id='proj-1', script_text='script')

    async def fake_get_analysis_payload(*args, **kwargs):
        return {
            'scenes': [
                {'scene_number': 59},
                {'scene_number': 60},
                {'scene_number': 61},
                {'scene_number': 70},
            ],
            'sequences': [
                {'sequence_id': 'seq_001', 'sequence_number': 1, 'title': 'Secuencia 1', 'summary': '', 'included_scenes': [59, 60, 61]},
                {'sequence_id': 'seq_002', 'sequence_number': 2, 'title': 'Secuencia 2', 'summary': '', 'included_scenes': [70]},
            ],
        }

    def fake_tenant():
        return TenantContext(user_id='u1', organization_id='org-1', role='admin', plan='free')

    async def override_db():
        yield _FakeDb()

    monkeypatch.setattr('routes.storyboard_routes.storyboard_service._get_project_for_tenant', fake_get_project)
    monkeypatch.setattr('routes.storyboard_routes.storyboard_service._get_analysis_payload', fake_get_analysis_payload)

    test_app.dependency_overrides[get_db] = override_db
    test_app.dependency_overrides[get_tenant_context] = fake_tenant

    with TestClient(test_app) as client:
        response = client.post('/api/projects/proj-1/storyboard/estimate-credits', json={
            'mode': 'SEQUENCE',
            'sequence_ids': ['seq_001'],
            'shots_per_scene': 3,
            'include_coverage_shots': True,
            'style_preset': 'hand_drawn_storyboard',
        })

    test_app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body['estimated_scenes'] == 3
    assert body['base_shots'] == 9
    assert body['coverage_shots'] == 6
    assert body['total_estimated_shots'] == 15
    assert body['credits']['script_analysis'] == 1
    assert body['credits']['prompt_generation'] == 3
    assert body['credits']['image_render'] == 15
    assert body['credits']['total'] == 19


def test_estimate_credits_nonexistent_sequence_does_not_use_global_scenes(test_app, monkeypatch: pytest.MonkeyPatch):
    from database import get_db
    from routes.auth_routes import get_tenant_context
    from schemas.auth_schema import TenantContext

    async def fake_get_project(*args, **kwargs):
        return SimpleNamespace(id='proj-1', script_text='script')

    async def fake_get_analysis_payload(*args, **kwargs):
        return {
            'scenes': [{'scene_number': 59}, {'scene_number': 60}, {'scene_number': 61}],
            'sequences': [
                {'sequence_id': 'seq_001', 'sequence_number': 1, 'title': 'Secuencia 1', 'summary': '', 'included_scenes': [59, 60, 61]},
            ],
        }

    def fake_tenant():
        return TenantContext(user_id='u1', organization_id='org-1', role='admin', plan='free')

    async def override_db():
        yield _FakeDb()

    monkeypatch.setattr('routes.storyboard_routes.storyboard_service._get_project_for_tenant', fake_get_project)
    monkeypatch.setattr('routes.storyboard_routes.storyboard_service._get_analysis_payload', fake_get_analysis_payload)

    test_app.dependency_overrides[get_db] = override_db
    test_app.dependency_overrides[get_tenant_context] = fake_tenant

    with TestClient(test_app) as client:
        response = client.post('/api/projects/proj-1/storyboard/estimate-credits', json={
            'mode': 'SEQUENCE',
            'sequence_ids': ['seq_002'],
            'shots_per_scene': 3,
            'include_coverage_shots': True,
            'style_preset': 'hand_drawn_storyboard',
        })

    test_app.dependency_overrides.clear()
    assert response.status_code == 200
    body = response.json()
    assert body['estimated_scenes'] == 0
    assert body['credits']['total'] == 0
    assert any('Secuencias no encontradas' in note for note in body['notes'])
