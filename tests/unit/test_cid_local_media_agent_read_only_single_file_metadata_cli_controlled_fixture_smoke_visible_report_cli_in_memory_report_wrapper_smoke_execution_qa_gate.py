from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate_v1.md"
SMOKE_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate_v1.md"
SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT_REL = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE_REL = f"{FIXTURE_ROOT_REL}/media/controlled_plain_text_marker.txt"
FIXTURE_ROOT = ROOT / FIXTURE_ROOT_REL
FIXTURE = ROOT / FIXTURE_REL
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_QA_GATE_V1_CLOSED"
BASE_HEAD = "849eaa7b65a0e1f26c88ddf5a79f6d08cf78ee4f"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-wrapper-smoke-execution-gate-v1-20260701"
SMOKE_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1"
SMOKE_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
VISIBLE_REPORT_FLAG = "--visible-report-markdown"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_wrapper_smoke_qa_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_keyword_values(tree: ast.AST) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg is None:
                continue
            values.setdefault(keyword.arg, set()).add(ast.unparse(keyword.value))
    return values


def fixture_tree_snapshot() -> dict[str, tuple[int, str]]:
    snapshot: dict[str, tuple[int, str]] = {}
    for path in sorted(FIXTURE_ROOT.rglob("*")):
        if path.is_file():
            data = path.read_bytes()
            snapshot[str(path.relative_to(FIXTURE_ROOT))] = (
                len(data),
                hashlib.sha256(data).hexdigest(),
            )
    return snapshot


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


def wrapper_base_args() -> list[str]:
    return [
        "--target-path",
        FIXTURE_REL,
        "--fixture-root",
        FIXTURE_ROOT_REL,
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--allowed-relative-path",
        ALLOWED_RELATIVE_PATH,
    ]


def run_wrapper(args: list[str]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(WRAPPER.relative_to(ROOT)), *args]
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
        check=False,
    )


def test_qa_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        SMOKE_PHASE,
        SMOKE_RESULT,
        VISIBLE_REPORT_FLAG,
        "Doc/test-only QA gate",
        "controlled smoke execution",
        "limited to the controlled non-customer fixture",
        "shell-free",
        "artifact-free",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_qa_document_references_smoke_artifacts_and_runtime_chain() -> None:
    paths = [
        SMOKE_DOC,
        SMOKE_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        IMPLEMENTATION_QA_TEST,
        IMPLEMENTATION_TEST,
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
        "The previous wrapper smoke execution document exists.",
        "The previous wrapper smoke execution test exists.",
        "The previous wrapper smoke execution document permits subprocess.run only inside the QA test.",
        "The previous wrapper smoke execution document requires sys.executable.",
        "The previous wrapper smoke execution document requires shell=False.",
        "The previous wrapper smoke execution test uses subprocess.run.",
        "The previous wrapper smoke execution test uses sys.executable.",
        "The previous wrapper smoke execution test uses shell=False.",
        "The previous wrapper smoke execution test uses capture_output=True.",
        "The previous wrapper smoke execution test verifies default status output.",
        "The previous wrapper smoke execution test verifies --result-json output.",
        "The previous wrapper smoke execution test verifies --visible-report-markdown output.",
        "The previous wrapper smoke execution test verifies rejected visible report exit code 2.",
        "The previous wrapper smoke execution test verifies fixture tree snapshots before and after execution.",
        "The previous wrapper smoke execution test allows existing README.md and manifest.controlled.json fixture support files.",
        "No implementation behavior changes.",
        "No wrapper behavior changes.",
        "No report file generation.",
        "No export behavior.",
        "No persistent output path.",
        "No shell=True.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
    ]
    for item in required:
        assert item in body


def test_previous_smoke_document_declares_controlled_subprocess_boundaries() -> None:
    body = read_text(SMOKE_DOC)
    required = [
        "subprocess.run only to execute the Python wrapper script",
        "sys.executable",
        "shell=False",
        "capture_output=True",
        "text=True",
        "timeout",
        "cwd set to repository root",
        "controlled fixture paths only",
        "no real or customer material",
        "does not permit subprocess usage in production implementation code",
        "No shell=True.",
    ]
    for item in required:
        assert item in body


def test_previous_smoke_test_is_parseable_and_uses_controlled_subprocess() -> None:
    tree = parse_python(SMOKE_TEST)
    body = read_text(SMOKE_TEST)
    assert "subprocess.run(" in body
    assert "sys.executable" in body
    assert "shell=False" in body
    assert "capture_output=True" in body
    assert "text=True" in body
    assert "timeout=10" in body
    assert "cwd=ROOT" in body
    assert "check=False" in body
    keyword_values = call_keyword_values(tree)
    assert "'False'" in keyword_values.get("shell", set()) or "False" in keyword_values.get("shell", set())
    assert "True" in keyword_values.get("capture_output", set())
    assert "True" in keyword_values.get("text", set())


def test_previous_smoke_test_covers_status_json_markdown_rejected_and_no_artifacts() -> None:
    body = read_text(SMOKE_TEST)
    required = [
        "test_wrapper_default_status_execution_smoke",
        "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK",
        "test_wrapper_result_json_execution_smoke",
        "json.loads",
        "test_wrapper_visible_report_markdown_execution_smoke",
        "Controlled Fixture Smoke Visible Report",
        "test_wrapper_visible_report_markdown_rejected_execution_smoke",
        "returncode == 2",
        "result.stderr == """,
        "fixture_tree_snapshot",
        "root_report_artifacts",
        "after_tree == before_tree",
        "after_reports == before_reports",
        "allowed_existing_fixture_support_files",
        "README.md",
        "manifest.controlled.json",
    ]
    for item in required:
        assert item in body


def test_wrapper_remains_thin_delegating_layer() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert VISIBLE_REPORT_FLAG not in body
    assert "subprocess" not in body
    assert "shell" not in body


def test_implementation_parser_still_exposes_visible_report_and_json_flags() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert VISIBLE_REPORT_FLAG in help_text
    assert "--result-json" in help_text


def test_controlled_fixture_integrity_and_existing_support_files() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    assert (FIXTURE_ROOT / "README.md").exists()
    assert (FIXTURE_ROOT / "manifest.controlled.json").exists()


def test_wrapper_visible_report_execution_remains_artifact_free() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(wrapper_base_args() + [VISIBLE_REPORT_FLAG])

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    assert "controlled_plain_text_marker_v1" in result.stdout
    assert EXPECTED_SHA256 in result.stdout
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_wrapper_json_execution_remains_artifact_free_and_non_markdown() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(wrapper_base_args() + ["--result-json"])

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["metadata"]["bytes"] == EXPECTED_BYTES
    assert payload["metadata"]["sha256"] == EXPECTED_SHA256
    assert "Controlled Fixture Smoke Visible Report" not in result.stdout
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_pyproject_does_not_register_visible_report_console_script() -> None:
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
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
