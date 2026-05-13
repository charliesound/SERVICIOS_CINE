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


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


@pytest.mark.asyncio
async def test_request_id_generated_if_not_sent(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/live")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    rid = resp.headers["X-Request-ID"]
    assert len(rid) == 32  # uuid4 hex


@pytest.mark.asyncio
async def test_request_id_respected_if_sent(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/health/live",
            headers={"X-Request-ID": "custom-request-123"},
        )
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == "custom-request-123"


@pytest.mark.asyncio
async def test_request_id_available_in_request_state(test_app):
    """If request_id is correctly stored in request.state, health endpoint exposes it."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/health/live",
            headers={"X-Request-ID": "state-test-456"},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["request_id"] == "state-test-456"
