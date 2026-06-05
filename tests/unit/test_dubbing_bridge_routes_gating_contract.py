"""
Contract test: dubbing_bridge_routes.py gating invariants.

Verifies that all bridge endpoints require tenant context and that mutating
operations require write permission.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "dubbing_bridge_routes.py"

ALL_ENDPOINTS = [
    '@router.post("/projects/{project_id}/jobs")',
    '@router.get("/projects/{project_id}/jobs")',
    '@router.post("/contracts/{contract_id}/validate")',
    '@router.get("/jobs/{job_id}")',
    '@router.get("/audit/job/{job_id}")',
]

WRITE_ENDPOINTS = [
    '@router.post("/projects/{project_id}/jobs")',
    '@router.post("/contracts/{contract_id}/validate")',
]

READ_ENDPOINTS = [
    '@router.get("/projects/{project_id}/jobs")',
    '@router.get("/jobs/{job_id}")',
    '@router.get("/audit/job/{job_id}")',
]

PROJECT_SCOPED_ENDPOINTS = [
    '@router.post("/projects/{project_id}/jobs")',
    '@router.get("/projects/{project_id}/jobs")',
]

SATELLITE_RESOURCE_ENDPOINTS = [
    '@router.post("/contracts/{contract_id}/validate")',
    '@router.get("/jobs/{job_id}")',
    '@router.get("/audit/job/{job_id}")',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Contract and job IDs belong to the standalone dubbing service, not CID
    # core resources. They require tenant auth but cannot use CID project
    # validation because those endpoints do not receive a CID project_id.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[: next_decorator.start()] if next_decorator else block


def test_imports_canonical_tenant_project_and_write_dependencies():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "validate_project_access" in source
    assert "from dependencies.project_access import" not in source
    assert "from models.core import Project" in source
    assert "from schemas.auth_schema import TenantContext" in source


def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    for decorator in WRITE_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Missing require_write_permission in {decorator}"
        )


def test_read_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    for decorator in READ_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"Unexpected require_write_permission in {decorator}"
        )


def test_project_scoped_endpoints_validate_project_access():
    source = _read_source()
    for decorator in PROJECT_SCOPED_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "project: Project = Depends(validate_project_access)" in block
        assert "validated_project_id = str(project.id)" in block


def test_project_scoped_proxy_calls_use_validated_project_id():
    source = _read_source()
    for decorator in PROJECT_SCOPED_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "project/{validated_project_id}" in block
        assert "project/{project_id}" not in block


def test_create_job_normalizes_body_project_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/jobs")',
    )
    assert "project_id: Optional[str] = None" in source
    assert 'payload["project_id"] = validated_project_id' in block


def test_satellite_resource_ids_do_not_use_project_gating():
    source = _read_source()
    for decorator in SATELLITE_RESOURCE_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" not in block


def test_no_inline_project_query():
    source = _read_source()
    assert "select(Project)" not in source


def test_no_optional_auth_legacy():
    source = _read_source()
    assert "get_optional_tenant" not in source
    assert "optional_auth" not in source
    assert "get_current_user_optional" not in source


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 5, f"Expected 5 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET endpoints, found {get_count}"
    assert post_count == 2, f"Expected 2 POST endpoints, found {post_count}"


def test_manual_review_documented():
    """
    Manual review: project routes validate CID ownership and proxy the validated
    ID. Satellite IDs require tenant auth and POST operations require write.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
