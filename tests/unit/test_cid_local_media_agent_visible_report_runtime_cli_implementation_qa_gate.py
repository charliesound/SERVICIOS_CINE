from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent import visible_report_runtime_cli as cli


QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_controlled_cli_implementation_qa_gate_v1.md"
)
IMPLEMENTATION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_controlled_cli_implementation_v1.md"
)
CLI_FILE = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
CLI_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py")
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_qa_gate_doc_and_files_under_qa_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert IMPLEMENTATION_DOC.exists()
    assert CLI_FILE.exists()
    assert CLI_TEST.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()

    qa_text = _text(QA_GATE_DOC)
    for item in (
        "visible_report_runtime_generator_controlled_cli_implementation_v1.md",
        "scripts/local_media_agent/visible_report_runtime_cli.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py",
        "scripts/local_media_agent/visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py",
    ):
        assert item in qa_text


def test_source_traceability_is_complete() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.CLI.IMPLEMENTATION.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTROLLED.CLI.IMPLEMENTATION.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_IMPLEMENTATION_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION_QA_GATE",
        "7093d22c0a1a2be45cec4a262acee40d52c98afa",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-cli-implementation-v1-20260620",
    ]

    for item in required:
        assert item in qa_text


def test_cli_public_entry_point_is_import_safe_and_narrow() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(CLI_FILE)

    assert callable(cli.main)
    assert "main(argv: Sequence[str] | None = None) -> int" in qa_text
    assert "def main(argv: Sequence[str] | None = None) -> int:" in source
    assert 'if __name__ == "__main__":' in source
    assert "raise SystemExit(main())" in source
    assert "Importing the CLI module must not execute rendering." in qa_text
    assert "Importing the CLI module must not read input files." in qa_text
    assert "Importing the CLI module must not write output files." in qa_text


def test_renderer_delegation_is_preserved() -> None:
    qa_text = _text(QA_GATE_DOC)
    cli_source = _text(CLI_FILE)
    runtime_source = _text(RUNTIME_GENERATOR)

    assert "generate_visible_report(scanner_result, output_root)" in qa_text
    assert "from scripts.local_media_agent.visible_report_runtime_generator import generate_visible_report" in cli_source
    assert "report_path = generate_visible_report(scanner_result, output_root)" in cli_source
    assert "def generate_visible_report(" in runtime_source
    assert "The CLI must not duplicate renderer logic." in qa_text
    assert "The CLI must not bypass runtime validation." in qa_text
    assert "The CLI must not widen the renderer interface." in qa_text


def test_required_optional_and_forbidden_flags_are_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    cli_source = _text(CLI_FILE)

    required_flags = [
        "--scanner-result-json",
        "--output-root",
        "--dry-run",
        "--strict",
        "--print-output-path",
    ]
    forbidden_flags = [
        "--scan",
        "--ffprobe",
        "--ffmpeg",
        "--sync",
        "--transcribe",
        "--subtitle",
        "--export-davinci",
        "--export-avid",
        "--upload",
        "--database-write",
        "--network",
        "--client-facing",
    ]

    for flag in required_flags:
        assert flag in qa_text
        assert flag in cli_source

    for flag in forbidden_flags:
        assert flag in qa_text
        assert flag in cli.FORBIDDEN_FLAGS
        assert flag in cli_source

    assert "The CLI must reject unsupported flags before reading input JSON." in qa_text


def test_forbidden_flag_is_rejected_before_json_loading(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(
        [
            "--scan",
            "--scanner-result-json",
            str(tmp_path / "missing.json"),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "unsupported flag" in captured.err
    assert "--scan" in captured.err
    assert "does not exist" not in captured.err


@pytest.mark.parametrize(
    "raw_path, expected",
    [
        ("https://example.test/input.json", "URL-like"),
        ("C:\\media\\input.json", "Windows drive"),
        ("\\\\server\\share\\input.json", "UNC"),
        ("/mnt/c/input.json", "mounted Windows"),
    ],
)
def test_input_path_safety_is_enforced(
    raw_path: str,
    expected: str,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(
        [
            "--scanner-result-json",
            raw_path,
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert expected in captured.err


def test_repository_input_path_is_rejected(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(
        [
            "--scanner-result-json",
            "pyproject.toml",
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "repository" in captured.err


def test_json_validation_is_enforced(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{invalid", encoding="utf-8")

    code = cli.main(
        [
            "--scanner-result-json",
            str(invalid_json),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )
    captured = capsys.readouterr()
    assert code != 0
    assert "invalid" in captured.err

    list_json = _write_json(tmp_path / "list.json", ["not", "object"])
    code = cli.main(
        [
            "--scanner-result-json",
            str(list_json),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )
    captured = capsys.readouterr()
    assert code != 0
    assert "root must be an object" in captured.err


def test_output_root_safety_is_enforced(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"ok": True})

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            "/mnt/c/out",
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "mounted Windows" in captured.err


def test_dry_run_validates_without_rendering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"ok": True})
    output_root = tmp_path / "out"

    def fail_if_called(scanner_result: dict[str, object], root: Path) -> Path:
        raise AssertionError("renderer must not be called")

    monkeypatch.setattr(cli, "generate_visible_report", fail_if_called)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--dry-run",
            "--strict",
        ]
    )

    assert code == 0
    assert not (output_root / "05_reports").exists()


def test_success_delegates_once_and_prints_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"project": "controlled"})
    output_root = tmp_path / "out"
    calls: list[tuple[dict[str, object], Path]] = []

    def fake_generate_visible_report(scanner_result: dict[str, object], root: Path) -> Path:
        calls.append((scanner_result, root))
        report = root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("# controlled report\n", encoding="utf-8")
        return report

    monkeypatch.setattr(cli, "generate_visible_report", fake_generate_visible_report)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ]
    )

    captured = capsys.readouterr()
    expected_report = output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"

    assert code == 0
    assert calls == [({"project": "controlled"}, output_root.resolve())]
    assert expected_report.exists()
    assert str(expected_report) in captured.out


def test_runtime_failure_is_reported_without_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"bad": True})
    output_root = tmp_path / "out"

    def fail_runtime(scanner_result: dict[str, object], root: Path) -> Path:
        raise ValueError("runtime validation failed")

    monkeypatch.setattr(cli, "generate_visible_report", fail_runtime)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "runtime validation failed" in captured.err
    assert captured.out == ""
    assert not (output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md").exists()


def test_no_disallowed_runtime_expansion_imports_are_added() -> None:
    source = _text(CLI_FILE)

    disallowed = [
        "subprocess",
        "requests",
        "httpx",
        "socket",
        "urllib.request",
        "sqlalchemy",
        "psycopg",
        "alembic",
    ]

    for item in disallowed:
        assert item not in source


def test_explicit_non_goals_and_validation_evidence_are_declared() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "scanner execution",
        "scanner implementation changes",
        "real media scanning",
        "public demo use",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS upload",
        "database writes",
        "network calls",
        "frontend/backend SaaS changes",
        "controlled CLI implementation test passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate test passing",
        "supporting implemented runtime chain tests passing",
        "Python compile passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_CLI_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_CONTROLLED_CLI_EXECUTION",
    ]

    for item in required:
        assert item in qa_text
