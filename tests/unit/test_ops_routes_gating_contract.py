"""
Contract test: ops_routes.py gating invariants.

Verifies that all ops endpoints require authentication/tenant context
and that write/execute endpoints also require write permission.

This is a static source-code analysis test — no DB, no backend.
"""

import re
from pathlib import Path

ROUTES_DIR = Path(__file__).resolve().parent.parent.parent / "src" / "routes"
OPS_FILE = ROUTES_DIR / "ops_routes.py"


def _read_source() -> str:
    assert OPS_FILE.exists(), f"File not found: {OPS_FILE}"
    return OPS_FILE.read_text("utf-8")


def test_imports_get_tenant_context():
    source = _read_source()
    assert "from dependencies.tenant_context import get_tenant_context" in source


def test_imports_require_write_permission():
    source = _read_source()
    assert "from dependencies.tenant_context import get_tenant_context, require_write_permission" in source


def test_router_has_get_tenant_context_dependency():
    source = _read_source()
    match = re.search(
        r'router = APIRouter\(prefix="/api/ops".*dependencies=\[Depends\(get_tenant_context\)\]',
        source,
    )
    assert match, "router /api/ops is missing dependencies=[Depends(get_tenant_context)]"


def test_pipeline_router_has_get_tenant_context_dependency():
    source = _read_source()
    match = re.search(
        r'pipeline_router = APIRouter\(prefix="/api/pipelines".*dependencies=\[Depends\(get_tenant_context\)\]',
        source,
    )
    assert match, "pipeline_router /api/pipelines is missing dependencies=[Depends(get_tenant_context)]"


def _find_post_decorators(source: str) -> list[str]:
    decorators = re.findall(
        r'@(?:router|pipeline_router)\.post\([^)]+\)',
        source,
    )
    return decorators


def test_all_post_endpoints_have_write_permission():
    source = _read_source()
    post_decorators = _find_post_decorators(source)
    assert len(post_decorators) > 0, "No POST endpoints found in ops_routes.py"
    for dec in post_decorators:
        assert "require_write_permission" in dec, (
            f"POST endpoint missing require_write_permission: {dec}"
        )


def test_no_get_current_user_optional():
    source = _read_source()
    assert "get_current_user_optional" not in source, (
        "ops_routes.py should NOT import or use get_current_user_optional"
    )


def test_router_level_count():
    source = _read_source()
    router_count = len(re.findall(r"@router\.(?:get|post|put|patch|delete)\(", source))
    pipeline_count = len(re.findall(r"@pipeline_router\.(?:get|post|put|patch|delete)\(", source))
    assert router_count >= 19, f"Expected >=19 endpoints on router, found {router_count}"
    assert pipeline_count >= 2, f"Expected >=2 endpoints on pipeline_router, found {pipeline_count}"
