from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

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


def _load_preflight_module():
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_preflight_under_test",
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


def test_preflight_implementation_document_exists_and_declares_limited_verdict() -> None:
    text = _read(IMPLEMENTATION_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.CLI.SYNTHETIC.VISIBLE.REPORT.PREFLIGHT.IMPLEMENTATION.V1" in text
    assert "isolated helper script" in text
    assert "development-only" in text
    assert "MINIMAL_SYNTHETIC_VISIBLE_REPORT_PREFLIGHT_IMPLEMENTED_AS_DEVELOPMENT_ONLY_HELPER" in text
    assert "does not authorize packaging" in text
    assert "installable entry point wiring" in text
    assert "real media processing" in text


def test_preflight_implementation_depends_on_contract_and_readiness_docs() -> None:
    assert IMPLEMENTATION_DOC.exists()
    assert READINESS_DOC.exists()
    assert CONTRACT_DOC.exists()
    assert PREFLIGHT_SCRIPT.exists()
    assert CLI_SCRIPT.exists()
    assert RENDERER_SCRIPT.exists()
    assert SCANNER_SCRIPT.exists()
    assert FIXTURE.exists()


def test_preflight_source_is_standard_library_only_and_isolated() -> None:
    source = _read(PREFLIGHT_SCRIPT)

    assert "COMMAND_NAME = \"synthetic-visible-report\"" in source
    assert "PREFLIGHT_NAME = \"synthetic-visible-report-preflight\"" in source
    assert "OUTPUT_FILENAME = \"cid_local_media_agent_synthetic_visible_report_v1.md\"" in source

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


def test_preflight_help_is_safe_and_does_not_generate_report(tmp_path: Path) -> None:
    rc, stdout, stderr = _run_preflight([])

    assert rc == 0
    assert stderr == ""
    assert "synthetic-visible-report-preflight" in stdout
    assert "No genera informe" in stdout
    assert "Revisión humana obligatoria" in stdout
    assert list(tmp_path.iterdir()) == []


def test_preflight_passes_for_existing_output_directory_without_creating_artifact(tmp_path: Path) -> None:
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
    assert "PREFLIGHT_PASS" in stdout
    assert f"expected_output={OUTPUT_FILENAME}" in stdout
    assert "mode=synthetic-local-only" in stdout
    assert "human_review=required" in stdout
    assert stderr == ""

    assert str(tmp_path) not in stdout
    assert str(FIXTURE.resolve()) not in stdout
    assert sorted(tmp_path.iterdir()) == []


def test_preflight_rejects_existing_output_without_overwrite_and_allows_with_flag(tmp_path: Path) -> None:
    output = tmp_path / OUTPUT_FILENAME
    output.write_text("existing report", encoding="utf-8")

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
    assert str(tmp_path) not in blocked_stderr
    assert _read(output) == "existing report"

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
    assert _read(output) == "existing report"


def test_preflight_rejects_bad_format_and_unsupported_options_without_stack_trace(tmp_path: Path) -> None:
    bad_format_rc, bad_format_stdout, bad_format_stderr = _run_preflight(
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
    assert bad_format_stdout == ""
    assert "PREFLIGHT_FAIL" in bad_format_stderr
    assert "reason=FORMAT_NOT_SUPPORTED" in bad_format_stderr
    assert "Traceback" not in bad_format_stderr

    bad_option_rc, bad_option_stdout, bad_option_stderr = _run_preflight(
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
    assert bad_option_stdout == ""
    assert "reason=OPTION_NOT_ALLOWED" in bad_option_stderr
    assert "Traceback" not in bad_option_stderr
    assert "/tmp/example.mov" not in bad_option_stderr


def test_preflight_rejects_missing_or_invalid_fixture_without_leaking_paths(tmp_path: Path) -> None:
    missing = tmp_path / "synthetic_demo_report_fixture_v1.json"

    missing_rc, missing_stdout, missing_stderr = _run_preflight(
        [
            "--fixture",
            str(missing),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert missing_rc == 2
    assert missing_stdout == ""
    assert "reason=FIXTURE_NOT_FOUND" in missing_stderr
    assert str(missing) not in missing_stderr

    invalid = tmp_path / "synthetic_demo_report_fixture_v1.json"
    invalid.write_text("{not-json", encoding="utf-8")

    invalid_rc, invalid_stdout, invalid_stderr = _run_preflight(
        [
            "--fixture",
            str(invalid),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert invalid_rc == 2
    assert invalid_stdout == ""
    assert "reason=FIXTURE_JSON_INVALID" in invalid_stderr
    assert "{not-json" not in invalid_stderr
    assert str(invalid) not in invalid_stderr

    invalid.write_text("{}", encoding="utf-8")

    schema_rc, schema_stdout, schema_stderr = _run_preflight(
        [
            "--fixture",
            str(invalid),
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown",
        ]
    )

    assert schema_rc == 2
    assert schema_stdout == ""
    assert "reason=FIXTURE_SCHEMA_INVALID" in schema_stderr


def test_preflight_rejects_missing_output_directory_and_file_output_without_path_leakage(tmp_path: Path) -> None:
    missing_output_dir = tmp_path / "missing-dir"

    missing_rc, missing_stdout, missing_stderr = _run_preflight(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(missing_output_dir),
            "--format",
            "markdown",
        ]
    )

    assert missing_rc == 3
    assert missing_stdout == ""
    assert "reason=OUTPUT_DIR_NOT_FOUND" in missing_stderr
    assert str(missing_output_dir) not in missing_stderr

    file_output = tmp_path / "not-a-directory"
    file_output.write_text("not a directory", encoding="utf-8")

    file_rc, file_stdout, file_stderr = _run_preflight(
        [
            "--fixture",
            str(FIXTURE),
            "--output-dir",
            str(file_output),
            "--format",
            "markdown",
        ]
    )

    assert file_rc == 4
    assert file_stdout == ""
    assert "reason=OUTPUT_DIR_NOT_DIRECTORY" in file_stderr
    assert str(file_output) not in file_stderr


def test_existing_cli_renderer_and_scanner_are_not_modified_by_preflight_phase() -> None:
    cli_source = _read(CLI_SCRIPT)
    renderer_source = _read(RENDERER_SCRIPT)
    scanner_source = _read(SCANNER_SCRIPT)

    assert "PREFLIGHT_PASS" not in cli_source
    assert "PREFLIGHT_FAIL" not in cli_source
    assert "--preflight" not in cli_source
    assert "synthetic-visible-report-preflight" not in cli_source

    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "synthetic-visible-report-preflight" not in renderer_source

    assert "synthetic-visible-report-preflight" not in scanner_source


def test_preflight_contract_readiness_and_implementation_are_consistent() -> None:
    combined = "\n".join(
        [
            _read(CONTRACT_DOC),
            _read(READINESS_DOC),
            _read(IMPLEMENTATION_DOC),
        ]
    )

    assert "PREFLIGHT_PASS" in combined
    assert "PREFLIGHT_FAIL" in combined
    assert "cid_local_media_agent_synthetic_visible_report_v1.md" in combined
    assert "local-only" in combined
    assert "human review" in combined
    assert "scanner" in combined
    assert "packaging" in combined
    assert "installable entry point wiring" in combined
    assert "real media" in combined
