"""
Contract test: client_feedback_routes.py gating invariants.

Verifies that client feedback endpoints require tenant context,
appropriate write permission, and use organization_id for deep ownership.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "client_feedback_routes.py"

# --- Decorators ---

ALL_ENDPOINTS = [
    '@router.post("/",',
    '@router.put("/{feedback_id}",',
    '@router.delete("/{feedback_id}",',
    '@router.get("/aggregated",',
    '@router.get("/{feedback_id}",',
    '@router.get("/",',
]

WRITE_ENDPOINTS = [
    '@router.post("/",',
    '@router.put("/{feedback_id}",',
    '@router.delete("/{feedback_id}",',
]

READ_ENDPOINTS = [
    '@router.get("/aggregated",',
    '@router.get("/{feedback_id}",',
    '@router.get("/",',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Router is tenant-scoped for client feedback.
    # Deep ownership is enforced by passing organization_id=tenant.organization_id to the service.
    # No project gating is directly applied at the route level since there is no project_id in this router.
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
    """Since the router is tenant-scoped without project_id, project elements are not expected."""
    source = _read_source()
    assert "validate_project_access" not in source, "validate_project_access is not expected here"
    assert "select(Project)" not in source, "select(Project) is not expected here"
    assert "Project" not in source, "Project model is not expected here"


def test_service_calls_use_tenant_organization_id():
    """All service calls must pass tenant.organization_id."""
    source = _read_source()
    
    # create_feedback
    create_block = _get_function_block(source, '@router.post("/",')
    assert "organization_id=tenant.organization_id" in create_block
    
    # update_feedback
    update_block = _get_function_block(source, '@router.put("/{feedback_id}",')
    assert "organization_id=tenant.organization_id" in update_block
    
    # delete_feedback
    delete_block = _get_function_block(source, '@router.delete("/{feedback_id}",')
    assert "organization_id=tenant.organization_id" in delete_block
    
    # get_aggregated_feedback
    agg_block = _get_function_block(source, '@router.get("/aggregated",')
    assert "organization_id=tenant.organization_id" in agg_block
    
    # get_feedback
    get_block = _get_function_block(source, '@router.get("/{feedback_id}",')
    assert "organization_id=tenant.organization_id" in get_block
    
    # list_feedback
    list_block = _get_function_block(source, '@router.get("/",')
    assert "organization_id=tenant.organization_id" in list_block


def test_endpoints_pass_feedback_id_and_organization_id():
    """Endpoints referencing a specific feedback must pass feedback_id and organization_id."""
    source = _read_source()
    
    # update_feedback
    update_block = _get_function_block(source, '@router.put("/{feedback_id}",')
    assert "feedback_id=feedback_id" in update_block
    assert "organization_id=tenant.organization_id" in update_block
    
    # delete_feedback
    delete_block = _get_function_block(source, '@router.delete("/{feedback_id}",')
    assert "feedback_id=feedback_id" in delete_block
    assert "organization_id=tenant.organization_id" in delete_block
    
    # get_feedback
    get_block = _get_function_block(source, '@router.get("/{feedback_id}",')
    assert "feedback_id=feedback_id" in get_block
    assert "organization_id=tenant.organization_id" in get_block


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    put_count = len(re.findall(r"@router\.put\(", source))
    delete_count = len(re.findall(r"@router\.delete\(", source))
    total = get_count + post_count + put_count + delete_count
    assert total == 6, f"Expected 6 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"
    assert put_count == 1, f"Expected 1 PUT, found {put_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: router is tenant-scoped for client feedback.
    Deep ownership is enforced by passing organization_id=tenant.organization_id to the service.
    No project gating is directly applied at the route level since there is no project_id in this router.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
