"""
Contract test: budget_routes.py gating invariants.

Verifies that all budget endpoints require tenant context,
project access validation, and write permission on POST endpoints.
Preserves require_module_access("budget_lite") and check_permission.

Static source-code analysis — no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "budget_routes.py"


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def test_imports_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source


def test_imports_validate_project_access():
    source = _read_source()
    assert "validate_project_access" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_conserves_require_module_access():
    source = _read_source()
    assert "require_module_access" in source
    assert 'require_module_access("budget_lite")' in source


def test_conserves_check_permission():
    source = _read_source()
    assert "check_permission" in source


def test_conserves_check_budget_access():
    source = _read_source()
    assert "_check_budget_access" in source


def test_conserves_budget_view():
    source = _read_source()
    assert '"budget.view"' in source
    assert '"budget.generate"' in source


def test_no_get_current_user_optional():
    source = _read_source()
    assert "get_current_user_optional" not in source


def test_no_UserResponse_import():
    source = _read_source()
    assert "UserResponse" not in source


def test_no_inline_401_checks():
    source = _read_source()
    assert '"Authentication required"' not in source


def test_router_has_get_tenant_context():
    source = _read_source()
    assert "Depends(get_tenant_context)" in source


def test_router_has_require_module_access():
    source = _read_source()
    assert 'Depends(require_module_access("budget_lite"))' in source


def test_all_endpoints_have_validate_project_access():
    source = _read_source()
    count = source.count("validate_project_access")
    assert count >= 9, (
        f"Expected >=9 occurrences of validate_project_access, found {count}"
    )


def test_write_endpoints_have_require_write_permission():
    source = _read_source()
    count = source.count("require_write_permission")
    assert count >= 4, (
        f"Expected >=4 occurrences of require_write_permission, found {count}"
    )


def test_get_endpoints_no_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        idx = source.index(dec)
        block_after = source[idx:]
        next_decorator = re.search(r"\n@", block_after)
        func_body = block_after[:next_decorator.start()] if next_decorator else block_after
        assert "require_write_permission" not in func_body, (
            f"GET endpoint should NOT have require_write_permission: {dec}"
        )


def test_post_endpoints_have_require_write_permission():
    source = _read_source()
    post_decorators = re.findall(r"@router\.post\([^)]+\)", source)
    for dec in post_decorators:
        idx = source.index(dec)
        block_after = source[idx:]
        next_decorator = re.search(r"\n@", block_after)
        func_body = block_after[:next_decorator.start()] if next_decorator else block_after
        assert "require_write_permission" in func_body, (
            f"POST endpoint missing require_write_permission: {dec}"
        )


def test_no_inline_project_query():
    source = _read_source()
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("from models.core import Project"):
            continue
        assert "Project.id == project_id" not in stripped, (
            "Found inline Project query -- should use validate_project_access instead"
        )


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 9, f"Expected 9 endpoints, found {total}"
    assert get_count == 5, f"Expected 5 GET, found {get_count}"
    assert post_count == 4, f"Expected 4 POST, found {post_count}"


def test_budget_id_endpoints_validate_project_id():
    source = _read_source()
    budget_id_endpoints = [
        "/{budget_id}",
        "/{budget_id}/activate",
        "/{budget_id}/recalculate",
        "/{budget_id}/archive",
        "/{budget_id}/export/json",
        "/{budget_id}/export/csv",
    ]
    for endpoint_path in budget_id_endpoints:
        escaped = endpoint_path.replace("{", r"\{").replace("}", r"\}")
        pattern = f'@router\\.(?:get|post)\\(\\"{escaped}\\"'
        idx = re.search(pattern, source)
        assert idx, f"Endpoint {endpoint_path} not found"
        block = source[idx.start():]
        next_dec = re.search(r"\n@", block)
        func = block[:next_dec.start()] if next_dec else block
        assert "budget.project_id != project_id" in func, (
            f"{endpoint_path} endpoint must validate budget.project_id != project_id"
        )
