from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT_PATH = Path("scripts/demo/run_sync_dialogue_demo_e2e.py")
DOC_PATH = Path("docs/product/ailink_sync_dialogue_demo_end_to_end_v1.md")


@pytest.fixture
def e2e_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_sync_dialogue_demo_e2e", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_creates_fixture_and_output_structure(tmp_path: Path, e2e_module: ModuleType) -> None:
    summary = e2e_module.run_demo(tmp_path / "demo")

    fixture_path = summary["fixture_path"]
    output_path = summary["output_path"]
    assert (fixture_path / "video").is_dir()
    assert (fixture_path / "audio").is_dir()
    assert (fixture_path / "notes").is_dir()
    assert output_path.is_dir()


def test_runner_generates_four_outputs(tmp_path: Path, e2e_module: ModuleType) -> None:
    summary = e2e_module.run_demo(tmp_path / "demo")
    output_path = summary["output_path"]

    assert (output_path / "scan_result.json").exists()
    assert (output_path / "media_files.csv").exists()
    assert (output_path / "match_suggestions.csv").exists()
    assert (output_path / "report.html").exists()


def test_summary_contains_paths_and_counts(
    tmp_path: Path, e2e_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    code = e2e_module.main(["--work-dir", str(tmp_path / "demo")])

    out = capsys.readouterr().out
    assert code == 0
    assert "AILink Sync Dialogue demo completed." in out
    assert "Fixture path:" in out
    assert "Output path:" in out
    assert "Video count: 3" in out
    assert "Audio count: 3" in out
    assert "Unsupported count: 1" in out
    assert "Match suggestions count: 0" in out
    assert "Report HTML:" in out


def test_scan_result_json_has_expected_counts(tmp_path: Path, e2e_module: ModuleType) -> None:
    summary = e2e_module.run_demo(tmp_path / "demo")
    payload = json.loads((summary["output_path"] / "scan_result.json").read_text(encoding="utf-8"))

    assert payload["summary"]["video_count"] == 3
    assert payload["summary"]["audio_count"] == 3
    assert payload["summary"]["unsupported_count"] == 1


def test_report_html_exists_and_contains_product_name(tmp_path: Path, e2e_module: ModuleType) -> None:
    summary = e2e_module.run_demo(tmp_path / "demo")
    report_html = summary["report_html"]

    assert report_html.exists()
    assert "AILink Sync Dialogue" in report_html.read_text(encoding="utf-8")


def test_without_force_fails_if_folders_exist(tmp_path: Path, e2e_module: ModuleType) -> None:
    work_dir = tmp_path / "demo"
    e2e_module.run_demo(work_dir)

    with pytest.raises(ValueError, match="already exists"):
        e2e_module.run_demo(work_dir)


def test_force_regenerates_existing_fixture_and_output(tmp_path: Path, e2e_module: ModuleType) -> None:
    work_dir = tmp_path / "demo"
    summary = e2e_module.run_demo(work_dir)
    extra = summary["output_path"] / "extra.txt"
    extra.write_text("remove me", encoding="utf-8")

    regenerated = e2e_module.run_demo(work_dir, force=True)

    assert not extra.exists()
    assert (regenerated["output_path"] / "report.html").exists()


def test_force_only_removes_fixture_and_output_not_other_work_dir_files(
    tmp_path: Path, e2e_module: ModuleType
) -> None:
    work_dir = tmp_path / "demo"
    e2e_module.run_demo(work_dir)
    keep = work_dir / "keep.txt"
    keep.write_text("keep", encoding="utf-8")

    e2e_module.run_demo(work_dir, force=True)

    assert keep.read_text(encoding="utf-8") == "keep"


@pytest.mark.parametrize("name", ["fixture", "output"])
def test_fixture_or_output_as_file_returns_error_2(
    tmp_path: Path,
    e2e_module: ModuleType,
    capsys: pytest.CaptureFixture[str],
    name: str,
) -> None:
    work_dir = tmp_path / "demo"
    work_dir.mkdir()
    (work_dir / name).write_text("not a dir", encoding="utf-8")

    code = e2e_module.main(["--work-dir", str(work_dir), "--force"])

    assert code == 2
    assert "not a directory" in capsys.readouterr().err


@pytest.mark.parametrize("bad_work_dir", ["", "   ", "/", "C:/demo", "C:\\demo", "/mnt/c/demo", "/mnt/other/demo"])
def test_work_dir_empty_or_dangerous_rejected(
    bad_work_dir: str, e2e_module: ModuleType
) -> None:
    with pytest.raises(ValueError):
        e2e_module.run_demo(bad_work_dir)


def test_main_returns_2_for_path_errors(
    tmp_path: Path, e2e_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    e2e_module.run_demo(tmp_path / "demo")

    code = e2e_module.main(["--work-dir", str(tmp_path / "demo")])

    assert code == 2
    assert "already exists" in capsys.readouterr().err


def test_main_returns_3_for_unexpected_errors(
    tmp_path: Path,
    e2e_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_scan(*args: object, **kwargs: object) -> int:
        return 3

    monkeypatch.setattr(e2e_module, "scan_main", fail_scan)
    code = e2e_module.main(["--work-dir", str(tmp_path / "demo")])

    assert code == 3
    assert "demo failed" in capsys.readouterr().err


def test_main_quiet_suppresses_success_summary(
    tmp_path: Path, e2e_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    code = e2e_module.main(["--work-dir", str(tmp_path / "demo"), "--quiet"])

    assert code == 0
    assert "AILink Sync Dialogue demo completed." not in capsys.readouterr().out


def test_quiet_still_generates_outputs(tmp_path: Path, e2e_module: ModuleType) -> None:
    work_dir = tmp_path / "demo"

    code = e2e_module.main(["--work-dir", str(work_dir), "--quiet"])

    assert code == 0
    assert (work_dir / "output" / "report.html").exists()


def test_summary_does_not_print_windows_like_paths(
    tmp_path: Path, e2e_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    code = e2e_module.main(["--work-dir", str(tmp_path / "demo")])

    out = capsys.readouterr().out
    assert code == 0
    assert "C:" not in out
    assert "\\" not in out


def test_parent_segments_are_normalized_by_resolve(
    tmp_path: Path, e2e_module: ModuleType
) -> None:
    work_dir = tmp_path / "parent" / ".." / "demo"

    summary = e2e_module.run_demo(work_dir)

    assert ".." not in str(summary["output_path"])


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
    def test_new_e2e_files_do_not_reference_backend_or_external_services(
        self, combined_source: str, forbidden: str
    ) -> None:
        assert forbidden not in combined_source
