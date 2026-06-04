"""
Contract test: shot_routes.py gating invariants.

Verifies that shot endpoints require tenant context,
project access validation on project routes, and write permission on
mutating/action endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "shot_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # shot_id is protected by project_id scope and further validated internally.
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

def test_imports_validate_project_access():
    source = _read_source()
    assert "validate_project_access" in source

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

def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = re.findall(r"@router\.[a-z]+\(\s*\"/\{project_id\}[^\"]*\"", source)
    assert len(decorators) == 5, f"Expected 5 project endpoints, found {len(decorators)}"
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped endpoint missing validate_project_access: {decorator}"
        )

def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = re.findall(r"@router\.(?:post|put|patch|delete)\([^)]*\)", source)

    assert len(decorators) == 4, f"Expected 4 mutating/action endpoints, found {len(decorators)}"

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
    put_count = len(re.findall(r"@router\.put\([^)]*\)", source))
    delete_count = len(re.findall(r"@router\.delete\([^)]*\)", source))
    total = get_count + post_count + put_count + delete_count
    assert total == 5, f"Expected 5 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"
    assert put_count == 2, f"Expected 2 PUT, found {put_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"
