from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from ailink_tools.sync_dialogue.local_scanner import scan_folder

SCRIPT_PATH = Path("scripts/demo/create_sync_dialogue_demo_fixture.py")
DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_fixture_v1.md")


@pytest.fixture
def fixture_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("create_sync_dialogue_demo_fixture", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_creates_expected_structure(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path)

    assert fixture_dir == tmp_path / "demo_sync_dialogue"
    assert (fixture_dir / "video" / "scene01_take01.mov").exists()
    assert (fixture_dir / "video" / "scene01_take02.mov").exists()
    assert (fixture_dir / "video" / "scene02_take01.mxf").exists()
    assert (fixture_dir / "audio" / "scene01_take01.wav").exists()
    assert (fixture_dir / "audio" / "scene01_take02.wav").exists()
    assert (fixture_dir / "audio" / "scene02_take01.wav").exists()
    assert (fixture_dir / "notes" / "readme.txt").exists()


def test_creates_three_videos_and_three_audios(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path)

    videos = list((fixture_dir / "video").iterdir())
    audios = list((fixture_dir / "audio").iterdir())
    assert len(videos) == 3
    assert len(audios) == 3


def test_files_contain_dummy_not_real_media_text(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path)

    for path in fixture_dir.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert "dummy" in text.lower() or "not real media" in text.lower()


def test_does_not_overwrite_without_force(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_module.create_fixture(tmp_path)

    with pytest.raises(ValueError, match="already exists"):
        fixture_module.create_fixture(tmp_path)


def test_force_regenerates_existing_fixture(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path)
    extra = fixture_dir / "extra.txt"
    extra.write_text("remove me", encoding="utf-8")

    regenerated = fixture_module.create_fixture(tmp_path, force=True)

    assert regenerated == fixture_dir
    assert not extra.exists()
    assert (fixture_dir / "video" / "scene01_take01.mov").exists()


@pytest.mark.parametrize("bad_output", ["", "   ", "/", "C:/demo", "C:\\demo", "/mnt/c/demo"])
def test_invalid_or_dangerous_output_path_rejected(
    bad_output: str, fixture_module: ModuleType
) -> None:
    with pytest.raises(ValueError):
        fixture_module.create_fixture(bad_output)


def test_main_success_and_quiet(tmp_path: Path, fixture_module: ModuleType, capsys: pytest.CaptureFixture[str]) -> None:
    code = fixture_module.main(["--output-dir", str(tmp_path), "--quiet"])

    assert code == 0
    assert capsys.readouterr().out == ""
    assert (tmp_path / "demo_sync_dialogue").exists()


def test_main_existing_without_force_returns_2(
    tmp_path: Path, fixture_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture_module.create_fixture(tmp_path)

    code = fixture_module.main(["--output-dir", str(tmp_path)])

    assert code == 2
    assert "already exists" in capsys.readouterr().err


def test_scanner_counts_fixture_with_no_probe(tmp_path: Path, fixture_module: ModuleType) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path)

    result = scan_folder(fixture_dir, probe=False)

    assert result.video_count == 3
    assert result.audio_count == 3
    assert result.unsupported_count == 1
    assert {media.probe_status for media in result.media_files} == {"not_run"}


def test_end_to_end_cli_scan_on_fixture_no_probe(
    tmp_path: Path, fixture_module: ModuleType
) -> None:
    fixture_dir = fixture_module.create_fixture(tmp_path / "fixture")
    output_dir = tmp_path / "out"

    from scripts.ailink_sync_dialogue_scan import main as scan_main

    code = scan_main(
        ["--input", str(fixture_dir), "--output-dir", str(output_dir), "--no-probe"]
    )

    assert code == 0
    assert (output_dir / "scan_result.json").exists()
    assert (output_dir / "media_files.csv").exists()
    assert (output_dir / "match_suggestions.csv").exists()
    assert (output_dir / "report.html").exists()
    payload = json.loads((output_dir / "scan_result.json").read_text(encoding="utf-8"))
    assert payload["summary"]["video_count"] == 3
    assert payload["summary"]["audio_count"] == 3
    assert payload["summary"]["unsupported_count"] == 1


class TestBoundaryNoBackend:
    @pytest.fixture(scope="class")
    def combined_source(self) -> str:
        return "\n".join(
            path.read_text(encoding="utf-8") for path in (SCRIPT_PATH, DOC_PATH)
        )

    @pytest.mark.parametrize(
        "forbidden",
        [
            "DATABASE_URL",
            "AsyncSessionLocal",
            "FastAPI",
            "APIRouter",
            "@router",
            "CreditLedger",
            "AIJob",
            "ComfyUI",
            "requests.",
            "httpx",
            "stripe",
            "docker",
            "alembic",
            "cdn",
            "http://",
            "https://",
            "sqli" + "te",
        ],
    )
    def test_new_demo_fixture_files_do_not_reference_backend_or_external_services(
        self, combined_source: str, forbidden: str
    ) -> None:
        assert forbidden not in combined_source
