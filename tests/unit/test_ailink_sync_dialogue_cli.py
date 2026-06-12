from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

CLI_PATH = Path("scripts/ailink_sync_dialogue_scan.py")
IMPLEMENTATION_PATHS = [
    Path("src/ailink_tools/sync_dialogue/local_scanner.py"),
    Path("src/ailink_tools/sync_dialogue/schemas.py"),
    Path("src/ailink_tools/sync_dialogue/matching.py"),
    Path("src/ailink_tools/sync_dialogue/exports.py"),
    Path("src/ailink_tools/sync_dialogue/report_html.py"),
    CLI_PATH,
]


@pytest.fixture
def cli_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ailink_sync_dialogue_scan", CLI_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _touch(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_input_missing_returns_exit_code_2(
    tmp_path: Path, cli_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    code = cli_module.main(
        ["--input", str(tmp_path / "missing"), "--output-dir", str(tmp_path / "out")]
    )

    assert code == 2
    assert "input path does not exist" in capsys.readouterr().err


def test_input_file_returns_exit_code_2(
    tmp_path: Path, cli_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    input_file = _touch(tmp_path / "clip.mov")
    code = cli_module.main(["--input", str(input_file), "--output-dir", str(tmp_path / "out")])

    assert code == 2
    assert "input path must be a directory" in capsys.readouterr().err


def test_success_creates_json_media_csv_matches_csv_and_html_with_no_probe(
    tmp_path: Path, cli_module: ModuleType
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    _touch(input_dir / "clip.mov")
    _touch(input_dir / "sound.wav")

    code = cli_module.main(
        ["--input", str(input_dir), "--output-dir", str(output_dir), "--no-probe"]
    )

    assert code == 0
    json_path = output_dir / "scan_result.json"
    csv_path = output_dir / "media_files.csv"
    matches_path = output_dir / "match_suggestions.csv"
    html_path = output_dir / "report.html"
    assert json_path.exists()
    assert csv_path.exists()
    assert matches_path.exists()
    assert html_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["summary"]["video_count"] == 1
    assert payload["summary"]["audio_count"] == 1
    assert "match_suggestions" in payload
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["probe_status"] for row in rows] == ["not_run", "not_run"]


def test_custom_output_names_work(tmp_path: Path, cli_module: ModuleType) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    _touch(input_dir / "clip.mov")

    code = cli_module.main(
        [
            "--input",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--no-probe",
            "--json-name",
            "custom.json",
            "--csv-name",
            "custom.csv",
            "--matches-name",
            "custom_matches.csv",
            "--html-name",
            "custom_report.html",
        ]
    )

    assert code == 0
    assert (output_dir / "custom.json").exists()
    assert (output_dir / "custom.csv").exists()
    assert (output_dir / "custom_matches.csv").exists()
    assert (output_dir / "custom_report.html").exists()


@pytest.mark.parametrize(
    "option",
    ["--json-name", "--csv-name", "--matches-name", "--html-name"],
)
@pytest.mark.parametrize(
    "bad_name",
    ["../escape.txt", "nested/file.txt", "/tmp/absolute.txt", "C:/escape.txt", "C:\\escape.txt", "", "   ", ".", ".."],
)
def test_output_names_reject_paths_before_writing_outputs(
    tmp_path: Path,
    cli_module: ModuleType,
    capsys: pytest.CaptureFixture[str],
    option: str,
    bad_name: str,
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    _touch(input_dir / "clip.mov")
    code = cli_module.main(
        [
            "--input",
            str(input_dir),
            "--output-dir",
            str(output_dir),
            "--no-probe",
            option,
            bad_name,
        ]
    )

    assert code == 2
    assert "must be a simple filename" in capsys.readouterr().err
    assert not output_dir.exists()


def test_summary_contains_counts(
    tmp_path: Path, cli_module: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "out"
    _touch(input_dir / "clip.mov")
    _touch(input_dir / "notes.txt")

    code = cli_module.main(
        ["--input", str(input_dir), "--output-dir", str(output_dir), "--no-probe"]
    )

    out = capsys.readouterr().out
    assert code == 0
    assert "total files: 2" in out
    assert "video count: 1" in out
    assert "audio count: 0" in out
    assert "unsupported count: 1" in out
    assert "match suggestions count: 0" in out
    assert "output json path:" in out
    assert "output csv path:" in out
    assert "output matches path:" in out
    assert "output html path:" in out


def test_unexpected_error_returns_exit_code_3(
    tmp_path: Path,
    cli_module: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    def fail_scan(*args: object, **kwargs: object) -> object:
        raise RuntimeError("short failure")

    monkeypatch.setattr(cli_module, "scan_folder", fail_scan)
    code = cli_module.main(["--input", str(input_dir), "--output-dir", str(tmp_path / "out")])

    assert code == 3
    assert "scan failed: short failure" in capsys.readouterr().err


class TestBoundaryNoBackend:
    @pytest.fixture(scope="class")
    def combined_source(self) -> str:
        return "\n".join(path.read_text(encoding="utf-8") for path in IMPLEMENTATION_PATHS)

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
            "sqli" + "te",
            "cdn",
            "http://",
            "https://",
        ],
    )
    def test_new_implementation_sources_do_not_reference_backend_or_external_services(
        self, combined_source: str, forbidden: str
    ) -> None:
        assert forbidden not in combined_source
