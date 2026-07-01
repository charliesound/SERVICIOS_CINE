from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate_v1.md"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate_v1.md"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py"
INTEGRATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate_v1.md"
INTEGRATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.IMPLEMENTATION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_IMPLEMENTATION_QA_GATE_V1_CLOSED"
BASE_HEAD = "bef4bae8dbb392fe7b5d5d8cc04196302b328ea8"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-implementation-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
VISIBLE_REPORT_FLAG = "--visible-report-markdown"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    parts: list[str] = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    return ".".join(reversed(parts))


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


def rejected_argv() -> list[str]:
    return [
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        "0" * 64,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--allowed-relative-path",
        ALLOWED_RELATIVE_PATH,
    ]


def run_cli_and_capture(argv: list[str]) -> tuple[int, str]:
    module = load_module(IMPLEMENTATION, "cid_lma_cli_visible_report_qa_impl")
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        exit_code = module.run_cli(argv)
    return exit_code, stdout.getvalue()


def test_qa_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        VISIBLE_REPORT_FLAG,
        "Doc/test-only QA gate",
        "does not add CLI behavior",
        "does not change renderer behavior",
        "does not change in-memory integration behavior",
        "does not generate report files",
        "does not add export behavior",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_qa_document_references_prior_source_chain_and_artifacts() -> None:
    paths = [
        IMPLEMENTATION,
        WRAPPER,
        INTEGRATION,
        RENDERER,
        IMPLEMENTATION_DOC,
        IMPLEMENTATION_TEST,
        READINESS_DOC,
        READINESS_TEST,
        INTEGRATION_QA_DOC,
        INTEGRATION_QA_TEST,
        CONTRACT_DOC,
        CONTRACT_TEST,
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
        "The implementation parser exposes --visible-report-markdown.",
        "The implementation parser still exposes --result-json.",
        "The default CLI status output remains unchanged.",
        "The --result-json output remains JSON and does not include Markdown.",
        "The --visible-report-markdown output starts with the visible report Markdown title.",
        "The --visible-report-markdown mode prints Markdown to stdout only.",
        "The --visible-report-markdown mode preserves deterministic exit code 0 for accepted metadata.",
        "The --visible-report-markdown mode preserves deterministic exit code 2 for rejected metadata.",
        "The wrapper still delegates to implementation.run_cli(argv).",
        "The wrapper does not implement --visible-report-markdown.",
        "The implementation does not import the wrapper.",
        "No new CLI behavior.",
        "No wrapper behavior changes.",
        "No report file generation.",
        "No export behavior.",
        "No persistent output path.",
        "No subprocess.",
        "No shell execution.",
        "No fixture modification.",
        "No scanner integration.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
    ]
    for item in required:
        assert item in body


def test_implementation_and_wrapper_are_parseable() -> None:
    assert isinstance(parse_python(IMPLEMENTATION), ast.Module)
    assert isinstance(parse_python(WRAPPER), ast.Module)
    assert isinstance(parse_python(INTEGRATION), ast.Module)
    assert isinstance(parse_python(RENDERER), ast.Module)


def test_parser_exposes_visible_report_and_result_json_flags() -> None:
    module = load_module(IMPLEMENTATION, "cid_lma_cli_visible_report_qa_parser")
    help_text = module.build_parser().format_help()
    assert VISIBLE_REPORT_FLAG in help_text
    assert "--result-json" in help_text


def test_implementation_imports_remain_allowed() -> None:
    roots = import_roots(parse_python(IMPLEMENTATION))
    assert roots <= {"__future__", "argparse", "hashlib", "json", "pathlib", "typing"}


def test_implementation_does_not_import_wrapper_or_forbidden_dependencies() -> None:
    body = read_text(IMPLEMENTATION)
    assert "read_only_single_file_metadata_cli" not in body
    forbidden_text = [
        "subprocess",
        "os.system",
        "shlex",
        "requests",
        "httpx",
        "socket",
        "urllib",
        "sql" + "ite3",
        "sqlalchemy",
        "psycopg",
        "fastapi",
        "uvicorn",
        "docker",
        "alembic",
        "stripe",
        "ffmpeg",
        "ffprobe",
    ]
    for item in forbidden_text:
        assert item not in body


def test_implementation_has_no_write_export_scan_or_process_calls() -> None:
    tree = parse_python(IMPLEMENTATION)
    forbidden_leaf_calls = {
        "write_text", "write_bytes", "touch", "mkdir", "unlink", "rename",
        "replace", "remove", "rmdir", "system", "popen", "run", "call",
        "check_call", "check_output", "glob", "rglob", "iterdir", "walk", "scandir",
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            leaf = name.rsplit(".", 1)[-1]
            if leaf in forbidden_leaf_calls:
                found.append(name)
    assert not found, sorted(found)


def test_default_status_output_remains_exact() -> None:
    exit_code, stdout = run_cli_and_capture(base_argv())
    assert exit_code == 0
    assert stdout == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK\n"


def test_result_json_output_remains_json_without_markdown() -> None:
    exit_code, stdout = run_cli_and_capture(base_argv() + ["--result-json"])
    assert exit_code == 0
    payload = json.loads(stdout)
    assert payload["ok"] is True
    assert payload["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
    assert payload["metadata"]["bytes"] == EXPECTED_BYTES
    assert payload["metadata"]["sha256"] == EXPECTED_SHA256
    assert "# CID Local Media Agent - Controlled Fixture Smoke Visible Report" not in stdout


def test_visible_report_markdown_stdout_for_accepted_metadata() -> None:
    exit_code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_REPORT_FLAG])
    assert exit_code == 0
    assert stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    required = [
        "controlled_plain_text_marker_v1",
        ALLOWED_RELATIVE_PATH,
        "controlled_plain_text_marker.txt",
        str(EXPECTED_BYTES),
        EXPECTED_SHA256,
        "read_only_single_file_metadata_visible_report_markdown_in_memory",
        "PASS_NO_STDERR_IN_PROCESS",
        "PASS_READ_ONLY_METADATA_COLLECTION",
        "PASS_NONE_CREATED",
        "PENDING_HUMAN_REVIEW",
        "PENDING_HUMAN_DECISION",
    ]
    for item in required:
        assert item in stdout


def test_visible_report_markdown_preserves_rejected_exit_code() -> None:
    exit_code, stdout = run_cli_and_capture(rejected_argv() + [VISIBLE_REPORT_FLAG])
    assert exit_code == 2
    assert stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    assert "FAIL" in stdout
    assert "2" in stdout


def test_wrapper_remains_delegating_and_does_not_implement_flag() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert VISIBLE_REPORT_FLAG not in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_visible_report_mode_or_cli_script() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "visible-report-markdown",
        "controlled_fixture_smoke_visible_report_cli_in_memory_report",
        "scripts.local_media_agent.read_only_single_file_metadata",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_qa_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
