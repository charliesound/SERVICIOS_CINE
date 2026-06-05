"""
Contract test: ollama_storyboard_routes.py gating invariants.

Verifies that the Ollama status endpoint is authenticated, project-scoped
endpoints validate CID project ownership, and mutating compute endpoints
require write permission and module access.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "ollama_storyboard_routes.py"

ALL_ENDPOINTS = [
    '@router.get("/ops/ollama/status")',
    '@router.post("/projects/{project_id}/analyze/local-ollama")',
    '@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")',
]

WRITE_ENDPOINTS = [
    '@router.post("/projects/{project_id}/analyze/local-ollama")',
    '@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")',
]

PROJECT_SCOPED_ENDPOINTS = [
    '@router.post("/projects/{project_id}/analyze/local-ollama")',
    '@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")',
]

MANUAL_REVIEW_ENDPOINTS = [
    # /ops/ollama/status is operational but authenticated.
    # Project endpoints validate CID Project ownership before running local
    # Ollama compute, while module gates still control script_analysis and
    # storyboard_ai access.
]


def _read_source() -> str:
    assert TARGET_FILE.exists(), f"File not found: {TARGET_FILE}"
    return TARGET_FILE.read_text("utf-8")


def _get_function_block(source: str, decorator: str) -> str:
    idx = source.index(decorator)
    block = source[idx:]
    next_decorator = re.search(r"\n@", block)
    return block[: next_decorator.start()] if next_decorator else block


def test_imports_tenant_context_project_and_write_dependencies():
    source = _read_source()
    assert "from dependencies.tenant_context import (" in source
    assert "TenantContext" in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "validate_project_access" in source
    assert "from routes.auth_routes import get_tenant_context" not in source
    assert "from models.core import Project" in source
    assert "require_module_access" in source


def test_all_endpoints_have_tenant_context():
    source = _read_source()
    for decorator in ALL_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Missing get_tenant_context in {decorator}"
        )


def test_status_endpoint_is_authenticated_but_not_write_or_project_gated():
    source = _read_source()
    block = _get_function_block(source, '@router.get("/ops/ollama/status")')
    assert "get_tenant_context" in block
    assert "require_write_permission" not in block
    assert "validate_project_access" not in block


def test_project_scoped_endpoints_validate_project_access():
    source = _read_source()
    for decorator in PROJECT_SCOPED_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "project: Project = Depends(validate_project_access)" in block
        assert "validated_project_id = str(project.id)" in block
        assert "organization_id = str(project.organization_id)" in block


def test_mutating_endpoints_have_write_permission_and_module_access():
    source = _read_source()
    script_block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/analyze/local-ollama")',
    )
    storyboard_block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")',
    )
    for block, module_key in [
        (script_block, 'script_analysis'),
        (storyboard_block, 'storyboard_ai'),
    ]:
        assert "require_write_permission" in block
        assert f'require_module_access("{module_key}")' in block


def test_no_inline_project_query_or_select_project():
    source = _read_source()
    assert "select(Project)" not in source
    assert "from models.core import Project" not in source[
        source.index('@router.post("/projects/{project_id}/analyze/local-ollama")') :
    ]
    assert "from models.core import Project" not in source[
        source.index('@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")') :
    ]


def test_analyze_script_uses_validated_project_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/analyze/local-ollama")',
    )
    assert "local_script_analysis_service.analyze_script_with_qwen(" in block
    assert "project_id=validated_project_id" in block
    assert "analysis[\"project_id\"] = validated_project_id" in block


def test_storyboard_prompt_generation_uses_validated_project_id():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/storyboard/prompts/from-analysis")',
    )
    assert 'analysis_payload = {' in block
    assert '"project_id": validated_project_id' in block
    assert "project_id=validated_project_id" not in block


def test_no_legacy_optional_auth():
    source = _read_source()
    assert "get_optional_tenant" not in source
    assert "optional_auth" not in source
    assert "get_current_user_optional" not in source


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 3, f"Expected 3 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET endpoint, found {get_count}"
    assert post_count == 2, f"Expected 2 POST endpoints, found {post_count}"


def test_manual_review_documented():
    """
    Manual review: /ops/ollama/status is authenticated and operational.
    Project endpoints validate CID Project ownership before local Ollama
    compute, and module gates still control script_analysis/storyboard_ai.
    """
    assert MANUAL_REVIEW_ENDPOINTS is not None
