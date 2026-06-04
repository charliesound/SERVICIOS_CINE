"""
Contract test: document_routes.py gating invariants.

Verifies that document endpoints require tenant context and mutating
endpoints require write permission.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "document_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{document_id}", response_model=DocumentAssetResponse)',
    '@router.get("/{document_id}/events", response_model=DocumentEventListResponse)',
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


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_no_validate_project_access_import_needed():
    source = _read_source()
    assert "validate_project_access" not in source


def test_all_endpoints_have_tenant_context():
    source = _read_source()
    count = source.count("tenant: TenantContext = Depends(get_tenant_context)")
    count += source.count("tenant: TenantContext = Depends(require_write_permission)")
    assert count == 11, f"Expected 11 endpoints with tenant context, found {count}"


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    write_decorators = [
        '@router.post("", response_model=DocumentAssetResponse)',
        '@router.patch("/{document_id}", response_model=DocumentAssetResponse)',
        '@router.post("/{document_id}/extract", response_model=DocumentAssetResponse)',
        '@router.post("/{document_id}/classify", response_model=DocumentAssetResponse)',
        '@router.post("/{document_id}/structure", response_model=DocumentAssetResponse)',
        '@router.post("/{document_id}/approve", response_model=DocumentAssetResponse)',
        '@router.post("/{document_id}/derive-preview", response_model=DerivePreviewResponse)',
        '@router.post("/{document_id}/derive-report", response_model=DeriveReportResponse)',
    ]
    for decorator in write_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating document endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_project_helper_validates_tenant_project_membership():
    source = _read_source()
    helper_start = source.index("async def _get_project_for_tenant_or_404(")
    helper_block = source[helper_start:source.index("def _parse_json_payload(")]
    assert "Project.id == project_id" in helper_block
    assert "Project.organization_id == str(tenant.organization_id)" in helper_block


def test_create_document_validates_payload_project_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("", response_model=DocumentAssetResponse)',
    )
    assert "_get_project_for_tenant_or_404(payload.project_id, tenant, db)" in block


def test_list_documents_validates_project_id_filter():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("", response_model=DocumentAssetListResponse)',
    )
    assert "if project_id:" in block
    assert "_get_project_for_tenant_or_404(project_id, tenant, db)" in block


def test_document_lookup_is_tenant_scoped():
    source = _read_source()
    helper_start = source.index("async def _get_document_or_404(")
    helper_block = source[helper_start:source.index('@router.post("", response_model=DocumentAssetResponse)')]
    assert 'document_service.get_document(db, document_id, str(tenant.organization_id))' in helper_block


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
    assert total == 11, f"Expected 11 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET, found {get_count}"
    assert post_count == 7, f"Expected 7 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"
