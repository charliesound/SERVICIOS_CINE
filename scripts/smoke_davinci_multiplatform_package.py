#!/usr/bin/env python3
"""
Smoke test for DaVinci multiplatform package generation.
Validates FCPXML generation for Windows, macOS, Linux, and offline modes.
"""
import json
import os
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("USE_ALEMBIC", "0")


def test_multiplatform_package_generation():
    """Test multiplatform package generation."""
    from services.davinci_platform_package_service import davinci_platform_package_service

    assembly_data = {
        "assembly_cut": {
            "id": "assembly-test-001",
            "project_id": "project-test",
            "name": "Test Assembly",
            "items": [
                {
                    "id": "item-1",
                    "scene_number": 1,
                    "shot_number": 1,
                    "take_number": 1,
                    "source_media_asset_id": "media-video-1",
                    "audio_media_asset_id": "media-audio-1",
                    "duration_frames": 96,
                    "fps": 24.0,
                    "timeline_in": 0,
                    "recommended_reason": "Circle take",
                },
                {
                    "id": "item-2",
                    "scene_number": 1,
                    "shot_number": 2,
                    "take_number": 1,
                    "source_media_asset_id": "media-video-2",
                    "audio_media_asset_id": "media-audio-2",
                    "duration_frames": 48,
                    "fps": 24.0,
                    "timeline_in": 96,
                    "recommended_reason": "Circle take",
                },
            ],
        }
    }

    resolved_assets = {
        "media-video-1": {"status": "resolved", "filename": "S1_SH1_TK1.mov"},
        "media-video-2": {"status": "resolved", "filename": "S1_SH2_TK1.mov"},
        "media-audio-1": {"status": "resolved", "filename": "S1_SH1_TK1.wav"},
        "media-audio-2": {"status": "resolved", "filename": "S1_SH2_TK1.wav"},
    }

    result = davinci_platform_package_service.build_multiplatform_package(
        project_name="Test_Project",
        assembly_cut=assembly_data,
        resolved_assets=resolved_assets,
        platforms=["windows", "mac", "linux", "offline"],
        root_paths={
            "windows": "C:/CID_DaVinci_Test",
            "mac": "/Users/testuser/CID_DaVinci_Test",
            "linux": "/home/testuser/CID_DaVinci_Test",
            "offline": "/tmp",
        },
        audio_mode="conservative",
    )

    packages = result["packages"]
    manifest = result["manifest"]

    errors = []

    if "windows" not in packages:
        errors.append("Windows package not generated")
    if "mac" not in packages:
        errors.append("Mac package not generated")
    if "linux" not in packages:
        errors.append("Linux package not generated")
    if "offline" not in packages:
        errors.append("Offline package not generated")

    if packages:
        windows_fcpxml = packages["windows"][0]
        windows_filename = packages["windows"][1]

        try:
            root = ET.fromstring(windows_fcpxml)
        except ET.ParseError as e:
            errors.append(f"Windows FCPXML parse error: {e}")

        assets = root.findall(".//resources/asset")
        if len(assets) < 2:
            errors.append(f"Windows FCPXML missing assets: {len(assets)}")

        has_windows_path = b"file:///C:/" in windows_fcpxml
        if not has_windows_path:
            errors.append("Windows FCPXML missing C:/ path")

    if packages.get("mac"):
        mac_fcpxml = packages["mac"][0]
        has_mac_path = b"file:///Users/" in mac_fcpxml or b"file:///Volumes/" in mac_fcpxml
        if not has_mac_path:
            errors.append("Mac FCPXML missing Users/Volumes path")

    if packages.get("linux"):
        linux_fcpxml = packages["linux"][0]
        has_linux_path = b"file:///home/" in linux_fcpxml or b"file:///mnt/" in linux_fcpxml
        if not has_linux_path:
            errors.append("Linux FCPXML missing home/mnt path")

    if packages.get("offline"):
        offline_fcpxml = packages["offline"][0]
        has_tmp_path = b"file:///tmp/" in offline_fcpxml
        if not has_tmp_path:
            errors.append("Offline FCPXML missing tmp path")

    if manifest.get("clip_count", 0) != 2:
        errors.append(f"Manifest clip count incorrect: {manifest.get('clip_count')}")

    return errors, packages, manifest


def test_relink_report_generation():
    """Test multiplatform relink report generation."""
    from services.davinci_platform_package_service import davinci_platform_package_service

    assembly_data = {
        "assembly_cut": {
            "id": "assembly-test-001",
            "project_id": "project-test",
            "name": "Test Assembly",
            "items": [
                {
                    "id": "item-1",
                    "scene_number": 1,
                    "shot_number": 1,
                    "take_number": 1,
                    "source_media_asset_id": "media-video-1",
                    "audio_media_asset_id": "media-audio-1",
                    "duration_frames": 96,
                    "fps": 24.0,
                },
            ],
        }
    }

    resolved_assets = {
        "media-video-1": {"status": "resolved", "filename": "S1_SH1_TK1.mov"},
    }

    relink_reports = davinci_platform_package_service.generate_multiplatform_relink_report(
        project_name="Test_Project",
        assembly_cut=assembly_data,
        resolved_assets=resolved_assets,
        platforms=["windows", "mac", "linux"],
    )

    errors = []

    for platform in ["windows", "mac", "linux"]:
        if platform not in relink_reports:
            errors.append(f"Relink report for {platform} not generated")
            continue

        report = relink_reports[platform]
        if not report.get("resources"):
            errors.append(f"Relink report {platform} has no resources")
        if report.get("platform") != platform:
            errors.append(f"Relink report {platform} has wrong platform value")

    return errors, relink_reports


def main():
    print("Running smoke tests for DaVinci multiplatform package...")
    print()

    all_errors = []

    print("Test 1: Multiplatform package generation")
    errors, packages, manifest = test_multiplatform_package_generation()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: Multiplatform packages generated")
        print(f"    - Platforms: {list(packages.keys())}")
        print(f"    - Clip count: {manifest.get('clip_count')}")

    print()
    print("Test 2: Relink report generation")
    errors, relink_reports = test_relink_report_generation()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: Relink reports generated")
        for platform, report in relink_reports.items():
            print(f"    - {platform}: {len(report.get('resources', {}))} resources")

    print()
    if all_errors:
        print(f"FAILED: {len(all_errors)} errors")
        return 1
    else:
        print("SUCCESS: All smoke tests passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())