from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_qa_gate_v1.md"
)
IMPLEMENTATION_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_cli_synthetic_visible_report_preflight_cli_integration_implementation_v1.md"
)

CLI_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
PREFLIGHT_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
APPROVED_FIXTURE_BASENAME = "synthetic_demo_report_fixture_v1.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_cli_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_cli",
        CLI_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_path() -> Path:
    matches = sorted(REPO_ROOT.rglob(APPROVED_FIXTURE_BASENAME))
    assert matches, "Approved synthetic fixture is required for QA gate."
    return matches[0]


def test_qa_gate_document_exists_and_declares_phase_decision_and_scope() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.QA.GATE.V1" in text
    assert "QA_GATE_READY_FOR_CONTROLLED_PREFLIGHT_USER_FLOW_OR_PACKAGING_READINESS_WITH_RESTRICTIONS" in text
    assert "This phase is documentation/test-only." in text
    assert "Allowed files:" in text
    assert "Runtime files audited but not modified" in text


def test_qa_gate_references_completed_implementation_and_current_command_shape() -> None:
    text = _read(QA_DOC)
    implementation_text = _read(IMPLEMENTATION_DOC)

    expected_command = (
        "synthetic-visible-report --preflight --fixture <fixture-json> "
        "--output-dir <existing-dir> --format markdown [--allow-overwrite]"
    )

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.CLI.INTEGRATION.IMPLEMENTATION.V1" in text
    assert expected_command in text
    assert expected_command in implementation_text
    assert "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py" in text


def test_qa_gate_documents_all_blocked_scope_boundaries() -> None:
    text = _read(QA_DOC)

    blocked_items = [
        "packaging",
        "installable entry point",
        "scanner integration",
        "ffprobe/ffmpeg execution",
        "real media analysis",
        "sync",
        "transcription",
        "translation",
        "subtitle generation",
        "NLE/export",
        "installer or licensing work",
        "SaaS/backend/frontend/database/Docker/Alembic work",
        "Stripe, AI Jobs, credits or ledger work",
        "upload or processing of client material",
    ]

    for item in blocked_items:
        assert item in text


def test_cli_source_contains_minimal_preflight_integration_without_scanner_or_packaging() -> None:
    source = _read(CLI_SCRIPT)

    assert "--preflight" in source
    assert "_PREFLIGHT_PATH" in source
    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in source
    assert "def _run_preflight" in source
    assert "preflight.main(preflight_args)" in source

    assert "cid_media_agent_scan" not in source
    assert "entry_points" not in source
    assert "console_scripts" not in source
    assert "ffprobe" not in source.lower()
    assert "ffmpeg" not in source.lower()
    assert "sqlalchemy" not in source.lower()
    assert "alembic" not in source.lower()
    assert "stripe" not in source.lower()


def test_preflight_mode_passes_without_generating_report(tmp_path, capsys) -> None:
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


def test_preflight_mode_preserves_helper_failure_exit_code_and_safe_output(tmp_path, capsys) -> None:
    cli = _load_cli_module()
    fixture = _fixture_path()
    expected_output = tmp_path / OUTPUT_FILENAME
    expected_output.write_text("existing report", encoding="utf-8")

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
    assert str(fixture.parent) not in captured.err
    assert "{" not in captured.err


def test_preflight_delegation_fallback_is_controlled_if_helper_load_fails(tmp_path, capsys) -> None:
    cli = _load_cli_module()

    cli._PREFLIGHT_PATH = tmp_path / "missing_preflight_helper.py"

    exit_code = cli.main(
        [
            "--preflight",
            "--fixture",
            str(tmp_path / APPROVED_FIXTURE_BASENAME),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "PREFLIGHT_FAIL" in captured.err
    assert "reason=UNEXPECTED_CONTROLLED_FAILURE" in captured.err
    assert "El preflight falló de forma controlada." in captured.err
    assert "Traceback" not in captured.err
    assert "missing_preflight_helper.py" not in captured.err


def test_generation_without_preflight_remains_preserved(tmp_path, capsys) -> None:
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


def test_renderer_scanner_and_helper_boundaries_remain_intact() -> None:
    cli_source = _read(CLI_SCRIPT)
    helper_source = _read(PREFLIGHT_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "PREFLIGHT_PASS" not in cli_source
    assert "PREFLIGHT_FAIL" in cli_source

    assert "PREFLIGHT_PASS" in helper_source
    assert "PREFLIGHT_FAIL" in helper_source
    assert "cid_media_agent_scan" not in helper_source

    assert "--preflight" not in renderer_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "synthetic-visible-report-preflight" not in renderer_source

    assert "--preflight" not in scanner_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source
    assert "synthetic-visible-report-preflight" not in scanner_source
