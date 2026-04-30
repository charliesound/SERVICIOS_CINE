from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT / "docs" / "validation" / "davinci_manual_20260428_windows"
FCPXML_PATH = PACKAGE_DIR / "assembly_windows.fcpxml"
MEDIA_DIR = PACKAGE_DIR / "media"
REPORT_PATH = PACKAGE_DIR / "media_relink_report_windows.json"
ZIP_PATH = PACKAGE_DIR / "CID_DaVinci_Validation_20260428_WINDOWS.zip"
EXPECTED_URI_PREFIX = "file:///C:/CID_DaVinci_Validation_20260428/media/"


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> None:
    if not FCPXML_PATH.exists():
        fail(f"Missing FCPXML: {FCPXML_PATH}")
    if not MEDIA_DIR.exists() or not MEDIA_DIR.is_dir():
        fail(f"Missing media directory: {MEDIA_DIR}")
    if not REPORT_PATH.exists():
        fail(f"Missing Windows relink report: {REPORT_PATH}")
    if not ZIP_PATH.exists():
        fail(f"Missing Windows ZIP: {ZIP_PATH}")

    xml_text = FCPXML_PATH.read_text(encoding="utf-8")
    if "/opt/SERVICIOS_CINE" in xml_text:
        fail("FCPXML still contains /opt/SERVICIOS_CINE paths")
    if "file:///tmp" in xml_text:
        fail("FCPXML still contains file:///tmp paths")
    if EXPECTED_URI_PREFIX not in xml_text:
        fail(f"FCPXML does not contain expected Windows URI prefix: {EXPECTED_URI_PREFIX}")

    tree = ET.parse(FCPXML_PATH)
    root = tree.getroot()
    asset_srcs = [asset.get("src") for asset in root.findall(".//asset") if asset.get("src")]
    missing_media_files = []
    for src in asset_srcs:
        filename = Path(src.replace("file:///C:/CID_DaVinci_Validation_20260428/media/", "")).name
        if not (MEDIA_DIR / filename).exists():
            missing_media_files.append(filename)
    if missing_media_files:
        fail(f"Referenced media files are missing: {missing_media_files}")

    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    if report.get("offline_media_count") != 0:
        fail(f"offline_media_count is not zero: {report.get('offline_media_count')}")
    report_missing = []
    for entry in report.get("entries", []):
        copied_media_path = Path(entry["copied_media_path"])
        if not copied_media_path.exists():
            report_missing.append(str(copied_media_path))
    if report_missing:
        fail(f"Copied media files missing from report: {report_missing}")

    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        names = set(archive.namelist())
    required = {
        "assembly_windows.fcpxml",
        "media_relink_report_windows.json",
        "assembly_summary.json",
        "recommended_takes.json",
        "editorial_notes.txt",
        "validation_log_windows.md",
        "README_WINDOWS_DAVINCI_IMPORT.md",
    }
    if not required.issubset(names):
        fail(f"ZIP is missing required entries: {sorted(required.difference(names))}")

    print(
        json.dumps(
            {
                "status": "PASS",
                "fcpxml_path": str(FCPXML_PATH),
                "media_dir": str(MEDIA_DIR),
                "zip_path": str(ZIP_PATH),
                "asset_count": len(asset_srcs),
                "copied_media_count": len(report.get("entries", [])),
                "expected_uri_prefix": EXPECTED_URI_PREFIX,
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, ensure_ascii=True, indent=2))
        sys.exit(1)
