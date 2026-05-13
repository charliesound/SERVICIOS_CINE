from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")

os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")
os.environ.setdefault("HEALTHCHECK_REDIS_ENABLED", "false")


@pytest.fixture(autouse=True)
def _reset_settings():
    from core.config import reload_settings

    reload_settings()


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    app = create_app()
    return app


@pytest.mark.asyncio
async def test_health_live_returns_200(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/live")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "request_id" in body


@pytest.mark.asyncio
async def test_health_startup_returns_200(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/startup")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "registered_routers" in body
    assert body["startup_ok"] is True


@pytest.mark.asyncio
async def test_health_ready_returns_200_when_ok(test_app):
    """All dependencies OK → 200 + status ok."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "checks" in body
    assert "request_id" in body


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_critical_dep_fails(monkeypatch):
    """Critical dependency failing → 503."""
    monkeypatch.setenv("HEALTHCHECK_REDIS_ENABLED", "true")
    monkeypatch.setenv("REDIS_URL", "127.0.0.1")

    from core.config import reload_settings

    reload_settings()
    from core.app_factory import create_app

    app = create_app()

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/ready")
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_health_ready_returns_503_when_degraded(monkeypatch):
    """Degraded status → 503 + request_id."""
    monkeypatch.setenv("HEALTHCHECK_REDIS_ENABLED", "true")
    monkeypatch.setenv("REDIS_URL", "127.0.0.1")

    from core.config import reload_settings

    reload_settings()
    from core.app_factory import create_app

    app = create_app()

    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/ready")
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "degraded"
    assert "request_id" in body
    assert "checks" in body


@pytest.mark.asyncio
async def test_health_ready_contains_request_id(test_app):
    """Body always contains a request_id."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/ready")
    body = resp.json()
    assert "request_id" in body
    assert isinstance(body["request_id"], str)
    assert len(body["request_id"]) > 0


@pytest.mark.asyncio
async def test_health_ready_respects_custom_x_request_id(test_app):
    """Custom X-Request-ID header is echoed in response body and header."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    custom_rid = "cid-test-001"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/health/ready", headers={"X-Request-ID": custom_rid}
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["request_id"] == custom_rid
    assert resp.headers.get("X-Request-ID") == custom_rid


@pytest.mark.asyncio
async def test_legacy_health_alias_works(test_app):
    """The original /health endpoint must still respond."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_legacy_ready_alias_works(test_app):
    """The original /ready endpoint must still respond."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/ready")
    assert resp.status_code in (200, 503)
    body = resp.json()
    assert "status" in body
