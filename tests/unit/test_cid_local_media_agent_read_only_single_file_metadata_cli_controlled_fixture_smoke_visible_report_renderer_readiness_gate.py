from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_renderer_readiness_gate_v1.md"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
EXEC_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate_v1.md"
EXEC_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate.py"
EXEC_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate_v1.md"
EXEC_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_qa_gate.py"
FIXTURE = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.RENDERER.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_RENDERER_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "5791d04987e57e10934e200b45ad454879fbe00f"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-contract-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_renderer_readiness_document_declares_phase_result_and_base() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "Doc/test-only readiness gate",
        "does not implement a renderer",
        "does not generate report files",
        "does not add export behavior",
        "does not change CLI behavior",
        "does not execute against real or customer material",
    ]
    for item in required:
        assert item in body


def test_renderer_readiness_references_prior_contract_and_smoke_evidence() -> None:
    for path in [CONTRACT_DOC, CONTRACT_TEST, EXEC_DOC, EXEC_TEST, EXEC_QA_DOC, EXEC_QA_TEST]:
        assert path.exists(), path
    body = read_text(DOC)
    for path in [CONTRACT_DOC, CONTRACT_TEST, EXEC_DOC, EXEC_TEST, EXEC_QA_DOC, EXEC_QA_TEST]:
        assert path.name in body


def test_renderer_readiness_declares_future_renderer_requirements() -> None:
    body = read_text(DOC)
    requirements = [
        "Accepts structured smoke result data as an explicit input object.",
        "Returns Markdown text in memory.",
        "Does not write report files.",
        "Does not mutate the controlled fixture.",
        "Does not execute the CLI.",
        "Does not call subprocess or shell execution.",
        "Does not scan folders.",
        "Does not perform batch processing.",
        "Does not perform recursive product traversal.",
        "Does not use FFmpeg.",
        "Does not use ffprobe.",
        "Does not access SaaS services.",
        "Does not access databases.",
        "Does not expose absolute user home paths.",
        "Does not expose secrets or environment variables.",
        "Does not expose real or customer material references.",
        "Includes the visible report sections defined by the prior contract.",
        "Keeps human review decision as an explicit placeholder.",
        "Keeps next allowed phase as an explicit placeholder.",
    ]
    for requirement in requirements:
        assert requirement in body


def test_renderer_readiness_declares_required_future_markdown_sections() -> None:
    body = read_text(DOC)
    sections = [
        "Report title.",
        "Phase identifier.",
        "Result identifier.",
        "Smoke status.",
        "Controlled fixture identity.",
        "Fixture root.",
        "Allowed relative path.",
        "File name.",
        "Byte size.",
        "SHA256 digest.",
        "CLI execution mode.",
        "Exit code.",
        "JSON stdout validation status.",
        "Stderr validation status.",
        "Fixture immutability status.",
        "Output file creation status.",
        "Forbidden boundary checklist.",
        "Human review decision placeholder.",
        "Next allowed phase placeholder.",
    ]
    for section in sections:
        assert section in body


def test_renderer_readiness_declares_forbidden_boundaries() -> None:
    body = read_text(DOC)
    forbidden = [
        "No renderer implementation.",
        "No report file generation.",
        "No export behavior.",
        "No CLI behavior changes.",
        "No new runtime execution.",
        "No new smoke scenario.",
        "No subprocess.",
        "No shell execution.",
        "No fixture modification.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive product traversal.",
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
    for item in forbidden:
        assert item in body


def test_controlled_fixture_integrity_remains_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_prior_contract_declares_visible_report_contract_values() -> None:
    body = read_text(CONTRACT_DOC)
    required = [
        "Smoke status: PASS.",
        "Fixture id: controlled_plain_text_marker_v1.",
        f"Allowed relative path: {ALLOWED_RELATIVE_PATH}.",
        "Byte size: 239.",
        f"SHA256 digest: {EXPECTED_SHA256}.",
        "Human review decision placeholder: PENDING_HUMAN_REVIEW.",
    ]
    for item in required:
        assert item in body


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


def test_renderer_readiness_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
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
