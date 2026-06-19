from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_qa_gate_v1.md"
IMPLEMENTATION_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_implementation_v1.md"
READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_readiness_gate_v1.md"
CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_cli_synthetic_visible_report_preflight_contract_v1.md"

PREFLIGHT_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py"
CLI_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py"
RENDERER_SCRIPT = REPO_ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts/cid_media_agent_scan.py"

FIXTURE = REPO_ROOT / "tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_preflight_under_qa",
        PREFLIGHT_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_preflight(argv: list[str]) -> tuple[int, str, str]:
    module = _load_preflight_module()
    stdout = io.StringIO()
    stderr = io.StringIO()

    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        rc = module.main(argv)

    return rc, stdout.getvalue(), stderr.getvalue()


def test_qa_gate_document_exists_and_declares_limited_verdict() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.IMPLEMENTATION.QA.GATE.V1" in text
    assert "documentation and test-only QA gate" in text
    assert "scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py" in text
    assert "QA_GATE_PASS_FOR_MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_HELPER_ONLY" in text
    assert "does not authorize packaging" in text
    assert "installable entry point wiring" in text
    assert "real media processing" in text
    assert "NLE export" in text


def test_qa_gate_has_expected_dependencies_available() -> None:
    for path in [
        QA_DOC,
        IMPLEMENTATION_DOC,
        READINESS_DOC,
        CONTRACT_DOC,
        PREFLIGHT_SCRIPT,
        CLI_SCRIPT,
        RENDERER_SCRIPT,
        SCANNER_SCRIPT,
        FIXTURE,
    ]:
        assert path.exists(), path


def test_preflight_source_remains_standard_library_and_development_only() -> None:
    source = _read(PREFLIGHT_SCRIPT)

    assert "COMMAND_NAME = \"synthetic-visible-report\"" in source
    assert "PREFLIGHT_NAME = \"synthetic-visible-report-preflight\"" in source
    assert "OUTPUT_FILENAME = \"cid_local_media_agent_synthetic_visible_report_v1.md\"" in source
    assert "--fixture" in source
    assert "--output-dir" in source
    assert "--format" in source
    assert "--allow-overwrite" in source
    assert "PREFLIGHT_PASS" in source
    assert "PREFLIGHT_FAIL" in source

    forbidden = [
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
        "argparse",
        "click",
        "typer",
        "cid_media" + "_agent_scan",
        "pyproject",
        "setup.py",
        "setup.cfg",
        "entry_" + "points",
        "console_" + "scripts",
        "ff" + "probe",
        "ff" + "mpeg",
    ]

    hits = [term for term in forbidden if term in source]
    assert hits == []


def test_preflight_success_is_safe_and_does_not_create_report(tmp_path: Path) -> None:
    fixture_hash_before = _sha256(FIXTURE)

    rc, stdout, stderr = _run_preflight(
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
    assert "PREFLIGHT_PASS" in stdout
    assert "command=synthetic-visible-report" in stdout
    assert f"expected_output={OUTPUT_FILENAME}" in stdout
    assert "mode=synthetic-local-only" in stdout
    assert "human_review=required" in stdout

    assert str(tmp_path) not in stdout
    assert str(FIXTURE.resolve()) not in stdout
    assert sorted(tmp_path.iterdir()) == []
    assert _sha256(FIXTURE) == fixture_hash_before


def test_preflight_failure_outputs_are_controlled_and_do_not_leak_paths(tmp_path: Path) -> None:
    missing_fixture = tmp_path / "synthetic_demo_report_fixture_v1.json"

    rc, stdout, stderr = _run_preflight(
        [
            "--fixture",
            str(missing_fixture),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert rc == 2
    assert stdout == ""
    assert "PREFLIGHT_FAIL" in stderr
    assert "reason=FIXTURE_NOT_FOUND" in stderr
    assert "Traceback" not in stderr
    assert str(missing_fixture) not in stderr
    assert "{" not in stderr


def test_preflight_respects_output_overwrite_safety_without_mutation(tmp_path: Path) -> None:
    output = tmp_path / OUTPUT_FILENAME
    output.write_text("existing", encoding="utf-8")

    blocked_rc, blocked_stdout, blocked_stderr = _run_preflight(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert blocked_rc == 4
    assert blocked_stdout == ""
    assert "PREFLIGHT_FAIL" in blocked_stderr
    assert "reason=OUTPUT_ALREADY_EXISTS" in blocked_stderr
    assert _read(output) == "existing"

    allowed_rc, allowed_stdout, allowed_stderr = _run_preflight(
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

    assert allowed_rc == 0
    assert "PREFLIGHT_PASS" in allowed_stdout
    assert allowed_stderr == ""
    assert _read(output) == "existing"


def test_preflight_rejects_unsupported_format_and_real_media_like_options(tmp_path: Path) -> None:
    format_rc, format_stdout, format_stderr = _run_preflight(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "pdf",
        ]
    )

    assert format_rc == 2
    assert format_stdout == ""
    assert "reason=FORMAT_NOT_SUPPORTED" in format_stderr
    assert "Traceback" not in format_stderr

    media_rc, media_stdout, media_stderr = _run_preflight(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
            "--source-media",
            "/tmp/client.mov",
        ]
    )

    assert media_rc == 2
    assert media_stdout == ""
    assert "reason=OPTION_NOT_ALLOWED" in media_stderr
    assert "/tmp/client.mov" not in media_stderr
    assert "Traceback" not in media_stderr


def test_cli_integration_exists_but_renderer_and_scanner_remain_unintegrated_with_preflight() -> None:
    cli_source = _read(CLI_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "--preflight" in cli_source
    assert "cid_local_media_agent_synthetic_visible_report_preflight_check.py" in cli_source
    assert "def _run_preflight" in cli_source
    assert "synthetic-visible-report-preflight" not in cli_source
    assert "PREFLIGHT_PASS" not in cli_source

    assert "synthetic-visible-report-preflight" not in renderer_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source

    assert "synthetic-visible-report-preflight" not in scanner_source


def test_qa_gate_documents_blocked_scope_after_helper_implementation() -> None:
    text = _read(QA_DOC)

    blocked = [
        "packaging",
        "installable entry point wiring",
        "CLI wrapper integration",
        "renderer changes",
        "scanner integration",
        "SaaS integration",
        "backend integration",
        "frontend integration",
        "database runtime behavior",
        "Docker changes",
        "Alembic changes",
        "external media probing binary execution",
        "real media analysis",
        "audio/video sync",
        "transcription",
        "translation",
        "subtitle generation",
        "NLE export",
        "installer behavior",
        "licensing behavior",
        "client media upload",
    ]

    for item in blocked:
        assert item in text
