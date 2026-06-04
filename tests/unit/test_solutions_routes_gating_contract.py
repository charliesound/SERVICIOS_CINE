"""
Contract test: solutions_routes.py gating invariants.

Verifies that solutions endpoints require tenant context and
appropriate write permission on mutating operations.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "solutions_routes.py"

# --- Decorators ---

ALL_ENDPOINTS = [
    '@router.get("",',
    '@router.post("",',
    '@router.get("/{solution_id}"',
    '@router.delete("/{solution_id}")',
    '@router.post("/{solution_id}/execute")',
    '@router.post("/seed")',
]

WRITE_ENDPOINTS = [
    '@router.post("",',
    '@router.delete("/{solution_id}")',
    '@router.post("/{solution_id}/execute")',
    '@router.post("/seed")',
]

READ_ENDPOINTS = [
    '@router.get("",',
    '@router.get("/{solution_id}"',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Router is not project-scoped (no project_id in path or query).
    # Catalog/registry of solutions is protected by tenant auth and write permission on mutators.
    # Ownership and global accessibility of solutions is delegated to solutions_service.
    # Future work may introduce multi-tenant isolation at the service/DB layer.
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


# --- No project / optional auth legacy ---

def test_no_optional_auth_legacy():
    """No optional auth or get_optional_tenant patterns should remain."""
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


def test_no_project_access_gating_if_not_project_scoped():
    """Since the router is not project-scoped, project elements are not expected."""
    source = _read_source()
    assert "validate_project_access" not in source, "validate_project_access is not expected here"
    assert "select(Project)" not in source, "select(Project) is not expected here"
    assert "Project" not in source, "Project model is not expected here"


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    put_count = len(re.findall(r"@router\.put\(", source))
    delete_count = len(re.findall(r"@router\.delete\(", source))
    total = get_count + post_count + put_count + delete_count
    assert total == 6, f"Expected 6 endpoints, found {total}"
    assert get_count == 2, f"Expected 2 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"
    assert put_count == 0, f"Expected 0 PUT, found {put_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: router is not project-scoped.
    Catalog/registry of solutions is protected by tenant auth and write permission on mutators.
    Ownership and global accessibility of solutions is delegated to solutions_service.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
