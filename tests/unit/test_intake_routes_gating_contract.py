"""
Contract test: intake_routes.py gating invariants.

Verifies that intake endpoints require tenant context,
project access validation on project routes, and write permission on
mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "intake_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/analysis/summary")',
    '@router.get("/{project_id}/breakdown/scenes")',
    '@router.get("/{project_id}/breakdown/departments")',
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


def test_conserves_module_access_dependencies():
    source = _read_source()
    assert 'require_module_access("script_analysis")' in source
    assert 'require_module_access("breakdown")' in source


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/intake/script")',
        '@router.post("/{project_id}/analysis/run")',
        '@router.get("/{project_id}/analysis/summary")',
        '@router.get("/{project_id}/breakdown/scenes")',
        '@router.get("/{project_id}/breakdown/departments")',
        '@router.get("/{project_id}/analysis/export")',
        '@router.get("/{project_id}/breakdown/export")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped intake endpoint missing validate_project_access: {decorator}"
        )


def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/intake/idea")',
        '@router.post("/{project_id}/intake/script")',
        '@router.post("/{project_id}/analysis/run")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating intake endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_inline_project_query_removed_from_project_endpoints():
    source = _read_source()
    for line in source.splitlines():
        stripped = line.strip()
        assert stripped != "select(Project).where(Project.id == project_id)", (
            "Found legacy inline project query; should use validate_project_access"
        )


def test_analysis_run_reuses_project_organization_id():
    source = _read_source()
    block = _get_function_block(source, '@router.post("/{project_id}/analysis/run")')
    assert "organization_id = str(project.organization_id)" in block
    assert "analysis_service.run_analysis(" in block


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 8, f"Expected 8 endpoints, found {total}"
    assert get_count == 5, f"Expected 5 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"
