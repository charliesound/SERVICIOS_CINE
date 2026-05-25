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


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


def test_contract_endpoints_do_not_return_500(test_app):
    with TestClient(test_app) as client:
        responses = [
            client.post("/api/projects/project-1/editorial/scan-media", json={"root_paths": []}),
            client.post("/api/projects/project-1/editorial/import-reports", json={}),
            client.post("/api/projects/project-1/editorial/match-takes", json={}),
            client.post("/api/projects/project-1/editorial/build-assembly", json={}),
            client.post("/api/projects/project-1/editorial/export/resolve", json={"nle_type": "resolve"}),
            client.post("/api/projects/project-1/editorial/export/premiere", json={"nle_type": "premiere"}),
            client.post("/api/projects/project-1/editorial/export/avid", json={"nle_type": "avid"}),
            client.get("/api/projects/project-1/editorial/reports/report-1"),
        ]

    assert all(response.status_code < 500 for response in responses)
    assert {response.status_code for response in responses} == {200}


def test_premiere_and_avid_routes_return_controlled_stub(test_app):
    with TestClient(test_app) as client:
        premiere = client.post("/api/projects/project-1/editorial/export/premiere", json={"nle_type": "premiere"})
        avid = client.post("/api/projects/project-1/editorial/export/avid", json={"nle_type": "avid"})

    assert premiere.status_code == 200
    assert "premiere_export_stub_controlled" in premiere.json()["warnings"]
    assert avid.status_code == 200
    assert "aaf_not_implemented_in_editorial_2a" in avid.json()["warnings"]


def test_resolve_route_returns_fcpxml_contract(test_app):
    with TestClient(test_app) as client:
        response = client.post("/api/projects/project-1/editorial/export/resolve", json={"nle_type": "resolve"})

    assert response.status_code == 200
    body = response.json()
    assert body["nle_type"] == "resolve"
    assert body["export_format"] == "fcpxml"
    assert body["manifest"]["status"] == "contract_ready"
