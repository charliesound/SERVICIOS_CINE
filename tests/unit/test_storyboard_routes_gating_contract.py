"""
Contract test: storyboard_routes.py gating invariants.

Verifies that all storyboard endpoints require tenant context,
project access validation, and write permission on mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "storyboard_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '/{project_id}/storyboard/trace',
    '/{project_id}/storyboard/shots/{shot_id}/trace',
    '/{project_id}/storyboard/assets/{asset_id}/trace',
    '/{project_id}/storyboard/sequences/{sequence_id}',
    '/{project_id}/storyboard/shots/{shot_id}/feedback',
    '/{project_id}/storyboard/shots/{shot_id}/regenerate',
    '/{project_id}/storyboard/sequences/{sequence_id}/regenerate-failed',
    '/{project_id}/storyboard/sequences/{sequence_id}/feedback',
    '/{project_id}/storyboard/sequences/{sequence_id}/export/zip',
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


def test_conserves_require_module_access():
    source = _read_source()
    assert "require_module_access" in source
    assert 'require_module_access("storyboard_ai")' in source


def test_no_auth_routes_import_for_tenant_context():
    source = _read_source()
    assert "from routes.auth_routes import get_tenant_context" not in source


def test_router_has_get_tenant_context_and_module_access():
    source = _read_source()
    assert "Depends(get_tenant_context)" in source
    assert 'Depends(require_module_access("storyboard_ai"))' in source


def test_all_project_scoped_endpoints_have_validate_project_access():
    source = _read_source()
    project_scoped_decorators = [
        '@router.get("/{project_id}/storyboard/options", response_model=StoryboardOptionsResponse)',
        '@router.get("/{project_id}/storyboard/sequences", response_model=list[StoryboardSequenceResponse])',
        '@router.post("/{project_id}/storyboard/generate", response_model=StoryboardJobResponse)',
        '@router.post("/{project_id}/storyboard/estimate-credits", response_model=StoryboardCreditEstimateResponse)',
        '@router.post("/{project_id}/storyboard/sequences/{sequence_id}/plan", response_model=SequenceStoryboardPlan)',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/generate",',
        '@router.post("/{project_id}/storyboard/comfyui/plan")',
        '@router.post("/{project_id}/storyboard/comfyui/render-dry-run")',
        '@router.post("/{project_id}/storyboard/render")',
        '@router.get("/{project_id}/storyboard", response_model=StoryboardListResponse)',
        '@router.get("/{project_id}/storyboard/trace", response_model=StoryboardTraceSummary)',
        '@router.get("/{project_id}/storyboard/shots/{shot_id}/trace", response_model=StoryboardTraceRecord)',
        '@router.get("/{project_id}/storyboard/assets/{asset_id}/trace", response_model=StoryboardTraceRecord)',
        '@router.get("/{project_id}/storyboard/shots/{shot_id}/image")',
        '@router.get("/{project_id}/storyboard/shots/{shot_id}/thumbnail")',
        '@router.get("/{project_id}/storyboard/sequences/{sequence_id}", response_model=StoryboardSequenceDetailResponse)',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate",',
        '@router.post(\n    "/{project_id}/storyboard/shots/{shot_id}/feedback",',
        '@router.post(\n    "/{project_id}/storyboard/shots/{shot_id}/regenerate",',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate-failed",',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/feedback",',
        '@router.get(\n    "/{project_id}/storyboard/shots/{shot_id}/revisions",',
        '@router.get(\n    "/{project_id}/storyboard/sequences/{sequence_id}/export/zip",',
        '@router.post("/{project_id}/storyboard/repair-assets")',
    ]
    for decorator in project_scoped_decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped endpoint missing validate_project_access: {decorator}"
        )


def test_all_post_endpoints_have_require_write_permission():
    source = _read_source()
    post_decorators = [
        '@router.post("/{project_id}/storyboard/generate", response_model=StoryboardJobResponse)',
        '@router.post("/{project_id}/storyboard/estimate-credits", response_model=StoryboardCreditEstimateResponse)',
        '@router.post("/{project_id}/storyboard/sequences/{sequence_id}/plan", response_model=SequenceStoryboardPlan)',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/generate",',
        '@router.post("/{project_id}/storyboard/comfyui/plan")',
        '@router.post("/{project_id}/storyboard/comfyui/render-dry-run")',
        '@router.post("/{project_id}/storyboard/render")',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate",',
        '@router.post(\n    "/{project_id}/storyboard/shots/{shot_id}/feedback",',
        '@router.post(\n    "/{project_id}/storyboard/shots/{shot_id}/regenerate",',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/regenerate-failed",',
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/feedback",',
        '@router.post("/{project_id}/storyboard/repair-assets")',
    ]
    for decorator in post_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"POST/action endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_local_shot_and_asset_helper_validates_project_membership():
    source = _read_source()
    helper_start = source.index("async def _get_storyboard_shot_and_asset(")
    helper_block = source[helper_start:source.index("def _file_response_for_storyboard_media")]
    assert "StoryboardShot.id == shot_id" in helper_block
    assert "StoryboardShot.project_id == project_id" in helper_block
    assert "MediaAsset.id == shot.asset_id" in helper_block
    assert "MediaAsset.project_id == project_id" in helper_block


def test_local_sequence_feedback_query_validates_project_and_sequence():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post(\n    "/{project_id}/storyboard/sequences/{sequence_id}/feedback",',
    )
    assert "StoryboardShot.project_id == project_id" in block
    assert "StoryboardShot.sequence_id == sequence_id" in block


def test_local_revision_history_query_validates_project_membership():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.get(\n    "/{project_id}/storyboard/shots/{shot_id}/revisions",',
    )
    assert "StoryboardShot.id == shot_id" in block
    assert "StoryboardShot.project_id == project_id" in block


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for decorator in MANUAL_REVIEW_ENDPOINTS:
        assert decorator in source, f"Manual review endpoint missing from source: {decorator}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    total = get_count + post_count
    assert total == 24, f"Expected 24 endpoints, found {total}"
    assert get_count == 11, f"Expected 11 GET, found {get_count}"
    assert post_count == 13, f"Expected 13 POST, found {post_count}"
