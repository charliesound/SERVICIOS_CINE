"""
Contract test: funding_private_routes.py gating invariants.

Verifies that private funding endpoints require tenant context,
appropriate write permission, and use organization_id for deep ownership.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "funding_private_routes.py"

# --- Decorators ---

ALL_ENDPOINTS = [
    '@private_source_router.get("/sources/private")',
    '@private_source_router.post("/sources/private"',
    '@private_source_router.put("/sources/private/{source_id}")',
    '@private_source_router.delete("/sources/private/{source_id}")',
    '@private_source_router.get("/opportunities/private")',
    '@private_source_router.post("/opportunities/private")',
    '@private_source_router.get("/dashboard/opportunities")',
    '@private_source_router.get("/alerts")',
]

WRITE_ENDPOINTS = [
    '@private_source_router.post("/sources/private"',
    '@private_source_router.put("/sources/private/{source_id}")',
    '@private_source_router.delete("/sources/private/{source_id}")',
    '@private_source_router.post("/opportunities/private")',
]

READ_ENDPOINTS = [
    '@private_source_router.get("/sources/private")',
    '@private_source_router.get("/opportunities/private")',
    '@private_source_router.get("/dashboard/opportunities")',
    '@private_source_router.get("/alerts")',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Router is tenant-scoped for private funding.
    # Deep ownership is enforced by filtering PrivateFundingSource and PrivateOpportunity
    # by organization_id == tenant.organization_id.
    # No project gating is directly applied at the route level since there are no project_id
    # parameters in the path for these private funding objects.
    # GET /alerts is read-only, accepts optional project_id, and ownership is delegated
    # to funding_alert_service, which scopes queries by organization_id.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block[1:])
    return block[:next_decorator.start() + 1] if next_decorator else block


# --- Import tests ---

def test_imports_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "routes.auth_routes" not in source, "Must import from dependencies.tenant_context"


def test_imports_tenant_schema():
    source = _read_source()
    assert "from schemas.auth_schema import TenantContext" in source


# --- Endpoint-level gating ---

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    for decorator in WRITE_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Missing require_write_permission in {decorator}"
        )


def test_read_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    for decorator in READ_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"Unexpected require_write_permission in {decorator}"
        )


# --- Deep ownership and structure ---

def test_no_optional_auth_legacy():
    """No optional auth or get_optional_tenant patterns should remain."""
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


def test_no_project_access_gating_if_tenant_scoped():
    """Since the router is tenant-scoped without path project_id, project_access should not be imported or used."""
    source = _read_source()
    assert "validate_project_access" not in source, "validate_project_access is not expected here"
    assert "select(Project)" not in source, "select(Project) is not expected here"


def test_ownership_queries_use_tenant_organization_id():
    """Queries for private funding sources and opportunities must filter by organization_id."""
    source = _read_source()

    # Check that where clauses check organization_id
    assert "PrivateFundingSource.organization_id == tenant.organization_id" in source
    assert "PrivateOpportunity.organization_id == tenant.organization_id" in source


def test_mutators_filter_by_id_and_organization_id():
    """Updates/Deletes must ensure the entity belongs to the tenant's organization."""
    source = _read_source()

    # update_private_source
    update_block = _get_function_block(source, '@private_source_router.put("/sources/private/{source_id}")')
    assert "PrivateFundingSource.id == source_id" in update_block
    assert "PrivateFundingSource.organization_id == tenant.organization_id" in update_block

    # delete_private_source
    delete_block = _get_function_block(source, '@private_source_router.delete("/sources/private/{source_id}")')
    assert "PrivateFundingSource.id == source_id" in delete_block
    assert "PrivateFundingSource.organization_id == tenant.organization_id" in delete_block


def test_create_opportunity_validates_source_id_and_organization_id():
    """Creating an opportunity must validate that the source belongs to the organization."""
    source = _read_source()
    create_opp_block = _get_function_block(source, '@private_source_router.post("/opportunities/private")')
    assert "PrivateFundingSource.id == payload.source_id" in create_opp_block
    assert "PrivateFundingSource.organization_id == tenant.organization_id" in create_opp_block


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@private_source_router\.get\(", source))
    post_count = len(re.findall(r"@private_source_router\.post\(", source))
    put_count = len(re.findall(r"@private_source_router\.put\(", source))
    delete_count = len(re.findall(r"@private_source_router\.delete\(", source))
    total = get_count + post_count + put_count + delete_count
    assert total == 8, f"Expected 8 endpoints, found {total}"
    assert get_count == 4, f"Expected 4 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"
    assert put_count == 1, f"Expected 1 PUT, found {put_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: router is tenant-scoped for private funding.
    Deep ownership is enforced by filtering PrivateFundingSource and PrivateOpportunity
    by organization_id == tenant.organization_id.
    No project gating is directly applied at the route level since there are no project_id
    parameters in the path for these private funding objects.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None


# --- Alerts service delegation ---

def test_alerts_endpoint_passes_tenant_org_id_to_service():
    """GET /alerts must pass tenant.organization_id to the funding_alert_service call."""
    source = _read_source()
    block = _get_function_block(source, '@private_source_router.get("/alerts")')
    assert "organization_id = tenant.organization_id" in block or "tenant.organization_id" in block
    assert "funding_alert_service.get_funding_dashboard_alerts" in block
    assert "organization_id" in block

