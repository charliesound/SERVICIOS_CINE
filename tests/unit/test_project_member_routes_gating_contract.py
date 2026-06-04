"""
Contract test: project_member_routes.py gating invariants.

Verifies that all project-scoped endpoints require tenant context,
project access validation, and write permission on mutating endpoints.
Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "project_member_routes.py"


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


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
    match = re.search(
        r"router = APIRouter\([^)]*\)",
        source,
    )
    assert match, "router = APIRouter(...) not found"
    block = match.group()
    assert "Depends(get_tenant_context)" in block, (
        "Router missing Depends(get_tenant_context)"
    )


ENDPOINTS_WITH_VALIDATE = {
    'GET /members':     '@router.get("")',
    'GET /members/me':  '@router.get("/me")',
    'POST /members':    '@router.post("")',
    'DELETE':           '@router.delete("/{user_id}")',
    'PATCH':            '@router.patch("/{user_id}")',
    'POST /delegate':   '@router.post("/delegate")',
    'GET /permissions': '@router.get("/{user_id}/permissions")',
}


def test_all_project_scoped_endpoints_have_validate_project_access():
    source = _read_source()
    for name, decorator in ENDPOINTS_WITH_VALIDATE.items():
        assert decorator in source, f"Missing decorator: {decorator}"
    validate_count = source.count("validate_project_access")
    assert validate_count >= 7, (
        f"Expected >=7 occurrences of validate_project_access, found {validate_count}"
    )


def test_write_endpoints_have_require_write_permission():
    source = _read_source()
    write_count = source.count("require_write_permission")
    assert write_count >= 4, (
        f"Expected >=4 occurrences of require_write_permission, found {write_count}"
    )


def test_roles_endpoint_excluded_from_validate_project_access():
    source = _read_source()
    roles_match = re.search(r'@router.get\("/roles"\)\s*\n', source)
    assert roles_match, "/roles endpoint not found"
    roles_start = roles_match.end()
    roles_block = source[roles_start:]
    next_decorator = re.search(r'\n@', roles_block)
    roles_body = roles_block[:next_decorator.start()] if next_decorator else roles_block
    assert "validate_project_access" not in roles_body, (
        "/roles endpoint should NOT have validate_project_access"
    )
    assert "require_organization" not in roles_body, (
        "/roles endpoint should NOT have require_organization"
    )


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    patch_count = len(re.findall(r"@router\.patch\([^)]+\)", source))
    delete_count = len(re.findall(r"@router\.delete\([^)]+\)", source))
    total = get_count + post_count + patch_count + delete_count
    assert total == 8, f"Expected 8 endpoints, found {total}"
    assert get_count >= 3, f"Expected >=3 GET, found {get_count}"
    assert post_count >= 2, f"Expected >=2 POST, found {post_count}"


def test_no_get_current_user_import():
    source = _read_source()
    assert "from routes.auth_routes import" not in source
