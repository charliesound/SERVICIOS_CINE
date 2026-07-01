from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate_v1.md"
IMPLEMENTATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate_v1.md"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py"
WRAPPER_SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py"
VISIBLE_REPORT_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
EXPORT_ROOT = ROOT / "tests/tmp/local_media_agent/controlled_visible_report_exports"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED"
BASE_HEAD = "17e6b81d5209e1c2ad5fce4dde45a4f355483474"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-implementation-qa-gate-v1-20260701"
FUTURE_FLAG = "--visible-report-output"
VISIBLE_FLAG = "--visible-report-markdown"
JSON_FLAG = "--result-json"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
EXPORT_OK = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK"
EXPORT_REJECTED = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_REJECTED"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_wrapper_smoke_export_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_args() -> list[str]:
    return [
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--allowed-relative-path",
        ALLOWED_RELATIVE_PATH,
    ]


def wrapper_command(extra_args: list[str]) -> list[str]:
    return [sys.executable, str(WRAPPER), *base_args(), *extra_args]


def run_wrapper(extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        wrapper_command(extra_args),
        cwd=ROOT,
        shell=False,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def reset_export_root() -> None:
    shutil.rmtree(EXPORT_ROOT, ignore_errors=True)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)


def cleanup_export_root() -> None:
    shutil.rmtree(EXPORT_ROOT, ignore_errors=True)


def export_path(name: str = "wrapper_smoke_visible_report.md") -> Path:
    return EXPORT_ROOT / name


def root_report_artifacts() -> set[str]:
    patterns = [
        "*.md",
        "*.markdown",
        "*visible*report*",
        "*smoke*report*",
        "*local_media_agent*report*",
    ]
    found: set[str] = set()
    for pattern in patterns:
        for path in ROOT.glob(pattern):
            if path.is_file():
                found.add(path.name)
    return found


def controlled_export_files() -> list[Path]:
    if not EXPORT_ROOT.exists():
        return []
    return sorted(path for path in EXPORT_ROOT.glob("*.md") if path.is_file())


def test_smoke_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_FLAG,
        VISIBLE_FLAG,
        "tests/tmp/local_media_agent/controlled_visible_report_exports",
        "Use subprocess.run only inside this smoke test.",
        "Use shell=False only.",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_required_artifacts_exist() -> None:
    for path in [
        IMPLEMENTATION_QA_DOC,
        IMPLEMENTATION_QA_TEST,
        IMPLEMENTATION_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        WRAPPER_SMOKE_QA_TEST,
        WRAPPER_SMOKE_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]:
        assert path.exists(), path


def test_wrapper_remains_thin_and_export_free() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert FUTURE_FLAG not in body
    assert VISIBLE_FLAG not in body
    assert JSON_FLAG not in body


def test_implementation_parser_exposes_export_and_existing_flags() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert FUTURE_FLAG in help_text
    assert VISIBLE_FLAG in help_text
    assert JSON_FLAG in help_text


def test_smoke_test_uses_subprocess_safely() -> None:
    body = read_text(Path(__file__))
    assert "subprocess.run(" in body
    assert "shell=False" in body
    assert "capture_output=True" in body
    assert "text=True" in body
    assert "timeout=10" in body
    assert "cwd=ROOT" in body
    unsafe_shell_marker = "shell=" + "True"
    assert unsafe_shell_marker not in body


def test_wrapper_visible_report_stdout_then_valid_export_exact_match() -> None:
    reset_export_root()
    before_reports = root_report_artifacts()

    try:
        markdown_run = run_wrapper([VISIBLE_FLAG])
        output = export_path()
        export_run = run_wrapper([VISIBLE_FLAG, FUTURE_FLAG, str(output)])

        after_reports = root_report_artifacts()
        files = controlled_export_files()

        assert markdown_run.returncode == 0
        assert markdown_run.stderr == ""
        assert markdown_run.stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
        assert EXPECTED_SHA256 in markdown_run.stdout
        assert ALLOWED_RELATIVE_PATH in markdown_run.stdout

        assert export_run.returncode == 0
        assert export_run.stderr == ""
        assert export_run.stdout == f"{EXPORT_OK}\n"

        assert files == [output]
        assert output.exists()
        assert output.parent == EXPORT_ROOT
        assert output.read_text(encoding="utf-8") == markdown_run.stdout

        assert after_reports == before_reports
    finally:
        cleanup_export_root()


def test_wrapper_rejects_export_without_visible_report_and_writes_nothing() -> None:
    reset_export_root()
    try:
        output = export_path("requires_visible_mode.md")
        run = run_wrapper([FUTURE_FLAG, str(output)])

        assert run.returncode == 2
        assert run.stderr == ""
        assert run.stdout == f"{EXPORT_REJECTED}:VISIBLE_REPORT_MARKDOWN_REQUIRED\n"
        assert not output.exists()
        assert controlled_export_files() == []
    finally:
        cleanup_export_root()


def test_wrapper_rejects_outside_root_non_md_and_overwrite_without_extra_files() -> None:
    reset_export_root()
    try:
        outside = ROOT / "wrapper_smoke_outside.md"
        wrong_suffix = export_path("wrong_suffix.txt")
        existing = export_path("existing.md")
        existing.write_text("existing", encoding="utf-8")

        outside_run = run_wrapper([VISIBLE_FLAG, FUTURE_FLAG, str(outside)])
        suffix_run = run_wrapper([VISIBLE_FLAG, FUTURE_FLAG, str(wrong_suffix)])
        overwrite_run = run_wrapper([VISIBLE_FLAG, FUTURE_FLAG, str(existing)])

        assert outside_run.returncode == 2
        assert "VISIBLE_REPORT_OUTPUT_OUTSIDE_CONTROLLED_ROOT_REJECTED" in outside_run.stdout
        assert not outside.exists()

        assert suffix_run.returncode == 2
        assert "VISIBLE_REPORT_OUTPUT_SUFFIX_REJECTED" in suffix_run.stdout
        assert not wrong_suffix.exists()

        assert overwrite_run.returncode == 2
        assert "VISIBLE_REPORT_OUTPUT_EXISTS_OVERWRITE_REJECTED" in overwrite_run.stdout
        assert existing.read_text(encoding="utf-8") == "existing"

        assert controlled_export_files() == [existing]
    finally:
        cleanup_export_root()


def test_controlled_fixture_integrity_and_support_files_remain_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    assert (FIXTURE_ROOT / "README.md").exists()
    assert (FIXTURE_ROOT / "manifest.controlled.json").exists()


def test_smoke_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
