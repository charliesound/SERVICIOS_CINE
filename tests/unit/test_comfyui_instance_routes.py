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
def _reset():
    from core.config import reload_settings

    reload_settings()
    from services.comfyui_instance_registry_service import registry

    registry._initialized = False
    registry.__init__()
    registry.load_instances()


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


class TestListInstances:
    @pytest.mark.asyncio
    async def test_list_instances_returns_five(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 5

    @pytest.mark.asyncio
    async def test_list_instances_has_expected_keys(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        body = resp.json()
        keys = {i["key"] for i in body}
        expected = {"image", "video_cine", "dubbing_audio", "restoration", "three_d"}
        assert keys == expected

    @pytest.mark.asyncio
    async def test_list_instances_json_valid(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        assert resp.headers["content-type"].startswith("application/json")

    @pytest.mark.asyncio
    async def test_list_instances_contains_required_fields(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances")
        body = resp.json()
        for inst in body:
            assert "key" in inst
            assert "name" in inst
            assert "base_url" in inst
            assert "port" in inst
            assert "enabled" in inst
            assert "task_types" in inst


class TestGetInstance:
    @pytest.mark.asyncio
    async def test_get_image_instance(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/image")
        assert resp.status_code == 200
        body = resp.json()
        assert body["key"] == "image"
        assert body["name"] == "Image"
        assert body["port"] == 8188

    @pytest.mark.asyncio
    async def test_get_video_cine_instance(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/video_cine")
        assert resp.status_code == 200
        body = resp.json()
        assert body["key"] == "video_cine"
        assert body["port"] == 8189

    @pytest.mark.asyncio
    async def test_get_dubbing_audio_instance(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/dubbing_audio")
        assert resp.status_code == 200
        body = resp.json()
        assert body["key"] == "dubbing_audio"
        assert body["port"] == 8190

    @pytest.mark.asyncio
    async def test_get_restoration_instance(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/restoration")
        assert resp.status_code == 200
        body = resp.json()
        assert body["key"] == "restoration"
        assert body["port"] == 8191

    @pytest.mark.asyncio
    async def test_get_three_d_instance(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/three_d")
        assert resp.status_code == 200
        body = resp.json()
        assert body["key"] == "three_d"
        assert body["port"] == 8192

    @pytest.mark.asyncio
    async def test_get_nonexistent_instance_returns_404(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/instances/nonexistent")
        assert resp.status_code == 404


class TestResolve:
    @pytest.mark.asyncio
    async def test_resolve_storyboard(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/storyboard")
        assert resp.status_code == 200
        body = resp.json()
        assert body["instance_key"] == "image"
        assert body["port"] == 8188

    @pytest.mark.asyncio
    async def test_resolve_i2v(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/i2v")
        assert resp.status_code == 200
        body = resp.json()
        assert body["instance_key"] == "video_cine"
        assert body["port"] == 8189

    @pytest.mark.asyncio
    async def test_resolve_lipsync(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/lipsync")
        assert resp.status_code == 200
        body = resp.json()
        assert body["instance_key"] == "dubbing_audio"
        assert body["port"] == 8190

    @pytest.mark.asyncio
    async def test_resolve_upscale(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/upscale")
        assert resp.status_code == 200
        body = resp.json()
        assert body["instance_key"] == "restoration"
        assert body["port"] == 8191

    @pytest.mark.asyncio
    async def test_resolve_mesh(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/mesh")
        assert resp.status_code == 200
        body = resp.json()
        assert body["instance_key"] == "three_d"
        assert body["port"] == 8192

    @pytest.mark.asyncio
    async def test_resolve_unknown_returns_404(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/resolve/nonexistent_xyz")
        assert resp.status_code == 404


class TestComfyUIHealth:
    @pytest.mark.asyncio
    async def test_health_endpoint_returns_json(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "total" in body
        assert "online" in body
        assert "offline" in body
        assert "instances" in body

    @pytest.mark.asyncio
    async def test_health_works_with_no_instances_running(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/comfyui/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 5
        assert "online" in body
        assert "offline" in body
        assert body["online"] + body["offline"] == 5


class TestInstanceHealth:
    @pytest.mark.asyncio
    async def test_instance_health_offline(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/instances/image/health"
            )
        assert resp.status_code == 200
        body = resp.json()
        assert "healthy" in body
        assert body["instance_key"] == "image"

    @pytest.mark.asyncio
    async def test_instance_health_unknown_key_returns_404(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/instances/nonexistent/health"
            )
        assert resp.status_code == 404


class TestLegacyHealth:
    @pytest.mark.asyncio
    async def test_health_live_still_works(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/live")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_ready_still_works(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/ready")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_startup_still_works(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health/startup")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_legacy_health_alias(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/health")
        assert resp.status_code == 200


class TestRequestId:
    @pytest.mark.asyncio
    async def test_request_id_in_error_response(self, test_app):
        from httpx import AsyncClient, ASGITransport

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/v1/comfyui/resolve/nonexistent_xyz",
                headers={"X-Request-ID": "cid-test-001"},
            )
        assert resp.status_code == 404
        body = resp.json()
        assert "error" in body
