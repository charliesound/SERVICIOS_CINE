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
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")
os.environ.setdefault("HEALTHCHECK_REDIS_ENABLED", "false")


@pytest.fixture(autouse=True)
def _reset_environment(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()
    from services.module_catalog_service import module_catalog_service

    module_catalog_service.reload_catalog()


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


def test_catalog_endpoint_returns_visible_modules(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/modules/catalog")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 14
    keys = {module["key"] for module in body["modules"]}
    assert "core" in keys
    assert "funding_grants" in keys


def test_module_detail_endpoint_returns_module(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/modules/script_analysis")

    assert response.status_code == 200
    body = response.json()
    assert body["key"] == "script_analysis"
    assert body["feature_flag_key"] == "module_script_analysis"


def test_module_detail_endpoint_returns_404_for_unknown_key(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/modules/unknown_module")

    assert response.status_code == 404


def test_me_endpoint_uses_free_fallback_in_dev_bypass(test_app):
    with TestClient(test_app) as client:
        response = client.get("/api/modules/me")

    assert response.status_code == 200
    body = response.json()
    assert body["plan"] == "free"
    available = {module["key"] for module in body["available_modules"]}
    locked = {module["key"] for module in body["locked_modules"]}
    assert "core" in available
    assert "script_analysis" in available
    assert "storyboard_ai" in locked
