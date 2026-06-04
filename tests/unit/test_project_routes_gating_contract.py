"""
Contract test: project_routes.py gating invariants.

Verifies that project-scoped endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "project_routes.py"


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


def test_conserves_require_module_access_for_script_analysis():
    source = _read_source()
    assert "require_module_access" in source
    assert 'require_module_access("script_analysis")' in source


def test_no_get_current_user_optional():
    source = _read_source()
    assert "get_current_user_optional" not in source


def test_project_id_endpoints_have_validate_project_access():
    source = _read_source()
    project_scoped_decorators = [
        '@router.get("/{project_id}", response_model=ProjectResponse)',
        '@router.get("/{project_id}/dashboard")',
        '@router.put("/{project_id}/script", response_model=ProjectResponse)',
        '@router.post("/{project_id}/script/upload", response_model=ProjectScriptUploadResponse)',
        '@router.post("/{project_id}/analyze", response_model=ScriptAnalysisResponse)',
        '@router.post("/{project_id}/storyboard", response_model=StoryboardResponse)',
        '@router.get("/{project_id}/jobs", response_model=ProjectJobListResponse)',
        '@router.get("/{project_id}/jobs/{job_id}", response_model=ProjectJobResponse)',
        '@router.get("/{project_id}/jobs/{job_id}/progress")',
        '@router.post("/{project_id}/jobs/{job_id}/retry", response_model=ProjectJobResponse)',
        '@router.get("/{project_id}/assets", response_model=ProjectAssetListResponse)',
        '@router.get("/{project_id}/metrics", response_model=ProjectMetricsResponse)',
        '@router.get("/{project_id}/export/json")',
        '@router.get("/{project_id}/export/zip")',
        '@router.get("/{project_id}/assets/image-assets", response_model=ProjectImageAssetsResponse)',
    ]
    for decorator in project_scoped_decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped endpoint missing validate_project_access: {decorator}"
        )


def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    write_decorators = [
        '@router.post("", response_model=ProjectResponse)',
        '@router.put("/{project_id}/script", response_model=ProjectResponse)',
        '@router.post("/{project_id}/script/upload", response_model=ProjectScriptUploadResponse)',
        '@router.post("/{project_id}/analyze", response_model=ScriptAnalysisResponse)',
        '@router.post("/{project_id}/storyboard", response_model=StoryboardResponse)',
        '@router.post("/{project_id}/jobs/{job_id}/retry", response_model=ProjectJobResponse)',
    ]
    for decorator in write_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating endpoint missing require_write_permission: {decorator}"
        )


def test_project_reads_do_not_gain_require_write_permission():
    source = _read_source()
    read_decorators = [
        '@router.get("")',
        '@router.get("/{project_id}", response_model=ProjectResponse)',
        '@router.get("/{project_id}/dashboard")',
        '@router.get("/{project_id}/jobs", response_model=ProjectJobListResponse)',
        '@router.get("/{project_id}/jobs/{job_id}", response_model=ProjectJobResponse)',
        '@router.get("/jobs/{job_id}")',
        '@router.get("/{project_id}/jobs/{job_id}/progress")',
        '@router.get("/{project_id}/assets", response_model=ProjectAssetListResponse)',
        '@router.get("/{project_id}/metrics", response_model=ProjectMetricsResponse)',
        '@router.get("/{project_id}/export/json")',
        '@router.get("/{project_id}/export/zip")',
        '@router.get("/{project_id}/assets/image-assets", response_model=ProjectImageAssetsResponse)',
    ]
    for decorator in read_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"Read endpoint should not have require_write_permission: {decorator}"
        )


def test_direct_job_lookup_stays_outside_project_validate():
    source = _read_source()
    block = _get_function_block(source, '@router.get("/jobs/{job_id}")')
    assert "validate_project_access" not in block
    assert "ProjectJob.organization_id == user_org_id" in block


def test_job_id_endpoints_validate_project_membership():
    source = _read_source()
    job_endpoints = [
        '@router.get("/{project_id}/jobs/{job_id}", response_model=ProjectJobResponse)',
        '@router.get("/{project_id}/jobs/{job_id}/progress")',
        '@router.post("/{project_id}/jobs/{job_id}/retry", response_model=ProjectJobResponse)',
    ]
    for decorator in job_endpoints:
        block = _get_function_block(source, decorator)
        assert "ProjectJob.id == job_id" in block, (
            f"{decorator} must query by job_id"
        )
        assert "ProjectJob.project_id == project_id" in block, (
            f"{decorator} must validate job belongs to project_id"
        )


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    put_count = len(re.findall(r"@router\.put\([^)]+\)", source))
    total = get_count + post_count + put_count
    assert total == 18, f"Expected 18 endpoints, found {total}"
    assert get_count == 12, f"Expected 12 GET, found {get_count}"
    assert post_count == 5, f"Expected 5 POST, found {post_count}"
    assert put_count == 1, f"Expected 1 PUT, found {put_count}"
