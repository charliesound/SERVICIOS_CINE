"""
Contract test: crm_routes.py gating invariants.

Verifies that CRM endpoints require tenant context,
project access validation where project-scoped, and write permission on
mutating endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "crm_routes.py"

MANUAL_REVIEW_ENDPOINTS = [
    '/projects/{project_id}/crm/summary',
    '/projects/{project_id}/crm/opportunities',
    '/projects/{project_id}/crm/communications',
    '/projects/{project_id}/crm/tasks',
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


def test_imports_require_write_permission():
    source = _read_source()
    assert "require_write_permission" in source


def test_imports_validate_project_access():
    source = _read_source()
    assert "validate_project_access" in source


def test_conserves_require_module_access():
    source = _read_source()
    assert "require_module_access" in source
    assert 'require_module_access("delivery_distribution")' in source


def test_no_auth_routes_import_for_tenant_context():
    source = _read_source()
    assert "from routes.auth_routes import get_tenant_context" not in source


def test_router_has_get_tenant_context_and_module_access():
    source = _read_source()
    assert "Depends(get_tenant_context)" in source
    assert 'Depends(require_module_access("delivery_distribution"))' in source


def test_project_scoped_endpoints_have_validate_project_access():
    source = _read_source()
    project_scoped_decorators = [
        '@router.get("/projects/{project_id}/crm/summary")',
        '@router.get("/projects/{project_id}/crm/opportunities")',
        '@router.post("/projects/{project_id}/crm/opportunities")',
        '@router.get("/projects/{project_id}/crm/opportunities/{opportunity_id}")',
        '@router.patch("/projects/{project_id}/crm/opportunities/{opportunity_id}")',
        '@router.post("/projects/{project_id}/crm/opportunities/{opportunity_id}/status")',
        '@router.get("/projects/{project_id}/crm/communications")',
        '@router.post("/projects/{project_id}/crm/communications")',
        '@router.get("/projects/{project_id}/crm/tasks")',
        '@router.post("/projects/{project_id}/crm/tasks")',
        '@router.post("/projects/{project_id}/crm/tasks/{task_id}/complete")',
        '@router.post("/projects/{project_id}/crm/tasks/{task_id}/cancel")',
    ]
    for decorator in project_scoped_decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped CRM endpoint missing validate_project_access: {decorator}"
        )


def test_all_write_endpoints_have_require_write_permission():
    source = _read_source()
    write_decorators = [
        '@router.post("/crm/contacts")',
        '@router.patch("/crm/contacts/{contact_id}")',
        '@router.post("/crm/contacts/{contact_id}/archive")',
        '@router.post("/projects/{project_id}/crm/opportunities")',
        '@router.patch("/projects/{project_id}/crm/opportunities/{opportunity_id}")',
        '@router.post("/projects/{project_id}/crm/opportunities/{opportunity_id}/status")',
        '@router.post("/projects/{project_id}/crm/communications")',
        '@router.post("/projects/{project_id}/crm/tasks")',
        '@router.post("/projects/{project_id}/crm/tasks/{task_id}/complete")',
        '@router.post("/projects/{project_id}/crm/tasks/{task_id}/cancel")',
    ]
    for decorator in write_decorators:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating CRM endpoint missing require_write_permission: {decorator}"
        )


def test_get_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    get_decorators = re.findall(r"@router\.get\([^)]+\)", source)
    for dec in get_decorators:
        block = _get_function_block(source, dec)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {dec}"
        )


def test_contact_endpoints_validate_tenant_ownership():
    source = _read_source()
    assert "_get_contact_for_tenant_or_404" in source
    helper_start = source.index("async def _get_contact_for_tenant_or_404(")
    helper_block = source[helper_start:source.index("async def _get_opportunity_for_project_or_404(")]
    assert "str(contact.organization_id) != str(tenant.organization_id)" in helper_block


def test_opportunity_endpoints_validate_project_and_tenant_ownership():
    source = _read_source()
    assert "_get_opportunity_for_project_or_404" in source
    helper_start = source.index("async def _get_opportunity_for_project_or_404(")
    helper_block = source[helper_start:source.index("async def _get_task_for_project_or_404(")]
    assert "opp.project_id != project_id" in helper_block
    assert "str(opp.organization_id) != str(tenant.organization_id)" in helper_block


def test_task_endpoints_validate_project_and_tenant_ownership():
    source = _read_source()
    assert "_get_task_for_project_or_404" in source
    helper_start = source.index("async def _get_task_for_project_or_404(")
    helper_block = source[helper_start:source.index("class CRMContactCreate(")]
    assert "CRMTask.id == task_id" in helper_block
    assert "CRMTask.project_id == project_id" in helper_block
    assert "CRMTask.organization_id == tenant.organization_id" in helper_block


def test_manual_review_endpoints_are_listed():
    source = _read_source()
    for endpoint_path in MANUAL_REVIEW_ENDPOINTS:
        assert endpoint_path in source, f"Manual review endpoint missing from source: {endpoint_path}"


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    patch_count = len(re.findall(r"@router\.patch\([^)]+\)", source))
    total = get_count + post_count + patch_count
    assert total == 17, f"Expected 17 endpoints, found {total}"
    assert get_count == 7, f"Expected 7 GET, found {get_count}"
    assert post_count == 8, f"Expected 8 POST, found {post_count}"
    assert patch_count == 2, f"Expected 2 PATCH, found {patch_count}"
