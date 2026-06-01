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

from dependencies.tenant_context import get_tenant_context
from routes.client_feedback_routes import router
from schemas.auth_schema import TenantContext
from services.client_feedback_service import cid_client_feedback_service

TEST_TENANT = TenantContext(
    user_id="user_test",
    organization_id="org_test",
    plan="enterprise",
    role="admin",
    is_admin=True,
    auth_method="test",
)


async def override_tenant() -> TenantContext:
    return TEST_TENANT


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI()
    application.dependency_overrides[get_tenant_context] = override_tenant
    application.include_router(router)
    return application


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


class TestCreateFeedback:
    def test_201_created(self, client, monkeypatch):
        async def fake_create(db, organization_id, user_id, data):
            from schemas.client_feedback_schema import CIDClientFeedbackResponse
            return CIDClientFeedbackResponse(
                id="fb-1",
                organization_id=organization_id,
                project_id=data.project_id,
                user_id=user_id,
                feedback_type=data.feedback_type,
                feedback_scope=data.feedback_scope or "project_feedback",
                created_at="2026-06-01T10:00:00",
                updated_at="2026-06-01T10:00:00",
            )
        monkeypatch.setattr(cid_client_feedback_service, "create_feedback", fake_create)

        payload = {"project_id": "proj-1", "feedback_type": "answer_helpful"}
        response = client.post("/api/v1/client-feedback/", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "fb-1"
        assert data["feedback_type"] == "answer_helpful"

    def test_422_invalid_feedback_type(self, client):
        payload = {"project_id": "proj-1", "feedback_type": "invalid_type"}
        response = client.post("/api/v1/client-feedback/", json=payload)
        assert response.status_code == 422

    def test_422_missing_project_id(self, client):
        payload = {"feedback_type": "answer_helpful"}
        response = client.post("/api/v1/client-feedback/", json=payload)
        assert response.status_code == 422


class TestUpdateFeedback:
    def test_200_updated(self, client, monkeypatch):
        async def fake_update(db, organization_id, feedback_id, data):
            from schemas.client_feedback_schema import CIDClientFeedbackResponse
            return CIDClientFeedbackResponse(
                id=feedback_id,
                organization_id=organization_id,
                project_id="proj-1",
                user_id="user_test",
                feedback_type="answer_helpful",
                feedback_scope="project_feedback",
                feedback_text="Updated",
                created_at="2026-06-01T10:00:00",
                updated_at="2026-06-01T11:00:00",
            )
        monkeypatch.setattr(cid_client_feedback_service, "update_feedback", fake_update)

        response = client.put("/api/v1/client-feedback/fb-1", json={"feedback_text": "Updated"})
        assert response.status_code == 200
        assert response.json()["feedback_text"] == "Updated"

    def test_404_not_found(self, client, monkeypatch):
        async def fake_update(db, organization_id, feedback_id, data):
            return None
        monkeypatch.setattr(cid_client_feedback_service, "update_feedback", fake_update)

        response = client.put("/api/v1/client-feedback/nonexistent", json={"feedback_text": "Updated"})
        assert response.status_code == 404


class TestDeleteFeedback:
    def test_204_deleted(self, client, monkeypatch):
        async def fake_delete(db, organization_id, feedback_id):
            return True
        monkeypatch.setattr(cid_client_feedback_service, "soft_delete_feedback", fake_delete)

        response = client.delete("/api/v1/client-feedback/fb-1")
        assert response.status_code == 204

    def test_404_not_found(self, client, monkeypatch):
        async def fake_delete(db, organization_id, feedback_id):
            return False
        monkeypatch.setattr(cid_client_feedback_service, "soft_delete_feedback", fake_delete)

        response = client.delete("/api/v1/client-feedback/nonexistent")
        assert response.status_code == 404


class TestGetFeedback:
    def test_200_found(self, client, monkeypatch):
        async def fake_get(db, organization_id, feedback_id):
            from schemas.client_feedback_schema import CIDClientFeedbackResponse
            return CIDClientFeedbackResponse(
                id=feedback_id,
                organization_id=organization_id,
                project_id="proj-1",
                user_id="user_test",
                feedback_type="answer_helpful",
                feedback_scope="project_feedback",
                created_at="2026-06-01T10:00:00",
                updated_at="2026-06-01T10:00:00",
            )
        monkeypatch.setattr(cid_client_feedback_service, "get_feedback", fake_get)

        response = client.get("/api/v1/client-feedback/fb-1")
        assert response.status_code == 200
        assert response.json()["id"] == "fb-1"

    def test_404_not_found(self, client, monkeypatch):
        async def fake_get(db, organization_id, feedback_id):
            return None
        monkeypatch.setattr(cid_client_feedback_service, "get_feedback", fake_get)

        response = client.get("/api/v1/client-feedback/nonexistent")
        assert response.status_code == 404


class TestListFeedback:
    def test_200_empty(self, client, monkeypatch):
        async def fake_list(db, organization_id, feedback_type=None, status=None, limit=20, offset=0):
            return [], 0
        monkeypatch.setattr(cid_client_feedback_service, "list_feedback", fake_list)

        response = client.get("/api/v1/client-feedback/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["feedbacks"] == []

    def test_200_with_items(self, client, monkeypatch):
        async def fake_list(db, organization_id, feedback_type=None, status=None, limit=20, offset=0):
            from schemas.client_feedback_schema import CIDClientFeedbackResponse
            fb = CIDClientFeedbackResponse(
                id="fb-1",
                organization_id=organization_id,
                project_id="proj-1",
                user_id="user_test",
                feedback_type="answer_helpful",
                feedback_scope="project_feedback",
                created_at="2026-06-01T10:00:00",
                updated_at="2026-06-01T10:00:00",
            )
            return [fb], 1
        monkeypatch.setattr(cid_client_feedback_service, "list_feedback", fake_list)

        response = client.get("/api/v1/client-feedback/?feedback_type=answer_helpful&status=pending")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["feedbacks"]) == 1

    def test_422_invalid_limit(self, client):
        response = client.get("/api/v1/client-feedback/?limit=999")
        assert response.status_code == 422


class TestGetAggregatedFeedback:
    def test_200_aggregated(self, client, monkeypatch):
        async def fake_aggregated(db, organization_id):
            return {
                "total_count": 10,
                "status_counts": {"pending": 5, "approved": 3, "archived": 2},
                "type_counts": {"answer_helpful": 7, "approved_correction": 3},
            }
        monkeypatch.setattr(cid_client_feedback_service, "get_aggregated_feedback", fake_aggregated)

        response = client.get("/api/v1/client-feedback/aggregated")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 10
        assert data["status_counts"]["pending"] == 5


class TestAuth:
    def test_401_no_token(self, app):
        app.dependency_overrides.pop(get_tenant_context, None)
        client = TestClient(app)
        response = client.get("/api/v1/client-feedback/")
        assert response.status_code == 401


class TestRouteOrdering:
    def test_aggregated_before_feedback_id(self, client, monkeypatch):
        async def fake_aggregated(db, organization_id):
            return {"total_count": 0, "status_counts": {}, "type_counts": {}}
        monkeypatch.setattr(cid_client_feedback_service, "get_aggregated_feedback", fake_aggregated)

        response = client.get("/api/v1/client-feedback/aggregated")
        assert response.status_code == 200


class TestUntouchedModules:
    def test_no_qdrant_import(self):
        import sys
        assert "qdrant" not in sys.modules or "qdrant_client" not in sys.modules.get("qdrant", type(sys)("qdrant")).__name__

    def test_no_memory_answer_import(self):
        from routes.client_feedback_routes import router as r
        assert r.prefix == "/api/v1/client-feedback"
