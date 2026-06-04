"""
Contract test: report_routes.py gating invariants.

Verifies that report endpoints require tenant context and mutating
endpoints require write permission.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "report_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '@router.get("/camera-reports/{report_id}", response_model=CameraReportResponse)',
    '@router.get("/sound-reports/{report_id}", response_model=SoundReportResponse)',
    '@router.get("/script-notes/{report_id}", response_model=ScriptNoteResponse)',
    '@router.get("/director-notes/{report_id}", response_model=DirectorNoteResponse)',
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


def test_no_optional_auth_pattern_remains():
    source = _read_source()
    assert "get_current_user_optional" not in source
    assert "UserResponse" not in source
    assert '_get_user_org_or_401' not in source


def test_all_endpoints_have_tenant_context():
    source = _read_source()
    count = source.count("tenant: TenantContext = Depends(get_tenant_context)")
    count += source.count("tenant: TenantContext = Depends(require_write_permission)")
    assert count == 16, f"Expected 16 endpoints with tenant context, found {count}"


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    decorators = [
        '@router.post("/camera-reports", response_model=CameraReportResponse)',
        '@router.patch("/camera-reports/{report_id}", response_model=CameraReportResponse)',
        '@router.post("/sound-reports", response_model=SoundReportResponse)',
        '@router.patch("/sound-reports/{report_id}", response_model=SoundReportResponse)',
        '@router.post("/script-notes", response_model=ScriptNoteResponse)',
        '@router.patch("/script-notes/{report_id}", response_model=ScriptNoteResponse)',
        '@router.post("/director-notes", response_model=DirectorNoteResponse)',
        '@router.patch("/director-notes/{report_id}", response_model=DirectorNoteResponse)',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating report endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_report_lookup_is_org_scoped():
    source = _read_source()
    helper_start = source.index("async def _get_report_or_404(")
    helper_block = source[helper_start:source.index('@router.post("/camera-reports", response_model=CameraReportResponse)')]
    assert 'report_service.get_report(' in helper_block
    assert 'organization_id' in helper_block


def test_create_and_update_reuse_tenant_user_and_org():
    source = _read_source()
    for decorator in [
        '@router.post("/camera-reports", response_model=CameraReportResponse)',
        '@router.patch("/camera-reports/{report_id}", response_model=CameraReportResponse)',
        '@router.post("/sound-reports", response_model=SoundReportResponse)',
        '@router.patch("/sound-reports/{report_id}", response_model=SoundReportResponse)',
        '@router.post("/script-notes", response_model=ScriptNoteResponse)',
        '@router.patch("/script-notes/{report_id}", response_model=ScriptNoteResponse)',
        '@router.post("/director-notes", response_model=DirectorNoteResponse)',
        '@router.patch("/director-notes/{report_id}", response_model=DirectorNoteResponse)',
    ]:
        block = _get_function_block(source, decorator)
        assert "tenant.organization_id" in block or "str(tenant.organization_id)" in block
        assert "tenant.user_id" in block


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
    assert total == 16, f"Expected 16 endpoints, found {total}"
    assert get_count == 8, f"Expected 8 GET, found {get_count}"
    assert post_count == 4, f"Expected 4 POST, found {post_count}"
    assert patch_count == 4, f"Expected 4 PATCH, found {patch_count}"
