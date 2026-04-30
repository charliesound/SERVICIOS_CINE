#!/usr/bin/env python3
"""
Smoke test for production real fixture.
Validates full workflow: media, reconcile, score, assembly, DaVinci export.
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


def test_fixture_structure():
    """Verify fixture directory structure."""
    fixture_base = ROOT / "docs" / "validation" / "production_real_20260428"
    errors = []

    required_dirs = ["camera", "sound", "reports", "script", "exports", "logs"]
    for d in required_dirs:
        dir_path = fixture_base / d
        if not dir_path.exists():
            errors.append(f"Missing directory: {d}")

    required_files = [
        "script/script_notes.md",
        "reports/camera_report.csv",
        "reports/sound_report.csv",
        "exports/assembly_windows.fcpxml",
        "exports/assembly_mac.fcpxml",
        "exports/assembly_linux.fcpxml",
        "exports/assembly_offline_relink.fcpxml",
    ]

    for f in required_files:
        file_path = fixture_base / f
        if not file_path.exists():
            errors.append(f"Missing file: {f}")

    return errors, fixture_base


def test_fcpxml_structure(platform, fcpxml_bytes):
    """Validate FCPXML structure."""
    errors = []
    try:
        root = ET.fromstring(fcpxml_bytes)
    except ET.ParseError as e:
        errors.append(f"FCPXML {platform} parse error: {e}")
        return errors

    resources = root.find(".//resources")
    if resources is None:
        errors.append(f"FCPXML {platform} missing resources")

    library = root.find(".//library")
    if library is None:
        errors.append(f"FCPXML {platform} missing library")

    assets = root.findall(".//resources/asset")
    if len(assets) < 2:
        errors.append(f"FCPXML {platform} has insufficient assets: {len(assets)}")

    spine_clips = root.findall(".//spine/asset-clip")
    if len(spine_clips) < 3:
        errors.append(f"FCPXML {platform} has insufficient clips: {len(spine_clips)}")

    return errors


def test_platform_uris(fcpxml_bytes, platform):
    """Validate platform-specific URIs."""
    errors = []

    platform_patterns = {
        "windows": [b"file:///", b"C:/", b"c:/"],
        "mac": [b"file:///", b"/Users/", b"/Volumes/"],
        "linux": [b"file:///", b"/home/", b"/mnt/"],
        "offline": [b"file:///tmp/"],
    }

    expected_patterns = platform_patterns.get(platform, [])
    if not any(p in fcpxml_bytes for p in expected_patterns):
        errors.append(f"FCPXML {platform} missing expected URI pattern: {expected_patterns}")

    return errors


def test_relink_report(fixture_base, platform):
    """Validate media relink report."""
    errors = []
    relink_path = fixture_base / "logs" / f"media_relink_report_{platform}.json"

    if not relink_path.exists():
        errors.append(f"Relink report {platform} not found")
        return errors, {}

    report = json.loads(relink_path.read_text())
    resources = report.get("resources", {})

    video_resources = [r for r in resources.values() if r.get("asset_type") == "video"]
    audio_resources = [r for r in resources.values() if r.get("asset_type") == "audio"]

    if not video_resources:
        errors.append(f"Relink report {platform} has no video resources")
    if not audio_resources:
        errors.append(f"Relink report {platform} has no audio resources")

    summary = report.get("dual_system_summary", {})
    if summary.get("matched", 0) < 6:
        errors.append(f"Relink report {platform} has insufficient matched items")

    return errors, report


def test_assembly_result(fixture_base):
    """Validate assembly result."""
    errors = []
    assembly_path = fixture_base / "logs" / "assembly_result.json"

    if not assembly_path.exists():
        errors.append("Assembly result not found")
        return errors, {}

    assembly = json.loads(assembly_path.read_text())
    items = assembly.get("assembly_cut", {}).get("items", [])

    if len(items) < 3:
        errors.append(f"Assembly has insufficient items: {len(items)}")

    return errors, assembly


def main():
    print("=== Running Production Real Fixture Smoke Tests ===")
    print()

    all_errors = []

    print("Test 1: Fixture structure")
    errors, fixture_base = test_fixture_structure()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: Fixture structure valid")
    print()

    print("Test 2: FCPXML exports")
    for platform in ["windows", "mac", "linux", "offline"]:
        fcpxml_path = fixture_base / "exports" / f"assembly_{platform}.fcpxml"
        if fcpxml_path.exists():
            errors = test_fcpxml_structure(platform, fcpxml_path.read_bytes())
            errors.extend(test_platform_uris(fcpxml_path.read_bytes(), platform))
            if errors:
                all_errors.extend(errors)
                for e in errors:
                    print(f"  FAIL [{platform}]: {e}")
            else:
                print(f"  PASS [{platform}]: FCPXML valid")
        else:
            all_errors.append(f"FCPXML {platform} not found")
            print(f"  FAIL [{platform}]: Not found")
    print()

    print("Test 3: Media relink reports")
    for platform in ["windows", "mac", "linux", "offline"]:
        errors, _ = test_relink_report(fixture_base, platform)
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(f"  FAIL [{platform}]: {e}")
        else:
            print(f"  PASS [{platform}]: Relink report valid")
    print()

    print("Test 4: Assembly result")
    errors, _ = test_assembly_result(fixture_base)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: Assembly result valid")
    print()

    print("Test 5: Editorial notes")
    notes_path = fixture_base / "exports" / "editorial_notes.txt"
    if notes_path.exists():
        print("  PASS: Editorial notes exist")
    else:
        all_errors.append("Editorial notes not found")
        print("  FAIL: Editorial notes not found")
    print()

    if all_errors:
        print(f"FAILED: {len(all_errors)} errors")
        return 1
    else:
        print("SUCCESS: All production real fixture smoke tests passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())