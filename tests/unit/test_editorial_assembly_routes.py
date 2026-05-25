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
    assert body["manifest"]["status"] == "resolve_fcpxml_ready"


def test_resolve_route_exports_real_fcpxml_with_relink_report(test_app):
    payload = {
        "nle_type": "resolve",
        "target_platform": "linux",
        "destination_root_path": "/mnt/editorial/export",
        "media_assets": [
            {
                "id": "video-1",
                "file_name": "A001_C001.mov",
                "file_path": "/media/A001_C001.mov",
                "asset_type": "video",
                "duration_frames": 48,
            },
            {
                "id": "audio-1",
                "file_name": "S001_T001.wav",
                "file_path": "/media/S001_T001.wav",
                "asset_type": "audio",
                "duration_frames": 48,
            },
        ],
        "timeline": {
            "id": "assembly-1",
            "project_id": "project-1",
            "name": "Assembly",
            "fps": 24.0,
            "total_duration_frames": 48,
            "sequences": [
                {
                    "id": "seq-1",
                    "name": "Scene 1",
                    "scene_number": 1,
                    "clips": [
                        {
                            "id": "clip-1",
                            "take_id": "take-1-1-1",
                            "clip_name": "S1_SH1_TK1",
                            "source_media_asset_id": "video-1",
                            "audio_media_asset_id": "audio-1",
                            "timeline_in": 0,
                            "timeline_out": 48,
                            "duration_frames": 48,
                            "fps": 24.0,
                        }
                    ],
                }
            ],
        },
    }

    with TestClient(test_app) as client:
        response = client.post("/api/projects/project-1/editorial/export/resolve", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["manifest"]["validation"]["valid"] is True
    assert body["manifest"]["relink_report"]["resolved_media_count"] == 2
    assert body["artifact_path"] == "/mnt/editorial/export/Assembly_assembly.fcpxml"
