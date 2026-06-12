from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT_PATH = Path("scripts/demo/create_sync_dialogue_metadata_demo.py")
DOC_PATH = Path("docs/product/ailink_sync_dialogue_real_metadata_demo_v1.md")


@pytest.fixture
def metadata_demo_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("create_sync_dialogue_metadata_demo", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_creates_four_outputs(tmp_path: Path, metadata_demo_module: ModuleType) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)

    assert (tmp_path / "scan_result.json").exists()
    assert (tmp_path / "media_files.csv").exists()
    assert (tmp_path / "match_suggestions.csv").exists()
    assert (tmp_path / "report.html").exists()


def test_json_contains_media_files_and_match_suggestions(
    tmp_path: Path, metadata_demo_module: ModuleType
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    payload = json.loads((tmp_path / "scan_result.json").read_text(encoding="utf-8"))

    assert len(payload["media_files"]) == 7
    assert len(payload["match_suggestions"]) >= 3


def test_at_least_two_high_timecode_matches(tmp_path: Path, metadata_demo_module: ModuleType) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    payload = json.loads((tmp_path / "scan_result.json").read_text(encoding="utf-8"))
    high_timecode = [
        item
        for item in payload["match_suggestions"]
        if item["confidence"] == "high" and item["strategy"] == "timecode"
    ]

    assert len(high_timecode) >= 2


def test_matches_csv_contains_confidence_score_and_reasons(
    tmp_path: Path, metadata_demo_module: ModuleType
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    with (tmp_path / "match_suggestions.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert {"confidence", "score", "reasons"}.issubset(rows[0].keys())
    assert any("matching_timecode" in row["reasons"] for row in rows)


def test_report_html_contains_match_suggestions_and_high(
    tmp_path: Path, metadata_demo_module: ModuleType
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    html = (tmp_path / "report.html").read_text(encoding="utf-8")

    assert "Match suggestions" in html
    assert "high" in html


def test_wildtrack_roomtone_is_not_high_confidence(
    tmp_path: Path, metadata_demo_module: ModuleType
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    payload = json.loads((tmp_path / "scan_result.json").read_text(encoding="utf-8"))

    wildtrack_matches = [
        item
        for item in payload["match_suggestions"]
        if item["audio_relative_path"] == "audio/wildtrack_roomtone.wav"
    ]
    assert not any(item["confidence"] == "high" for item in wildtrack_matches)


def test_quiet_suppresses_summary_but_generates_outputs(
    tmp_path: Path,
    metadata_demo_module: ModuleType,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = metadata_demo_module.main(["--output-dir", str(tmp_path), "--quiet"])

    assert code == 0
    assert capsys.readouterr().out == ""
    assert (tmp_path / "report.html").exists()


def test_without_force_fails_if_outputs_exist(
    tmp_path: Path,
    metadata_demo_module: ModuleType,
    capsys: pytest.CaptureFixture[str],
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)

    code = metadata_demo_module.main(["--output-dir", str(tmp_path)])

    assert code == 2
    assert "already contains demo outputs" in capsys.readouterr().err


def test_force_regenerates_outputs_and_preserves_unrelated_files(
    tmp_path: Path, metadata_demo_module: ModuleType
) -> None:
    metadata_demo_module.create_metadata_demo(tmp_path)
    keep = tmp_path / "keep.txt"
    keep.write_text("keep", encoding="utf-8")

    metadata_demo_module.create_metadata_demo(tmp_path, force=True)

    assert keep.read_text(encoding="utf-8") == "keep"
    assert (tmp_path / "report.html").exists()


@pytest.mark.parametrize("bad_output", ["", "   ", "/", "C:/demo", "C:\\demo", "/mnt/c/demo", "/mnt/other/demo"])
def test_output_dir_empty_or_dangerous_rejected(
    bad_output: str, metadata_demo_module: ModuleType
) -> None:
    with pytest.raises(ValueError):
        metadata_demo_module.create_metadata_demo(bad_output)


def test_main_returns_2_for_path_errors(
    tmp_path: Path,
    metadata_demo_module: ModuleType,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tmp_path.joinpath("scan_result.json").write_text("exists", encoding="utf-8")

    code = metadata_demo_module.main(["--output-dir", str(tmp_path)])

    assert code == 2
    assert "already contains demo outputs" in capsys.readouterr().err


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
    def test_new_metadata_demo_files_do_not_reference_backend_or_external_services(
        self, combined_source: str, forbidden: str
    ) -> None:
        assert forbidden not in combined_source
