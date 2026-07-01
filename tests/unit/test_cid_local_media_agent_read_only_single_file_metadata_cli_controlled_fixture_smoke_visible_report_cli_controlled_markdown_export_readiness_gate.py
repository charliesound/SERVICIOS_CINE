from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_readiness_gate_v1.md"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py"
CONTRACT_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate_v1.md"
CONTRACT_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py"
VISIBLE_REPORT_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "60993d8aabbc113fb9c2d9ec1f559d72f38fc54d"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-qa-gate-v1-20260701"
FUTURE_FLAG = "--visible-report-output"
VISIBLE_FLAG = "--visible-report-markdown"
JSON_FLAG = "--result-json"
CONTROLLED_OUTPUT_ROOT = "tests/tmp/local_media_agent/controlled_visible_report_exports"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_controlled_markdown_export_readiness_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_argv() -> list[str]:
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


def run_cli_and_capture(argv: list[str]) -> tuple[int, str]:
    module = load_implementation_module()
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        exit_code = module.run_cli(argv)
    return exit_code, stdout.getvalue()


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


def test_readiness_document_declares_phase_result_base_and_future_flag() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_FLAG,
        VISIBLE_FLAG,
        JSON_FLAG,
        "Doc/test-only readiness gate",
        "does not implement it",
        "allowed implementation files",
        CONTROLLED_OUTPUT_ROOT,
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_prior_contract_and_runtime_artifacts_exist_and_are_referenced() -> None:
    paths = [
        CONTRACT_DOC,
        CONTRACT_TEST,
        CONTRACT_QA_DOC,
        CONTRACT_QA_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        WRAPPER_SMOKE_QA_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]
    for path in paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in paths:
        assert path.name in body or str(path.relative_to(ROOT)) in body


def test_readiness_document_declares_future_allowed_files_and_output_root() -> None:
    body = read_text(DOC)
    required = [
        "tests/tmp/local_media_agent/controlled_visible_report_exports",
        "scripts/local_media_agent/read_only_single_file_metadata.py",
        "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate_v1.md",
        "test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py",
        "The public wrapper must remain unchanged",
    ]
    for item in required:
        assert item in body


def test_readiness_document_declares_future_implementation_requirements() -> None:
    body = read_text(DOC)
    required = [
        "Add --visible-report-output to the implementation parser only.",
        "Keep the wrapper delegating to implementation.run_cli(argv).",
        "Require --visible-report-markdown when --visible-report-output is used.",
        "Accept exactly one output file path.",
        "Resolve the output path safely.",
        "Allow output only inside tests/tmp/local_media_agent/controlled_visible_report_exports",
        "Reject missing parent directories.",
        "Reject output paths whose parent is a symlink.",
        "Reject output file paths that are symlinks.",
        "Reject output paths outside the controlled output root.",
        "Reject output paths inside tests/fixtures.",
        "Reject output paths that resolve to the repository root.",
        "Reject Windows-style path strings inside WSL.",
        "Reject paths with suffix other than .md.",
        "Reject overwrite by default.",
        "Write UTF-8 Markdown text only.",
        "Write exactly the Markdown currently emitted by --visible-report-markdown.",
        "Keep default status output unchanged.",
        "Keep --result-json behavior unchanged.",
        "Keep --visible-report-markdown stdout-only behavior unchanged when no output path is provided.",
        "Preserve exit code 0 for accepted metadata and valid export.",
        "Preserve exit code 2 for rejected metadata or rejected output policy.",
    ]
    for item in required:
        assert item in body


def test_readiness_document_declares_future_test_requirements_and_forbidden_scope() -> None:
    body = read_text(DOC)
    required = [
        "Parser exposes --visible-report-output.",
        "Wrapper remains unchanged and does not implement --visible-report-output.",
        "Valid controlled output path writes one .md file inside the controlled output root.",
        "Written .md file content exactly matches the in-memory Markdown output.",
        "Existing output file is rejected by default.",
        "Missing parent directory is rejected.",
        "Symlink parent directory is rejected.",
        "Symlink output file is rejected.",
        "Output path inside fixture root is rejected.",
        "Output path inside tests/fixtures is rejected.",
        "Output path at repository root is rejected.",
        "Windows-style path string is rejected.",
        "Non-.md suffix is rejected.",
        "Rejected output policy leaves no new report file.",
        "No implementation of --visible-report-output.",
        "No parser change.",
        "No CLI behavior change.",
        "No wrapper behavior change.",
        "No report file generation.",
        "No export behavior.",
        "No subprocess.",
        "No shell execution.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
    ]
    for item in required:
        assert item in body


def test_current_parser_does_not_expose_future_output_but_keeps_existing_flags() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert FUTURE_FLAG not in help_text
    assert VISIBLE_FLAG in help_text
    assert JSON_FLAG in help_text


def test_wrapper_remains_delegating_and_does_not_expose_future_output() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert FUTURE_FLAG not in body
    assert VISIBLE_FLAG not in body


def test_current_status_json_and_markdown_stdout_behaviors_remain_artifact_free() -> None:
    before_reports = root_report_artifacts()

    status_code, status_stdout = run_cli_and_capture(base_argv())
    json_code, json_stdout = run_cli_and_capture(base_argv() + [JSON_FLAG])
    markdown_code, markdown_stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG])

    after_reports = root_report_artifacts()

    assert status_code == 0
    assert status_stdout == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK\n"

    assert json_code == 0
    payload = json.loads(json_stdout)
    assert payload["ok"] is True
    assert payload["metadata"]["bytes"] == EXPECTED_BYTES
    assert payload["metadata"]["sha256"] == EXPECTED_SHA256
    assert "Controlled Fixture Smoke Visible Report" not in json_stdout

    assert markdown_code == 0
    assert markdown_stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    assert EXPECTED_SHA256 in markdown_stdout
    assert ALLOWED_RELATIVE_PATH in markdown_stdout

    assert after_reports == before_reports


def test_controlled_fixture_integrity_and_support_files_remain_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    assert (FIXTURE_ROOT / "README.md").exists()
    assert (FIXTURE_ROOT / "manifest.controlled.json").exists()


def test_pyproject_does_not_register_future_output_console_script() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "visible-report-output",
        "controlled-markdown-export",
        "controlled_markdown_export",
        "scripts.local_media_agent.read_only_single_file_metadata",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_readiness_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
