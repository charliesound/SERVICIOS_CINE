"""
Contract test: storyboard_presentation_routes.py gating invariants.

Verifies that storyboard presentation endpoints require tenant context
and appropriate write permission, while preserving module gate,
ownership delegation, and response shapes.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "storyboard_presentation_routes.py"

ALL_ENDPOINTS = [
    '@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")',
    '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
]

WRITE_ENDPOINTS = [
    '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
]

READ_ENDPOINTS = [
    '@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")',
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
    assert "require_write_permission" in source
    assert "routes.auth_routes" not in source, "Must import from dependencies.tenant_context"


def test_no_legacy_auth_imports():
    source = _read_source()
    assert "from routes.auth_routes" not in source
    assert "from schemas.auth_schema import" not in source


# --- Module access preserved ---

def test_module_access_preserved():
    source = _read_source()
    assert 'require_module_access("storyboard_ai")' in source


def test_router_level_module_gate():
    """Router-level dependencies list must include require_module_access('storyboard_ai')."""
    source = _read_source()
    assert 'dependencies=[Depends(require_module_access("storyboard_ai"))]' in source


# --- Endpoint-level gating ---

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


# --- Download endpoint (GET artifact) specifics ---

def test_download_endpoint_keeps_project_access_helper():
    source = _read_source()
    block = _get_function_block(
        source, '@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")'
    )
    assert "_ensure_project_access" in block, (
        "GET artifact must keep _ensure_project_access"
    )


def test_download_endpoint_keeps_file_response():
    source = _read_source()
    block = _get_function_block(
        source, '@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")'
    )
    assert "FileResponse" in block, "GET artifact must keep FileResponse"


# --- Generate endpoint (POST sheet) specifics ---

def test_generate_endpoint_keeps_project_access_helper():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
    )
    assert "_ensure_project_access" in block, (
        "POST sheet must keep _ensure_project_access"
    )


def test_generate_endpoint_keeps_payload_project_id_check():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
    )
    assert "payload.project_id != project_id" in block, (
        "POST sheet must keep payload.project_id != project_id check"
    )


def test_generate_endpoint_keeps_storyboard_frame_service():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
    )
    assert "storyboard_frame_service" in block, (
        "POST sheet must keep storyboard_frame_service usage"
    )


def test_generate_endpoint_keeps_storyboard_export_service():
    source = _read_source()
    block = _get_function_block(
        source,
        '@router.post("/{project_id}/storyboard/sheet", response_model=StoryboardSheetResponse)',
    )
    assert "storyboard_export_service.export_png" in block
    assert "storyboard_export_service.export_pdf" in block


# --- Endpoint count ---

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\(", source))
    post_count = len(re.findall(r"@router\.post\(", source))
    total = get_count + post_count
    assert total == 2, f"Expected 2 endpoints, found {total}"
    assert get_count == 1, f"Expected 1 GET, found {get_count}"
    assert post_count == 1, f"Expected 1 POST, found {post_count}"


# --- No optional auth ---

def test_no_optional_auth_legacy():
    """No optional auth or get_optional_tenant patterns should remain."""
    source = _read_source()
    assert "get_optional_tenant" not in source, "Legacy optional auth found"
    assert "optional_auth" not in source, "Legacy optional_auth found"
    assert "get_current_user_optional" not in source, "Legacy get_current_user_optional found"


# --- Manual review documentation ---

MANUAL_REVIEW_NOTES = """
Manual review:
- download_storyboard_sheet_artifact is read-only and serves a generated
  artifact on disk for an already-stored project, so it requires tenant auth
  and module access but not write permission.
- generate_storyboard_sheet is a mutating/export endpoint that consumes
  frames, renders pages, exports PNG/PDF and writes a new artifact on disk,
  so it requires tenant auth, module access and write permission.
- Project ownership is delegated to _ensure_project_access for both
  endpoints in this phase (no validate_project_access Depends migration yet).
"""


def test_manual_review_documented():
    assert "download" in MANUAL_REVIEW_NOTES
    assert "generate" in MANUAL_REVIEW_NOTES
    assert "_ensure_project_access" in MANUAL_REVIEW_NOTES
