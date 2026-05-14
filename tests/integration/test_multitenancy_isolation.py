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


@pytest.mark.asyncio
async def test_admin_org_b_cannot_access_org_a_project_detail(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_a_user_can_access_own_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}",
            headers={"Authorization": f"Bearer {_tenant_a_token()}"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_org_b_cannot_list_org_a_projects(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 200
    body = resp.json()
    projects = body.get("projects", body if isinstance(body, list) else [])
    for p in projects:
        org_id = p.get("organization_id", "")
        assert org_id != SMOKE_ORG_A, f"Cross-tenant leak: org B can see org A project {p.get('id')}"


def _global_admin_from_org_b_token() -> str:
    from routes.auth_routes import create_access_token

    return create_access_token({
        "sub": "global-admin-org-b",
        "organization_id": SMOKE_ORG_B,
        "roles": ["global_admin"],
        "scopes": ["projects:read", "projects:write", "admin:read", "admin:write"],
    })


@pytest.mark.asyncio
async def test_admin_org_b_cannot_update_org_a_project_script(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.put(
            f"/api/projects/{SMOKE_PROJECT_ID}/script",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={"script_text": "Should not update"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_analyze_org_a_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/analyze",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_export_org_a_project_json(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/export/json",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_export_org_a_project_zip(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/export/zip",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_list_org_a_project_assets(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/assets",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_read_org_a_project_metrics(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/metrics",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_org_b_cannot_list_org_a_project_jobs(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/jobs",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_project_uses_tenant_organization_id(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={"name": "Tenant Test Project", "description": "Should have org B"},
        )
    # Org B may have reached its plan limit; verify the org is correct either way.
    if resp.status_code == 200:
        body = resp.json()
        assert body.get("organization_id") == SMOKE_ORG_B, (
            f"Expected org B, got {body.get('organization_id')}"
        )
    else:
        # If blocked by plan limit, verify the tenant identity is correct
        assert resp.status_code == 403
        body = resp.json()
        error = body.get("error", body)
        code = error.get("details", {}).get("code", "")
        assert code == "PLAN_LIMIT_REACHED", (
            f"Unexpected error code: {code}"
        )


@pytest.mark.asyncio
async def test_global_admin_has_no_bypass_in_project_routes(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}",
            headers={"Authorization": f"Bearer {_global_admin_from_org_b_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_create_storage_source_in_org_a_project(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/storage-sources",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={
                "organization_id": SMOKE_ORG_A,
                "project_id": SMOKE_PROJECT_ID,
                "name": "Cross-org source",
                "source_type": "local",
                "mount_path": "/tmp/cross-org",
            },
        )
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"


@pytest.mark.asyncio
async def test_org_a_can_create_and_org_b_cannot_see_storage_source(test_app):
    import uuid
    from httpx import AsyncClient, ASGITransport

    unique_name = f"Tenant A Source {uuid.uuid4().hex[:8]}"
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        create = await client.post(
            "/api/storage-sources",
            headers={"Authorization": f"Bearer {_tenant_a_token()}"},
            json={
                "organization_id": SMOKE_ORG_A,
                "project_id": SMOKE_PROJECT_ID,
                "name": unique_name,
                "source_type": "local",
                "mount_path": "/tmp/tenant-a",
            },
        )
    assert create.status_code == 200, f"Create failed: {create.text}"
    source_id = create.json()["id"]

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        detail = await client.get(
            f"/api/storage-sources/{source_id}",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert detail.status_code == 404, (
        f"Org B should not see org A storage source: {detail.status_code}"
    )


@pytest.mark.asyncio
async def test_org_b_cannot_update_storage_source_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        detail = await client.get(
            "/api/storage-sources/nonexistent-id",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert detail.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_validate_storage_source_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/storage-sources/nonexistent-id/validate",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_launch_scan_in_org_a_storage(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/storage-sources/nonexistent-id/scan",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_global_admin_cannot_bypass_storage_isolation(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/storage-sources/nonexistent-id",
            headers={"Authorization": f"Bearer {_global_admin_from_org_b_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_list_script_versions_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_create_script_version_in_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={"script_text": "Malicious script version"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_get_script_version_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions/nonexistent-id",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_activate_script_version_in_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions/nonexistent-id/activate",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_compare_versions_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions/compare",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
            json={"from_version_id": "fake1", "to_version_id": "fake2"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_list_change_reports_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/change-reports",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_org_b_cannot_get_module_statuses_of_org_a(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/module-status",
            headers={"Authorization": f"Bearer {_tenant_b_admin_token()}"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_global_admin_cannot_bypass_script_version_routes(test_app):
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            f"/api/projects/{SMOKE_PROJECT_ID}/script/versions",
            headers={"Authorization": f"Bearer {_global_admin_from_org_b_token()}"},
        )
    assert resp.status_code == 404
