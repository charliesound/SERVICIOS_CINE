from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ["AUTH_SECRET_KEY"] = "a" * 32
os.environ["APP_SECRET_KEY"] = "a" * 32
os.environ["JWT_SECRET"] = "a" * 32
os.environ["AUTH_DISABLED"] = "true"

SMOKE_ORG_A = "db4d7a5dadc9457ebaa2993a30d48201"
SMOKE_ORG_B = "54c10f417b714c558dc6da6015a96cc3"
SMOKE_TENANT_A_USER_ID = "4b153c715f76428b9e299698e5ab5561"
SMOKE_PROJECT_ID = "32fb858f66ef4569a7bc12db3b5ef2fd"


def _tenant_a_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": SMOKE_TENANT_A_USER_ID,
        "organization_id": SMOKE_ORG_A,
        "roles": ["admin"],
        "scopes": ["projects:read", "projects:write", "comfyui:read", "comfyui:health"],
    })


def _tenant_b_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": "tenant-b-user",
        "organization_id": SMOKE_ORG_B,
        "roles": ["viewer"],
        "scopes": ["projects:read", "comfyui:read"],
    })


def _tenant_b_admin_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": "tenant-b-admin",
        "organization_id": SMOKE_ORG_B,
        "roles": ["admin"],
        "scopes": ["projects:read", "projects:write", "comfyui:read", "comfyui:health"],
    })


def _tenant_b_producer_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": "tenant-b-producer",
        "organization_id": SMOKE_ORG_B,
        "roles": ["producer"],
        "scopes": ["projects:read", "projects:write", "comfyui:read"],
    })


@pytest.fixture(scope="module")
def test_app():
    from core.app_factory import create_app

    return create_app()


@pytest.mark.asyncio
async def test_tenant_a_can_access_own_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/v1/comfyui/instances",
            headers={"Authorization": f"Bearer {_tenant_a_token()}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_tenant_b_cannot_access_tenant_a_project_documents(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_b_token()}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_tenant_b_cannot_trigger_matcher_for_tenant_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/trigger"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_b_token()}"},
            json={},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_health_still_public(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/live")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_comfyui_without_token_still_protected(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/comfyui/instances")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_nonexistent_project_returns_404(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/nonexistent-project-id/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_a_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_access_org_a_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_org_b_cannot_trigger_matcher_for_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/trigger"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_producer_org_b_cannot_access_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_tenant_b_producer_token()}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_matcher_without_token_returns_401(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
        )
    assert resp.status_code == 401


def _global_admin_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": "global-admin-user",
        "organization_id": SMOKE_ORG_A,
        "roles": ["global_admin"],
        "scopes": ["projects:read", "projects:write", "admin:read", "admin:write"],
    })


@pytest.mark.asyncio
async def test_admin_org_b_cannot_access_org_a_funding(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matches",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_org_b_cannot_access_org_a_project_funding(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_org_b_cannot_access_org_a_queue(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/queue/status/nonexistent-job",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_global_admin_can_access_org_a_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers={"Authorization": f"Bearer {_global_admin_token()}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_post_private_funding_source(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers={"Authorization": f"Bearer {_tenant_b_token()}"},
            json={"source_name": "Test", "source_type": "grant", "amount": 1000},
        )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_404_returns_json_with_detail(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/nonexistent-route",
            headers={
                "Authorization": f"Bearer {_tenant_a_token()}",
                "X-Request-ID": "cid-test-404-001",
            },
        )
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error"].get("request_id") == "cid-test-404-001"
