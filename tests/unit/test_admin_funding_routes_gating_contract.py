"""
Contract test: admin_funding_routes.py gating invariants.

Verifies that admin endpoints require tenant context,
preserves the _require_admin function call,
and require write permission on mutating/action endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "admin_funding_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # call_id is resolved globally, which is correct for a global admin endpoint.
    # The admin policy (_require_admin) protects it.
]

def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")

def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block

def test_imports_tenant_context():
    source = _read_source()
    assert "from routes.auth_routes import get_tenant_context" in source or "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source

def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    decorators = re.findall(r"@router\.[a-z]+\([^)]*\)", source)
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Endpoint missing get_tenant_context: {decorator}"
        )

def test_all_endpoints_preserve_admin_policy():
    source = _read_source()
    decorators = re.findall(r"@router\.[a-z]+\([^)]*\)", source)
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "_require_admin" in block, (
            f"Endpoint missing _require_admin call: {decorator}"
        )

def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = re.findall(r"@router\.(?:post|put|patch|delete)\([^)]*\)", source)

    assert len(decorators) == 5, f"Expected 5 mutating/action endpoints, found {len(decorators)}"

    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating/action endpoint missing require_write_permission: {decorator}"
        )

def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    decorators = re.findall(r"@router\.get\([^)]*\)", source)
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {decorator}"
        )

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]*\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]*\)", source))
    patch_count = len(re.findall(r"@router\.patch\([^)]*\)", source))
    total = get_count + post_count + patch_count
    assert total == 8, f"Expected 8 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET, found {get_count}"
    assert post_count == 4, f"Expected 4 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"
