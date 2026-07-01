from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate_v1.md"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py"
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
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_QA_GATE_V1_CLOSED"
BASE_HEAD = "760b37939fac7b9ec95755b8eae178494f671689"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-v1-20260701"
CONTRACT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.V1"
CONTRACT_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_V1_CLOSED"
FUTURE_FLAG = "--visible-report-output"
EXISTING_FLAG = "--visible-report-markdown"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_controlled_markdown_export_contract_qa_impl", IMPLEMENTATION)
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


def called_function_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            parts = [func.attr]
            value = func.value
            while isinstance(value, ast.Attribute):
                parts.append(value.attr)
                value = value.value
            if isinstance(value, ast.Name):
                parts.append(value.id)
            names.add(".".join(reversed(parts)))
    return names


def test_qa_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        CONTRACT_PHASE,
        CONTRACT_RESULT,
        FUTURE_FLAG,
        EXISTING_FLAG,
        "Doc/test-only QA gate",
        "future --visible-report-output mode remains contract-only",
        "no implementation or parser change exists yet",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_qa_document_references_audited_contract_and_runtime_artifacts() -> None:
    paths = [
        CONTRACT_DOC,
        CONTRACT_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        WRAPPER_SMOKE_QA_TEST,
        WRAPPER_SMOKE_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]
    for path in paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in paths:
        assert path.name in body or str(path.relative_to(ROOT)) in body


def test_qa_document_declares_audit_requirements_and_forbidden_scope() -> None:
    body = read_text(DOC)
    required = [
        "The audited contract document declares --visible-report-output as future reserved only.",
        "The audited contract document says the future export flag is not implemented in that phase.",
        "The audited contract document forbids parser changes in that phase.",
        "The audited contract document forbids CLI behavior changes in that phase.",
        "The audited contract document forbids report file generation in that phase.",
        "The audited contract document defines safe output root policy.",
        "The audited contract document requires rejecting fixture source tree paths.",
        "The audited contract document requires rejecting tests/fixtures paths.",
        "The audited contract document requires rejecting repository root output paths.",
        "The audited contract document requires rejecting Windows-style paths inside WSL.",
        "The audited contract document requires rejecting overwrite by default.",
        "The audited contract document requires .md suffix restriction.",
        "The existing implementation parser still does not expose --visible-report-output.",
        "No implementation of --visible-report-output.",
        "No parser change.",
        "No CLI behavior change.",
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


def test_audited_contract_document_declares_policy_and_no_current_implementation() -> None:
    body = read_text(CONTRACT_DOC)
    required = [
        CONTRACT_PHASE,
        CONTRACT_RESULT,
        FUTURE_FLAG,
        EXISTING_FLAG,
        "Future reserved CLI flag",
        "No implementation of --visible-report-output.",
        "No parser change.",
        "No CLI behavior change.",
        "No report file generation.",
        "No export behavior.",
        "Reject paths outside the future approved controlled output root.",
        "Reject paths that point inside the controlled fixture source tree.",
        "Reject paths that point inside tests/fixtures.",
        "Reject paths that point to the repository root directly.",
        "Reject Windows-style paths inside WSL.",
        "Reject overwrite by default.",
        "Restrict the output suffix to .md.",
        "Write UTF-8 text only.",
        "Write exactly the Markdown returned by the existing in-memory visible report integration.",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_audited_contract_test_is_parseable_and_guards_no_future_flag_implementation() -> None:
    tree = parse_python(CONTRACT_TEST)
    body = read_text(CONTRACT_TEST)
    assert FUTURE_FLAG in body
    assert "test_existing_implementation_parser_does_not_expose_future_export_flag_yet" in body
    assert "assert FUTURE_FLAG not in help_text" in body
    assert "test_existing_wrapper_does_not_expose_future_export_flag" in body
    assert "assert FUTURE_FLAG not in body" in body
    assert "test_existing_default_json_and_markdown_stdout_behaviors_remain_unchanged" in body
    assert "test_contract_test_itself_avoids_process_execution_and_file_writes" in body
    assert isinstance(tree, ast.Module)


def test_audited_contract_test_does_not_call_subprocess_or_write_files() -> None:
    calls = called_function_names(parse_python(CONTRACT_TEST))
    forbidden = {
        "subprocess.run",
        "write_text",
        "write_bytes",
        "Path.write_text",
        "Path.write_bytes",
        "mkdir",
        "unlink",
        "rename",
        "replace",
    }
    assert not (calls & forbidden)


def test_existing_runtime_parser_keeps_future_export_absent_and_current_flags_present() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert FUTURE_FLAG not in help_text
    assert EXISTING_FLAG in help_text
    assert "--result-json" in help_text


def test_wrapper_remains_delegating_and_future_export_absent() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert FUTURE_FLAG not in body
    assert EXISTING_FLAG not in body


def test_existing_behavior_status_json_and_markdown_stdout_remain_unchanged_and_artifact_free() -> None:
    before_reports = root_report_artifacts()

    status_code, status_stdout = run_cli_and_capture(base_argv())
    json_code, json_stdout = run_cli_and_capture(base_argv() + ["--result-json"])
    markdown_code, markdown_stdout = run_cli_and_capture(base_argv() + [EXISTING_FLAG])

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


def test_pyproject_does_not_register_future_export_console_script() -> None:
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


def test_qa_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
