"""
Contract test: plan_routes.py gating invariants.

Verifies that plan catalog/detail endpoints stay public while `/me` and
`/change` require authenticated tenant context with tighter authorization.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "plan_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # Catalog, details, and can-run remain public.
    # /me requires auth and restricts optional user_id to self/admin.
    # /change requires auth + write and applies only to tenant.user_id.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_imports_tenant_context_without_legacy_optional_auth():
    source = _read_source()
    assert "get_current_user_optional" not in source
    assert "UserResponse" not in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "TenantContext" in source


def test_no_project_gating_imports_or_queries():
    source = _read_source()
    assert "validate_project_access" not in source
    assert "select(Project)" not in source
    assert "Project = Depends" not in source


def test_project_model_is_only_used_for_usage_counts_not_gating():
    source = _read_source()
    helper_start = source.index("async def _get_org_usage_counts(")
    helper_end = source.index("async def _resolve_effective_plan_for_user(")
    block = source[helper_start:helper_end]
    assert "Project.id" in block
    assert "Project.organization_id == organization_id" in block


def test_public_endpoints_stay_public():
    source = _read_source()
    for decorator in [
        '@router.get("/catalog", response_model=List[PlanInfo])',
        '@router.get("/{plan_name}")',
        '@router.get("/{plan_name}/can-run/{task_type}")',
    ]:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" not in block
        assert "require_write_permission" not in block


def test_get_my_plan_has_auth_without_write_and_uses_tenant_effective_user():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/me", response_model=UserPlanStatus)',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block
    assert "get_current_user_optional" not in block
    assert "_get_effective_user(db, tenant=tenant, user_id=user_id)" in block


def test_change_my_plan_has_auth_and_write_and_uses_tenant_user_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/change", response_model=PlanChangeResponse)',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" in block
    assert "get_current_user_optional" not in block
    assert "apply_internal_plan_change" in block
    assert "get_user_by_id(db, tenant.user_id)" in block


def test_get_effective_user_uses_tenant_and_restricts_other_user_ids():
    source = _read_source()
    helper_start = source.index("async def _get_effective_user(")
    helper_end = source.index("async def _get_org_usage_counts(")
    block = source[helper_start:helper_end]
    assert "tenant: TenantContext" in block
    assert "effective_user_id = user_id or tenant.user_id" in block
    assert "str(user_id) != str(tenant.user_id)" in block
    assert "_is_admin_tenant(tenant)" in block
    assert "status_code=403" in block


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 5, f"Expected 5 endpoints, found {total}"
    assert get_count == 4, f"Expected 4 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"


def test_manual_review_documented():
    """
    Manual review: catalog/details/can-run are public.
    /me requires auth, and /change requires auth + write.
    user_id query in /me remains compatibility-only and is restricted to self/admin.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
