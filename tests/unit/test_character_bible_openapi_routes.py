from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest
from app import app


EXPECTED_CB_PATHS = {
    "/api/projects/{project_id}/character-bible",
    "/api/projects/{project_id}/character-bible/{character_id}",
    "/api/projects/{project_id}/character-bible/{character_id}/look-variants",
    "/api/projects/{project_id}/character-bible/{character_id}/references",
    "/api/projects/{project_id}/character-bible/{character_id}/resolve",
    "/api/projects/{project_id}/character-bible/{character_id}/trace",
}


def test_openapi_contains_all_character_bible_routes() -> None:
    schema = app.openapi()
    all_paths = set(schema["paths"].keys())
    cb_paths = {p for p in all_paths if "character-bible" in p}
    missing = EXPECTED_CB_PATHS - cb_paths
    assert not missing, f"Character Bible paths missing from OpenAPI: {sorted(missing)}"


def test_openapi_cb_list_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible"]
    assert "get" in ops


def test_openapi_cb_get_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible/{character_id}"]
    assert "get" in ops
    assert "put" in ops


def test_openapi_cb_look_variants_path_has_post_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible/{character_id}/look-variants"]
    assert "post" in ops


def test_openapi_cb_references_path_has_post_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible/{character_id}/references"]
    assert "post" in ops


def test_openapi_cb_resolve_path_has_post_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible/{character_id}/resolve"]
    assert "post" in ops


def test_openapi_cb_trace_path_has_get_method() -> None:
    schema = app.openapi()
    ops = schema["paths"]["/api/projects/{project_id}/character-bible/{character_id}/trace"]
    assert "get" in ops


@pytest.mark.parametrize("expected_path", sorted(EXPECTED_CB_PATHS))
def test_all_cb_paths_in_openapi(expected_path: str) -> None:
    schema = app.openapi()
    assert expected_path in schema["paths"], (
        f"Expected path {expected_path} not found in OpenAPI schema"
    )
