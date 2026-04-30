from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "validation" / "davinci_manual_20260428"
OUTPUT_DIR = ROOT / "docs" / "validation" / "davinci_manual_20260428_windows"
MEDIA_DIR = OUTPUT_DIR / "media"
ZIP_NAME = "CID_DaVinci_Validation_20260428_WINDOWS.zip"
STATIC_FILES = (
    "assembly_summary.json",
    "recommended_takes.json",
    "editorial_notes.txt",
)


def normalize_windows_root(windows_root: str) -> str:
    normalized = windows_root.replace("\\", "/").rstrip("/")
    if len(normalized) < 3 or normalized[1:3] != ":/":
        raise ValueError("--windows-root must look like C:/CID_DaVinci_Validation_20260428")
    return normalized


def windows_uri(windows_root: str, filename: str) -> str:
    return f"file:///{windows_root}/media/{filename}"


def windows_display_path(windows_root: str, filename: str) -> str:
    return f"{windows_root}/media/{filename}".replace("/", "\\")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_clean_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if MEDIA_DIR.exists():
        shutil.rmtree(MEDIA_DIR)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def copy_static_files() -> None:
    for name in STATIC_FILES:
        shutil.copy2(SOURCE_DIR / name, OUTPUT_DIR / name)


def build_windows_report(report: dict[str, Any], windows_root: str) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for entry in report.get("entries", []):
        src = Path(entry["resolved_path"])
        dest = MEDIA_DIR / src.name
        if not src.exists():
            raise FileNotFoundError(f"Missing source media: {src}")
        shutil.copy2(src, dest)
        item = dict(entry)
        item["original_resolved_path"] = entry["resolved_path"]
        item["copied_media_path"] = str(dest)
        item["expected_windows_path"] = f"{windows_root}/media/{src.name}"
        item["fcpxml_uri"] = windows_uri(windows_root, src.name)
        item["status"] = "copied"
        entries.append(item)

    windows_report = dict(report)
    windows_report["generated_at"] = datetime.now(timezone.utc).isoformat()
    windows_report["windows_root"] = windows_root
    windows_report["portable_package_dir"] = str(OUTPUT_DIR)
    windows_report["entries"] = entries
    return windows_report


def rewrite_fcpxml(fcpxml_path: Path, windows_report: dict[str, Any], windows_root: str) -> str:
    tree = ET.parse(fcpxml_path)
    root = tree.getroot()
    filename_to_uri = {
        Path(entry["original_resolved_path"]).name: windows_uri(windows_root, Path(entry["original_resolved_path"]).name)
        for entry in windows_report["entries"]
    }

    for asset in root.findall(".//asset"):
        src = asset.get("src")
        if not src:
            continue
        filename = Path(src.replace("file://", "")).name
        if filename in filename_to_uri:
            asset.set("src", filename_to_uri[filename])

    xml_text = ET.tostring(root, encoding="unicode")
    xml_text = "<?xml version='1.0' encoding='utf-8'?>\n" + xml_text
    return xml_text


def write_validation_log(windows_root: str, windows_report: dict[str, Any]) -> None:
    log_path = OUTPUT_DIR / "validation_log_windows.md"
    expected_unzip_root = windows_root.replace("/", "\\")
    lines = [
        "# DaVinci Windows Validation Log - 2026-04-28",
        "",
        "## Package Preparation",
        "",
        f"- Generated at: `{windows_report['generated_at']}`",
        f"- Source package: `docs/validation/davinci_manual_20260428`",
        f"- Windows package: `docs/validation/davinci_manual_20260428_windows`",
        f"- Windows root expected after unzip: `{expected_unzip_root}`",
        f"- FCPXML: `assembly_windows.fcpxml`",
        f"- Media files copied: `{len(windows_report['entries'])}`",
        f"- offline_media_count: `{windows_report['offline_media_count']}`",
        "",
        "## Manual Resolve Checklist",
        "",
        "| # | Check | Status | Evidence / Note |",
        "|---|---|---|---|",
        "| 1 | DaVinci opens correctly | NOT TESTED | Pending Windows workstation run. |",
        "| 2 | New project can be created | NOT TESTED | Project name: `CID_DaVinci_Validation_20260428`. |",
        "| 3 | FCPXML can be imported | NOT TESTED | Import `assembly_windows.fcpxml`. |",
        "| 4 | Timeline appears | NOT TESTED | Verify timeline opens after import. |",
        "| 5 | Clips appear in order | NOT TESTED | Expected order: `S1_SH1_TK1`, `S2_SH1_TK1`, `S3_SH1_TK1`. |",
        "| 6 | Clip names are correct | NOT TESTED | scene/shot/take naming should match clip names. |",
        "| 7 | Basic duration is correct | NOT TESTED | Expected durations: 96f, 120f, 144f at 24 fps. |",
        "| 8 | Clips relink with media | NOT TESTED | Media should resolve from `media/`. |",
        "| 9 | No unexpected offline clips appear | NOT TESTED | Prepackaged report expects 0 offline clips. |",
        "| 10 | Notes / metadata are acceptable | NOT TESTED | Notes are present in FCPXML; verify Resolve behavior. |",
        "| 11 | Timeline is usable as base premontage | NOT TESTED | Final manual acceptance gate. |",
        "",
        "## Manual Result",
        "",
        "- DaVinci Resolve version: `PENDING`",
        "- Windows version: `PENDING`",
        "- Import result: `NOT TESTED`",
        "- Relink result: `NOT TESTED`",
        "- Clip count imported: `PENDING`",
        "- Offline clip count: `PENDING`",
        "- Observations: `PENDING`",
    ]
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_readme(windows_root: str) -> None:
    readme_path = OUTPUT_DIR / "README_WINDOWS_DAVINCI_IMPORT.md"
    unzip_dir = windows_root.replace("/", "\\")
    content = "\n".join(
        [
            "# Windows DaVinci Import Guide",
            "",
            "1. Copy `CID_DaVinci_Validation_20260428_WINDOWS.zip` to the Windows workstation.",
            f"2. Unzip the package to `{unzip_dir}\\`.",
            "3. Open DaVinci Resolve.",
            "4. Create a new project named `CID_DaVinci_Validation_20260428`.",
            f"5. Import `{unzip_dir}\\assembly_windows.fcpxml`.",
            "6. Verify the following:",
            "   - timeline appears",
            "   - clips appear in order",
            "   - media is relinked",
            "   - no unexpected offline clips appear",
            "   - durations are coherent",
            "   - clip names match scene/shot/take",
            "7. Record the manual result in `validation_log_windows.md` inside the unzipped folder.",
        ]
    )
    readme_path.write_text(content + "\n", encoding="utf-8")


def write_zip() -> Path:
    zip_path = OUTPUT_DIR / ZIP_NAME
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_name in (
            "assembly_windows.fcpxml",
            "media_relink_report_windows.json",
            "assembly_summary.json",
            "recommended_takes.json",
            "editorial_notes.txt",
            "validation_log_windows.md",
            "README_WINDOWS_DAVINCI_IMPORT.md",
        ):
            archive.write(OUTPUT_DIR / file_name, arcname=file_name)
        for media_path in sorted(MEDIA_DIR.iterdir()):
            if media_path.is_file():
                archive.write(media_path, arcname=f"media/{media_path.name}")
    return zip_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a Windows-portable DaVinci validation package")
    parser.add_argument(
        "--windows-root",
        default="C:/CID_DaVinci_Validation_20260428",
        help="Expected absolute Windows extraction root, e.g. C:/CID_DaVinci_Validation_20260428",
    )
    args = parser.parse_args()

    windows_root = normalize_windows_root(args.windows_root)
    ensure_clean_output_dir()
    copy_static_files()

    source_report = load_json(SOURCE_DIR / "media_relink_report.json")
    windows_report = build_windows_report(source_report, windows_root)
    (OUTPUT_DIR / "media_relink_report_windows.json").write_text(
        json.dumps(windows_report, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    xml_text = rewrite_fcpxml(SOURCE_DIR / "assembly.fcpxml", windows_report, windows_root)
    (OUTPUT_DIR / "assembly_windows.fcpxml").write_text(xml_text, encoding="utf-8")

    write_validation_log(windows_root, windows_report)
    write_readme(windows_root)
    zip_path = write_zip()

    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "windows_root": windows_root,
                "fcpxml_path": str(OUTPUT_DIR / "assembly_windows.fcpxml"),
                "media_dir": str(MEDIA_DIR),
                "media_file_count": len(list(MEDIA_DIR.iterdir())),
                "zip_path": str(zip_path),
            },
            ensure_ascii=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
