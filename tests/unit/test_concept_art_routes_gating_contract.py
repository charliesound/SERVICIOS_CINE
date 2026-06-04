"""
Contract test: concept_art_routes.py gating invariants.

Verifies that concept art endpoints require tenant context,
appropriate write permission, and use validated project ID for deep ownership.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "concept_art_routes.py"

# --- Decorators ---

ALL_ENDPOINTS = [
    '@router.post("/{project_id}/concept-art/compile-workflow-dry-run")',
    '@router.post("/{project_id}/key-visual/compile-workflow-dry-run")',
    '@router.get("/{project_id}/concept-art/jobs")',
]

WRITE_ENDPOINTS = [
    '@router.post("/{project_id}/concept-art/compile-workflow-dry-run")',
    '@router.post("/{project_id}/key-visual/compile-workflow-dry-run")',
]

READ_ENDPOINTS = [
    '@router.get("/{project_id}/concept-art/jobs")',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Router is project-scoped (project_id in path, prefix is /api/projects).
    # All endpoints are guarded by validate_project_access (Depends) which loads the Project model.
    # Service calls receive the validated project ID (validated_project_id = str(project.id)).
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block[1:])
    return block[:next_decorator.start() + 1] if next_decorator else block


# --- Import tests ---

def test_imports_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source
    assert "routes.auth_routes" not in source, "Must import from dependencies.tenant_context"


def test_imports_project_access():
    source = _read_source()
    assert "from dependencies.project_access import" in source
    assert "validate_project_access" in source
    assert "require_write_permission" in source


def test_imports_project_model():
    source = _read_source()
    assert "from models.core import Project" in source


def test_no_query_imported_if_unused():
    source = _read_source()
    assert ", Query" not in source
    assert "import Query" not in source


# --- Endpoint-level gating ---

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_all_endpoints_have_project_access_validation():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Missing validate_project_access in {decorator}"
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


# --- Deep ownership and structure ---

def test_no_optional_auth_legacy():
    """No optional auth or get_optional_tenant patterns should remain."""
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


def test_no_inline_project_query():
    """Endpoints should not query Project directly since they use validate_project_access."""
    source = _read_source()
    assert "select(Project)" not in source, "Unexpected select(Project) query"


def test_service_calls_use_validated_project_id():
    """All service calls must receive validated_project_id instead of raw path project_id."""
    source = _read_source()

    # project_concept_art_compile_dry_run
    dry_run_block = _get_function_block(source, '@router.post("/{project_id}/concept-art/compile-workflow-dry-run")')
    assert "validated_project_id = str(project.id)" in dry_run_block
    assert "project_id=validated_project_id" in dry_run_block
    assert "project_id=project_id" not in dry_run_block

    # project_key_visual_compile_dry_run
    key_visual_block = _get_function_block(source, '@router.post("/{project_id}/key-visual/compile-workflow-dry-run")')
    assert "validated_project_id = str(project.id)" in key_visual_block
    assert "project_id=validated_project_id" in key_visual_block
    assert "project_id=project_id" not in key_visual_block

    # project_concept_art_list_jobs
    jobs_block = _get_function_block(source, '@router.get("/{project_id}/concept-art/jobs")')
    assert "validated_project_id = str(project.id)" in jobs_block
    assert "project_id=validated_project_id" in jobs_block
    assert "project_id=project_id" not in jobs_block
    assert '"project_id": validated_project_id' in jobs_block


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 3, f"Expected 3 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: router is project-scoped.
    All endpoints are guarded by validate_project_access (Depends) which loads the Project model.
    Service calls receive the validated project ID (validated_project_id = str(project.id)).
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
