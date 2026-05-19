from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")


@pytest.fixture(autouse=True)
def _reset_environment(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture(autouse=True)
def _reset_taxonomy_service():
    from services.cinematic_taxonomy_service import CinematicTaxonomyService

    CinematicTaxonomyService._instance = None


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


def test_get_full_taxonomy_returns_categories(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy")
    assert response.status_code == 200
    body = response.json()
    assert "categories" in body
    assert "total_elements" in body
    assert body["total_elements"] > 0
    assert "shot_types" in body["categories"]
    assert "cinematic_presets" not in body["categories"]  # presets are separate


def test_get_category_returns_elements(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy/shot_types")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    for el in body:
        assert "id" in el
        assert "name" in el
        assert "prompt_tags" in el
        assert "negative_prompt_tags" in el


def test_get_category_not_found(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy/nonexistent")
    assert response.status_code == 404


def test_get_presets_returns_list(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy/presets")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) > 0
    for p in body:
        assert "id" in p
        assert "name" in p
        assert "shot_types" in p
        assert "composition" in p
        assert "camera_movements" in p
        assert "prompt_tags" in p
        assert "negative_prompt_tags" in p


def test_get_preset_by_id(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy/presets/noir_classic")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "noir_classic"
    assert body["name"] == "Classic Film Noir"
    assert "cu" in body["shot_types"]


def test_get_preset_not_found(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/cinematic-taxonomy/presets/nonexistent")
    assert response.status_code == 404


def test_enrich_prompt_with_preset(test_app):
    with TestClient(test_app) as client:
        response = client.post(
            "/api/cinematic-taxonomy/enrich-prompt",
            json={
                "base_prompt": "A detective in the rain",
                "preset_id": "noir_classic",
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["base_prompt"] == "A detective in the rain"
    assert body["enriched_prompt"].startswith("A detective in the rain")
    assert body["applied_preset"] is not None
    assert body["applied_preset"]["id"] == "noir_classic"
    assert len(body["applied_tags"]) > 0
    assert isinstance(body["negative_prompt"], str)
    assert isinstance(body["warnings"], list)


def test_enrich_prompt_with_selected_tags(test_app):
    with TestClient(test_app) as client:
        response = client.post(
            "/api/cinematic-taxonomy/enrich-prompt",
            json={
                "base_prompt": "A couple dancing",
                "selected_tags": ["golden hour", "romantic mood"],
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["applied_preset"] is None
    assert len(body["applied_tags"]) == 2
    assert all(t["source"] == "user_selected" for t in body["applied_tags"])


def test_enrich_prompt_with_both(test_app):
    with TestClient(test_app) as client:
        response = client.post(
            "/api/cinematic-taxonomy/enrich-prompt",
            json={
                "base_prompt": "A car chase",
                "preset_id": "epic_blockbuster",
                "selected_tags": ["night time"],
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["applied_preset"]["id"] == "epic_blockbuster"


def test_enrich_prompt_preset_not_found(test_app):
    with TestClient(test_app) as client:
        response = client.post(
            "/api/cinematic-taxonomy/enrich-prompt",
            json={
                "base_prompt": "A scene",
                "preset_id": "nonexistent",
            },
        )
    assert response.status_code == 404


def test_enrich_prompt_no_payload_options(test_app):
    with TestClient(test_app) as client:
        response = client.post(
            "/api/cinematic-taxonomy/enrich-prompt",
            json={"base_prompt": "A simple scene"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["enriched_prompt"] == "A simple scene"
    assert body["applied_preset"] is None
    assert body["applied_tags"] == []
    assert body["negative_prompt"] == ""
    assert body["warnings"] == []
