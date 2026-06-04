"""
Contract test: change_governance_routes.py gating invariants.

Verifies that all endpoints require tenant context, project access validation,
and write permission on mutating endpoints.
Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
SERVICE_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "services"
TARGET_FILE = ROUTES_DIR / "change_governance_routes.py"
SERVICE_FILE = SERVICE_DIR / "change_governance_service.py"


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _read_service() -> str:
    assert SERVICE_FILE.exists(), f"File not found: {SERVICE_FILE}"
    return SERVICE_FILE.read_text("utf-8")


def test_imports_get_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source


def test_imports_validate_project_access():
    source = _read_source()
    assert "validate_project_access" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_no_get_current_user_optional():
    source = _read_source()
    assert "get_current_user_optional" not in source


def test_no_UserResponse_import():
    source = _read_source()
    assert "UserResponse" not in source


def test_router_has_get_tenant_context_dependency():
    source = _read_source()
    match = re.search(r"router = APIRouter\([^)]*\)", source)
    assert match, "router = APIRouter(...) not found"
    block = match.group()
    assert "Depends(get_tenant_context)" in block, (
        "Router missing Depends(get_tenant_context)"
    )


def test_all_endpoints_have_validate_project_access():
    source = _read_source()
    validate_count = source.count("validate_project_access")
    assert validate_count >= 6, (
        f"Expected >=6 occurrences of validate_project_access, found {validate_count}"
    )


def test_write_endpoints_have_require_write_permission():
    source = _read_source()
    write_count = source.count("require_write_permission")
    assert write_count >= 4, (
        f"Expected >=4 occurrences of require_write_permission, found {write_count}"
    )


def test_get_endpoints_no_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r'@router\.get\([^)]+\)', source)
    for dec in get_decorators:
        idx = source.index(dec)
        # Look at the function body after this decorator
        block_after = source[idx:]
        next_decorator = re.search(r'\n@', block_after)
        func_body = block_after[:next_decorator.start()] if next_decorator else block_after
        assert "require_write_permission" not in func_body, (
            f"GET endpoint should NOT have require_write_permission: {dec}"
        )


def test_apply_uses_project_id():
    source = _read_source()
    apply_idx = source.index('@router.post("/{change_request_id}/apply")')
    block = source[apply_idx:]
    next_dec = re.search(r'\n@', block)
    func_body = block[:next_dec.start()] if next_dec else block
    assert "cr.project_id != project_id" in func_body, (
        "apply endpoint must validate change request belongs to project_id"
    )


def test_apply_has_require_write_permission():
    source = _read_source()
    apply_idx = source.index('@router.post("/{change_request_id}/apply")')
    block = source[apply_idx:]
    next_dec = re.search(r'\n@', block)
    func_body = block[:next_dec.start()] if next_dec else block
    assert "require_write_permission" in func_body, (
        "apply endpoint must have require_write_permission"
    )


def test_can_approve_delegates():
    service = _read_service()
    lines = service.splitlines()
    in_func = False
    found_delegation = False
    found_unconditional = False
    for line in lines:
        if re.match(r"^(async\s+)?def can_approve\(", line):
            in_func = True
            continue
        if in_func:
            if re.match(r"^(async\s+)?def ", line) or line.startswith("class "):
                break
            if "can_approve_async" in line:
                found_delegation = True
            if "return True" in line:
                found_unconditional = True
    assert found_delegation, "can_approve must delegate to can_approve_async"
    assert not found_unconditional, "can_approve must not return True unconditionally"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 6, f"Expected 6 endpoints, found {total}"
    assert get_count == 2, f"Expected 2 GET, found {get_count}"
    assert post_count == 4, f"Expected 4 POST, found {post_count}"
