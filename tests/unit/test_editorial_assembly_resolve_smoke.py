from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
for path in (ROOT, SRC_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


def _write_minimal_fixture(root: Path) -> None:
    camera_root = root / "media_roots" / "camera"
    sound_root = root / "media_roots" / "sound"
    reports_root = root / "reports"
    camera_root.mkdir(parents=True)
    sound_root.mkdir(parents=True)
    reports_root.mkdir(parents=True)
    (camera_root / "S01_SH01_TK01_CAM.mov").write_text("video", encoding="utf-8")
    (sound_root / "S01_SH01_TK01_SOUND.wav").write_text("audio", encoding="utf-8")
    (reports_root / "camera_report.csv").write_text(
        "reel,scene,shot,take,filmroll,camera,lens,rate,fps,circular,notes\n"
        "R001,01,01,01,A001,cam1,35mm,24,24,OK,Good take\n",
        encoding="utf-8",
    )
    (reports_root / "sound_report.csv").write_text(
        "reel,scene,shot,take,roll,circular,notes,sync\n"
        "S001,01,01,01,001,OK,Good sound,Slate\n",
        encoding="utf-8",
    )
    (reports_root / "script_notes.csv").write_text(
        "scene,shot,description,action,dialogue,notes\n"
        "01,01,INT. TEST - DAY,Actor enters,Hello,\n",
        encoding="utf-8",
    )
    (reports_root / "director_notes.md").write_text(
        "# Director Notes\n\n## Scene 1\n- SH01: Preferred smoke take\n",
        encoding="utf-8",
    )


def test_smoke_script_importable():
    module = importlib.import_module("scripts.dev.smoke_editorial_assembly_resolve_real")

    assert callable(module.run_smoke)


def test_smoke_generates_timeline_fcpxml_and_relink_report(tmp_path):
    module = importlib.import_module("scripts.dev.smoke_editorial_assembly_resolve_real")
    fixture_root = tmp_path / "fixture"
    output_dir = tmp_path / "out"
    _write_minimal_fixture(fixture_root)

    manifest = module.run_smoke(fixture_root=fixture_root, output_dir=output_dir)

    fcpxml_path = Path(manifest["fcpxml_path"])
    relink_report_path = Path(manifest["relink_report_path"])
    assert manifest["clip_count"] == 1
    assert manifest["camera_assets_count"] == 1
    assert manifest["sound_assets_count"] == 1
    assert fcpxml_path.exists()
    assert fcpxml_path.stat().st_size > 0
    assert b"<asset" in fcpxml_path.read_bytes()
    assert relink_report_path.exists()
    assert manifest["export_manifest"]["relink_report"]["resolved_media_count"] == 2
