from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate_v1.md"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate_v1.md"
RENDERER_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py"
RENDERER_IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate_v1.md"
RENDERER_IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py"
RENDERER_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate_v1.md"
RENDERER_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.IN_MEMORY.INTEGRATION.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_IN_MEMORY_INTEGRATION_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "71277ef3c3b278defceaf3e173d6e3c1abb3f6a8"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-renderer-implementation-qa-gate-v1-20260701"
FUTURE_ARTIFACT = "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_renderer_module():
    spec = importlib.util.spec_from_file_location("cid_lma_renderer_in_memory_readiness", RENDERER)
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


def test_readiness_document_declares_phase_result_base_and_future_artifact() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_ARTIFACT,
        "The future integration artifact is not implemented in this phase.",
        "Doc/test-only readiness gate",
        "does not implement the integration",
        "does not change CLI behavior",
        "does not change renderer behavior",
        "does not generate report files",
        "does not add export behavior",
    ]
    for item in required:
        assert item in body


def test_readiness_document_references_prior_source_chain() -> None:
    prior_paths = [
        RENDERER_QA_DOC, RENDERER_QA_TEST,
        RENDERER_IMPLEMENTATION_DOC, RENDERER_IMPLEMENTATION_TEST,
        RENDERER_READINESS_DOC, RENDERER_READINESS_TEST,
        CONTRACT_DOC, CONTRACT_TEST,
    ]
    for path in prior_paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in prior_paths:
        assert path.name in body


def test_readiness_document_defines_in_memory_integration_contract() -> None:
    body = read_text(DOC)
    required = [
        "Accept structured controlled fixture smoke result data in memory.",
        "Pass that structured data to render_controlled_fixture_smoke_visible_report.",
        "Return Markdown text in memory.",
        "Preserve the smoke result data without mutation.",
        "Preserve controlled fixture identity values.",
        "Preserve byte size and SHA256 digest values.",
        "Avoid any filesystem writes.",
        "Avoid any report export behavior.",
        "Avoid CLI behavior changes.",
        "Avoid scanner integration.",
        "Avoid media probing.",
        "Avoid subprocess and shell execution.",
    ]
    for item in required:
        assert item in body


def test_readiness_document_declares_forbidden_scope() -> None:
    body = read_text(DOC)
    forbidden_lines = [
        "No integration implementation.",
        "No renderer behavior changes.",
        "No CLI behavior changes.",
        "No CLI execution.",
        "No report file generation.",
        "No export behavior.",
        "No subprocess.",
        "No shell execution.",
        "No fixture modification.",
        "No scanner integration.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
        "No SaaS integration.",
        "No database access.",
        "No real material.",
        "No customer material.",
    ]
    for line in forbidden_lines:
        assert line in body


def test_existing_renderer_is_ready_for_in_memory_integration() -> None:
    assert RENDERER.exists()
    assert isinstance(parse_python(RENDERER), ast.Module)
    module = load_renderer_module()
    assert hasattr(module, "render_controlled_fixture_smoke_visible_report")
    assert callable(module.render_controlled_fixture_smoke_visible_report)


def test_existing_renderer_imports_remain_minimal_and_safe() -> None:
    roots = import_roots(parse_python(RENDERER))
    assert roots <= {"__future__", "collections", "typing"}


def test_existing_renderer_has_no_file_process_scan_or_media_probe_calls() -> None:
    tree = parse_python(RENDERER)
    forbidden_leaf_calls = {
        "open", "write", "write_text", "write_bytes", "touch", "mkdir",
        "unlink", "rename", "replace", "remove", "rmdir",
        "system", "popen", "run", "call", "check_call", "check_output",
        "glob", "rglob", "iterdir", "walk", "scandir",
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            leaf = name.rsplit(".", 1)[-1]
            if leaf in forbidden_leaf_calls:
                found.append(name)
    assert not found, sorted(found)


def test_existing_renderer_can_render_sample_structured_smoke_data_in_memory() -> None:
    module = load_renderer_module()
    smoke_result = {
        "smoke_status": "PASS",
        "fixture_id": "controlled_plain_text_marker_v1",
        "fixture_root": "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1",
        "allowed_relative_path": ALLOWED_RELATIVE_PATH,
        "file_name": "controlled_plain_text_marker.txt",
        "byte_size": EXPECTED_BYTES,
        "sha256": EXPECTED_SHA256,
        "cli_execution_mode": "isolated main argv smoke",
        "exit_code": 0,
        "json_stdout_validation_status": "PASS",
        "stderr_validation_status": "PASS_EMPTY",
        "fixture_immutability_status": "PASS_UNCHANGED",
        "output_file_creation_status": "PASS_NONE_CREATED",
    }
    original = dict(smoke_result)
    report = module.render_controlled_fixture_smoke_visible_report(smoke_result)
    assert isinstance(report, str)
    assert smoke_result == original
    for value in ["controlled_plain_text_marker_v1", ALLOWED_RELATIVE_PATH, str(EXPECTED_BYTES), EXPECTED_SHA256]:
        assert value in report


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_renderer_or_future_integration() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "controlled_fixture_smoke_visible_report_renderer",
        "controlled_fixture_smoke_visible_report_in_memory_integration",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_renderer",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_in_memory_integration",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_readiness_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
