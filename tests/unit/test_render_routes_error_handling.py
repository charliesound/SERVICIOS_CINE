import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from enum import Enum

from app import app
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext


class MockStatus(Enum):
    FAILED = "failed"


class MockResponse:
    def __init__(self, status, error=None):
        self.status = status
        self.error = error
        self.job_id = "test_job_id"
        self.backend = "test_backend"
        self.queue_position = 0
        self.estimated_time = 0


def _response_text(response):
    return str(response.json()).lower()


@pytest.fixture
def override_auth():
    def mock_tenant():
        return TenantContext(
            user_id="test_user",
            organization_id="test_org",
            role="admin",
            plan="enterprise",
        )
    app.dependency_overrides[get_tenant_context] = mock_tenant
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_auth):
    return TestClient(app)


def test_render_routes_failed_job_no_queue_item(client):
    with patch(
        "routes.render_routes.render_job_service.submit_job",
        new_callable=AsyncMock
    ) as mock_submit:
        # Mocking submit_job to return (failed_response, None)
        mock_response = MockResponse(status=MockStatus.FAILED, error="Backend unavailable")
        mock_submit.return_value = (mock_response, None)

        payload = {
            "user_id": "test_user",
            "user_plan": "enterprise",
            "task_type": "still",
            "workflow_key": "test_workflow",
            "prompt": {"test": "prompt"},
            "project_id": "test_project",
            "priority": 5,
            "parameters": {"prompt": "test prompt"}
        }
        
        response = client.post("/api/render/jobs", json=payload)
        
        # Debe responder controladamente, en este caso 503 por contener "unavailable" o "backend"
        assert response.status_code == 503
        assert "backend unavailable" in _response_text(response)


def test_render_routes_failed_job_plan_not_allowed(client):
    with patch(
        "routes.render_routes.render_job_service.submit_job",
        new_callable=AsyncMock
    ) as mock_submit:
        mock_response = MockResponse(status=MockStatus.FAILED, error="plan not allowed")
        mock_submit.return_value = (mock_response, None)

        payload = {
            "user_id": "test_user",
            "user_plan": "enterprise",
            "task_type": "still",
            "workflow_key": "test_workflow",
            "prompt": {"test": "prompt"},
            "project_id": "test_project",
            "priority": 5,
            "parameters": {"prompt": "test prompt"}
        }
        
        response = client.post("/api/render/jobs", json=payload)
        
        assert response.status_code == 403
        body = _response_text(response)
        assert "plan" in body
        assert "not allowed" in body


def test_render_routes_failed_job_generic_error(client):
    with patch(
        "routes.render_routes.render_job_service.submit_job",
        new_callable=AsyncMock
    ) as mock_submit:
        mock_response = MockResponse(status=MockStatus.FAILED, error="Some generic error")
        mock_submit.return_value = (mock_response, None)

        payload = {
            "user_id": "test_user",
            "user_plan": "enterprise",
            "task_type": "still",
            "workflow_key": "test_workflow",
            "prompt": {"test": "prompt"},
            "project_id": "test_project",
            "priority": 5,
            "parameters": {"prompt": "test prompt"}
        }
        
        response = client.post("/api/render/jobs", json=payload)
        
        assert response.status_code == 422
        assert "some generic error" in _response_text(response)
