from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")

from routes.auth_routes import get_tenant_context
from routes.integration_routes import router as integration_router
from schemas.auth_schema import TenantContext
from schemas.integration_schema import IntegrationEventPayload
from services.n8n_webhook_service import n8n_webhook_service


TEST_TENANT = TenantContext(
    user_id="user_test",
    organization_id="org_test",
    plan="enterprise",
    role="admin",
    is_admin=True,
    auth_method="test",
)


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


async def override_tenant() -> TenantContext:
    return TEST_TENANT


@pytest.fixture
def app() -> FastAPI:
    application = FastAPI()
    application.dependency_overrides[get_tenant_context] = override_tenant
    application.include_router(integration_router)
    return application


def test_n8n_service_disabled_returns_skipped_without_http_call(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("N8N_ENABLED", "false")
    from core.config import reload_settings

    reload_settings()

    def fail_client(*args, **kwargs):
        raise AssertionError("http client should not be created when n8n is disabled")

    monkeypatch.setattr("services.n8n_webhook_service.httpx.AsyncClient", fail_client)

    response = asyncio.run(
        n8n_webhook_service.send_test_event(
            IntegrationEventPayload(event_type="cid.integration.test", trace_id="trace-disabled")
        )
    )

    assert response.status == "skipped"
    assert response.sent is False
    assert response.trace_id == "trace-disabled"


def test_n8n_status_redacts_base_url_and_secret(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("N8N_ENABLED", "false")
    monkeypatch.setenv("N8N_BASE_URL", "http://user:secret@127.0.0.1:5678/private?token=abc")
    monkeypatch.setenv("N8N_WEBHOOK_SECRET", "super-secret")
    from core.config import reload_settings

    reload_settings()

    response = asyncio.run(n8n_webhook_service.get_status(trace_id="trace-status"))

    assert response.base_url == "http://127.0.0.1:5678"
    assert response.error is None
    dumped = response.model_dump_json()
    assert "secret" not in dumped
    assert "super-secret" not in dumped
    assert "token=abc" not in dumped


def test_n8n_service_handles_timeout_as_failed(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("N8N_ENABLED", "true")
    monkeypatch.setenv("N8N_BASE_URL", "http://127.0.0.1:5678")
    from core.config import reload_settings

    reload_settings()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, *args, **kwargs):
            raise httpx.TimeoutException("boom")

    monkeypatch.setattr("services.n8n_webhook_service.httpx.AsyncClient", lambda *args, **kwargs: FakeClient())

    response = asyncio.run(
        n8n_webhook_service.send_test_event(
            IntegrationEventPayload(event_type="cid.integration.test", trace_id="trace-timeout")
        )
    )

    assert response.status == "failed"
    assert response.sent is False
    assert "Timed out" in (response.error or "")


def test_n8n_test_route_returns_skipped_when_disabled(app: FastAPI, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("N8N_ENABLED", "false")
    from core.config import reload_settings

    reload_settings()

    with TestClient(app) as client:
        response = client.post(
            "/api/integrations/n8n/test",
            json={
                "event_type": "cid.integration.test",
                "project_id": "proj-1",
                "message": "hello",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "skipped"
    assert body["sent"] is False
