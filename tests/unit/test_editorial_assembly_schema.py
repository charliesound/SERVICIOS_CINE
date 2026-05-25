from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


def test_editorial_assembly_schemas_serialize():
    from schemas.editorial_assembly_schema import (
        AssemblyClip,
        AssemblySequence,
        AssemblyTimeline,
        EditorialMediaAsset,
        NLEExportResult,
        TakeDecision,
    )

    asset = EditorialMediaAsset(
        id="asset-1",
        file_name="A001_C001.mov",
        file_path="/media/A001_C001.mov",
        asset_type="video",
        duration_frames=96,
    )
    decision = TakeDecision(
        take_id="take-1-1-1",
        scene_number=1,
        shot_number=1,
        take_number=1,
        score=0.9,
        is_recommended=True,
        recommended_reason="circled_take",
        camera_asset_id=asset.id,
    )
    clip = AssemblyClip(
        id="clip-1",
        take_id=decision.take_id,
        clip_name="S1_SH1_TK1",
        source_media_asset_id=asset.id,
        timeline_out=96,
        duration_frames=96,
    )
    timeline = AssemblyTimeline(
        id="assembly-1",
        project_id="project-1",
        name="Assembly",
        total_duration_frames=96,
        sequences=[AssemblySequence(id="seq-1", name="Scene 1", scene_number=1, clips=[clip])],
    )
    result = NLEExportResult(
        nle_type="resolve",
        export_format="fcpxml",
        file_name="assembly.fcpxml",
        file_bytes_b64=base64.b64encode(b"<fcpxml />").decode("ascii"),
    )

    dumped = timeline.model_dump(mode="json")
    assert dumped["sequences"][0]["clips"][0]["assigned_tracks"] == ["V1", "A1"]
    assert result.model_dump()["nle_type"] == "resolve"


def test_export_request_accepts_embedded_timeline():
    from schemas.editorial_assembly_schema import AssemblyTimeline, NLEExportRequest

    timeline = AssemblyTimeline(id="assembly-1", project_id="project-1", name="Assembly")
    request = NLEExportRequest(nle_type="resolve", timeline=timeline)

    assert request.timeline is not None
    assert request.timeline.project_id == "project-1"
