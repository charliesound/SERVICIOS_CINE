from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_qa_gate_v1.md"
IMPLEMENTATION_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_v1.md"
CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_contract_v1.md"
READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_command_implementation_readiness_gate_v1.md"

CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

FIXTURE = REPO_ROOT / "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_cli_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_cli_under_qa",
        CLI_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    module = _load_cli_module()
    stdout = io.StringIO()
    stderr = io.StringIO()

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = module.main(argv)

    return rc, stdout.getvalue(), stderr.getvalue()


def test_qa_gate_document_exists_and_declares_limited_verdict() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.COMMAND.IMPLEMENTATION.QA.GATE.V1" in text
    assert "documentation and test-only QA gate" in text
    assert "QA_GATE_PASS_FOR_CURRENT_MINIMAL_DEVELOPMENT_CLI_WRAPPER_ONLY" in text
    assert "does not authorize packaging" in text
    assert "installable entry point wiring" in text
    assert "real media processing" in text
    assert "NLE export" in text
    assert "SaaS integration" in text


def test_qa_gate_has_expected_phase_dependencies_available() -> None:
    assert QA_DOC.exists()
    assert IMPLEMENTATION_DOC.exists()
    assert CONTRACT_DOC.exists()
    assert READINESS_DOC.exists()
    assert CLI_SCRIPT.exists()
    assert RENDERER_SCRIPT.exists()
    assert SCANNER_SCRIPT.exists()
    assert FIXTURE.exists()


def test_cli_source_remains_development_wrapper_only() -> None:
    source = _read(CLI_SCRIPT)

    assert "COMMAND_NAME = \"synthetic-visible-report\"" in source
    assert "OUTPUT_FILENAME = \"cid_local_media_agent_synthetic_visible_report_v1.md\"" in source
    assert "--fixture" in source
    assert "--output-dir" in source
    assert "--allow-overwrite" in source
    assert "--format" in source
    assert "markdown" in source
    assert "argparse" not in source
    assert "click" not in source
    assert "typer" not in source
    assert "cid_media" + "_agent_scan" not in source


def test_cli_source_does_not_introduce_external_runtime_or_packaging_wiring() -> None:
    source = _read(CLI_SCRIPT)

    forbidden_terms = [
        "import sub" + "process",
        "from sub" + "process",
        "os.system",
        "Popen(",
        "check_output(",
        "check_call(",
        "import socket",
        "from socket",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import httpx",
        "from httpx",
        "import ftplib",
        "import smtplib",
        "pyproject",
        "setup.py",
        "setup.cfg",
        "entry_" + "points",
        "console_" + "scripts",
        "ff" + "probe",
        "ff" + "mpeg",
    ]

    hits = [term for term in forbidden_terms if term in source]
    assert hits == []


def test_cli_help_preserves_synthetic_local_first_boundaries(capsys) -> None:
    module = _load_cli_module()

    rc = module.main([])
    captured = capsys.readouterr()
    combined = captured.out + captured.err

    assert rc == 0
    assert "synthetic-visible-report" in combined
    assert "sintética" in combined or "sintético" in combined
    assert "local" in combined
    assert "No analiza media real" in combined
    assert "No sincroniza audio/vídeo real" in combined
    assert "No transcribe audio real" in combined
    assert "No traduce diálogo real" in combined
    assert "No genera subtítulos finales" in combined
    assert "No exporta a NLE" in combined
    assert "sube" not in combined.lower() or "cliente" in combined.lower() or "local" in combined.lower()
    assert "revisión humana" in combined.lower() or "humana" in combined.lower()
    assert "asistivo" in combined.lower() or "cid" in combined.lower()


def test_cli_generates_only_expected_markdown_report_without_path_leakage(tmp_path: Path) -> None:
    rc, stdout, stderr = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert rc == 0
    assert stderr == ""
    assert OUTPUT_FILENAME in stdout
    assert str(tmp_path) not in stdout
    assert str(FIXTURE.resolve()) not in stdout

    outputs = sorted(path.name for path in tmp_path.iterdir())
    assert outputs == [OUTPUT_FILENAME]

    report = tmp_path / OUTPUT_FILENAME
    text = _read(report)

    assert "CID Local Media Agent" in text
    assert "demo sintética" in text.lower()
    assert "local-first" in text.lower()
    assert "revisión humana" in text.lower()
    lower = text.lower()
    assert "media real" in lower
    assert "sincron" in lower and "audio" in lower and "vídeo" in lower
    assert "transcrib" in lower and "audio" in lower
    assert "traduc" in lower and "diálogo" in lower
    assert "nle" in lower


def test_cli_rejects_overwrite_by_default_and_allows_explicit_overwrite(tmp_path: Path) -> None:
    first_rc, _, _ = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )
    assert first_rc == 0

    report = tmp_path / OUTPUT_FILENAME
    before = _read(report)

    second_rc, second_stdout, second_stderr = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert second_rc != 0
    assert str(tmp_path) not in second_stdout
    assert str(tmp_path) not in second_stderr
    assert _read(report) == before

    third_rc, _, _ = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
            "--allow-overwrite",
        ]
    )

    assert third_rc == 0
    assert _read(report) == before


def test_cli_rejects_unsupported_options_and_formats_without_stack_trace(tmp_path: Path) -> None:
    bad_format_rc, bad_format_stdout, bad_format_stderr = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "pdf",
        ]
    )

    assert bad_format_rc == 2
    assert "format" in bad_format_stderr.lower()
    assert "Traceback" not in bad_format_stdout + bad_format_stderr

    bad_option_rc, bad_option_stdout, bad_option_stderr = _run_cli(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
            "--source-media",
            "/tmp/example.mov",
        ]
    )

    assert bad_option_rc == 2
    assert "opción no permitida" in bad_option_stderr.lower()
    assert "Traceback" not in bad_option_stdout + bad_option_stderr


def test_contract_readiness_and_implementation_docs_remain_consistent() -> None:
    combined = "\n".join(
        [
            _read(CONTRACT_DOC),
            _read(READINESS_DOC),
            _read(IMPLEMENTATION_DOC),
            _read(QA_DOC),
        ]
    )

    assert "synthetic-visible-report" in combined
    assert "--fixture" in combined
    assert "--output-dir" in combined
    assert "--allow-overwrite" in combined
    assert "--format markdown" in combined
    assert OUTPUT_FILENAME in combined
    assert "scanner integration" in combined
    assert "SaaS" in combined
    assert "backend" in combined
    assert "frontend" in combined
    assert "Docker" in combined
    assert "Alembic" in combined
    assert "media real" in combined or "real media" in combined
    assert "NLE" in combined
