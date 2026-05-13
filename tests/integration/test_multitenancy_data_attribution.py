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


def _make_token(*, sub: str, org_id: str, roles: list[str]) -> str:
    from routes.auth_routes import create_access_token
    scopes_map = {
        "global_admin": ["projects:read", "projects:write", "admin:read", "admin:write"],
        "admin": ["projects:read", "projects:write", "comfyui:read", "comfyui:health"],
        "viewer": ["projects:read"],
    }
    role_key = roles[0] if roles else "viewer"
    scopes = scopes_map.get(role_key, scopes_map["viewer"])
    return create_access_token({
        "sub": sub,
        "organization_id": org_id,
        "roles": roles,
        "scopes": scopes,
    })


def _org_a_admin() -> str:
    return _make_token(sub=SMOKE_TENANT_A_USER_ID, org_id=SMOKE_ORG_A, roles=["admin"])


def _org_b_admin() -> str:
    return _make_token(sub="org-b-admin", org_id=SMOKE_ORG_B, roles=["admin"])


def _org_b_viewer() -> str:
    return _make_token(sub="org-b-viewer", org_id=SMOKE_ORG_B, roles=["viewer"])


def _global_admin() -> str:
    return _make_token(sub="global-root", org_id=SMOKE_ORG_A, roles=["global_admin"])


@pytest.fixture(scope="module")
def test_app():
    from core.app_factory import create_app
    return create_app()


@pytest.mark.asyncio
async def test_global_admin_creates_funding_source_attributed_to_project_org(test_app):
    """global_admin from Org X creates funding source on Org A project.
    Resource must be attributed to Org A (project.organization_id)."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    headers = {"Authorization": f"Bearer {_global_admin()}"}
    payload = {"source_name": "GA Test Grant", "source_type": "grant", "amount": 50000}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers=headers,
            json=payload,
        )
    assert resp.status_code == 200, f"global_admin create source failed: {resp.text}"
    body = resp.json()
    source = body.get("source", body)
    # Verify the source is attributed correctly
    source_org = source.get("organization_id", "")
    assert source_org == SMOKE_ORG_A, (
        f"Expected organization_id={SMOKE_ORG_A}, got {source_org}. "
        "global_admin-created resource leaked to wrong org."
    )


@pytest.mark.asyncio
async def test_org_a_user_can_see_funding_source_created_by_global_admin(test_app):
    """User from Org A can see the funding source created by global_admin."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    headers = {"Authorization": f"Bearer {_org_a_admin()}"}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers=headers,
        )
    assert resp.status_code == 200, f"Org A user cannot see sources: {resp.text}"
    body = resp.json()
    assert body.get("count", 0) >= 1, "Org A should see at least 1 source"


@pytest.mark.asyncio
async def test_org_b_user_cannot_see_funding_source_of_org_a(test_app):
    """User from Org B cannot see Org A's funding sources (cross-org blocked)."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    token = _make_token(sub="org-b-nobody", org_id=SMOKE_ORG_B, roles=["admin"])

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 403, (
        f"Expected 403 for cross-org, got {resp.status_code}. "
        "Cross-org data leak detected."
    )


@pytest.mark.asyncio
async def test_admin_org_b_cannot_create_source_in_org_a(test_app):
    """Admin from Org B cannot create funding source in Org A."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    payload = {"source_name": "Cross Org Grant", "source_type": "grant", "amount": 1000}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers={"Authorization": f"Bearer {_org_b_admin()}"},
            json=payload,
        )
    assert resp.status_code == 403, (
        f"Expected 403 for cross-org admin write, got {resp.status_code}."
    )


@pytest.mark.asyncio
async def test_viewer_cannot_create_funding_source(test_app):
    """Viewer cannot create funding source (write permission enforced)."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    payload = {"source_name": "Viewer Source", "source_type": "grant", "amount": 100}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/private-sources",
            headers={"Authorization": f"Bearer {_org_b_viewer()}"},
            json=payload,
        )
    assert resp.status_code == 403, (
        f"Expected 403 for viewer write, got {resp.status_code}."
    )


@pytest.mark.asyncio
async def test_matcher_global_admin_can_access_org_a(test_app):
    """global_admin can access matcher for Org A project."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    headers = {"Authorization": f"Bearer {_global_admin()}"}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers=headers,
        )
    assert resp.status_code == 200, (
        f"Expected 200 for global_admin matcher access, got {resp.status_code}: {resp.text}"
    )


@pytest.mark.asyncio
async def test_matcher_admin_org_b_blocked_from_org_a(test_app):
    """Admin from Org B cannot access Org A matcher."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    headers = {"Authorization": f"Bearer {_org_b_admin()}"}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/status"
            f"?organization_id={SMOKE_ORG_A}",
            headers=headers,
        )
    assert resp.status_code == 403, (
        f"Expected 403 for cross-org admin, got {resp.status_code}."
    )


@pytest.mark.asyncio
async def test_matcher_viewer_cannot_trigger(test_app):
    """Viewer cannot trigger matcher job (write permission enforced)."""
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    headers = {"Authorization": f"Bearer {_org_b_viewer()}"}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/funding/matcher/trigger"
            f"?organization_id={SMOKE_ORG_A}",
            headers=headers,
            json={},
        )
    assert resp.status_code == 403, (
        f"Expected 403 for viewer trigger, got {resp.status_code}."
    )
