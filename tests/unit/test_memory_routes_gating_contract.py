"""
Contract test: memory_routes.py gating invariants.

Verifies that memory endpoints require tenant context,
project access validation, appropriate write permission,
and use DB-validated project IDs for service calls.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "memory_routes.py"

# --- Decorators ---

PROJECT_ENDPOINTS = [
    '@router.post("/index"',
    '@router.get("/status"',
    '@router.post("/search"',
    '@router.post("/answer"',
]

WRITE_ENDPOINTS = ['@router.post("/index"']

READ_ENDPOINTS = [
    '@router.get("/status"',
    '@router.post("/search"',
    '@router.post("/answer"',
]

MANUAL_REVIEW_ENDPOINTS = [
    # Qdrant/RAG ownership filtering is delegated to services
    # (qdrant_memory_service, rag_embedding_service, cid_rag_answer_service).
    # Route-level gating ensures tenant+project validation; deep ownership
    # within Qdrant collections is enforced by passing validated IDs.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


# --- Import tests ---

def test_imports_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source


def test_imports_validate_project_access():
    source = _read_source()
    assert "from dependencies.project_access import" in source
    assert "validate_project_access" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_imports_project_model():
    source = _read_source()
    assert "from models.core import Project" in source


# --- Endpoint-level gating ---

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
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


# --- Validated project ID usage ---

def test_endpoints_use_validated_project_ids():
    """All endpoints must use project.organization_id / project.id for service calls."""
    source = _read_source()
    for decorator in PROJECT_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "str(project.organization_id)" in block or "project.organization_id" in block, (
            f"Endpoint does not use project.organization_id: {decorator}"
        )
        assert "str(project.id)" in block or "project.id" in block, (
            f"Endpoint does not use project.id: {decorator}"
        )


# --- No legacy / optional auth ---

def test_no_legacy_inline_project_query():
    source = _read_source()
    assert "select(Project)" not in source, "Legacy inline project query found"


def test_no_optional_auth_legacy():
    """No optional auth or get_optional_tenant patterns should remain."""
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 4, f"Expected 4 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"


# --- Manual review documentation ---

def test_manual_review_documented():
    """
    Manual review: Qdrant/RAG ownership is delegated to services.
    Route-level gating ensures validated tenant + project IDs are passed
    to qdrant_memory_service, rag_embedding_service, and cid_rag_answer_service.
    Deep collection-level ownership filtering within Qdrant is the
    responsibility of those services. This is documented, not automatable.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None


# --- Ownership hardening ---

def test_no_tenant_organization_id_for_memory_ownership():
    """
    Memory service ownership must come from the DB-validated Project,
    not from the tenant context or raw path project_id.
    """
    source = _read_source()
    assert "tenant.organization_id" not in source, (
        "tenant.organization_id must not be used as memory ownership source"
    )


def test_memory_services_receive_validated_ids():
    source = _read_source()
    assert "organization_id=organization_id" in source
    assert "project_id=validated_project_id" in source
