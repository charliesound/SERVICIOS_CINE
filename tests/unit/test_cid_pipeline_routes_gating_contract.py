"""
Contract test: cid_pipeline_routes.py gating invariants.

Verifies that pipeline endpoints require tenant context,
appropriate write permission, feature flag gating, and
centralized project validation via helper (not inline queries).

This router is MIXED tenant/project — project_id comes from
body or query, NOT from path. Therefore validate_project_access
(which expects path param) is NOT usable as Depends() here.
A local helper _validate_pipeline_project_access is used instead.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "cid_pipeline_routes.py"

# --- Endpoint decorators ---

ALL_ENDPOINTS = [
    '@router.get(\n    "/presets"',
    '@router.post(\n    "/generate"',
    '@router.post(\n    "/validate"',
    '@router.post(\n    "/execute"',
    '@router.get(\n    "/jobs"',
    '@router.get(\n    "/jobs/{job_id}"',
]

WRITE_ENDPOINTS = [
    '@router.post(\n    "/generate"',
    '@router.post(\n    "/validate"',
    '@router.post(\n    "/execute"',
]

READ_ENDPOINTS = [
    '@router.get(\n    "/presets"',
    '@router.get(\n    "/jobs"',
    '@router.get(\n    "/jobs/{job_id}"',
]

# Endpoints that receive a project_id (body or query)
PROJECT_AWARE_ENDPOINTS = [
    '@router.post(\n    "/generate"',
    '@router.post(\n    "/validate"',
    '@router.post(\n    "/execute"',
    '@router.get(\n    "/jobs"',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Router is mixed tenant/project. validate_project_access (Depends) is
    # not applicable because project_id does not come from URL path.
    # Local helper _validate_pipeline_project_access provides equivalent
    # gating using canonical get_project_for_tenant from tenant_access_service.
    # Deep ownership for jobs is scoped by organization_id + user_id in
    # cid_pipeline_simulated_job_service. get_pipeline_job has no project_id
    # and scopes by tenant.organization_id + user_id + is_global_admin.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    # Find next decorator (but skip multiline decorator blocks)
    next_at = re.search(r"\n@router\.", block[1:])
    return block[:next_at.start() + 1] if next_at else block


# --- Import tests ---

def test_imports_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source
    assert "TenantContext" in source or "from schemas.auth_schema import TenantContext" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_imports_project_model():
    source = _read_source()
    assert "from models.core import Project" in source


def test_imports_get_project_for_tenant():
    """Canonical tenant access function should be imported."""
    source = _read_source()
    assert "from services.tenant_access_service import get_project_for_tenant" in source


# --- Feature flag ---

def test_all_endpoints_have_feature_flag():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_cid_pipeline_builder_enabled" in block, (
            f"Missing require_cid_pipeline_builder_enabled in {decorator!r}"
        )


# --- Tenant context ---

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator!r}"
        )


# --- Write permission ---

def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    for decorator in WRITE_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Missing require_write_permission in {decorator!r}"
        )


def test_read_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    for decorator in READ_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"Unexpected require_write_permission in {decorator!r}"
        )


# --- Centralized project validation ---

def test_centralized_validation_helper_exists():
    """A centralized local helper should exist for pipeline project access."""
    source = _read_source()
    assert "_validate_pipeline_project_access" in source


def test_no_legacy_get_project_or_403():
    """Legacy inline project check must be replaced by centralized helper."""
    source = _read_source()
    assert "_get_project_or_403" not in source, (
        "Legacy _get_project_or_403 should be replaced by _validate_pipeline_project_access"
    )


def test_validation_helper_uses_canonical_function():
    """The local validation helper should use get_project_for_tenant."""
    source = _read_source()
    # Find the helper body
    idx = source.index("_validate_pipeline_project_access")
    helper_block = source[idx:idx + 800]
    assert "get_project_for_tenant" in helper_block, (
        "_validate_pipeline_project_access must use canonical get_project_for_tenant"
    )


def test_no_inline_validation_in_endpoints():
    """Endpoints should not have inline select(Project) queries."""
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "select(Project)" not in block, (
            f"Inline select(Project) found in endpoint {decorator!r}"
        )


def test_select_project_only_in_helper():
    """select(Project) should only appear in centralized validation helper."""
    source = _read_source()
    # If select(Project) exists at all, it must be in the helper only
    occurrences = [m.start() for m in re.finditer(r"select\(Project\)", source)]
    if occurrences:
        helper_start = source.index("def _validate_pipeline_project_access")
        # Next def after helper
        next_def = re.search(r"\ndef [a-z]", source[helper_start + 10:])
        helper_end = helper_start + next_def.start() if next_def else len(source)
        for occ in occurrences:
            assert helper_start <= occ <= helper_end, (
                "select(Project) found outside _validate_pipeline_project_access"
            )


# --- Validated project ID usage ---

def test_project_aware_endpoints_use_validated_ids():
    """Endpoints with project_id should use validated_project_id after validation."""
    source = _read_source()
    assert "validated_project_id" in source, "No validated_project_id usage found"


def test_generate_normalizes_project_id_before_building_pipeline():
    """generate_pipeline must normalize payload.project_id with validated Project
    before passing payload to build_pipeline."""
    source = _read_source()
    block = _get_function_block(source, '@router.post(\n    "/generate"')
    assert "_validate_pipeline_project_access" in block, (
        "generate_pipeline must call _validate_pipeline_project_access"
    )
    assert "payload.project_id = str(project.id)" in block, (
        "generate_pipeline must normalize payload.project_id with str(project.id)"
    )
    assert "build_pipeline(payload)" in block, (
        "generate_pipeline must call build_pipeline(payload) after normalization"
    )


def test_execute_uses_project_org_id():
    """execute_pipeline should derive resolved_org_id from project when available."""
    source = _read_source()
    block = _get_function_block(source, '@router.post(\n    "/execute"')
    assert "project.organization_id" in block, (
        "execute_pipeline must use project.organization_id for resolved_org_id"
    )
    assert "validated_project_id" in block, (
        "execute_pipeline must use validated_project_id for job creation"
    )


def test_list_jobs_uses_validated_ids():
    """list_pipeline_jobs should use validated IDs when project_id is provided."""
    source = _read_source()
    block = _get_function_block(source, '@router.get(\n    "/jobs"')
    assert "_validate_pipeline_project_access" in block or "validated_project_id" in block, (
        "list_pipeline_jobs must validate project_id"
    )


# --- No legacy / optional auth ---

def test_no_optional_auth_legacy():
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    put_count = len(re.findall(r"@router\.put\(", source))
    total = get_count + post_count + put_count
    assert total == 6, f"Expected 6 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: this router is mixed tenant/project.
    validate_project_access (Depends) cannot be used directly because
    project_id does not come from URL path — it arrives via body or query.
    A local helper _validate_pipeline_project_access provides equivalent
    gating using the canonical get_project_for_tenant function from
    tenant_access_service. get_pipeline_job has no project_id and scopes
    via organization_id + user_id + is_global_admin at service level.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
