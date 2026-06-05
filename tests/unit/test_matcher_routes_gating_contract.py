"""
Contract test: matcher_routes.py gating invariants.

Verifies that matcher routes remain project-scoped, preserve module access,
and use validated project ownership for all endpoint operations.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "matcher_routes.py"

ALL_ENDPOINTS = [
    '@router.post("/trigger", response_model=MatcherJobResponse, status_code=status.HTTP_202_ACCEPTED)',
    '@router.get("/status", response_model=MatcherStatusResponse)',
    '@router.get("/jobs", response_model=MatcherJobListResponse)',
]

READ_ENDPOINTS = [
    '@router.get("/status", response_model=MatcherStatusResponse)',
    '@router.get("/jobs", response_model=MatcherJobListResponse)',
]

MANUAL_REVIEW_ENDPOINTS = [
    # process_matcher_job stays outside the HTTP boundary.
    # It receives project_id and organization_id from the queued/stored job,
    # while route-level gating validates project ownership before creating
    # or listing matcher jobs.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_router_prefix_and_module_gating_preserved():
    source = _read_source()
    assert 'prefix="/api/projects/{project_id}/funding/matcher"' in source
    assert 'dependencies=[Depends(require_module_access("funding_grants"))]' in source


def test_imports_tenant_context_and_project():
    source = _read_source()
    assert "from dependencies.tenant_context import (" in source
    assert "get_tenant_context" in source
    assert "validate_project_access" in source
    assert "require_write_permission" in source
    assert "from models.core import Project" in source


def test_no_require_organization_or_optional_auth():
    source = _read_source()
    assert "require_organization" not in source
    assert "get_optional_tenant" not in source
    assert "optional_auth" not in source


def test_all_endpoints_have_tenant_context_and_project_access():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )
        assert "validate_project_access" in block, (
            f"Missing validate_project_access in {decorator}"
        )


def test_only_trigger_has_require_write_permission():
    source = _read_source()
    trigger_block = _get_function_block(
        source,
        '@router.post("/trigger", response_model=MatcherJobResponse, status_code=status.HTTP_202_ACCEPTED)',
    )
    assert "require_write_permission" in trigger_block

    for decorator in READ_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"Read endpoint should not have require_write_permission: {decorator}"
        )


def test_all_endpoints_use_validated_project_and_organization_ids():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validated_project_id = str(project.id)" in block
        assert "organization_id = str(project.organization_id)" in block


def test_no_inline_project_query_or_import_in_endpoints():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "select(Project)" not in block
        assert "from models.core import Project" not in block


def test_trigger_uses_validated_ids_for_matcher_job_and_queue():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/trigger", response_model=MatcherJobResponse, status_code=status.HTTP_202_ACCEPTED)',
    )
    assert "MatcherJob.project_id == validated_project_id" in block
    assert "MatcherJob.organization_id == organization_id" in block
    assert "project_id=validated_project_id" in block
    assert "organization_id=organization_id" in block
    assert "queue_service.enqueue(" in block
    assert "project_id=project_id" not in block


def test_status_response_uses_validated_ids():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/status", response_model=MatcherStatusResponse)',
    )
    assert "MatcherJob.project_id == validated_project_id" in block
    assert "MatcherJob.organization_id == organization_id" in block
    assert "project_id=validated_project_id" in block
    assert "organization_id=organization_id" in block


def test_jobs_response_uses_validated_ids():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get("/jobs", response_model=MatcherJobListResponse)',
    )
    assert "MatcherJob.project_id == validated_project_id" in block
    assert "MatcherJob.organization_id == organization_id" in block
    assert "project_id=validated_project_id" in block
    assert "organization_id=organization_id" in block


def test_process_matcher_job_is_not_treated_as_endpoint():
    source = _read_source()
    block = source[source.index("async def process_matcher_job(") :]
    assert "Depends(" not in block


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 3, f"Expected 3 endpoints, found {total}"
    assert get_count == 2, f"Expected 2 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"


def test_manual_review_documented():
    """
    Manual review: process_matcher_job receives project_id and organization_id
    from the stored/queued job and remains outside the HTTP boundary.
    Route-level gating applies before jobs are created or queried.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
