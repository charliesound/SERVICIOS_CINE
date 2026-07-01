from __future__ import annotations

import ast
import hashlib
import importlib.util
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate_v1.md"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.RENDERER.IMPLEMENTATION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_GATE_V1_CLOSED"
BASE_HEAD = "48167782b4376c42d0d3ed4436b66ba049efb811"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-renderer-readiness-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


def load_renderer_module():
    spec = importlib.util.spec_from_file_location("cid_lma_visible_report_renderer", RENDERER)
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


def test_implementation_document_declares_phase_result_base_scope_and_files() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py",
        "Controlled implementation gate",
        "does not change CLI behavior",
        "does not generate report files",
        "does not add export behavior",
        "does not execute the CLI",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_implementation_document_references_readiness_and_contract_sources() -> None:
    for path in [READINESS_DOC, READINESS_TEST, CONTRACT_DOC, CONTRACT_TEST]:
        assert path.exists(), path
    body = read_text(DOC)
    for path in [READINESS_DOC, READINESS_TEST, CONTRACT_DOC, CONTRACT_TEST]:
        assert path.name in body


def test_renderer_file_exists_is_parseable_and_exposes_expected_function() -> None:
    assert RENDERER.exists()
    tree = parse_python(RENDERER)
    assert isinstance(tree, ast.Module)
    module = load_renderer_module()
    assert hasattr(module, "render_controlled_fixture_smoke_visible_report")
    assert callable(module.render_controlled_fixture_smoke_visible_report)


def test_renderer_imports_do_not_cross_forbidden_boundaries() -> None:
    roots = import_roots(parse_python(RENDERER))
    forbidden = {
        "os", "pathlib", "subprocess", "shlex", "sys",
        "requests", "httpx", "socket", "urllib",
        "sql" + "ite3", "sqlalchemy", "psycopg", "psycopg2",
        "fastapi", "uvicorn", "docker", "alembic", "stripe",
        "ffmpeg", "ffprobe", "cv2", "av", "moviepy", "pymediainfo",
    }
    assert roots.isdisjoint(forbidden), sorted(roots & forbidden)


def test_renderer_has_no_file_mutation_or_process_calls() -> None:
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


def test_renderer_returns_markdown_with_required_sections_and_values() -> None:
    module = load_renderer_module()
    smoke_result = sample_smoke_result()
    original = deepcopy(smoke_result)
    report = module.render_controlled_fixture_smoke_visible_report(smoke_result)
    assert isinstance(report, str)
    assert report.endswith("\n")
    assert smoke_result == original
    required = [
        "# CID Local Media Agent - Controlled Fixture Smoke Visible Report",
        "## Phase identifier",
        PHASE,
        "## Result identifier",
        RESULT,
        "## Smoke status",
        "PASS",
        "controlled_plain_text_marker_v1",
        ALLOWED_RELATIVE_PATH,
        "controlled_plain_text_marker.txt",
        str(EXPECTED_BYTES),
        EXPECTED_SHA256,
        "isolated main argv smoke",
        "## Exit code",
        "0",
        "PASS_EMPTY",
        "PASS_UNCHANGED",
        "PASS_NONE_CREATED",
        "## Forbidden boundary checklist",
        "PENDING_HUMAN_REVIEW",
        "PENDING_HUMAN_DECISION",
    ]
    for item in required:
        assert item in report


def test_renderer_redacts_obvious_private_absolute_paths() -> None:
    module = load_renderer_module()
    smoke_result = sample_smoke_result()
    smoke_result["fixture_root"] = "/home/private_user/secret/project"
    smoke_result["allowed_relative_path"] = "C:\\\\private\\\\customer\\\\file.mov"
    report = module.render_controlled_fixture_smoke_visible_report(smoke_result)
    assert "/home/private_user" not in report
    assert "C:\\\\private" not in report
    assert "[REDACTED_PRIVATE_PATH]" in report


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_renderer_or_cli() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "controlled_fixture_smoke_visible_report_renderer",
        "read_only_single_file_metadata_cli",
        "scripts.local_media_agent.controlled_fixture_smoke_visible_report_renderer",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_implementation_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
