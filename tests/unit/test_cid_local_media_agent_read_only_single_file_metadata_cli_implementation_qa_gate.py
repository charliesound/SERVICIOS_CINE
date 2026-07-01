from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate_v1.md"
CLI = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
PYPROJECT = ROOT / "pyproject.toml"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.QA.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_QA_GATE_V1_CLOSED"
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
EXPECTED_BYTES = 239


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cli_tree() -> ast.Module:
    return ast.parse(read_text(CLI), filename=str(CLI))


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


def test_document_declares_phase_result_scope_and_closure() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        "Doc/test-only QA gate",
        "does not add runtime features",
        "No pyproject.toml modification.",
        "No console script registration.",
        "No scanner integration.",
        "No ffprobe.",
        "No FFmpeg.",
        "No batch processing.",
        "No recursive folder traversal.",
        "No fixture modification.",
        "No real material.",
        "No customer material.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No installer work.",
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
        "Only this QA document and QA unit test are staged.",
    ]
    for item in required:
        assert item in body


def test_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_implementation_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_implementation_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "bash scripts/dev/guard_no_sqlite_regressions.sh",
    ]
    for command in commands:
        assert command in body


def test_cli_exists_and_is_python_parseable() -> None:
    assert CLI.exists()
    assert isinstance(cli_tree(), ast.Module)


def test_cli_has_no_forbidden_imports() -> None:
    roots = import_roots(cli_tree())
    forbidden = {
        "alembic", "av", "boto3", "cv2", "docker", "fastapi",
        "ffmpeg", "ffprobe", "httpx", "mediainfo", "moviepy",
        "openai", "psycopg", "psycopg2", "pymediainfo",
        "qdrant_client", "requests", "socket", "sqlalchemy",
        "sqlite3", "stripe", "subprocess", "urllib", "uvicorn",
        "websocket", "websockets",
    }
    assert roots.isdisjoint(forbidden), sorted(roots & forbidden)


def test_cli_has_no_mutation_process_or_traversal_calls() -> None:
    tree = cli_tree()
    forbidden_leaf_calls = {
        "chmod", "execv", "execve", "execvp", "execvpe",
        "glob", "hardlink_to", "iglob", "iterdir", "makedirs",
        "mkdir", "popen", "remove", "rename", "replace", "rglob",
        "rmdir", "scandir", "spawnl", "spawnle", "spawnlp",
        "spawnlpe", "spawnv", "spawnve", "spawnvp", "spawnvpe",
        "symlink_to", "system", "touch", "unlink", "walk",
        "write_bytes", "write_text",
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = call_name(node)
            leaf = name.rsplit(".", 1)[-1]
            if leaf in forbidden_leaf_calls:
                found.append(name)
    assert not found, sorted(found)


def test_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_pyproject_does_not_register_cli() -> None:
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
