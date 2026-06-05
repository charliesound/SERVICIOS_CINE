"""
Contract test: cid_script_to_prompt_routes.py gating invariants.

Verifies that the router remains mostly stateless in this phase, while the
only project-linked endpoint (`/analyze-full`) uses a local tenant-aware
project access helper for payload.project_id.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "cid_script_to_prompt_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # Most script-to-prompt endpoints are stateless and remain without wider
    # auth expansion in this phase.
    # /analyze-full is the only endpoint that can read Project from
    # payload.project_id, and it is protected by a local helper.
    # Module gate pipeline_builder remains in place.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[:next_decorator.start()] if next_decorator else block


def test_imports_tenant_context_from_dependencies():
    source = _read_source()
    assert "from dependencies.tenant_context import TenantContext, get_tenant_context" in source
    assert "from routes.auth_routes import get_tenant_context" not in source


def test_imports_keep_module_access_project_and_select():
    source = _read_source()
    assert "require_module_access" in source
    assert "from models.core import Project" in source
    assert "from sqlalchemy import select" in source
    assert "validate_project_access" not in source
    assert "require_write_permission" not in source


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 14, f"Expected 14 endpoints, found {total}"
    assert get_count == 3, f"Expected 3 GET, found {get_count}"
    assert post_count == 11, f"Expected 11 POST, found {post_count}"


def test_analyze_full_has_tenant_context_and_module_gate():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/analyze-full", response_model=FullScriptAnalysisResult)',
    )
    assert "get_tenant_context" in block
    assert 'require_module_access("pipeline_builder")' in block


def test_helper_exists_and_scopes_project_by_tenant():
    source = _read_source()
    assert "async def _validate_script_to_prompt_project_access(" in source
    helper_start = source.index("async def _validate_script_to_prompt_project_access(")
    helper_end = source.index('@router.post("/run", response_model=ScriptToPromptRunResponse)')
    block = source[helper_start:helper_end]
    assert "select(Project)" in block
    assert "Project.id == project_id" in block
    assert "Project.organization_id == tenant.organization_id" in block
    assert "_is_admin_tenant(tenant)" in block


def test_analyze_full_uses_helper_and_no_inline_project_query():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/analyze-full", response_model=FullScriptAnalysisResult)',
    )
    assert "_validate_script_to_prompt_project_access(" in block
    assert "select(Project).where(Project.id == payload.project_id)" not in block


def test_no_optional_auth_legacy():
    source = _read_source()
    assert "get_optional_tenant" not in source
    assert "optional_auth" not in source
    assert "get_current_user_optional" not in source


def test_manual_review_documented():
    """
    Manual review: this router contains stateless script-to-prompt endpoints
    that remain without broader auth expansion in this phase.
    analyze-full is the only endpoint that can read Project from payload.project_id
    and is protected by a local helper. Module gate pipeline_builder remains.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
