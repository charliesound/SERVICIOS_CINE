"""
Contract test: project_document_routes.py gating invariants.

Verifies that project document endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "project_document_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/documents/{document_id}", response_model=ProjectDocumentResponse)',
    '@router.get("/{project_id}/documents/{document_id}/download")',
    '@router.get(\n    "/{project_id}/documents/{document_id}/chunks",',
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


def test_no_auth_routes_import_for_tenant_context():
    source = _read_source()
    assert "from routes.auth_routes import get_tenant_context" not in source


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/documents", response_model=ProjectDocumentResponse, status_code=201)',
        '@router.get("/{project_id}/documents", response_model=ProjectDocumentListResponse)',
        '@router.get("/{project_id}/documents/{document_id}", response_model=ProjectDocumentResponse)',
        '@router.get("/{project_id}/documents/{document_id}/download")',
        '@router.delete("/{project_id}/documents/{document_id}")',
        '@router.post("/{project_id}/documents/reindex", response_model=ProjectDocumentReindexResponse)',
        '@router.get(\n    "/{project_id}/documents/{document_id}/chunks",',
        '@router.post("/{project_id}/ask", response_model=ProjectDocumentAskResponse)',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped project document endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/documents", response_model=ProjectDocumentResponse, status_code=201)',
        '@router.delete("/{project_id}/documents/{document_id}")',
        '@router.post("/{project_id}/documents/reindex", response_model=ProjectDocumentReindexResponse)',
        '@router.post("/{project_id}/ask", response_model=ProjectDocumentAskResponse)',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating project document endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_inline_project_helper_removed():
    source = _read_source()
    assert "async def _get_project_or_403(" not in source


def test_document_id_endpoints_keep_document_membership_checks():
    source = _read_source()
    for decorator in [
        '@router.get("/{project_id}/documents/{document_id}", response_model=ProjectDocumentResponse)',
        '@router.get("/{project_id}/documents/{document_id}/download")',
        '@router.delete("/{project_id}/documents/{document_id}")',
        '@router.get(\n    "/{project_id}/documents/{document_id}/chunks",',
    ]:
        block = _get_function_block(source, decorator)
        assert "project_document_service.get_document(" in block, (
            f"Document endpoint must keep scoped document lookup: {decorator}"
        )
        assert "project_id=str(project.id)" in block, (
            f"Document endpoint must scope lookup by project.id: {decorator}"
        )
        assert "organization_id=str(project.organization_id)" in block, (
            f"Document endpoint must scope lookup by project.organization_id: {decorator}"
        )


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    delete_count = len(re.findall(r"@router\.delete\([^)]+\)", source))
    total = get_count + post_count + delete_count
    assert total == 8, f"Expected 8 endpoints, found {total}"
    assert get_count == 4, f"Expected 4 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"
