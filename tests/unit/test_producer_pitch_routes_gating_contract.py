"""
Contract test: producer_pitch_routes.py gating invariants.

Verifies that producer pitch endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "producer_pitch_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/producer-pitch/{pack_id}")',
    '@router.get("/{project_id}/producer-pitch/{pack_id}/export/json")',
    '@router.get("/{project_id}/producer-pitch/{pack_id}/export/zip")',
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
    assert 'require_module_access("pitch_deck")' in source


def test_no_auth_routes_import_for_tenant_context():
    source = _read_source()
    assert "from routes.auth_routes import get_tenant_context" not in source


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.get("/{project_id}/producer-pitch")',
        '@router.get("/{project_id}/producer-pitch/active")',
        '@router.post("/{project_id}/producer-pitch/generate")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}")',
        '@router.patch("/{project_id}/producer-pitch/{pack_id}")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/approve")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/archive")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/json")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/markdown")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/zip")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped producer pitch endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/producer-pitch/generate")',
        '@router.patch("/{project_id}/producer-pitch/{pack_id}")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/approve")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/archive")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating producer pitch endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_pack_id_endpoints_still_validate_project_membership():
    source = _read_source()
    for decorator in [
        '@router.get("/{project_id}/producer-pitch/{pack_id}")',
        '@router.patch("/{project_id}/producer-pitch/{pack_id}")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/approve")',
        '@router.post("/{project_id}/producer-pitch/{pack_id}/archive")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/json")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/markdown")',
        '@router.get("/{project_id}/producer-pitch/{pack_id}/export/zip")',
    ]:
        block = _get_function_block(source, decorator)
        assert "pack.project_id != project_id" in block, (
            f"Pack endpoint must still validate pack belongs to project: {decorator}"
        )


def test_inline_project_query_removed():
    source = _read_source()
    for line in source.splitlines():
        stripped = line.strip()
        assert stripped != "project = await db.get(Project, project_id)", (
            "Found legacy inline project lookup; should use validate_project_access"
        )


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    patch_count = len(re.findall(r"@router\.patch\([^)]+\)", source))
    total = get_count + post_count + patch_count
    assert total == 10, f"Expected 10 endpoints, found {total}"
    assert get_count == 6, f"Expected 6 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"
