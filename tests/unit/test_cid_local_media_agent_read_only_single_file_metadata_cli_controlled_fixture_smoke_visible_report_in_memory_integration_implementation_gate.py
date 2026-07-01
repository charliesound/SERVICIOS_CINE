from __future__ import annotations

import ast
import hashlib
import importlib.util
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate_v1.md"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate_v1.md"
RENDERER_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py"
RENDERER_IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate_v1.md"
RENDERER_IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.IN_MEMORY.INTEGRATION.IMPLEMENTATION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_IN_MEMORY_INTEGRATION_IMPLEMENTATION_GATE_V1_CLOSED"
BASE_HEAD = "cd8d002f30b4b71e1ec2f59d199d32745f52ff18"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-in-memory-integration-readiness-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_integration_module():
    spec = importlib.util.spec_from_file_location("cid_lma_in_memory_integration", INTEGRATION)
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


def import_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


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


def test_implementation_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "Controlled implementation gate",
        "does not change CLI behavior",
        "does not change renderer behavior",
        "does not generate report files",
        "does not add export behavior",
        "does not execute the CLI",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_implementation_document_references_prior_source_chain() -> None:
    prior_paths = [
        READINESS_DOC,
        READINESS_TEST,
        RENDERER_QA_DOC,
        RENDERER_QA_TEST,
        RENDERER_IMPLEMENTATION_DOC,
        RENDERER_IMPLEMENTATION_TEST,
        CONTRACT_DOC,
        CONTRACT_TEST,
    ]
    for path in prior_paths:
        assert path.exists(), path
    body = read_text(DOC)
    for path in prior_paths:
        assert path.name in body


def test_implementation_document_declares_contract_and_forbidden_scope() -> None:
    body = read_text(DOC)
    required = [
        "Expose render_controlled_fixture_smoke_result_in_memory.",
        "Accept structured controlled fixture smoke result data in memory.",
        "Validate that input is a mapping.",
        "Copy structured smoke result data before passing it to the renderer.",
        "Call render_controlled_fixture_smoke_visible_report.",
        "Return Markdown text in memory.",
        "Preserve the original smoke result mapping without mutation.",
        "Avoid any filesystem writes.",
        "Avoid any report export behavior.",
        "Avoid CLI behavior changes.",
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
    ]
    for item in required:
        assert item in body


def test_integration_module_exists_is_parseable_and_exposes_expected_function() -> None:
    assert INTEGRATION.exists()
    assert isinstance(parse_python(INTEGRATION), ast.Module)
    module = load_integration_module()
    assert hasattr(module, "render_controlled_fixture_smoke_result_in_memory")
    assert callable(module.render_controlled_fixture_smoke_result_in_memory)


def test_integration_imports_only_safe_dependencies_and_renderer() -> None:
    tree = parse_python(INTEGRATION)
    roots = import_roots(tree)
    assert roots <= {"__future__", "collections", "typing", "scripts"}
    modules = import_modules(tree)
    assert "scripts.local_media_agent.controlled_fixture_smoke_visible_report_renderer" in modules
    forbidden_modules = {
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
        "subprocess",
        "os",
        "pathlib",
        "sys",
        "shlex",
        "ffmpeg",
        "ffprobe",
        "sql" + "ite3",
        "sqlalchemy",
        "fastapi",
        "docker",
        "alembic",
        "stripe",
    }
    assert modules.isdisjoint(forbidden_modules), sorted(modules & forbidden_modules)


def test_integration_has_no_file_process_scan_or_media_probe_calls() -> None:
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


def test_integration_returns_markdown_in_memory_and_does_not_mutate_input() -> None:
    module = load_integration_module()
    smoke_result = sample_smoke_result()
    original = deepcopy(smoke_result)
    report = module.render_controlled_fixture_smoke_result_in_memory(smoke_result)
    assert isinstance(report, str)
    assert report.endswith("\n")
    assert smoke_result == original
    required = [
        "# CID Local Media Agent - Controlled Fixture Smoke Visible Report",
        "controlled_plain_text_marker_v1",
        ALLOWED_RELATIVE_PATH,
        "controlled_plain_text_marker.txt",
        str(EXPECTED_BYTES),
        EXPECTED_SHA256,
        "PASS_EMPTY",
        "PASS_UNCHANGED",
        "PASS_NONE_CREATED",
        "PENDING_HUMAN_REVIEW",
        "PENDING_HUMAN_DECISION",
    ]
    for item in required:
        assert item in report


def test_integration_passes_custom_human_placeholders_to_renderer() -> None:
    module = load_integration_module()
    report = module.render_controlled_fixture_smoke_result_in_memory(
        sample_smoke_result(),
        human_review_decision="APPROVED_FOR_INTERNAL_REVIEW",
        next_allowed_phase="NEXT_CONTROLLED_QA_GATE",
    )
    assert "APPROVED_FOR_INTERNAL_REVIEW" in report
    assert "NEXT_CONTROLLED_QA_GATE" in report


def test_integration_rejects_non_mapping_input() -> None:
    module = load_integration_module()
    try:
        module.render_controlled_fixture_smoke_result_in_memory(["not", "a", "mapping"])
    except TypeError as exc:
        assert "smoke_result must be a mapping" in str(exc)
    else:
        raise AssertionError("integration accepted non-mapping input")


def test_existing_renderer_still_exists_and_is_parseable() -> None:
    assert RENDERER.exists()
    assert isinstance(parse_python(RENDERER), ast.Module)


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_renderer_integration_or_cli() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "controlled_fixture_smoke_visible_report_in_memory_integration",
        "controlled_fixture_smoke_visible_report_renderer",
        "read_only_single_file_metadata_cli",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_in_memory_integration",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_renderer",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_implementation_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_in_memory_integration_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
