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


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


class TestSecurityHeadersPresent:
    @pytest.mark.asyncio
    async def test_x_content_type_options_present(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options_present(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_referrer_policy_present(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.headers.get("referrer-policy") == "no-referrer"

    @pytest.mark.asyncio
    async def test_permissions_policy_present(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.headers.get("permissions-policy") == "camera=(), microphone=(), geolocation=()"

    @pytest.mark.asyncio
    async def test_security_headers_on_all_endpoints(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/ready")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_cors_still_works_with_security_headers(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options(
                "/health/live",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
            )
        security_ok = resp.headers.get("x-content-type-options") == "nosniff"
        cors_ok = resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert security_ok and cors_ok
