from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_implementation_readiness_gate_v1.md"
CLI_CONTRACT_DOC = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate_v1.md"
IMPLEMENTATION = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
FUTURE_CLI = REPO_ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.IMPLEMENTATION.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_READINESS_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_ISOLATED_READ_ONLY_SINGLE_FILE_METADATA_CLI_IMPLEMENTATION_GATE_WITHOUT_PYPROJECT_REGISTRATION"
ENTRYPOINT = "cid-local-media-agent-read-only-single-file-metadata"
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
EXPECTED_FIXTURE = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"


def _doc() -> str:
    assert DOC.is_file(), f"missing readiness doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_phase_and_result_tokens_are_exact():
    text = _doc()
    assert PHASE in text
    assert RESULT in text
    assert DECISION in text


def test_required_predecessor_cli_contract_and_implementation_exist():
    assert CLI_CONTRACT_DOC.is_file()
    assert IMPLEMENTATION.is_file()
    assert "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTRACT.GATE.V1" in CLI_CONTRACT_DOC.read_text(encoding="utf-8")


def test_future_entrypoint_is_documented_but_not_registered_here():
    text = _doc()
    assert ENTRYPOINT in text
    assert "register console scripts" in text
    assert "modify `pyproject.toml`" in text


def test_future_cli_file_is_documented_but_not_created_by_readiness_gate():
    text = _doc()
    assert "scripts/local_media_agent/read_only_single_file_metadata_cli.py" in text
    assert "must not create" in text
    assert not FUTURE_CLI.exists()


def test_allowed_arguments_match_cli_contract():
    text = _doc()
    for arg in ["--target-path", "--fixture-root", "--expected-sha256", "--expected-bytes", "--result-json"]:
        assert arg in text
    assert "--scan-root" not in text
    assert "--input-folder" not in text


def test_success_and_rejection_exit_codes_are_frozen():
    text = _doc()
    assert "Exit code `0` for success" in text
    assert "Exit code `2` for deterministic validation rejection" in text
    assert "READ_ONLY_SINGLE_FILE_METADATA_COLLECTED" in text


def test_fixture_boundary_and_identity_are_preserved():
    text = _doc()
    assert EXPECTED_FIXTURE in text
    assert "expected bytes: `239`" in text
    assert EXPECTED_SHA256 in text


def test_no_external_media_tools_scanner_batch_or_recursion_are_authorized():
    text = _doc().lower()
    assert "call external media tools" in text
    assert "create scanner behavior" in text
    assert "create batch behavior" in text
    assert "create recursive traversal" in text
    assert "scan folders" in text
    assert "recurse" in text


def test_no_product_packaging_or_console_script_registration_is_authorized():
    text = _doc().lower()
    assert "modify `pyproject.toml`" in text
    assert "register console scripts" in text
    assert "create installation metadata" in text
    assert "not registered" in text


def test_no_real_or_customer_material_is_authorized():
    text = _doc().lower()
    assert "read real material" in text
    assert "read customer material" in text
    assert "touch real or customer material" in text


def test_no_fixture_or_existing_implementation_modification_is_authorized():
    text = _doc()
    assert "modify `scripts/local_media_agent/read_only_single_file_metadata.py`" in text
    assert "modify fixture files" in text
    assert "The implementation script already exists and remains unchanged by this gate" in text


def test_next_step_is_isolated_cli_implementation_only():
    text = _doc()
    assert "the only authorized next step is a separate isolated CLI implementation gate" in text
    assert "no packaging registration" in text
    forbidden_surface_terms = ["backend", "frontend", "installer", "database", "SaaS"]
    for term in forbidden_surface_terms:
        assert term in text
