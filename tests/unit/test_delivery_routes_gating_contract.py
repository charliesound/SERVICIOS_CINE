"""
Contract test: delivery_routes.py gating invariants.

Verifies that delivery endpoints require tenant context, project access
validation on project-scoped routes, and write permission on mutating
endpoints.

Static source-code analysis - no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
TARGET_FILE = ROUTES_DIR / "delivery_routes.py"

PROJECT_SCOPED_ENDPOINTS = [
    '@router.get("/projects/{project_id}/deliverables", response_model=DeliverableListResponse)',
    '@router.post("/projects/{project_id}/deliverables", response_model=DeliverableResponse)',
    '@router.post("/projects/{project_id}/export")',
]

WRITE_ENDPOINTS = [
    '@router.post("/projects/{project_id}/deliverables", response_model=DeliverableResponse)',
    '@router.patch("/deliverables/{deliverable_id}", response_model=DeliverableResponse)',
    '@router.post("/projects/{project_id}/export")',
]

READ_ENDPOINTS = [
    '@router.get("/projects/{project_id}/deliverables", response_model=DeliverableListResponse)',
    '@router.get("/deliverables/{deliverable_id}", response_model=DeliverableResponse)',
    '@router.get("/reviews/{review_id}/deliverable", response_model=DeliverableResponse)',
    '@router.get("/deliverables/{deliverable_id}/download")',
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
    assert "from dependencies.tenant_context import (" in source
    assert "get_tenant_context" in source
    assert "require_write_permission" in source
    assert "validate_project_access" in source


def test_does_not_import_project_access_module():
    source = _read_source()
    assert "from dependencies.project_access import" not in source


def test_imports_project_model_and_select():
    source = _read_source()
    assert "from models.core import Project" in source
    assert "from sqlalchemy import select" in source


def test_project_scoped_endpoints_have_validate_project_access():
    source = _read_source()
    for decorator in PROJECT_SCOPED_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" in block, (
            f"Project-scoped endpoint missing validate_project_access: {decorator}"
        )


def test_project_scoped_endpoints_use_validated_project_id():
    source = _read_source()
    for decorator in PROJECT_SCOPED_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "validated_project_id = str(project.id)" in block
        assert "organization_id = str(project.organization_id)" in block


def test_service_calls_use_validated_project_id():
    source = _read_source()

    list_block = _get_function_block(
        source,
        '@router.get("/projects/{project_id}/deliverables", response_model=DeliverableListResponse)',
    )
    assert "project_id=project_id" not in list_block
    assert "validated_project_id" in list_block
    assert "delivery_service.list_deliverables" in list_block

    create_block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/deliverables", response_model=DeliverableResponse)',
    )
    assert "project_id=project_id" not in create_block
    assert "project_id=validated_project_id" in create_block
    assert "organization_id=organization_id" in create_block

    export_block = _get_function_block(
        source,
        '@router.post("/projects/{project_id}/export")',
    )
    assert "project_id=project_id" not in export_block
    assert "project_id=validated_project_id" in export_block
    assert "organization_id=organization_id" in export_block


def test_mutating_endpoints_have_require_write_permission():
    source = _read_source()
    for decorator in WRITE_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" in block, (
            f"Mutating endpoint missing require_write_permission: {decorator}"
        )


def test_read_endpoints_do_not_have_require_write_permission():
    source = _read_source()
    for decorator in READ_ENDPOINTS:
        block = _get_function_block(source, decorator)
        assert "require_write_permission" not in block, (
            f"GET endpoint should not have require_write_permission: {decorator}"
        )


def test_non_project_endpoints_do_not_have_validate_project_access():
    source = _read_source()
    decorators = [
        '@router.get("/deliverables/{deliverable_id}", response_model=DeliverableResponse)',
        '@router.patch("/deliverables/{deliverable_id}", response_model=DeliverableResponse)',
        '@router.get("/reviews/{review_id}/deliverable", response_model=DeliverableResponse)',
        '@router.get("/deliverables/{deliverable_id}/download")',
    ]
    for decorator in decorators:
        block = _get_function_block(source, decorator)
        assert "validate_project_access" not in block, (
            f"Non-project endpoint should not have validate_project_access: {decorator}"
        )


def test_no_inline_project_query_remains():
    source = _read_source()
    assert "select(Project)" not in source


def test_router_level_count():
    source = _read_source()
    get_count = len(re.findall(r"@router\.get\([^)]+\)", source))
    post_count = len(re.findall(r"@router\.post\([^)]+\)", source))
    patch_count = len(re.findall(r"@router\.patch\([^)]+\)", source))
    total = get_count + post_count + patch_count
    assert total == 7, f"Expected 7 endpoints, found {total}"
    assert get_count == 4, f"Expected 4 GET, found {get_count}"
    assert post_count == 2, f"Expected 2 POST, found {post_count}"
    assert patch_count == 1, f"Expected 1 PATCH, found {patch_count}"
