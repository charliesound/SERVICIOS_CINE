"""
Contract test: storage_routes.py gating invariants.

Verifies that storage endpoints require tenant context and that mutating
endpoints also require write permission.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "storage_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("", response_model=StorageSourceListResponse)',
    '@router.get("/{source_id}", response_model=StorageSourceResponse)',
    '@router.get(\n    "/{source_id}/authorizations", response_model=StorageAuthorizationListResponse\n)',
    '@router.get("/{source_id}/watch-paths", response_model=StorageWatchPathListResponse)',
    '@router.get("/{source_id}/handshake", response_model=StorageHandshakeResponse)',
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
        '@router.post("", response_model=StorageSourceResponse)',
        '@router.patch("/{source_id}", response_model=StorageSourceResponse)',
        '@router.post("/{source_id}/validate", response_model=StorageSourceValidateResponse)',
        '@router.post("/{source_id}/authorize", response_model=AuthResponseSchema)',
        '@router.post("/{source_id}/watch-paths", response_model=StorageWatchPathResponse)',
        '@router.post("/{source_id}/scan", response_model=IngestScanResponse)',
    ]
    for decorator in write_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating storage endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_storage_source_access_helper_validates_org_ownership():
    source = _read_source()
    helper_start = source.index("async def _check_storage_source_access(")
    helper_block = source[helper_start:source.index("def _source_response(")]
    assert "storage_service.get_storage_source" in helper_block
    assert "str(source.organization_id) != str(tenant.organization_id)" in helper_block


def test_watch_path_access_helper_validates_source_membership():
    source = _read_source()
    helper_start = source.index("async def _check_watch_path_access(")
    helper_block = source[helper_start:source.index("def _source_response(")]
    assert "StorageWatchPath.id == watch_path_id" in helper_block
    assert "StorageWatchPath.storage_source_id == source_id" in helper_block
    assert "_check_storage_source_access(source_id, tenant, db)" in helper_block


def test_launch_scan_validates_watch_path_when_present():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/{source_id}/scan", response_model=IngestScanResponse)',
    )
    assert "if payload.watch_path_id:" in block
    assert "_check_watch_path_access(" in block


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
    assert get_count == 5, f"Expected 5 GET, found {get_count}"
    assert post_count == 5, f"Expected 5 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"
