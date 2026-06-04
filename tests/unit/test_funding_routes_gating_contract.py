"""
Contract test: funding_routes.py gating invariants.

Verifies that project-scoped funding endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "funding_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/funding/matches/{match_id}/evidence")',
    '@router.get("/{project_id}/funding/matcher-status")',
    '@router.get("/{project_id}/funding/profile")',
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


def test_sync_sources_is_write_gated():
    source = _read_source()
    block = _get_function_block(source, '@funding_router.post("/sources/sync")')
    assert "require_write_permission" in block


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.get("/{project_id}/funding/dossier")',
        '@router.get("/{project_id}/funding/dossier/export/pdf")',
        '@router.post("/{project_id}/funding/dossier/export/pdf/persist")',
        '@router.post("/{project_id}/funding/recompute")',
        '@router.get("/{project_id}/funding/matches")',
        '@router.post("/{project_id}/funding/recompute-rag")',
        '@router.get("/{project_id}/funding/matches-rag")',
        '@router.get("/{project_id}/funding/matches/{match_id}/evidence")',
        '@router.get("/{project_id}/funding/matcher-status")',
        '@router.get("/{project_id}/funding/checklist")',
        '@router.get("/{project_id}/funding/profile")',
        '@router.post("/{project_id}/budget/estimate")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped funding endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@funding_router.post("/sources/sync")',
        '@router.post("/{project_id}/funding/dossier/export/pdf/persist")',
        '@router.post("/{project_id}/funding/recompute")',
        '@router.post("/{project_id}/funding/recompute-rag")',
        '@router.post("/{project_id}/budget/estimate")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating funding endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@(?:router|funding_router)\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_inline_project_query_removed_from_project_endpoints():
    source = _read_source()
    assert "async def _get_project_or_403(" not in source
    for line in source.splitlines():
        stripped = line.strip()
        assert stripped != 'select(Project).where(Project.id == project_id)', (
            "Found legacy inline project query; should use validate_project_access"
        )


def test_project_endpoints_reuse_project_organization_id():
    source = _read_source()
    for decorator in [
        '@router.get("/{project_id}/funding/dossier")',
        '@router.get("/{project_id}/funding/dossier/export/pdf")',
        '@router.post("/{project_id}/funding/dossier/export/pdf/persist")',
        '@router.post("/{project_id}/funding/recompute")',
        '@router.get("/{project_id}/funding/matches")',
        '@router.post("/{project_id}/funding/recompute-rag")',
        '@router.get("/{project_id}/funding/matches-rag")',
        '@router.get("/{project_id}/funding/matches/{match_id}/evidence")',
        '@router.get("/{project_id}/funding/matcher-status")',
        '@router.get("/{project_id}/funding/checklist")',
        '@router.post("/{project_id}/budget/estimate")',
    ]:
        block = _get_function_block(source, decorator)
        assert "organization_id = str(project.organization_id)" in block, (
            f"Endpoint must reuse dependency project.organization_id: {decorator}"
        )


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    funding_public_post = len(re.findall(r"@funding_router\.post\([^)]+\)", source))
    funding_public_get = len(re.findall(r"@funding_router\.get\([^)]+\)", source))
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = funding_public_post + funding_public_get + get_count + post_count
    assert total == 15, f"Expected 15 endpoints, found {total}"
    assert funding_public_post == 1, f"Expected 1 public POST, found {funding_public_post}"
    assert funding_public_get == 2, f"Expected 2 public GET, found {funding_public_get}"
    assert get_count == 8, f"Expected 8 project GET, found {get_count}"
    assert post_count == 4, f"Expected 4 project POST, found {post_count}"
