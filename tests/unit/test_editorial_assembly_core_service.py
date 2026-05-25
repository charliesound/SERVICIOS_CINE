from __future__ import annotations

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


def test_scan_media_roots_indexes_video_and_audio(tmp_path):
    from services.editorial_assembly_core_service import editorial_assembly_core_service

    (tmp_path / "A001_C001.mov").write_text("video", encoding="utf-8")
    (tmp_path / "A001_T001.wav").write_text("audio", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    assets, warnings = editorial_assembly_core_service.scan_media_roots(
        project_id="project-1",
        root_paths=[str(tmp_path)],
    )

    assert warnings == []
    assert {asset.asset_type for asset in assets} == {"video", "audio"}
    assert len(assets) == 2


def test_match_takes_builds_decision_and_sync_candidate():
    from schemas.editorial_assembly_schema import (
        CameraReportEntry,
        DirectorNote,
        EditorialMediaAsset,
        ScriptSupervisorNote,
        SoundReportEntry,
    )
    from services.editorial_assembly_core_service import editorial_assembly_core_service

    video = EditorialMediaAsset(id="video-1", file_name="A001_C001.mov", file_path="/m/A001_C001.mov", asset_type="video")
    audio = EditorialMediaAsset(id="audio-1", file_name="A001_T001.wav", file_path="/m/A001_T001.wav", asset_type="audio")

    matches, decisions, sync_candidates, warnings = editorial_assembly_core_service.match_takes(
        project_id="project-1",
        media_assets=[video, audio],
        camera_reports=[CameraReportEntry(card_or_mag="A001", clip_name=video.file_name, scene=1, shot=1, take=1)],
        sound_reports=[SoundReportEntry(sound_roll="S001", file_name=audio.file_name, scene=1, take=1)],
        script_notes=[ScriptSupervisorNote(scene_number=1, shot_number=1, take_number=1, is_circled=True)],
        director_notes=[DirectorNote(scene_number=1, shot_number=1, take_number=1, is_preferred=True)],
    )

    assert warnings == []
    assert matches[0].matching_method == "exact_report_asset"
    assert decisions[0].is_recommended is True
    assert decisions[0].camera_asset_id == "video-1"
    assert sync_candidates[0].audio_asset_id == "audio-1"


def test_build_neutral_assembly_and_relink_report():
    from schemas.editorial_assembly_schema import EditorialMediaAsset, TakeDecision
    from services.editorial_assembly_core_service import editorial_assembly_core_service

    assets = [
        EditorialMediaAsset(
            id="video-1",
            file_name="A001_C001.mov",
            file_path="/source/A001_C001.mov",
            asset_type="video",
            duration_frames=48,
        )
    ]
    decisions = [
        TakeDecision(
            take_id="take-1-1-1",
            scene_number=1,
            shot_number=1,
            take_number=1,
            score=0.9,
            is_recommended=True,
            recommended_reason="score_threshold",
            camera_asset_id="video-1",
        )
    ]

    timeline = editorial_assembly_core_service.build_neutral_assembly(
        project_id="project-1",
        take_decisions=decisions,
        media_assets=assets,
    )
    report, missing = editorial_assembly_core_service.generate_relink_report(
        timeline=timeline,
        media_assets=assets,
        destination_root_path="/dest",
    )

    assert timeline.total_duration_frames == 48
    assert timeline.sequences[0].clips[0].clip_name == "S1_SH1_TK1"
    assert report.resolved_media_count == 1
    assert report.path_mappings["/source/A001_C001.mov"] == "/dest/A001_C001.mov"
    assert missing[0].role == "audio"
