from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_readiness_gate_v1.md"
CLI = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "a68448bafd0e837c90cedbfa46d4b464acaf2527"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-implementation-qa-gate-correction-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"


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


def test_readiness_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "Doc/test-only readiness gate",
        "does not execute the CLI as a product smoke yet",
        "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "controlled_plain_text_marker_v1",
        "Expected bytes: 239",
        EXPECTED_SHA256,
    ]
    for item in required:
        assert item in body


def test_readiness_document_declares_forbidden_boundaries() -> None:
    body = read_text(DOC)
    forbidden_markers = [
        "No CLI behavior changes.",
        "No product smoke execution in this phase.",
        "No fixture modification.",
        "No batch processing.",
        "No recursive traversal.",
        "No scanner integration.",
        "No FFmpeg.",
        "No ffprobe.",
        "No pyproject modification.",
        "No console script registration.",
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
        "No real material.",
        "No customer material.",
    ]
    for marker in forbidden_markers:
        assert marker in body


def test_future_smoke_readiness_conditions_are_explicit() -> None:
    body = read_text(DOC)
    conditions = [
        "The input is exactly the controlled non-customer fixture declared in this document.",
        "The fixture byte size and SHA256 match the expected values.",
        "The CLI remains isolated under scripts/local_media_agent.",
        "The CLI remains read-only.",
        "The future smoke result is visible and auditable.",
        "Any output, if introduced later, must be controlled and explicitly scoped by a later phase.",
    ]
    for condition in conditions:
        assert condition in body


def test_controlled_fixture_integrity_is_ready_for_future_smoke() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_isolated_cli_exists_and_is_python_parseable() -> None:
    assert CLI.exists()
    assert isinstance(cli_tree(), ast.Module)


def test_cli_imports_do_not_cross_future_smoke_boundaries() -> None:
    roots = import_roots(cli_tree())
    forbidden = {
        "alembic", "av", "boto3", "cv2", "docker", "fastapi",
        "ffmpeg", "ffprobe", "httpx", "mediainfo", "moviepy",
        "openai", "psycopg", "psycopg2", "pymediainfo",
        "qdrant_client", "requests", "socket", "sqlalchemy",
        "sql" + "ite3", "stripe", "subprocess", "urllib", "uvicorn",
        "websocket", "websockets",
    }
    assert roots.isdisjoint(forbidden), sorted(roots & forbidden)


def test_pyproject_does_not_register_isolated_cli_for_future_smoke() -> None:
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


def test_readiness_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
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
