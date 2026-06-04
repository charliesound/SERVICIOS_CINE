"""
Contract test: project_visual_bible_routes.py gating invariants.

Verifies that visual bible endpoints require tenant context,
project access validation, appropriate write permission,
and use DB-validated project IDs for service calls.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "project_visual_bible_routes.py"

# --- Decorators ---

PROJECT_ENDPOINTS = [
    '@router.get("",',
    '@router.put("",',
    '@router.post("/preview-prompt",',
    '@router.post("/reset",',
]

WRITE_ENDPOINTS = [
    '@router.put("",',
    '@router.post("/reset",',
]

READ_ENDPOINTS = [
    '@router.get("",',
    '@router.post("/preview-prompt",',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Deep ownership is delegated to project_visual_bible_service which
    # receives tenant + validated_project_id. The service performs its own
    # organization_id scoped queries via _get_project_for_tenant_or_404.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


# --- Import tests ---

def test_imports_tenant_context():
    source = _read_source()
    assert "get_tenant_context" in source
    assert "TenantContext" in source


def test_imports_validate_project_access():
    source = _read_source()
    assert "from dependencies.project_access import" in source
    assert "validate_project_access" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_imports_project_model():
    source = _read_source()
    assert "from models.core import Project" in source


# --- Endpoint-level gating ---

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_all_endpoints_have_validate_project_access():
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Missing validate_project_access in {decorator}"
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


# --- Validated project ID usage ---

def test_endpoints_use_validated_project_id():
    """All endpoints must use project.id for service calls."""
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "str(project.id)" in block or "project.id" in block, (
            f"Endpoint does not use project.id: {decorator}"
        )


def test_services_receive_validated_project_id():
    source = _read_source()
    assert "validated_project_id" in source
    # Each service call should use validated_project_id, not raw project_id
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validated_project_id" in block, (
            f"Service call does not use validated_project_id: {decorator}"
        )


# --- No legacy / optional auth ---

def test_no_legacy_inline_project_query():
    source = _read_source()
    assert "select(Project)" not in source, "Legacy inline project query found in routes"


def test_no_optional_auth_legacy():
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    put_count = len(re.findall(r"@router\.put\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + put_count + post_count
    assert total == 4, f"Expected 4 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert put_count == 1, f"Expected 1 PUT, found {put_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: deep ownership is delegated to project_visual_bible_service.
    The service receives tenant + validated_project_id and performs its own
    organization_id-scoped queries via _get_project_for_tenant_or_404.
    Route-level gating ensures validated project access before any service call.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
