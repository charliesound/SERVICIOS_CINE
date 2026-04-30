#!/usr/bin/env python3
"""
Smoke test for FCPXML dual-system variants.
Validates conservative and experimental FCPXML files.
"""
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

FIXTURE_BASE = Path("/opt/SERVICIOS_CINE/docs/validation/dual_system_real_20260428")
FCPXML_DIR = FIXTURE_BASE / "fcpxml"


def validate_fcpxml_structure(xml_bytes: bytes, variant_name: str) -> list[str]:
    """Validate FCPXML structure."""
    errors = []
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as e:
        errors.append(f"{variant_name}: XML parse error - {e}")
        return errors

    if root.tag != "fcpxml":
        errors.append(f"{variant_name}: Root element must be fcpxml")

    resources = root.find(".//resources")
    if resources is None:
        errors.append(f"{variant_name}: Missing resources element")

    library = root.find(".//library")
    if library is None:
        errors.append(f"{variant_name}: Missing library element")

    return errors


def validate_conservative_fcpxml(xml_bytes: bytes) -> list[str]:
    """Validate conservative FCPXML."""
    errors = validate_fcpxml_structure(xml_bytes, "conservative")

    root = ET.fromstring(xml_bytes)
    assets = root.findall(".//resources/asset")
    if len(assets) < 2:
        errors.append("conservative: Expected at least 2 assets")

    asset_names = [a.get("name", "") for a in assets]
    audio_assets = [n for n in asset_names if "AUDIO" in n]
    if not audio_assets:
        errors.append("conservative: Missing audio assets")

    clips = root.findall(".//spine/asset-clip")
    if not clips:
        errors.append("conservative: Missing spine clips")

    return errors


def validate_experimental_fcpxml(xml_bytes: bytes) -> list[str]:
    """Validate experimental FCPXML with linked audio."""
    errors = validate_fcpxml_structure(xml_bytes, "experimental")

    root = ET.fromstring(xml_bytes)
    assets = root.findall(".//resources/asset")
    if len(assets) < 2:
        errors.append("experimental: Expected at least 2 assets")

    video_assets = [a for a in assets if a.get("hasVideo") == "1"]
    if not video_assets:
        errors.append("experimental: Missing video-only assets")

    audio_assets = [a for a in assets if a.get("hasAudio") == "1"]
    if not audio_assets:
        errors.append("experimental: Missing audio assets")

    tracks = root.findall(".//sequence/track")
    audio_tracks = [t for t in tracks if t.get("type") == "audio"]
    if not audio_tracks:
        errors.append("experimental: Missing audio track")

    spines = root.findall(".//spine/asset-clip")
    if not spines:
        errors.append("experimental: Missing spine clips")

    return errors


def validate_media_relink_report() -> list[str]:
    """Validate media relink report contains both video and audio."""
    errors = []
    relink_path = FIXTURE_BASE / "reports" / "media_relink_report.json"
    if not relink_path.exists():
        errors.append("media_relink_report.json not found")
        return errors

    report = json.loads(relink_path.read_text())
    resources = report.get("resources", {})

    video_resources = [r for r in resources.values() if r.get("asset_type") == "video"]
    audio_resources = [r for r in resources.values() if r.get("asset_type") == "audio"]

    if not video_resources:
        errors.append("media_relink_report: No video resources")
    if not audio_resources:
        errors.append("media_relink_report: No audio resources")

    return errors


def main():
    print("Running smoke tests for FCPXML dual-system variants...")
    print()

    all_errors = []

    conservative_path = FCPXML_DIR / "Apartment_conservative.fcpxml"
    if conservative_path.exists():
        errors = validate_conservative_fcpxml(conservative_path.read_bytes())
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(f"FAIL: {e}")
        else:
            print("PASS: conservative FCPXML structure valid")
    else:
        all_errors.append("conservative.fcpxml not found")
        print("FAIL: conservative.fcpxml not found")

    experimental_path = FCPXML_DIR / "Apartment_linked_audio_experimental.fcpxml"
    if experimental_path.exists():
        errors = validate_experimental_fcpxml(experimental_path.read_bytes())
        if errors:
            all_errors.extend(errors)
            for e in errors:
                print(f"FAIL: {e}")
        else:
            print("PASS: experimental FCPXML structure valid")
    else:
        all_errors.append("experimental.fcpxml not found")
        print("FAIL: experimental.fcpxml not found")

    errors = validate_media_relink_report()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"FAIL: {e}")
    else:
        print("PASS: media_relink_report.json valid")

    print()
    if all_errors:
        print(f"FAILED: {len(all_errors)} errors")
        return 1
    else:
        print("SUCCESS: All smoke tests passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())