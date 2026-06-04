"""
Contract test: presentation_routes.py gating invariants.

Verifies that presentation endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "presentation_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/presentation/assets/{asset_id}/preview")',
    '@router.get("/{project_id}/presentation/assets/{asset_id}/thumbnail")',
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
        '@router.get("/{project_id}/presentation/filmstrip", response_model=PresentationFilmstripResponse)',
        '@router.get("/{project_id}/presentation/filmstrip.html", response_class=HTMLResponse)',
        '@router.get("/{project_id}/presentation/export/pdf")',
        '@router.post(\n    "/{project_id}/presentation/export/pdf/persist",',
        '@router.get("/{project_id}/presentation/assets/{asset_id}/preview")',
        '@router.get("/{project_id}/presentation/assets/{asset_id}/thumbnail")',
        '@router.post("/{project_id}/presentation/export-pdf", response_model=PresentationPdfExportResponse)',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped presentation endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post(\n    "/{project_id}/presentation/export/pdf/persist",',
        '@router.post("/{project_id}/presentation/export-pdf", response_model=PresentationPdfExportResponse)',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating presentation endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_asset_id_endpoints_keep_preview_service_scope():
    source = _read_source()
    for decorator in [
        '@router.get("/{project_id}/presentation/assets/{asset_id}/preview")',
        '@router.get("/{project_id}/presentation/assets/{asset_id}/thumbnail")',
    ]:
        block = _get_function_block(source, decorator)
        assert "presentation_service.get_asset_preview_payload(" in block, (
            f"Asset endpoint must keep scoped preview service lookup: {decorator}"
        )
        assert "project_id=project_id" in block, (
            f"Asset endpoint must pass project_id into preview lookup: {decorator}"
        )
        assert "asset_id=asset_id" in block, (
            f"Asset endpoint must pass asset_id into preview lookup: {decorator}"
        )


def test_persist_endpoint_uses_project_from_dependency():
    source = _read_source()
    block = _get_function_block(source, '@router.post(\n    "/{project_id}/presentation/export/pdf/persist",')
    assert "str(payload.project.organization_id)" in block
    assert "str(payload.project.id)" in block


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 7, f"Expected 7 endpoints, found {total}"
    assert get_count == 5, f"Expected 5 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"
