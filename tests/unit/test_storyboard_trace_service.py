from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)

from schemas.auth_schema import TenantContext  # noqa: E402
from services.storyboard_trace_service import storyboard_trace_service  # noqa: E402


class _Scalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _Result:
    def __init__(self, row=None, rows=None):
        self._row = row
        self._rows = rows if rows is not None else ([] if row is None else [row])

    def scalar_one_or_none(self):
        return self._row

    def scalars(self):
        return _Scalars(self._rows)


class _TraceDb:
    def __init__(self, *, shot, asset, job=None, versions=None):
        self.shot = shot
        self.asset = asset
        self.job = job
        self.versions = versions if versions is not None else [shot]
        self.storyboard_query_count = 0

    async def execute(self, stmt):
        sql = str(stmt)
        if "project_jobs" in sql:
            return _Result(self.job)
        if "media_assets" in sql:
            return _Result(self.asset, [self.asset] if self.asset is not None else [])
        if "storyboard_shots" in sql:
            if "storyboard_shots.is_active" in sql and "storyboard_shots.id" not in sql:
                return _Result(rows=[self.shot])
            if "storyboard_shots.asset_id" in sql:
                return _Result(self.shot)
            self.storyboard_query_count += 1
            if self.storyboard_query_count == 1:
                return _Result(self.shot)
            return _Result(rows=self.versions)
        return _Result()


def _tenant() -> TenantContext:
    return TenantContext(user_id="user-1", organization_id="org-1", role="admin", plan="enterprise", is_admin=True)


def _objects():
    now = datetime.now(timezone.utc)
    previous = SimpleNamespace(
        id="shot-old",
        project_id="proj-1",
        organization_id="org-1",
        sequence_id="seq-1",
        sequence_order=1,
        scene_number=2,
        narrative_text="Old prompt",
        asset_id="asset-old",
        shot_type="WS",
        visual_mode="hand_drawn_storyboard",
        generation_mode="SEQUENCE",
        generation_job_id="gen-job-0",
        version=1,
        is_active=False,
        created_at=now,
        updated_at=now,
        metadata_json=json.dumps({"prompt_spec": {"positive_prompt": "old"}}),
    )
    shot = SimpleNamespace(
        id="shot-1",
        project_id="proj-1",
        organization_id="org-1",
        sequence_id="seq-1",
        sequence_order=1,
        scene_number=2,
        narrative_text="Original narrative",
        asset_id="asset-1",
        shot_type="MS",
        visual_mode="hand_drawn_storyboard",
        generation_mode="SEQUENCE",
        generation_job_id="gen-job-1",
        version=2,
        is_active=True,
        created_at=now,
        updated_at=now,
        metadata_json=json.dumps({
            "render_job_id": "render-job-1",
            "source_scene_heading": "INT. CASA ABANDONADA - NOCHE",
            "source_action_summary": "MARTA entra con una linterna. Una sombra cruza al fondo del pasillo.",
            "source_dialogue_summary": "MARTA: ¿Hay alguien ahí?",
            "width": 1024,
            "height": 576,
            "prompt_spec": {
                "positive_prompt": "cinematic corridor shot",
                "negative_prompt": "watermark",
                "checkpoint": "/opt/SERVICIOS_CINE/models/checkpoint.safetensors",
                "seed": 123,
                "steps": 20,
                "cfg": 7.0,
                "sampler_name": "euler",
            },
            "model_family": "sdxl",
            "asset_association": {
                "association_method": "direct_metadata_link",
                "association_confidence": 1.0,
                "association_reason": "metadata_json.storyboard_shot_id",
                "repaired_at": now.isoformat(),
            },
        }),
    )
    asset = SimpleNamespace(
        id="asset-1",
        project_id="proj-1",
        organization_id="org-1",
        file_name="frame.png",
        file_size=1024,
        mime_type="image/png",
        job_id="render-job-1",
        canonical_path="/opt/SERVICIOS_CINE/private/frame.png",
        metadata_json=json.dumps({
            "storage_path": "/mnt/private/frame.png",
            "storyboard_shot_id": "shot-1",
            "workflow_key": "still_storyboard_frame",
            "prompt": "cinematic corridor shot",
            "negative_prompt": "watermark",
            "checkpoint": "Realistic_Vision_V2.0.safetensors",
            "seed": 123,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "width": 1024,
            "height": 576,
            "workflow_profile": {"requested": "storyboard_safe", "executed": "storyboard_safe"},
            "workflow_fallback_report": {"fallback_applied": False, "reason": "none"},
        }),
    )
    job = SimpleNamespace(
        id="render-job-1",
        project_id="proj-1",
        organization_id="org-1",
        result_data=json.dumps({"workflow_key": "still_storyboard_frame"}),
    )
    return shot, asset, job, [previous, shot]


def test_shot_trace_returns_prompt_workflow_asset_and_version(monkeypatch: pytest.MonkeyPatch) -> None:
    shot, asset, job, versions = _objects()
    db = _TraceDb(shot=shot, asset=asset, job=job, versions=versions)

    async def fake_project(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    monkeypatch.setattr("services.storyboard_trace_service.storyboard_service._get_project_for_tenant", fake_project)

    trace = asyncio.run(storyboard_trace_service.get_shot_trace(db, "proj-1", "shot-1", _tenant()))

    assert trace.prompt_trace.positive_prompt_enriched == "cinematic corridor shot"
    assert trace.prompt_trace.source_scene_heading == "INT. CASA ABANDONADA - NOCHE"
    assert "linterna" in (trace.prompt_trace.source_action_summary or "").lower()
    assert "marta" in (trace.prompt_trace.source_dialogue_summary or "").lower()
    assert trace.workflow_trace.workflow_key == "still_storyboard_frame"
    assert trace.model_trace.model_family == "sdxl"
    assert trace.model_trace.checkpoint == "checkpoint.safetensors"
    assert trace.model_trace.seed == 123
    assert trace.model_trace.width == 1024
    assert trace.model_trace.height == 576
    assert trace.render_job_id == "render-job-1"
    assert trace.asset_trace.media_asset_id == "asset-1"
    assert trace.version_trace.current_version == 2
    assert trace.version_trace.has_previous_versions is True
    assert "/opt/" not in trace.model_dump_json()
    assert "/mnt/" not in trace.model_dump_json()
    assert "canonical_path" not in trace.model_dump_json()
    assert "storage_path" not in trace.model_dump_json()


def test_project_trace_summary_returns_metrics(monkeypatch: pytest.MonkeyPatch) -> None:
    shot, asset, _job, _versions = _objects()
    db = _TraceDb(shot=shot, asset=asset)

    async def fake_project(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    monkeypatch.setattr("services.storyboard_trace_service.storyboard_service._get_project_for_tenant", fake_project)

    summary = asyncio.run(storyboard_trace_service.get_project_trace_summary(db, "proj-1", _tenant()))

    assert summary.total_shots == 1
    assert summary.shots_with_prompt == 1
    assert summary.shots_with_workflow == 1
    assert summary.shots_with_model == 1
    assert summary.shots_with_asset == 1
    assert summary.shots_with_render_job == 1
    assert summary.workflow_keys == ["still_storyboard_frame"]
    assert summary.checkpoints == ["checkpoint.safetensors"]


def test_asset_trace_inverse_finds_linked_shot(monkeypatch: pytest.MonkeyPatch) -> None:
    shot, asset, job, versions = _objects()
    db = _TraceDb(shot=shot, asset=asset, job=job, versions=versions)

    async def fake_project(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id)

    monkeypatch.setattr("services.storyboard_trace_service.storyboard_service._get_project_for_tenant", fake_project)

    trace = asyncio.run(storyboard_trace_service.get_asset_trace(db, "proj-1", "asset-1", _tenant()))

    assert trace.shot_id == "shot-1"
    assert trace.asset_trace.media_asset_id == "asset-1"
    assert trace.asset_trace.image_url == "/api/projects/proj-1/storyboard/shots/shot-1/image"
