from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate_v1.md"
CLI = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
INTEGRATION_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate_v1.md"
INTEGRATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py"
INTEGRATION_IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate_v1.md"
INTEGRATION_IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py"
INTEGRATION_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate_v1.md"
INTEGRATION_READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate_v1.md"
RENDERER_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.IN_MEMORY.REPORT.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_IN_MEMORY_REPORT_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "0c6963e348072d8901513e7a89289cc6e25c831b"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-in-memory-integration-implementation-qa-gate-v1-20260701"
FUTURE_FLAG = "--visible-report-markdown"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


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


def function_names(tree: ast.AST) -> set[str]:
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


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


def sample_smoke_result() -> dict[str, object]:
    return {
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


def test_readiness_document_declares_phase_result_base_future_flag_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_FLAG,
        "The future flag is not implemented in this phase.",
        "Doc/test-only readiness gate",
        "does not implement a CLI flag",
        "does not change CLI behavior",
        "does not change renderer behavior",
        "does not change in-memory integration behavior",
        "does not generate report files",
        "does not add export behavior",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_readiness_document_references_existing_artifacts_and_prior_chain() -> None:
    prior_paths = [
        CLI,
        INTEGRATION,
        RENDERER,
        INTEGRATION_QA_DOC,
        INTEGRATION_QA_TEST,
        INTEGRATION_IMPLEMENTATION_DOC,
        INTEGRATION_IMPLEMENTATION_TEST,
        INTEGRATION_READINESS_DOC,
        INTEGRATION_READINESS_TEST,
        RENDERER_QA_DOC,
        RENDERER_QA_TEST,
        CONTRACT_DOC,
        CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]
    for path in prior_paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in prior_paths:
        assert path.name in body or str(path.relative_to(ROOT)) in body


def test_readiness_document_defines_future_cli_contract() -> None:
    body = read_text(DOC)
    required = [
        "Keep the visible report mode explicit and opt-in.",
        "Use the reserved --visible-report-markdown flag.",
        "Keep the current default CLI behavior unchanged.",
        "Keep existing --result-json behavior unchanged.",
        "Build structured controlled fixture smoke result data in memory.",
        "Pass structured data to render_controlled_fixture_smoke_result_in_memory.",
        "Print Markdown to stdout only when the explicit visible report flag is used.",
        "Avoid writing report files.",
        "Avoid adding export behavior.",
        "Avoid adding persistent report paths.",
        "Avoid scanning folders.",
        "Avoid media probing.",
        "Avoid subprocess and shell execution.",
        "Avoid real or customer material.",
        "Preserve non-zero exit behavior for validation failures.",
    ]
    for item in required:
        assert item in body


def test_readiness_document_declares_forbidden_scope() -> None:
    body = read_text(DOC)
    forbidden_lines = [
        "No CLI behavior changes.",
        "No CLI flag implementation.",
        "No CLI execution.",
        "No renderer behavior changes.",
        "No in-memory integration behavior changes.",
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


def test_existing_cli_artifact_is_parseable_and_exposes_main() -> None:
    assert CLI.exists()
    tree = parse_python(CLI)
    assert isinstance(tree, ast.Module)
    assert "main" in function_names(tree)


def test_existing_integration_and_renderer_artifacts_are_parseable_and_callable() -> None:
    integration = load_module(INTEGRATION, "cid_lma_cli_report_readiness_integration")
    renderer = load_module(RENDERER, "cid_lma_cli_report_readiness_renderer")
    assert hasattr(integration, "render_controlled_fixture_smoke_result_in_memory")
    assert callable(integration.render_controlled_fixture_smoke_result_in_memory)
    assert hasattr(renderer, "render_controlled_fixture_smoke_visible_report")
    assert callable(renderer.render_controlled_fixture_smoke_visible_report)


def test_existing_integration_can_render_markdown_from_structured_smoke_data() -> None:
    integration = load_module(INTEGRATION, "cid_lma_cli_report_readiness_integration_render")
    smoke_result = sample_smoke_result()
    original = dict(smoke_result)
    report = integration.render_controlled_fixture_smoke_result_in_memory(smoke_result)
    assert isinstance(report, str)
    assert report.endswith("\n")
    assert smoke_result == original
    for value in ["# CID Local Media Agent - Controlled Fixture Smoke Visible Report", "controlled_plain_text_marker_v1", ALLOWED_RELATIVE_PATH, str(EXPECTED_BYTES), EXPECTED_SHA256]:
        assert value in report


def test_existing_integration_imports_remain_safe() -> None:
    roots = import_roots(parse_python(INTEGRATION))
    assert roots <= {"__future__", "collections", "typing", "scripts"}


def test_existing_integration_has_no_file_process_scan_or_media_probe_calls() -> None:
    tree = parse_python(INTEGRATION)
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


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_future_report_mode() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "visible-report-markdown",
        "controlled_fixture_smoke_visible_report_cli_in_memory_report",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_cli_in_memory_report",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_readiness_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
