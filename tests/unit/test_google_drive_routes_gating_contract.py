"""
Contract test: google_drive_routes.py gating invariants.

Verifies that google drive endpoints require tenant context,
project access validation on project routes, and write permission on
mutating/action endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "google_drive_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    # link_id validated locally by project scope pass-down
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
    assert "from routes.auth_routes import get_tenant_context" in source or "from dependencies.tenant_context import" in source
    assert "get_tenant_context" in source

def test_imports_validate_project_access():
    source = _read_source()
    assert "validate_project_access" in source

def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source

def test_all_endpoints_have_tenant_context():
    source = _read_source()
    decorators = re.findall(r"@router\.[a-z]+\([^)]*\)", source)
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "get_tenant_context" in block, (
            f"Endpoint missing get_tenant_context: {decorator}"
        )

def test_all_project_endpoints_have_validate_project_access():
    source = _read_source()
    decorators = re.findall(r"@router\.[a-z]+\(\s*\"/api/projects/\{project_id\}[^\)]*\)", source)
    assert len(decorators) == 6, f"Expected 6 project endpoints, found {len(decorators)}"
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped endpoint missing validate_project_access: {decorator}"
        )

def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    # Explicit list of mutators / action endpoints
    action_decorators = [
        '"/api/integrations/google-drive/connect"',
        '"/api/integrations/google-drive/callback"',
        '"/api/integrations/google-drive/disconnect"',
        '"/api/projects/{project_id}/integrations/google-drive/link-folder"', # POST
        '"/api/projects/{project_id}/integrations/google-drive/link-folder/{link_id}"', # DELETE
        '"/api/projects/{project_id}/integrations/google-drive/sync"', # POST
    ]
    for action in action_decorators:
        # Find the block starting near this route
        idx = source.find(action)
        assert idx != -1, f"Route not found: {action}"
        block = source[idx:]
        next_decorator = re.search(r"\n@", block)
        block = block[:next_decorator.start()] if next_decorator else block

        # Exception for GET vs POST on link-folder since there are two with same path
        if "link-folder" in action and "link_id" not in action:
            # We want to check the POST one.
            # We will use re to grab all router.post to be sure.
            pass

    decorators = re.findall(r"@router\.(?:post|put|patch|delete)\([^)]*\)", source)
    # Add connect and callback which are GET but actions
    decorators.extend(re.findall(r"@router\.get\(\s*\"/api/integrations/google-drive/connect\"[^)]*\)", source))
    decorators.extend(re.findall(r"@router\.get\(\s*\"/api/integrations/google-drive/callback\"[^)]*\)", source))

    assert len(decorators) == 6, f"Expected 6 mutating/action endpoints, found {len(decorators)}"

    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating/action endpoint missing require_write_permission: {decorator}"
        )

def test_inline_project_query_removed():
    source = _read_source()
    assert "_get_project_or_403" not in source, "Found obsolete inline project query"

def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]*\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]*\)", source))
    delete_count = len(re.findall(r"@router\.delete\([^)]*\)", source))
    total = get_count + post_count + delete_count
    assert total == 10, f"Expected 10 endpoints, found {total}"
    assert get_count == 6, f"Expected 6 GET, found {get_count}"
    assert post_count == 3, f"Expected 3 POST, found {post_count}"
    assert delete_count == 1, f"Expected 1 DELETE, found {delete_count}"
