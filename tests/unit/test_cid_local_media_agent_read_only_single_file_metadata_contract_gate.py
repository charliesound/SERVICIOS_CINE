from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_contract_gate_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CONTRACT.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_READINESS_GATE_WITH_FIXTURE_BOUNDARIES"
FIXTURE_ROOT = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE_FILE = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
FIXTURE_SHA = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
FIXTURE_BYTES = "239"


def _text() -> str:
    assert DOC.exists(), f"missing contract gate doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_contract_gate_declares_phase_result_and_decision():
    text = _text()
    assert PHASE in text
    assert RESULT in text
    assert DECISION in text


def test_contract_gate_depends_on_closed_creation_integrity_and_readiness_gates():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1" in text


def test_contract_gate_names_exact_fixture_boundary_once():
    text = _text()
    assert FIXTURE_ROOT in text
    assert FIXTURE_FILE in text
    assert "controlled_plain_text_marker_v1" in text
    assert text.count("fixture file:") == 1


def test_contract_gate_records_integrity_requirements():
    text = _text()
    assert f"expected bytes: `{FIXTURE_BYTES}`" in text
    assert f"expected SHA256: `{FIXTURE_SHA}`" in text
    assert "expected_sha256" in text
    assert "expected_bytes" in text


def test_contract_gate_defines_required_input_fields():
    text = _text()
    for required_field in [
        "fixture_root",
        "target_file",
        "expected_fixture_id",
        "expected_bytes",
        "expected_sha256",
        "mode",
        "read_only_single_file_metadata",
    ]:
        assert required_field in text


def test_contract_gate_defines_deterministic_output_fields():
    text = _text()
    for output_field in [
        "status",
        "fixture_id",
        "target_file",
        "bytes",
        "sha256",
        "read_only",
        "scanner_used",
        "external_media_tool_used",
        "fixture_mutated",
        "customer_material_used",
        "metadata",
        "errors",
    ]:
        assert output_field in text
    assert "READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_VERIFIED" in text


def test_contract_gate_limits_metadata_to_safe_file_level_metadata():
    text = _text()
    assert "safe file-level metadata" in text
    assert "file name" in text
    assert "relative path under fixture root" in text
    assert "Media-stream metadata" in text
    assert "codec metadata" in text
    assert "container metadata" in text


def test_contract_gate_declares_failure_modes():
    text = _text()
    for failure_mode in [
        "TARGET_FILE_MISSING",
        "TARGET_FILE_NOT_A_FILE",
        "TARGET_FILE_OUTSIDE_FIXTURE_ROOT",
        "TARGET_FILE_MULTIPLE_MATCHES_FORBIDDEN",
        "TARGET_FILE_BYTES_MISMATCH",
        "TARGET_FILE_SHA256_MISMATCH",
        "CUSTOMER_MATERIAL_FORBIDDEN",
        "REAL_PRODUCTION_MATERIAL_FORBIDDEN",
        "SCANNER_USAGE_FORBIDDEN",
        "EXTERNAL_MEDIA_TOOL_USAGE_FORBIDDEN",
        "FIXTURE_MUTATION_FORBIDDEN",
    ]:
        assert failure_mode in text


def test_contract_gate_blocks_external_media_tools_scanner_and_batch_behaviors():
    text = _text()
    assert "execution of ffprobe" in text
    assert "execution of FFmpeg" in text
    assert "scanner implementation" in text
    assert "recursive folder traversal" in text
    assert "batch media processing" in text
    assert "no-recursion policy" in text
    assert "no-batch policy" in text


def test_contract_gate_blocks_product_surface_expansion_and_fixture_mutation():
    text = _text()
    for forbidden_surface in [
        "SaaS integration",
        "database integration",
        "backend or frontend changes",
        "installer work",
        "pyproject or dependency changes",
        "runtime command changes",
        "fixture mutation",
    ]:
        assert forbidden_surface in text


def test_contract_gate_requires_safety_invariants_and_redaction_policy():
    text = _text()
    for invariant in [
        "read_only` must be `true`",
        "scanner_used` must be `false`",
        "external_media_tool_used` must be `false`",
        "fixture_mutated` must be `false`",
        "customer_material_used` must be `false`",
        "real_production_material_used` must be `false`",
        "redaction policy",
    ]:
        assert invariant in text


def test_contract_gate_documents_future_safe_chain_order():
    text = _text()
    expected_order = [
        "Read-only single-file metadata contract gate.",
        "Read-only single-file metadata implementation readiness gate.",
        "Read-only single-file metadata implementation gate on the controlled fixture only.",
        "Visible report over controlled fixture metadata.",
        "Scanner minimum limited to the controlled fixture root, only after separate gates.",
    ]
    positions = [text.index(item) for item in expected_order]
    assert positions == sorted(positions)
