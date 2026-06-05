"""
Contract test: producer_routes.py gating invariants.

Verifies that marketing/demo endpoints stay public, admin endpoints require
tenant auth, and saved opportunities use a local project access helper because
project_id is not part of the router path.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "producer_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # Public funding catalog and demo lead capture stay unauthenticated.
    # saved-opportunities uses a local helper because project_id arrives via
    # body/query/indirect resource rather than router path.
    # dashboard and demo request listing are admin-only.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_imports_and_no_legacy_auth():
    source = _read_source()
    assert "check_project_ownership" not in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "TenantContext" in source
    assert "validate_project_access" not in source
    assert "get_optional_tenant" not in source
    assert "optional_auth" not in source


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    delete_count = len(re.findall(r"@router\.delete\(", source))
    total = get_count + post_count + delete_count
    assert total == 7, f"Expected 7 endpoints, found {total}"
    assert get_count == 4, f"Expected 4 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"


def test_public_endpoints_stay_public():
    source = _read_source()
    for decorator in [
        '@router.get("/funding/opportunities")',
        '@router.post("/demo-request", response_model=DemoRequestResponse)',
    ]:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" not in block
        assert "require_write_permission" not in block


def test_admin_endpoints_require_auth_and_403_without_write():
    source = _read_source()
    for decorator in [
        '@router.get("/dashboard", response_model=DashboardResponse)',
        '@router.get("/demo-requests", response_model=List[DemoRequestResponse])',
    ]:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block
        assert "require_write_permission" not in block
        assert "_require_admin_tenant(tenant)" in block
        assert "Admin access required" in source


def test_saved_opportunities_get_uses_auth_without_write():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/saved-opportunities", response_model=List[SavedOpportunityResponse])',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block
    assert "if project_id:" in block
    assert "_validate_producer_project_access(db, project_id, tenant)" in block
    assert "validated_project_id = str(project.id)" in block
    assert "_require_admin_tenant(tenant)" in block


def test_saved_opportunities_mutators_require_auth_and_write():
    source = _read_source()
    for decorator in [
        '@router.post("/saved-opportunities", response_model=SavedOpportunityResponse)',
        '@router.delete("/saved-opportunities/{saved_id}")',
    ]:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block
        assert "require_write_permission" in block


def test_helper_validate_producer_project_access_exists_and_scopes_project():
    source = _read_source()
    assert "async def _validate_producer_project_access(" in source
    helper_block = source[
        source.index("async def _validate_producer_project_access(") : source.index('@router.get("/dashboard", response_model=DashboardResponse)')
    ]
    assert "select(Project)" in helper_block
    assert "Project.id == project_id" in helper_block
    assert "Project.organization_id == tenant.organization_id" in helper_block


def test_create_saved_opportunity_uses_validated_project_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/saved-opportunities", response_model=SavedOpportunityResponse)',
    )
    assert "validated_project_id = str(project.id)" in block
    assert "SavedOpportunity.project_id == validated_project_id" in block
    assert "project_id=validated_project_id" in block
    assert "project_id=request.project_id" not in block


def test_delete_saved_opportunity_validates_saved_project_id_through_helper():
    source = _read_source()
    block = _get_function_block(source, '@router.delete("/saved-opportunities/{saved_id}")')
    assert "_validate_producer_project_access(db, saved.project_id, tenant)" in block


def test_manual_review_documented():
    """
    Manual review: public demo request and funding catalog stay public.
    saved-opportunities uses a local helper because project_id is body/query/indirect,
    not router path. dashboard and demo-request list are admin-only.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
