from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

import pytest
from app import app


EXPECTED_TRACE_PATHS = {
    "/api/projects/{project_id}/storyboard/trace",
    "/api/projects/{project_id}/storyboard/shots/{shot_id}/trace",
    "/api/projects/{project_id}/storyboard/assets/{asset_id}/trace",
}


def test_openapi_contains_all_storyboard_trace_routes() -> None:
    schema = app.openapi()
    all_paths = set(schema["paths"].keys())

    trace_paths = {p for p in all_paths if "storyboard" in p and "trace" in p}

    missing = EXPECTED_TRACE_PATHS - trace_paths
    extra = trace_paths - EXPECTED_TRACE_PATHS

    assert not missing, f"Trace paths missing from OpenAPI: {sorted(missing)}"
    assert not extra, f"Unexpected trace paths in OpenAPI: {sorted(extra)}"
    assert trace_paths == EXPECTED_TRACE_PATHS, (
        f"Trace path mismatch.\n"
        f"  Expected: {sorted(EXPECTED_TRACE_PATHS)}\n"
        f"  Got:      {sorted(trace_paths)}"
    )


def test_openapi_shot_trace_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/storyboard/shots/{shot_id}/trace"]
    assert "get" in ops, "Shot trace endpoint must have GET method"
    assert "parameters" in ops["get"], "Shot trace endpoint must define path parameters"


def test_openapi_project_trace_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/storyboard/trace"]
    assert "get" in ops, "Project trace summary endpoint must have GET method"


def test_openapi_asset_trace_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/storyboard/assets/{asset_id}/trace"]
    assert "get" in ops, "Asset trace endpoint must have GET method"


@pytest.mark.parametrize("expected_path", sorted(EXPECTED_TRACE_PATHS))
def test_all_trace_paths_in_openapi(expected_path: str) -> None:
    schema = app.openapi()
    assert expected_path in schema["paths"], (
        f"Expected path {expected_path} not found in OpenAPI schema"
    )
