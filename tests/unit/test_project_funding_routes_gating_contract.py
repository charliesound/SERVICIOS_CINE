"""
Contract test: project_funding_routes.py gating invariants.

Verifies that all project funding endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "project_funding_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/funding/tracking/{tracking_id}")',
    '@router.get("/{project_id}/funding/tracking/{tracking_id}/checklist")',
    '@router.get("/{project_id}/funding/notifications")',
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
    assert 'require_module_access("funding_grants")' in source


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.get("/{project_id}/funding/private-sources")',
        '@router.post("/{project_id}/funding/private-sources")',
        '@router.patch("/{project_id}/funding/private-sources/{source_id}")',
        '@router.delete("/{project_id}/funding/private-sources/{source_id}")',
        '@router.get("/{project_id}/funding/private-summary")',
        '@router.post("/{project_id}/funding/tracking")',
        '@router.get("/{project_id}/funding/tracking")',
        '@router.get("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.delete("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.get("/{project_id}/funding/tracking/{tracking_id}/checklist")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}/checklist/{item_id}")',
        '@router.get("/{project_id}/funding/notifications")',
        '@router.patch("/{project_id}/funding/notifications/{notification_id}/read")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped funding endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/funding/private-sources")',
        '@router.patch("/{project_id}/funding/private-sources/{source_id}")',
        '@router.delete("/{project_id}/funding/private-sources/{source_id}")',
        '@router.post("/{project_id}/funding/tracking")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.delete("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}/checklist/{item_id}")',
        '@router.patch("/{project_id}/funding/notifications/{notification_id}/read")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating funding endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_inline_project_query_removed():
    source = _read_source()
    for line in source.splitlines():
        stripped = line.strip()
        assert stripped != 'select(Project).where(Project.id == project_id)', (
            "Found legacy inline project query; should use validate_project_access"
        )


def test_tracking_and_notification_endpoints_still_scope_by_org():
    source = _read_source()
    for decorator in [
        '@router.get("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.delete("/{project_id}/funding/tracking/{tracking_id}")',
        '@router.get("/{project_id}/funding/tracking/{tracking_id}/checklist")',
        '@router.patch("/{project_id}/funding/tracking/{tracking_id}/checklist/{item_id}")',
        '@router.get("/{project_id}/funding/notifications")',
        '@router.patch("/{project_id}/funding/notifications/{notification_id}/read")',
    ]:
        block = _get_function_block(source, decorator)
        assert "organization_id=str(project.organization_id)" in block, (
            f"Endpoint must keep organization scoping: {decorator}"
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
    delete_count = len(re.findall(r"@router\.delete\([^)]+\)", source))
    total = get_count + post_count + patch_count + delete_count
    assert total == 14, f"Expected 14 endpoints, found {total}"
    assert get_count == 6, f"Expected 6 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"
    assert patch_count == 4, f"Expected 4 PATCH, found {patch_count}"
    assert delete_count == 2, f"Expected 2 DELETE, found {delete_count}"
