from __future__ import annotations

import asyncio

import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("HEALTHCHECK_DB_ENABLED", "false")


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("AUTH_DISABLED", "true")
    monkeypatch.setenv("APP_ENV", "development")
    from core.config import reload_settings

    reload_settings()


class TestExtractVisualBibleMetadata:
    def test_extracts_full_visual_bible_from_dict(self):
        from services.job_tracking_service import JobTrackingService

        source = {
            "visual_bible_enabled": True,
            "visual_bible_applied": True,
            "visual_bible_id": "vb-abc-123",
            "visual_bible_preset": "noir_classic",
        }
        result = JobTrackingService._extract_visual_bible_metadata(source)
        assert result == {
            "visual_bible": {
                "enabled": True,
                "applied": True,
                "visual_bible_id": "vb-abc-123",
                "visual_bible_preset": "noir_classic",
                "source": "render_job_metadata",
            }
        }

    def test_parses_string_json(self):
        from services.job_tracking_service import JobTrackingService

        source = json.dumps({
            "visual_bible_enabled": True,
            "visual_bible_applied": True,
            "visual_bible_id": "vb-json-1",
            "visual_bible_preset": "cinematic_real",
        })
        result = JobTrackingService._extract_visual_bible_metadata(source)
        assert result["visual_bible"]["visual_bible_id"] == "vb-json-1"
        assert result["visual_bible"]["visual_bible_preset"] == "cinematic_real"

    def test_invalid_json_returns_empty(self):
        from services.job_tracking_service import JobTrackingService

        result = JobTrackingService._extract_visual_bible_metadata("not valid json")
        assert result == {}

    def test_none_metadata_returns_empty(self):
        from services.job_tracking_service import JobTrackingService

        result = JobTrackingService._extract_visual_bible_metadata(None)
        assert result == {}

    def test_empty_dict_returns_empty(self):
        from services.job_tracking_service import JobTrackingService

        result = JobTrackingService._extract_visual_bible_metadata({})
        assert result == {}

    def test_no_visual_bible_keys_returns_empty(self):
        from services.job_tracking_service import JobTrackingService

        source = {"storyboard_shot_id": "shot-1", "style_preset": "realistic"}
        result = JobTrackingService._extract_visual_bible_metadata(source)
        assert result == {}

    def test_preserves_partial_visual_bible(self):
        from services.job_tracking_service import JobTrackingService

        source = {
            "visual_bible_enabled": True,
            "visual_bible_applied": False,
        }
        result = JobTrackingService._extract_visual_bible_metadata(source)
        assert result["visual_bible"]["enabled"] is True
        assert result["visual_bible"]["applied"] is False
        assert result["visual_bible"]["visual_bible_id"] is None
        assert result["visual_bible"]["visual_bible_preset"] is None

    def test_visual_bible_applied_false_preserved(self):
        from services.job_tracking_service import JobTrackingService

        source = {
            "visual_bible_enabled": True,
            "visual_bible_applied": False,
            "visual_bible_id": "vb-false-1",
            "visual_bible_preset": "noir_classic",
        }
        result = JobTrackingService._extract_visual_bible_metadata(source)
        assert result["visual_bible"]["enabled"] is True
        assert result["visual_bible"]["applied"] is False
        assert result["visual_bible"]["visual_bible_preset"] == "noir_classic"

    def test_non_dict_non_string_returns_empty(self):
        from services.job_tracking_service import JobTrackingService

        result = JobTrackingService._extract_visual_bible_metadata(42)
        assert result == {}
        result = JobTrackingService._extract_visual_bible_metadata([])
        assert result == {}


class TestPersistSchedulerSuccessAssetsMergesVisualBible:
    def test_asset_metadata_contains_visual_bible(self):
        from services.job_tracking_service import JobTrackingService

        svc = JobTrackingService()
        db = AsyncMock()
        db.get = AsyncMock(return_value=MagicMock(
            organization_id="org-1",
            project_id="proj-1",
            id="job-1",
            created_by="user-1",
        ))

        history_entry = {
            "outputs": {
                "node_1": {
                    "images": [
                        {"filename": "frame_0001.png", "subfolder": "", "type": "output"}
                    ]
                }
            }
        }

        source_metadata = {
            "storyboard_shot_id": "shot-1",
            "visual_bible_enabled": True,
            "visual_bible_applied": True,
            "visual_bible_id": "vb-integration-1",
            "visual_bible_preset": "noir_classic",
            "prompt": "grounded prompt",
            "negative_prompt": "no watermark",
            "checkpoint": "Realistic_Vision_V2.0.safetensors",
            "seed": 123,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "width": 1024,
            "height": 576,
            "source_scene_heading": "INT. CASA ABANDONADA - NOCHE",
            "source_action_summary": "Marta enters with a flashlight.",
            "source_dialogue_summary": "MARTA: ¿Hay alguien ahí?",
        }

        with (
            patch.object(svc, "_download_backend_asset", return_value=(b"fake-bytes", "http://ref")),
            patch.object(svc, "_build_local_asset_paths", return_value=(Path("/tmp/test.png"), "renders/test.png")),
            patch.object(svc, "_create_thumbnail_webp", return_value={}),
            patch.object(svc, "upsert_job_asset", new_callable=AsyncMock) as mock_upsert,
        ):
            assets = asyncio.run(svc.persist_scheduler_success_assets(
                db,
                job_id="job-1",
                prompt_id="prompt-1",
                backend_base_url="http://backend",
                history_entry=history_entry,
                source_metadata=source_metadata,
            ))

        mock_upsert.assert_awaited_once()
        _call_kwargs = mock_upsert.call_args.kwargs
        meta = _call_kwargs["metadata_json"]
        assert "visual_bible" in meta
        assert meta["visual_bible"]["enabled"] is True
        assert meta["visual_bible"]["applied"] is True
        assert meta["visual_bible"]["visual_bible_id"] == "vb-integration-1"
        assert meta["visual_bible"]["visual_bible_preset"] == "noir_classic"
        assert meta["visual_bible"]["source"] == "render_job_metadata"
        assert meta["prompt"] == "grounded prompt"
        assert meta["seed"] == 123
        assert meta["width"] == 1024
        assert meta["height"] == 576
        assert meta["source_scene_heading"] == "INT. CASA ABANDONADA - NOCHE"
        assert meta["prompt_id"] == "prompt-1"
        assert meta["node_id"] == "node_1"

    def test_no_visual_bible_does_not_add_key(self):
        from services.job_tracking_service import JobTrackingService

        svc = JobTrackingService()
        db = AsyncMock()
        db.get = AsyncMock(return_value=MagicMock(
            organization_id="org-1",
            project_id="proj-1",
            id="job-1",
            created_by="user-1",
        ))

        history_entry = {
            "outputs": {
                "node_1": {
                    "images": [
                        {"filename": "frame_0001.png", "subfolder": "", "type": "output"}
                    ]
                }
            }
        }

        with (
            patch.object(svc, "_download_backend_asset", return_value=(b"fake-bytes", "http://ref")),
            patch.object(svc, "_build_local_asset_paths", return_value=(Path("/tmp/test.png"), "renders/test.png")),
            patch.object(svc, "_create_thumbnail_webp", return_value={}),
            patch.object(svc, "upsert_job_asset", new_callable=AsyncMock) as mock_upsert,
        ):
            asyncio.run(svc.persist_scheduler_success_assets(
                db,
                job_id="job-1",
                prompt_id="prompt-1",
                backend_base_url="http://backend",
                history_entry=history_entry,
                source_metadata={"storyboard_shot_id": "shot-1"},
            ))

        mock_upsert.assert_awaited_once()
        _call_kwargs = mock_upsert.call_args.kwargs
        meta = _call_kwargs["metadata_json"]
        assert "visual_bible" not in meta

    def test_non_storyboard_job_no_visual_bible(self):
        from services.job_tracking_service import JobTrackingService

        svc = JobTrackingService()
        db = AsyncMock()
        db.get = AsyncMock(return_value=MagicMock(
            organization_id="org-1",
            project_id="proj-1",
            id="job-1",
            created_by="user-1",
        ))

        history_entry = {
            "outputs": {
                "node_1": {
                    "images": [
                        {"filename": "video_0001.mp4", "subfolder": "", "type": "output"}
                    ]
                }
            }
        }

        with (
            patch.object(svc, "_download_backend_asset", return_value=(b"fake-video", "http://ref")),
            patch.object(svc, "_build_local_asset_paths", return_value=(Path("/tmp/test.mp4"), "renders/test.mp4")),
            patch.object(svc, "_create_thumbnail_webp", return_value={}),
            patch.object(svc, "upsert_job_asset", new_callable=AsyncMock) as mock_upsert,
        ):
            asyncio.run(svc.persist_scheduler_success_assets(
                db,
                job_id="job-1",
                prompt_id="prompt-1",
                backend_base_url="http://backend",
                history_entry=history_entry,
                source_metadata=None,
            ))

        mock_upsert.assert_awaited_once()
        _call_kwargs = mock_upsert.call_args.kwargs
        meta = _call_kwargs["metadata_json"]
        assert "visual_bible" not in meta
        assert meta["prompt_id"] == "prompt-1"
        assert meta["node_id"] == "node_1"
