from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate_v1.md"
EXEC_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate_v1.md"
EXEC_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py"
CLI = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
PYPROJECT = ROOT / "pyproject.toml"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.EXECUTION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_EXECUTION_QA_GATE_V1_CLOSED"
BASE_HEAD = "e6f2fde098bb538c7acd5f4793d8f6aeb70d0357"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-execution-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_python(path: Path) -> ast.Module:
    return ast.parse(read_text(path), filename=str(path))


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


def import_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def test_qa_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "Doc/test-only QA gate",
        "does not change CLI behavior",
        "does not execute against real or customer material",
        "No CLI behavior changes.",
        "No new product runtime behavior.",
        "No output file creation.",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_qa_document_declares_audited_artifacts_and_fixture() -> None:
    body = read_text(DOC)
    required = [
        "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate_v1.md",
        "test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py",
        "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "controlled_plain_text_marker.txt",
        ALLOWED_RELATIVE_PATH,
        "Expected bytes: 239",
        EXPECTED_SHA256,
    ]
    for item in required:
        assert item in body


def test_prior_smoke_execution_artifacts_exist_and_are_parseable() -> None:
    assert EXEC_DOC.exists()
    assert EXEC_TEST.exists()
    assert CLI.exists()
    assert isinstance(parse_python(EXEC_TEST), ast.Module)
    assert isinstance(parse_python(CLI), ast.Module)


def test_prior_smoke_execution_test_uses_in_memory_cli_main_execution() -> None:
    body = read_text(EXEC_TEST)
    required = [
        "def run_cli_smoke()",
        "module.main(argv)",
        "contextlib.redirect_stdout(stdout)",
        "contextlib.redirect_stderr(stderr)",
        "io.StringIO()",
        "json.loads(stdout)",
        "--result-json",
        "--target-path",
        "--fixture-root",
        "--expected-sha256",
        "--expected-bytes",
        "--allowed-relative-path",
    ]
    for item in required:
        assert item in body


def test_prior_smoke_execution_test_is_limited_to_controlled_fixture() -> None:
    body = read_text(EXEC_TEST)
    required = [
        "controlled_non_customer_fixture_pack_v1",
        "controlled_plain_text_marker.txt",
        ALLOWED_RELATIVE_PATH,
        str(EXPECTED_BYTES),
        EXPECTED_SHA256,
        "before_bytes == after_bytes",
        "before_digest == after_digest == EXPECTED_SHA256",
        "before == after",
    ]
    for item in required:
        assert item in body


def test_prior_smoke_execution_test_has_no_external_process_imports() -> None:
    tree = parse_python(EXEC_TEST)
    roots = import_roots(tree)
    forbidden = {
        "os",
        "shlex",
        "subprocess",
        "sys",
    }
    assert roots.isdisjoint(forbidden), sorted(roots & forbidden)


def test_prior_smoke_execution_test_has_no_mutating_file_calls() -> None:
    tree = parse_python(EXEC_TEST)
    forbidden_leaf_calls = {
        "open",
        "write",
        "write_text",
        "write_bytes",
        "touch",
        "mkdir",
        "unlink",
        "rename",
        "replace",
        "remove",
        "rmdir",
        "system",
        "popen",
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


def test_pyproject_does_not_register_isolated_cli() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "read_only_single_file_metadata_cli",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
        "local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_qa_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
