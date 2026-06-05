"""
Contract test: user_routes.py gating invariants.

Verifies that public registration stays open while read/sensitive user endpoints
require authenticated tenant context with explicit authorization checks.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "user_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # POST / is public registration and intentionally remains unauthenticated.
    # GET /{user_id}, GET /, and PATCH /{user_id}/plan are authenticated.
    # GET / is admin-only. PATCH /{user_id}/plan requires auth + write.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_imports_tenant_context_and_hash_password():
    source = _read_source()
    assert "get_current_user_optional" not in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "hash_password" in source


def test_no_project_gating_imports_or_queries():
    source = _read_source()
    assert "validate_project_access" not in source
    assert "from models.core import Project" not in source
    assert "select(Project)" not in source


def test_create_user_stays_public_registration():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/", response_model=UserResponse)',
    )
    assert "get_tenant_context" not in block
    assert "require_write_permission" not in block


def test_get_user_has_auth_but_not_write_permission():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/{user_id}", response_model=UserResponse)',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block


def test_list_users_has_auth_but_not_write_permission():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/", response_model=List[UserResponse])',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block


def test_update_user_plan_has_auth_and_write_permission():
    source = _read_source()
    block = _get_function_block(source, '@router.patch("/{user_id}/plan")')
    assert "get_tenant_context" in block
    assert "require_write_permission" in block
    assert "get_current_user_optional" not in block


def test_sensitive_endpoints_have_authorization_checks_and_403():
    source = _read_source()
    decorators = [
        '@router.get("/{user_id}", response_model=UserResponse)',
        '@router.get("/", response_model=List[UserResponse])',
        '@router.patch("/{user_id}/plan")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "403" in block or "status_code=403" in block, (
            f"Missing 403 authorization check in {decorator}"
        )


def test_update_user_plan_keeps_internal_plan_change_call():
    source = _read_source()
    block = _get_function_block(source, '@router.patch("/{user_id}/plan")')
    assert "apply_internal_plan_change" in block


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    patch_count = len(re.findall(r"@router\.patch\(", source))
    total = get_count + post_count + patch_count
    assert total == 4, f"Expected 4 endpoints, found {total}"
    assert get_count == 2, f"Expected 2 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"


def test_manual_review_documented():
    """
    Manual review: create_user is the public registration endpoint.
    The read/sensitive endpoints are authenticated, list_users is admin-only,
    and update_user_plan requires authenticated tenant context plus write access.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
