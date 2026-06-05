"""
Contract test: comfyui_storyboard_routes.py gating invariants.

Verifies that comfyui storyboard endpoints require tenant context
and appropriate write permission.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "comfyui_storyboard_routes.py"

ALL_ENDPOINTS = [
    '@router.get("/ops/comfyui/storyboard/status")',
    '@router.post("/projects/{project_id}/storyboard/render")',
]

WRITE_ENDPOINTS = [
    '@router.post("/projects/{project_id}/storyboard/render")',
]

READ_ENDPOINTS = [
    '@router.get("/ops/comfyui/storyboard/status")',
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
    assert "routes.auth_routes" not in source, "Must import from dependencies.tenant_context"


def test_no_legacy_auth_imports():
    source = _read_source()
    assert "from routes.auth_routes" not in source
    assert "from schemas.auth_schema import" not in source


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


def test_render_endpoint_has_module_access():
    source = _read_source()
    block = _get_function_block(
        source, '@router.post("/projects/{project_id}/storyboard/render")'
    )
    assert 'require_module_access("storyboard_ai")' in block


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 2, f"Expected 2 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"
