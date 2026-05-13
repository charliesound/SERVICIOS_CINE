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
os.environ.setdefault("JWT_SECRET", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")
os.environ.setdefault("HEALTHCHECK_REDIS_ENABLED", "false")


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "false")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


TOKEN_PAYLOAD = {
    "sub": "test-user",
    "roles": ["admin"],
    "scopes": ["comfyui:read", "comfyui:health", "admin:read", "admin:write"],
    "organization_id": "test-org",
}


def _valid_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token(TOKEN_PAYLOAD)


class TestComfyUIEndpointsProtected:
    @pytest.mark.asyncio
    async def test_instances_without_token_returns_401(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_instances_with_valid_token_returns_200(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/instances",
                headers={"Authorization": f"Bearer {_valid_token()}"},
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_resolve_without_token_returns_401(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/storyboard")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_resolve_with_valid_token_returns_200(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/resolve/storyboard",
                headers={"Authorization": f"Bearer {_valid_token()}"},
            )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_summary_without_token_returns_401(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/health")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_instance_detail_without_token_returns_401(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/image")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_instance_health_without_token_returns_401(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/image/health")
        assert resp.status_code == 401


class TestHealthEndpointsPublic:
    @pytest.mark.asyncio
    async def test_health_live_is_public(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_ready_is_public(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/ready")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_startup_is_public(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/startup")
        assert resp.status_code == 200


class TestInvalidToken:
    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, test_app):
        from datetime import datetime, timedelta
        from jose import jwt
        from routes.auth_routes import _get_secret_key

        expired_token = jwt.encode(
            {
                "sub": "user",
                "exp": datetime.utcnow() - timedelta(hours=1),
                "iat": datetime.utcnow() - timedelta(hours=2),
                "nbf": datetime.utcnow() - timedelta(hours=2),
                "iss": "ailinkcinema",
                "aud": "cid-api",
            },
            _get_secret_key(),
            algorithm="HS256",
        )
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/instances",
                headers={"Authorization": f"Bearer {expired_token}"},
            )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_issuer_returns_401(self, test_app):
        from datetime import datetime, timedelta
        from jose import jwt
        from routes.auth_routes import _get_secret_key

        bad_token = jwt.encode(
            {
                "sub": "user",
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "nbf": datetime.utcnow(),
                "iss": "evil-issuer",
                "aud": "cid-api",
            },
            _get_secret_key(),
            algorithm="HS256",
        )
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/instances",
                headers={"Authorization": f"Bearer {bad_token}"},
            )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_no_sensitive_detail_in_auth_error(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        body = resp.json()
        body_str = str(body).lower()
        assert resp.status_code == 401
        assert "invalid" in body_str or "missing" in body_str or "error" in body_str
