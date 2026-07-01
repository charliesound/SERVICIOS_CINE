from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_execution_gate_v1.md"
CLI = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
TARGET = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.EXECUTION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_EXECUTION_GATE_V1_CLOSED"
BASE_HEAD = "58c2d1d2519d5cab4e832d4e62110eccd8d351fd"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-readiness-gate-v1-20260701"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fixture_digest() -> str:
    return hashlib.sha256(TARGET.read_bytes()).hexdigest()


def load_cli_module():
    spec = importlib.util.spec_from_file_location("cid_lma_read_only_single_file_metadata_cli_smoke", CLI)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cli_smoke() -> tuple[int, str, str]:
    module = load_cli_module()
    assert hasattr(module, "main")
    assert callable(module.main)

    argv = [
        "--target-path",
        str(TARGET),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--allowed-relative-path",
        ALLOWED_RELATIVE_PATH,
        "--result-json",
    ]

    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        exit_code = module.main(argv)

    return int(exit_code), stdout.getvalue(), stderr.getvalue()


def test_document_declares_phase_result_base_and_scope() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        "Controlled smoke execution gate",
        "without writing files or crossing integration boundaries",
        "No subprocess.",
        "No shell execution.",
        "No output file creation.",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
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


def test_controlled_fixture_integrity_before_smoke_execution() -> None:
    assert TARGET.exists()
    assert TARGET.is_file()
    data = TARGET.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256


def test_cli_smoke_execution_returns_visible_json_result() -> None:
    before_bytes = TARGET.read_bytes()
    before_digest = hashlib.sha256(before_bytes).hexdigest()

    exit_code, stdout, stderr = run_cli_smoke()

    after_bytes = TARGET.read_bytes()
    after_digest = hashlib.sha256(after_bytes).hexdigest()

    assert exit_code == 0
    assert stdout.strip()
    assert stderr == ""
    assert before_bytes == after_bytes
    assert before_digest == after_digest == EXPECTED_SHA256

    payload = json.loads(stdout)
    assert isinstance(payload, dict)
    payload_text = json.dumps(payload, sort_keys=True)
    assert "controlled_plain_text_marker.txt" in payload_text
    assert str(EXPECTED_BYTES) in payload_text
    assert EXPECTED_SHA256 in payload_text


def test_cli_smoke_execution_does_not_create_output_files_near_fixture() -> None:
    before = sorted(path.relative_to(FIXTURE_ROOT).as_posix() for path in FIXTURE_ROOT.rglob("*"))
    exit_code, _stdout, _stderr = run_cli_smoke()
    after = sorted(path.relative_to(FIXTURE_ROOT).as_posix() for path in FIXTURE_ROOT.rglob("*"))
    assert exit_code == 0
    assert before == after


def test_pyproject_does_not_register_cli_as_console_script() -> None:
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
