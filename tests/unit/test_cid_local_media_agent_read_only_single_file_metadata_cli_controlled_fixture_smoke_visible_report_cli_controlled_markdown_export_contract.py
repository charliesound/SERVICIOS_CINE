from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
WRAPPER_SMOKE_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate_v1.md"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py"
WRAPPER_SMOKE_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate_v1.md"
WRAPPER_SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py"
IMPLEMENTATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate_v1.md"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py"
VISIBLE_REPORT_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CONTRACT_V1_CLOSED"
BASE_HEAD = "b0fb9dd8dc8b42461e3a1924cd1916bdc28e086d"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-qa-gate-v1-20260701"
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
    spec = importlib.util.spec_from_file_location("cid_lma_controlled_markdown_export_contract_impl", IMPLEMENTATION)
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


def test_contract_document_declares_phase_result_base_and_future_flag() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_FLAG,
        EXISTING_FLAG,
        "Doc/test-only contract",
        "does not implement that flag",
        "does not change CLI behavior",
        "does not write report files",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_contract_document_references_existing_chain_and_artifacts() -> None:
    paths = [
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        WRAPPER_SMOKE_QA_DOC,
        WRAPPER_SMOKE_QA_TEST,
        WRAPPER_SMOKE_DOC,
        WRAPPER_SMOKE_TEST,
        IMPLEMENTATION_QA_DOC,
        IMPLEMENTATION_QA_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]
    for path in paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in paths:
        assert path.name in body or str(path.relative_to(ROOT)) in body


def test_contract_document_declares_future_export_policy() -> None:
    body = read_text(DOC)
    required = [
        "Be explicit and opt-in.",
        "Require --visible-report-markdown or an equivalent explicit visible report mode.",
        "Accept one output path argument.",
        "Treat the output path as a file path, not a directory scan request.",
        "Resolve the output path safely before writing.",
        "Reject missing parent directories.",
        "Reject symlink output files.",
        "Reject symlink parent directories.",
        "Reject paths outside the future approved controlled output root.",
        "Reject paths that point inside the controlled fixture source tree.",
        "Reject paths that point inside tests/fixtures.",
        "Reject paths that point to the repository root directly.",
        "Reject Windows-style paths inside WSL.",
        "Reject overwrite by default.",
        "Require a future explicit overwrite flag before replacing an existing report file.",
        "Restrict the output suffix to .md.",
        "Write UTF-8 text only.",
        "Write exactly the Markdown returned by the existing in-memory visible report integration.",
        "Keep default CLI status output unchanged.",
        "Keep --result-json behavior unchanged.",
        "Keep --visible-report-markdown stdout behavior unchanged when no output path is provided.",
        "Preserve accepted exit code 0.",
        "Preserve rejected exit code 2.",
        "Never write media-derived absolute paths into the report.",
        "Preserve redacted paths only.",
    ]
    for item in required:
        assert item in body


def test_contract_document_explicitly_forbids_current_phase_implementation_and_integrations() -> None:
    body = read_text(DOC)
    forbidden_scope = [
        "No implementation of --visible-report-output.",
        "No parser change.",
        "No CLI behavior change.",
        "No wrapper behavior change.",
        "No renderer behavior change.",
        "No in-memory integration behavior change.",
        "No report file generation.",
        "No export behavior.",
        "No filesystem writes except adding this contract document and test.",
        "No persistent output path.",
        "No subprocess.",
        "No shell execution.",
        "No fixture modification.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive product traversal.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
    ]
    for item in forbidden_scope:
        assert item in body


def test_existing_implementation_parser_does_not_expose_future_export_flag_yet() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert FUTURE_FLAG not in help_text
    assert EXISTING_FLAG in help_text
    assert "--result-json" in help_text


def test_existing_wrapper_does_not_expose_future_export_flag() -> None:
    body = read_text(WRAPPER)
    assert FUTURE_FLAG not in body
    assert EXISTING_FLAG not in body
    assert "ArgumentParser" not in body
    assert "implementation.run_cli(argv)" in body


def test_existing_implementation_source_does_not_implement_future_export() -> None:
    body = read_text(IMPLEMENTATION)
    assert FUTURE_FLAG not in body
    assert "visible_report_output" not in body
    assert "write_text" not in body
    assert "write_bytes" not in body

    forbidden_write_open_markers = [
        '.open("w',
        ".open('w",
        '.open("a',
        ".open('a",
        '.open("x',
        ".open('x",
        '.open(mode="w',
        ".open(mode='w",
        '.open(mode="a',
        ".open(mode='a",
        '.open(mode="x',
        ".open(mode='x",
    ]
    for marker in forbidden_write_open_markers:
        assert marker not in body

    assert "mkdir" not in body
    assert "unlink" not in body


def test_existing_default_json_and_markdown_stdout_behaviors_remain_unchanged() -> None:
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


def test_contract_test_itself_avoids_process_execution_and_file_writes() -> None:
    tree = parse_python(TEST)
    forbidden_calls = {"subprocess.run", "write_text", "write_bytes", "mkdir", "unlink", "rename", "replace"}
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            name_parts = [func.attr]
            value = func.value
            while isinstance(value, ast.Attribute):
                name_parts.append(value.attr)
                value = value.value
            if isinstance(value, ast.Name):
                name_parts.append(value.id)
            name = ".".join(reversed(name_parts))
        elif isinstance(func, ast.Name):
            name = func.id
        else:
            name = ""
        if name in forbidden_calls:
            found.append(name)
    assert not found


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


def test_contract_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
