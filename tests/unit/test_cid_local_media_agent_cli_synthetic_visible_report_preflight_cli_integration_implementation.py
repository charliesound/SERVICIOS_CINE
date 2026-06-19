from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI_PATH = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
APPROVED_FIXTURE_BASENAME = "synthetic_demo_report_fixture_v1.json"


def _load_cli_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_cli",
        CLI_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_path() -> Path:
    matches = sorted(REPO_ROOT.rglob(APPROVED_FIXTURE_BASENAME))
    assert matches, "Approved synthetic fixture is required for CLI integration tests."
    return matches[0]


def test_preflight_mode_delegates_to_helper_without_generating_report(tmp_path, capsys):
    cli = _load_cli_module()
    fixture = _fixture_path()

    exit_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "PREFLIGHT_PASS" in captured.out
    assert f"expected_output={OUTPUT_FILENAME}" in captured.out
    assert "OK: generado" not in captured.out
    assert not (tmp_path / OUTPUT_FILENAME).exists()


def test_preflight_mode_propagates_safe_helper_failure_without_traceback(tmp_path, capsys):
    cli = _load_cli_module()
    fixture = _fixture_path()
    existing_output = tmp_path / OUTPUT_FILENAME
    existing_output.write_text("existing synthetic report", encoding="utf-8")

    exit_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 4
    assert "PREFLIGHT_FAIL" in captured.err
    assert "reason=OUTPUT_ALREADY_EXISTS" in captured.err
    assert "Traceback" not in captured.err
    assert "{" not in captured.err


def test_generation_without_preflight_preserves_previous_behavior(tmp_path, capsys):
    cli = _load_cli_module()
    fixture = _fixture_path()

    exit_code = cli.main(
        [
            "--fixture",
            str(fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "OK: generado" in captured.out
    assert OUTPUT_FILENAME in captured.out
    assert "PREFLIGHT_PASS" not in captured.out
    assert "PREFLIGHT_FAIL" not in captured.err
    assert (tmp_path / OUTPUT_FILENAME).exists()


def test_help_documents_preflight_mode(capsys):
    cli = _load_cli_module()

    exit_code = cli.main(["--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "synthetic-visible-report --preflight" in captured.out
    assert "--preflight" in captured.out
    assert "Valida parámetros sintéticos sin generar informe." in captured.out


def test_preflight_help_is_delegated_to_preflight_helper(capsys):
    cli = _load_cli_module()

    exit_code = cli.main(["--preflight", "--help"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "synthetic-visible-report-preflight" in captured.out
    assert "Preflight local de demo sintética. No genera informe." in captured.out


def test_cli_integration_remains_local_synthetic_and_does_not_import_scanner_or_packaging():
    source = CLI_PATH.read_text(encoding="utf-8")

    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in source
    assert "cid_media_agent_scan" not in source
    assert "entry_points" not in source
    assert "console_scripts" not in source
    assert "sqlalchemy" not in source.lower()
    assert "alembic" not in source.lower()
    assert "stripe" not in source.lower()
