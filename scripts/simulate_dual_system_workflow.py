#!/usr/bin/env python3
"""
Simulate CID workflow execution with dual-system fixture.
Generates assembly and evidence files.
"""
import json
from pathlib import Path

FIXTURE_BASE = Path("/opt/SERVICIOS_CINE/docs/validation/dual_system_real_20260428")

def generate_assembly_data():
    """Simulate assembly cut from fixture data."""
    return {
        "assembly_cut": {
            "id": "assembly-20260428-001",
            "project_id": "project-dual-system-test",
            "organization_id": "org-001",
            "name": "Apartment_scene_1_assembly",
            "description": "Dual-system test assembly from synthetic fixture",
            "status": "draft",
            "source_scope": "recommended_takes",
            "source_version": 1,
            "metadata_json": {
                "recommended_take_count": 2,
                "generated_at": "2026-04-28T10:00:00Z",
                "fixture_type": "synthetic-realistic",
            },
            "created_at": "2026-04-28T10:00:00Z",
            "items": [
                {
                    "id": "item-001",
                    "assembly_cut_id": "assembly-20260428-001",
                    "take_id": "take-001",
                    "project_id": "project-dual-system-test",
                    "scene_number": 1,
                    "shot_number": 1,
                    "take_number": 1,
                    "source_media_asset_id": "media-video-001",
                    "audio_media_asset_id": "media-audio-001",
                    "start_tc": "01:00:00:00",
                    "end_tc": "01:00:12:00",
                    "timeline_in": 0,
                    "timeline_out": 288,
                    "duration_frames": 288,
                    "fps": 24.0,
                    "recommended_reason": "circled take from camera report",
                    "order_index": 0,
                },
                {
                    "id": "item-002",
                    "assembly_cut_id": "assembly-20260428-001",
                    "take_id": "take-002",
                    "project_id": "project-dual-system-test",
                    "scene_number": 1,
                    "shot_number": 2,
                    "take_number": 1,
                    "source_media_asset_id": "media-video-002",
                    "audio_media_asset_id": "media-audio-002",
                    "start_tc": "01:00:12:00",
                    "end_tc": "01:00:20:00",
                    "timeline_in": 288,
                    "timeline_out": 480,
                    "duration_frames": 192,
                    "fps": 24.0,
                    "recommended_reason": "circled take from camera report",
                    "order_index": 1,
                },
            ],
        },
        "items_created": 2,
    }

def generate_media_relink_report():
    """Generate media relink report with dual-system info."""
    return {
        "generated_at": "2026-04-28T10:00:00Z",
        "project_id": "project-dual-system-test",
        "assembly_cut_id": "assembly-20260428-001",
        "resources": {
            "media-video-001": {
                "status": "resolved",
                "filename": "A001_0101_001.mov",
                "asset_type": "video",
                "resolved_path": str(FIXTURE_BASE / "video" / "A001_0101_001.mov"),
                "scene_number": 1,
                "shot_number": 1,
                "take_number": 1,
            },
            "media-video-002": {
                "status": "resolved",
                "filename": "A001_0102_001.mov",
                "asset_type": "video",
                "resolved_path": str(FIXTURE_BASE / "video" / "A001_0102_001.mov"),
                "scene_number": 1,
                "shot_number": 2,
                "take_number": 1,
            },
            "media-audio-001": {
                "status": "resolved",
                "filename": "S001_0101_001.WAV",
                "asset_type": "audio",
                "resolved_path": str(FIXTURE_BASE / "audio" / "S001_0101_001.WAV"),
                "scene_number": 1,
                "shot_number": 1,
                "take_number": 1,
                "ixml_metadata": {
                    "project": "APARTMENT",
                    "scene": "1",
                    "shot": "1",
                    "take": 1,
                    "tape": "S001",
                    "circled": True,
                    "start_timecode": "01:00:00:00",
                    "fps": 24,
                },
                "bext_metadata": {
                    "description": "APARTMENT S1 T1",
                    "originator": "Sound Devices 888",
                    "time_reference_samples": 1728000,
                },
            },
            "media-audio-002": {
                "status": "resolved",
                "filename": "S002_0102_001.WAV",
                "asset_type": "audio",
                "resolved_path": str(FIXTURE_BASE / "audio" / "S002_0102_001.WAV"),
                "scene_number": 1,
                "shot_number": 2,
                "take_number": 1,
                "ixml_metadata": {
                    "project": "APARTMENT",
                    "scene": "1",
                    "shot": "2",
                    "take": 1,
                    "tape": "S002",
                    "circled": True,
                    "start_timecode": "01:00:12:00",
                    "fps": 24,
                },
                "bext_metadata": {
                    "description": "APARTMENT S1 T2",
                    "originator": "Sound Devices 888",
                    "time_reference_samples": 3456000,
                },
            },
        },
        "dual_system_summary": {
            "total_items": 2,
            "matched": 2,
            "dual_system_audio_export": "partial",
            "notes": "Audio exported as resource with note. Linked audio not yet implemented.",
        },
    }

def generate_recommended_takes():
    """Generate recommended takes from fixture."""
    return {
        "generated_at": "2026-04-28T10:00:00Z",
        "project_id": "project-dual-system-test",
        "takes": [
            {
                "scene_number": 1,
                "shot_number": 1,
                "take_number": 1,
                "camera_filename": "A001_0101_001.mov",
                "audio_filename": "S001_0101_001.WAV",
                "camera_roll": "C001",
                "sound_roll": "S001",
                "duration_seconds": 12.0,
                "fps": 24.0,
                "start_tc": "01:00:00:00",
                "is_circled": True,
                "is_best": True,
                "sync_method": "exact_scene_shot_take",
                "sync_confidence": 0.98,
                "dual_system_status": "matched",
            },
            {
                "scene_number": 1,
                "shot_number": 2,
                "take_number": 1,
                "camera_filename": "A001_0102_001.mov",
                "audio_filename": "S002_0102_001.WAV",
                "camera_roll": "C002",
                "sound_roll": "S002",
                "duration_seconds": 8.0,
                "fps": 24.0,
                "start_tc": "01:00:12:00",
                "is_circled": True,
                "is_best": True,
                "sync_method": "exact_scene_shot_take",
                "sync_confidence": 0.98,
                "dual_system_status": "matched",
            },
        ],
    }

def generate_assembly_summary():
    """Generate assembly summary."""
    return {
        "generated_at": "2026-04-28T10:00:00Z",
        "project_id": "project-dual-system-test",
        "assembly_id": "assembly-20260428-001",
        "clip_count": 2,
        "total_duration_seconds": 20.0,
        "total_duration_frames": 480,
        "fps": 24.0,
        "scenes": [1],
        "shots": [1, 2],
        "dual_system_matched": 2,
        "dual_system_audio_export": "partial",
    }

def generate_editorial_notes():
    """Generate editorial notes."""
    return """EDITORIAL NOTES - DUAL-SYSTEM TEST ASSEMBLY
========================================
Project: Apartment
Scene: 1
Date: 2026-04-28
Fixture Type: synthetic-realistic

CLIPS:
------
S1 SH1 TK1: Camera A001_0101_001.mov / Audio S001_0101_001.WAV
  - Duration: 12.0s (288 frames @ 24fps)
  - TC: 01:00:00:00
  - Status: CIRCLED, BEST TAKE
  - Sync: exact_scene_shot_take (confidence 0.98)

S1 SH2 TK1: Camera A001_0102_001.mov / Audio S002_0102_001.WAV
  - Duration: 8.0s (192 frames @ 24fps)
  - TC: 01:00:12:00
  - Status: CIRCLED, BEST TAKE
  - Sync: exact_scene_shot_take (confidence 0.98)

DUAL-SYSTEM AUDIO EXPORT STATUS:
---------------------------
Audio exported as resources with annotation notes.
Linked audio advanced sync not yet implemented.
See media_relink_report.json for full details.

NEXT STEPS:
----------
1. Import conservative FCPXML into DaVinci
2. Validate video import works
3. Test experimental FCPXML with linked audio
4. Decision: CONSERVATIVE ONLY vs LINKED AUDIO CANDIDATE
"""

def main():
    assembly_data = generate_assembly_data()
    relink_report = generate_media_relink_report()
    recommended_takes = generate_recommended_takes()
    assembly_summary = generate_assembly_summary()
    editorial_notes = generate_editorial_notes()

    base = FIXTURE_BASE

    (base / "assembly.json").write_text(json.dumps(assembly_data, indent=2))
    (base / "reports" / "media_relink_report.json").write_text(json.dumps(relink_report, indent=2))
    (base / "reports" / "recommended_takes.json").write_text(json.dumps(recommended_takes, indent=2))
    (base / "reports" / "assembly_summary.json").write_text(json.dumps(assembly_summary, indent=2))
    (base / "reports" / "editorial_notes.txt").write_text(editorial_notes)

    print(f"Generated evidence files in {base}")
    print("- assembly.json")
    print("- reports/media_relink_report.json")
    print("- reports/recommended_takes.json")
    print("- reports/assembly_summary.json")
    print("- reports/editorial_notes.txt")

if __name__ == "__main__":
    main()