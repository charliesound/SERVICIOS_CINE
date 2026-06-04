"""
Contract test: editorial_routes.py gating invariants.

Verifies that all editorial endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "editorial_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/{project_id}/editorial/assembly", response_model=AssemblyCutResponse)',
    '@router.get("/{project_id}/editorial/export/fcpxml")',
    '@router.get("/{project_id}/editorial/media-relink-report", response_model=EditorialMediaRelinkReportResponse)',
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


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.get("/{project_id}/editorial/takes", response_model=EditorialTakeListResponse)',
        '@router.post("/{project_id}/editorial/reconcile", response_model=EditorialReconcileResponse, dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/score", response_model=EditorialScoreResponse, dependencies=[Depends(require_write_permission)])',
        '@router.get("/{project_id}/editorial/audio-metadata", response_model=EditorialAudioMetadataListResponse)',
        '@router.post("/{project_id}/editorial/audio-metadata/scan", response_model=EditorialAudioMetadataScanResponse, dependencies=[Depends(require_write_permission)])',
        '@router.get("/{project_id}/editorial/recommended-takes", response_model=EditorialRecommendedTakeListResponse)',
        '@router.post("/{project_id}/editorial/assembly", response_model=AssemblyCutCreateResponse, dependencies=[Depends(require_write_permission)])',
        '@router.get("/{project_id}/editorial/assembly", response_model=AssemblyCutResponse)',
        '@router.get("/{project_id}/editorial/export/fcpxml")',
        '@router.get("/{project_id}/editorial/export/fcpxml/validate", response_model=EditorialFCPXMLValidationResponse)',
        '@router.get("/{project_id}/editorial/media-relink-report", response_model=EditorialMediaRelinkReportResponse)',
        '@router.post("/{project_id}/editorial/export/package", dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/export/davinci-package", dependencies=[Depends(require_write_permission)])',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped editorial endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/{project_id}/editorial/reconcile", response_model=EditorialReconcileResponse, dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/score", response_model=EditorialScoreResponse, dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/audio-metadata/scan", response_model=EditorialAudioMetadataScanResponse, dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/assembly", response_model=AssemblyCutCreateResponse, dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/export/package", dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/export/davinci-package", dependencies=[Depends(require_write_permission)])',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating editorial endpoint missing require_write_permission: {decorator}"
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
    assert "async def _get_project_for_tenant(" not in source


def test_editorial_exports_reuse_project_organization_id():
    source = _read_source()
    for decorator in [
        '@router.post("/{project_id}/editorial/assembly", response_model=AssemblyCutCreateResponse, dependencies=[Depends(require_write_permission)])',
        '@router.get("/{project_id}/editorial/export/fcpxml")',
        '@router.post("/{project_id}/editorial/export/package", dependencies=[Depends(require_write_permission)])',
        '@router.post("/{project_id}/editorial/export/davinci-package", dependencies=[Depends(require_write_permission)])',
    ]:
        block = _get_function_block(source, decorator)
        assert "str(project.organization_id)" in block, (
            f"Endpoint must reuse dependency project.organization_id: {decorator}"
        )


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 13, f"Expected 13 endpoints, found {total}"
    assert get_count == 7, f"Expected 7 GET, found {get_count}"
    assert post_count == 6, f"Expected 6 POST, found {post_count}"
