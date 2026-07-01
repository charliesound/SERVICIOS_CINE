from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate_v1.md"
IMPLEMENTATION = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
CLI_READINESS_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_readiness_gate_v1.md"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTRACT_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_READINESS_GATE_WITH_ISOLATED_ENTRYPOINT_CONTRACT"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.READINESS.GATE.V1"
ENTRYPOINT = "cid-local-media-agent-read-only-single-file-metadata"
FIXTURE_PATH = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
EXPECTED_BYTES = "239"


def _doc() -> str:
    assert DOC.is_file(), f"Missing contract doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_contract_document_exists_and_declares_phase_result_and_decision():
    text = _doc()
    assert PHASE in text
    assert RESULT in text
    assert DECISION in text
    assert NEXT_PHASE in text


def test_contract_is_documentation_and_test_only_scope():
    text = _doc()
    assert "Documentation and test only" in text
    assert "does not create the command" in text
    assert "does not register any console script" in text
    assert "does not change packaging configuration" in text


def test_contract_depends_on_closed_readiness_and_qa_gates():
    text = _doc()
    required = [
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_READINESS_GATE_V1_CLOSED",
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_QA_GATE_V1_CLOSED",
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_GATE_V1_CLOSED",
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_V1_CLOSED",
        "LOCAL_MEDIA_AGENT_CONTROLLED_NON_CUSTOMER_FIXTURE_PACK_INTEGRITY_QA_GATE_V1_CLOSED",
    ]
    for token in required:
        assert token in text
    assert CLI_READINESS_DOC.is_file()


def test_future_entrypoint_is_contractual_placeholder_only():
    text = _doc()
    assert ENTRYPOINT in text
    assert "contractual only" in text
    assert "must not be registered" in text


def test_fixture_boundary_identity_is_exact():
    text = _doc()
    assert FIXTURE_PATH in text
    assert f"bytes: `{EXPECTED_BYTES}`" in text
    assert f"sha256: `{EXPECTED_SHA256}`" in text
    assert "allowed relative path: `media/controlled_plain_text_marker.txt`" in text


def test_allowed_arguments_are_limited_to_contract_surface():
    text = _doc()
    for arg in ["--target-path", "--fixture-root", "--expected-sha256", "--expected-bytes", "--result-json"]:
        assert arg in text
    assert "No other operational argument is approved" in text


def test_json_success_output_contract_is_complete_and_parseable_by_design():
    text = _doc()
    for token in [
        "ok: true",
        "status: READ_ONLY_SINGLE_FILE_METADATA_COLLECTED",
        "mode: READ_ONLY_SINGLE_FILE_METADATA",
        "target.file_name",
        "target.extension",
        "target.relative_path",
        "target.redacted_path",
        "target.bytes",
        "target.sha256",
        "target.is_file",
    ]:
        assert token in text


def test_safety_flags_are_required_in_json_success():
    text = _doc()
    for token in [
        "safety.python_standard_library_only: true",
        "safety.external_media_tools_used: false",
        "safety.scanner_used: false",
        "safety.batch_used: false",
        "safety.recursion_used: false",
    ]:
        assert token in text


def test_plain_output_and_exit_code_contract_are_deterministic():
    text = _doc()
    assert "READ_ONLY_SINGLE_FILE_METADATA_COLLECTED" in text
    assert "Plain output must not print absolute local paths" in text
    assert "exit code `0`: success" in text
    assert "exit code `2`: deterministic validation rejection" in text


def test_rejection_reasons_are_complete_and_deterministic():
    text = _doc()
    for reason in [
        "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT",
        "TARGET_RELATIVE_PATH_NOT_ALLOWED",
        "TARGET_IS_SYMLINK",
        "TARGET_NOT_FOUND",
        "TARGET_BYTES_MISMATCH",
        "TARGET_SHA256_MISMATCH",
    ]:
        assert reason in text
    assert "Every rejection response must avoid leaking private absolute paths" in text


def test_path_redaction_contract_is_present():
    text = _doc()
    assert "<CONTROLLED_FIXTURE_ROOT>/media/controlled_plain_text_marker.txt" in text
    assert "must not print the absolute repository path" in text
    assert "user home path" in text
    assert "temp extraction path" in text


def test_prohibitions_and_stage_scope_remain_strict():
    text = _doc()
    for item in [
        "batch mode",
        "recursive traversal",
        "scanner integration",
        "ffprobe execution",
        "FFmpeg execution",
        "external media tool execution",
        "real media processing",
        "customer material",
        "fixture modification",
        "packaging registration",
        "console script registration",
        "installer work",
        "SaaS integration",
        "backend integration",
        "frontend integration",
    ]:
        assert item in text
    assert "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py" in text
    assert IMPLEMENTATION.is_file()
