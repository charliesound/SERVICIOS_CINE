from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate_v1.md"
DEMO_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate_v1.md"
DEMO_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py"
WRAPPER_SMOKE_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate_v1.md"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py"
WRAPPER_SMOKE_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate_v1.md"
WRAPPER_SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py"
IMPLEMENTATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate_v1.md"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py"
IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate_v1.md"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
LEGACY_WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py"
LEGACY_WRAPPER_SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py"
VISIBLE_REPORT_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
EXPORT_ROOT = ROOT / "tests/tmp/local_media_agent/controlled_visible_report_exports"
EXPORT_FILE = EXPORT_ROOT / "controlled_demo_visible_report_qa.md"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTROLLED_DEMO.EXECUTION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTROLLED_DEMO_EXECUTION_QA_GATE_V1_CLOSED"
BASE_HEAD = "fb90fead00dff1ba196bf368deb368eec6666a7e"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-controlled-demo-execution-gate-v1-20260701"
VISIBLE_FLAG = "--visible-report-markdown"
OUTPUT_FLAG = "--visible-report-output"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
EXPORT_OK = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK"
EXPORT_REJECTED = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_REJECTED"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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


def qa_command(extra_args: list[str]) -> list[str]:
    return [sys.executable, str(WRAPPER), *base_args(), *extra_args]


def run_qa(extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        qa_command(extra_args),
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


def controlled_export_files() -> list[Path]:
    if not EXPORT_ROOT.exists():
        return []
    return sorted(path for path in EXPORT_ROOT.glob("*.md") if path.is_file())


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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_qa_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        VISIBLE_FLAG,
        OUTPUT_FLAG,
        "controlled_demo_visible_report_qa.md",
        "Doc/test-only QA gate",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_required_prior_and_runtime_artifacts_exist() -> None:
    for path in [
        DEMO_DOC,
        DEMO_TEST,
        WRAPPER_SMOKE_QA_DOC,
        WRAPPER_SMOKE_QA_TEST,
        WRAPPER_SMOKE_DOC,
        WRAPPER_SMOKE_TEST,
        IMPLEMENTATION_QA_DOC,
        IMPLEMENTATION_QA_TEST,
        IMPLEMENTATION_DOC,
        IMPLEMENTATION_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        LEGACY_WRAPPER_SMOKE_QA_TEST,
        LEGACY_WRAPPER_SMOKE_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]:
        assert path.exists(), path


def test_prior_demo_document_and_test_declare_reproducible_bounded_demo() -> None:
    doc_body = read_text(DEMO_DOC)
    test_body = read_text(DEMO_TEST)

    for item in [
        "sys.executable",
        "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "exported file SHA256",
        "Temporary export root is removed by the test.",
        "No real material.",
        "No customer material.",
    ]:
        assert item in doc_body

    for item in [
        "subprocess.run(",
        "sys.executable",
        "shell=False",
        "cwd=ROOT",
        "capture_output=True",
        "text=True",
        "timeout=10",
        "sha256_bytes",
        "cleanup_export_root()",
    ]:
        assert item in test_body

    unsafe_shell_marker = "shell=" + "True"
    assert unsafe_shell_marker not in test_body


def test_qa_command_shape_uses_public_wrapper_and_controlled_fixture() -> None:
    command = qa_command([VISIBLE_FLAG, OUTPUT_FLAG, str(EXPORT_FILE)])
    body = read_text(Path(__file__))

    assert command[0] == sys.executable
    assert command[1] == str(WRAPPER)
    assert "--target-path" in command
    assert str(FIXTURE) in command
    assert "--fixture-root" in command
    assert str(FIXTURE_ROOT) in command
    assert "--expected-sha256" in command
    assert EXPECTED_SHA256 in command
    assert "--expected-bytes" in command
    assert str(EXPECTED_BYTES) in command
    assert "--allowed-relative-path" in command
    assert ALLOWED_RELATIVE_PATH in command
    assert VISIBLE_FLAG in command
    assert OUTPUT_FLAG in command
    assert str(EXPORT_FILE) in command

    assert "subprocess.run(" in body
    assert "shell=False" in body
    assert "cwd=ROOT" in body
    assert "capture_output=True" in body
    assert "text=True" in body
    assert "timeout=10" in body
    unsafe_shell_marker = "shell=" + "True"
    assert unsafe_shell_marker not in body


def test_qa_demo_visible_stdout_export_sha_cleanup_and_no_root_artifacts() -> None:
    reset_export_root()
    before_reports = root_report_artifacts()

    try:
        visible_run = run_qa([VISIBLE_FLAG])
        export_run = run_qa([VISIBLE_FLAG, OUTPUT_FLAG, str(EXPORT_FILE)])

        after_reports = root_report_artifacts()
        files = controlled_export_files()

        assert visible_run.returncode == 0
        assert visible_run.stderr == ""
        assert visible_run.stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
        assert EXPECTED_SHA256 in visible_run.stdout
        assert ALLOWED_RELATIVE_PATH in visible_run.stdout

        assert export_run.returncode == 0
        assert export_run.stderr == ""
        assert export_run.stdout == f"{EXPORT_OK}\n"

        assert files == [EXPORT_FILE]
        assert EXPORT_FILE.exists()
        assert EXPORT_FILE.parent == EXPORT_ROOT

        exported_bytes = EXPORT_FILE.read_bytes()
        exported_text = exported_bytes.decode("utf-8")
        exported_sha256 = sha256_bytes(exported_bytes)

        assert exported_text == visible_run.stdout
        assert EXPECTED_SHA256 in exported_text
        assert ALLOWED_RELATIVE_PATH in exported_text
        assert SHA256_RE.fullmatch(exported_sha256)

        assert after_reports == before_reports
    finally:
        cleanup_export_root()

    assert not EXPORT_ROOT.exists()


def test_qa_rejected_demo_paths_write_nothing_or_preserve_existing_content() -> None:
    reset_export_root()
    try:
        requires_mode = EXPORT_ROOT / "requires_visible_mode.md"
        outside_root = ROOT / "controlled_demo_outside.md"
        existing = EXPORT_ROOT / "existing.md"
        existing.write_text("existing-content", encoding="utf-8")

        mode_run = run_qa([OUTPUT_FLAG, str(requires_mode)])
        outside_run = run_qa([VISIBLE_FLAG, OUTPUT_FLAG, str(outside_root)])
        overwrite_run = run_qa([VISIBLE_FLAG, OUTPUT_FLAG, str(existing)])

        assert mode_run.returncode == 2
        assert mode_run.stderr == ""
        assert mode_run.stdout == f"{EXPORT_REJECTED}:VISIBLE_REPORT_MARKDOWN_REQUIRED\n"
        assert not requires_mode.exists()

        assert outside_run.returncode == 2
        assert "VISIBLE_REPORT_OUTPUT_OUTSIDE_CONTROLLED_ROOT_REJECTED" in outside_run.stdout
        assert not outside_root.exists()

        assert overwrite_run.returncode == 2
        assert "VISIBLE_REPORT_OUTPUT_EXISTS_OVERWRITE_REJECTED" in overwrite_run.stdout
        assert existing.read_text(encoding="utf-8") == "existing-content"

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


def test_qa_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py",
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
