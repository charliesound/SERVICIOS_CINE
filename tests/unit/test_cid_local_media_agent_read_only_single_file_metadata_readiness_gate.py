from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_readiness_gate_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_READINESS_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_CONTRACT_GATE_WITH_FIXTURE_BOUNDARIES"
FIXTURE_ROOT = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE_FILE = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
FIXTURE_SHA = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
FIXTURE_BYTES = "239"


def _text() -> str:
    assert DOC.exists(), f"missing readiness gate doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_readiness_gate_declares_phase_and_result_token():
    text = _text()
    assert PHASE in text
    assert RESULT in text


def test_readiness_gate_depends_on_closed_fixture_pack_creation_and_integrity():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1" in text


def test_readiness_gate_names_exact_single_fixture_target():
    text = _text()
    assert FIXTURE_ROOT in text
    assert FIXTURE_FILE in text
    assert "controlled_plain_text_marker_v1" in text
    assert text.count("fixture file:") == 1


def test_readiness_gate_records_fixture_integrity_evidence():
    text = _text()
    assert f"expected bytes: `{FIXTURE_BYTES}`" in text
    assert f"expected SHA256: `{FIXTURE_SHA}`" in text


def test_readiness_gate_freezes_decision_for_contract_gate_not_implementation():
    text = _text()
    assert DECISION in text
    assert "separate contract gate" in text
    assert "not direct implementation" in text


def test_readiness_gate_blocks_external_media_tool_execution():
    text = _text()
    assert "does not execute any external media tool" in text
    assert "execution of ffprobe" in text
    assert "execution of FFmpeg" in text


def test_readiness_gate_blocks_scanner_batch_and_recursion():
    text = _text()
    assert "scanner implementation" in text
    assert "recursive folder traversal" in text
    assert "batch media processing" in text
    assert "no-recursion policy" in text
    assert "no-batch policy" in text


def test_readiness_gate_blocks_customer_real_material_and_new_media_fixtures():
    text = _text()
    assert "customer material" in text
    assert "real production material" in text
    assert "video or audio fixture creation" in text
    assert "no-customer-material policy" in text


def test_readiness_gate_blocks_product_surface_expansion():
    text = _text()
    for forbidden_surface in [
        "SaaS integration",
        "database integration",
        "backend or frontend changes",
        "installer work",
        "pyproject or dependency changes",
        "runtime command changes",
    ]:
        assert forbidden_surface in text


def test_readiness_gate_requires_future_schema_redaction_and_failure_modes():
    text = _text()
    assert "deterministic result schema" in text
    assert "redaction policy" in text
    assert "failure mode for missing, moved, or mutated fixture files" in text


def test_readiness_gate_preserves_fixture_pack_without_mutation():
    text = _text()
    assert "no new fixture file is created by this gate" in text
    assert "no existing fixture file is modified by this gate" in text
    assert "no external tool is executed by this gate" in text


def test_readiness_gate_documents_future_safe_chain_order():
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
