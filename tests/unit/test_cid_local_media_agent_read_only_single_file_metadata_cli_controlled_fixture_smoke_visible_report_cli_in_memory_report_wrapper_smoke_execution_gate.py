from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate_v1.md"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
IMPLEMENTATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate_v1.md"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py"
IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate_v1.md"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT_REL = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE_REL = f"{FIXTURE_ROOT_REL}/media/controlled_plain_text_marker.txt"
FIXTURE_ROOT = ROOT / FIXTURE_ROOT_REL
FIXTURE = ROOT / FIXTURE_REL
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.WRAPPER.SMOKE.EXECUTION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_WRAPPER_SMOKE_EXECUTION_GATE_V1_CLOSED"
BASE_HEAD = "5f10e075d64146be5a2c9d8959ffeb6ddbe67ac8"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-in-memory-report-implementation-qa-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
VISIBLE_REPORT_FLAG = "--visible-report-markdown"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_wrapper_smoke_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def base_args() -> list[str]:
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


def rejected_args() -> list[str]:
    return [
        "--target-path",
        FIXTURE_REL,
        "--fixture-root",
        FIXTURE_ROOT_REL,
        "--expected-sha256",
        "0" * 64,
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


def test_execution_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        VISIBLE_REPORT_FLAG,
        "Doc/test-only controlled smoke execution gate",
        "public isolated CLI wrapper",
        "subprocess.run only to execute the Python wrapper script",
        "shell=False",
        "does not generate report files",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_execution_document_references_audited_chain_and_artifacts() -> None:
    paths = [
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
        IMPLEMENTATION_QA_DOC,
        IMPLEMENTATION_QA_TEST,
        IMPLEMENTATION_DOC,
        IMPLEMENTATION_TEST,
        READINESS_DOC,
        READINESS_TEST,
        CONTRACT_DOC,
        CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]
    for path in paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in paths:
        assert path.name in body or str(path.relative_to(ROOT)) in body


def test_execution_document_declares_smoke_requirements_and_forbidden_scope() -> None:
    body = read_text(DOC)
    required = [
        "Default wrapper execution returns exit code 0 and exact status stdout.",
        "--result-json wrapper execution returns exit code 0 and valid JSON stdout.",
        "--visible-report-markdown wrapper execution returns exit code 0 and Markdown stdout.",
        "Rejected --visible-report-markdown wrapper execution returns exit code 2 and Markdown stdout with FAIL.",
        "The fixture tree is unchanged before and after smoke execution.",
        "No report file is created in the repository root or controlled fixture tree.",
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


def test_wrapper_and_implementation_are_parseable() -> None:
    assert isinstance(parse_python(WRAPPER), ast.Module)
    assert isinstance(parse_python(IMPLEMENTATION), ast.Module)
    assert isinstance(parse_python(INTEGRATION), ast.Module)
    assert isinstance(parse_python(RENDERER), ast.Module)


def test_wrapper_remains_thin_delegating_layer() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert VISIBLE_REPORT_FLAG not in body
    assert "subprocess" not in body
    assert "shell" not in body


def test_implementation_parser_exposes_visible_report_flag() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert VISIBLE_REPORT_FLAG in help_text
    assert "--result-json" in help_text


def test_controlled_fixture_integrity_before_execution() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_wrapper_default_status_execution_smoke() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(base_args())

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 0
    assert result.stdout == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK\n"
    assert result.stderr == ""
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_wrapper_result_json_execution_smoke() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(base_args() + ["--result-json"])

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
    assert payload["metadata"]["bytes"] == EXPECTED_BYTES
    assert payload["metadata"]["sha256"] == EXPECTED_SHA256
    assert "# CID Local Media Agent - Controlled Fixture Smoke Visible Report" not in result.stdout
    assert result.stderr == ""
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_wrapper_visible_report_markdown_execution_smoke() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(base_args() + [VISIBLE_REPORT_FLAG])

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 0
    assert result.stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
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
        assert item in result.stdout
    assert result.stderr == ""
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_wrapper_visible_report_markdown_rejected_execution_smoke() -> None:
    before_tree = fixture_tree_snapshot()
    before_reports = root_report_artifacts()

    result = run_wrapper(rejected_args() + [VISIBLE_REPORT_FLAG])

    after_tree = fixture_tree_snapshot()
    after_reports = root_report_artifacts()

    assert result.returncode == 2
    assert result.stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    assert "FAIL" in result.stdout
    assert "2" in result.stdout
    assert result.stderr == ""
    assert after_tree == before_tree
    assert after_reports == before_reports


def test_no_generated_report_artifacts_exist_inside_controlled_fixture_tree() -> None:
    allowed_existing_fixture_support_files = {"README.md", "manifest.controlled.json"}
    report_like_suffixes = {".md", ".markdown", ".json"}
    report_like_files: set[str] = set()

    for path in FIXTURE_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in report_like_suffixes:
            report_like_files.add(str(path.relative_to(FIXTURE_ROOT)))

    unexpected = sorted(report_like_files - allowed_existing_fixture_support_files)
    assert not unexpected


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


def test_execution_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
