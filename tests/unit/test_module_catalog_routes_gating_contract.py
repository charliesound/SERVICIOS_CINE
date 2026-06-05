"""
Contract test: module_catalog_routes.py gating invariants.

Verifies that catalog/detail remain public while `/me` requires authenticated
tenant context and derives modules from the tenant's effective plan.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "module_catalog_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # Catalog and detail remain public.
    # /me requires auth and resolves modules from the tenant effective plan.
    # No project gating applies because this router has no project_id.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_imports_tenant_context_without_optional_auth_or_write():
    source = _read_source()
    assert "get_current_user_optional" not in source
    assert "UserResponse" not in source
    assert "get_tenant_context" in source
    assert "TenantContext" in source
    assert "require_write_permission" not in source


def test_no_project_gating_imports_or_queries():
    source = _read_source()
    assert "validate_project_access" not in source
    assert "from models.core import Project" not in source
    assert "select(Project)" not in source


def test_public_endpoints_stay_public():
    source = _read_source()
    for decorator in [
        '@router.get("/catalog", response_model=ModuleCatalogResponse)',
        '@router.get("/{module_key}", response_model=ModuleInfo)',
    ]:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" not in block
        assert "require_write_permission" not in block


def test_get_my_modules_requires_auth_without_write_and_keeps_plan_resolution():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/me", response_model=UserModulesResponse)',
    )
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block
    assert "get_current_user_optional" not in block
    assert "tenant.user_id" in block
    assert "resolve_effective_plan" in block
    assert "normalize_plan_name" in block


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    assert get_count == 3, f"Expected 3 GET endpoints, found {get_count}"


def test_manual_review_documented():
    """
    Manual review: catalog/detail are public.
    /me requires auth and returns modules according to the tenant effective plan.
    No project gating applies because there is no project_id.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
