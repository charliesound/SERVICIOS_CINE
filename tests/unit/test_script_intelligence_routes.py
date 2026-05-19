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


@pytest.fixture(autouse=True)
def _env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


@pytest.fixture
def test_app():
    from core.app_factory import create_app

    return create_app()


def _payload(*, fallback_used: bool = False, with_sources: bool = True) -> dict:
    return {
        "project_id": "proj-1",
        "overall_diagnosis": "ok",
        "syd_field": {"act_structure": "ok", "plot_point_1": "", "midpoint": "", "plot_point_2": "", "resolution": "", "issues": [], "recommendations": []},
        "comparato": {"idea": "", "conflict_matrix": "", "dramatic_action": "", "character_function": "", "issues": [], "recommendations": []},
        "mckee": {"scene_value_shifts": [], "conflict_levels": [], "crisis_climax_resolution": "", "subtext_notes": [], "issues": [], "recommendations": []},
        "scores": {
            "dramatic_clarity": 60,
            "conflict_strength": 61,
            "character_drive": 62,
            "structure_strength": 63,
            "pacing": 64,
            "cinematic_potential": 65,
        },
        "storyboard_actionables": ["a"],
        "theory_sources_used": [{"title": "Syd Field"}] if with_sources else [],
        "fallback_used": fallback_used,
    }


def test_script_intelligence_endpoint_returns_expected_sections(test_app, monkeypatch: pytest.MonkeyPatch):
    async def fake_analyze(*args, **kwargs):
        return _payload()

    monkeypatch.setattr("routes.script_intelligence_routes.cid_script_intelligence_service.analyze_project", fake_analyze)

    with TestClient(test_app) as client:
        resp = client.post("/api/projects/proj-1/script-intelligence/analyze", json={})

    assert resp.status_code == 200
    body = resp.json()
    assert "syd_field" in body
    assert "comparato" in body
    assert "mckee" in body
    for value in body["scores"].values():
        assert 0 <= int(value) <= 100
    assert body["theory_sources_used"]


def test_script_intelligence_fallback_works_without_qdrant(test_app, monkeypatch: pytest.MonkeyPatch):
    async def fake_analyze(*args, **kwargs):
        return _payload(fallback_used=True, with_sources=False)

    monkeypatch.setattr("routes.script_intelligence_routes.cid_script_intelligence_service.analyze_project", fake_analyze)

    with TestClient(test_app) as client:
        resp = client.post("/api/projects/proj-1/script-intelligence/analyze", json={"sequence_ids": ["seq_01"]})

    assert resp.status_code == 200
    body = resp.json()
    assert body["fallback_used"] is True


def test_script_intelligence_accepts_sequence_ids_mvp(test_app, monkeypatch: pytest.MonkeyPatch):
    captured = {"sequence_ids": None}

    async def fake_analyze(*args, **kwargs):
        captured["sequence_ids"] = kwargs.get("sequence_ids")
        return _payload()

    monkeypatch.setattr("routes.script_intelligence_routes.cid_script_intelligence_service.analyze_project", fake_analyze)

    with TestClient(test_app) as client:
        resp = client.post(
            "/api/projects/proj-1/script-intelligence/analyze",
            json={"sequence_ids": ["seq_01", "seq_02"]},
        )

    assert resp.status_code == 200
    assert captured["sequence_ids"] == ["seq_01", "seq_02"]


def test_projects_analyze_route_still_available(test_app):
    with TestClient(test_app) as client:
        resp = client.post("/api/projects/non-existent/analyze")
    assert resp.status_code == 404
    body = resp.json()
    assert body.get("error", {}).get("message") == "Project not found"
