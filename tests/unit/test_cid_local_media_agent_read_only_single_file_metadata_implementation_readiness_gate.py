from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_implementation_readiness_gate_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.IMPLEMENTATION.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_READINESS_GATE_V1_CLOSED"
DECISION = "READY_FOR_SEPARATE_READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_GATE_WITH_PYTHON_STANDARD_LIBRARY_ONLY"
FIXTURE_ROOT = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE_FILE = "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt"
FIXTURE_SHA = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
FIXTURE_BYTES = "239"


def _text() -> str:
    assert DOC.exists(), f"missing implementation readiness gate doc: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_implementation_readiness_gate_declares_phase_result_and_decision():
    text = _text()
    assert PHASE in text
    assert RESULT in text
    assert DECISION in text


def test_implementation_readiness_gate_depends_on_closed_fixture_and_metadata_chain():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.CREATION.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.CONTROLLED.NON_CUSTOMER.FIXTURE.PACK.INTEGRITY.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.READINESS.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CONTRACT.GATE.V1" in text


def test_implementation_readiness_gate_names_exact_fixture_boundary():
    text = _text()
    assert FIXTURE_ROOT in text
    assert FIXTURE_FILE in text
    assert "controlled_plain_text_marker_v1" in text
    assert f"expected bytes: `{FIXTURE_BYTES}`" in text
    assert f"expected SHA256: `{FIXTURE_SHA}`" in text


def test_implementation_readiness_gate_limits_future_metadata_to_safe_file_level_fields():
    text = _text()
    for allowed in [
        "file name",
        "suffix",
        "relative path under fixture root",
        "byte size",
        "SHA256",
        "deterministic status",
        "deterministic errors",
        "safety flags",
    ]:
        assert allowed in text


def test_implementation_readiness_gate_blocks_media_stream_interpretation():
    text = _text()
    for blocked in [
        "codec",
        "container",
        "duration",
        "frame rate",
        "audio stream",
        "video stream",
        "timecode",
        "waveform",
        "subtitle",
        "transcript",
        "thumbnail",
        "editorial metadata",
    ]:
        assert blocked in text


def test_implementation_readiness_gate_defines_allowed_future_surface():
    text = _text()
    assert "one isolated Python standard library module" in text
    assert "one focused unit test file" in text
    assert "one closure document" in text
    assert "must not expose a new installed command" in text
    assert "must not modify packaging" in text
    assert "must not integrate with any product surface" in text


def test_implementation_readiness_gate_requires_structured_input_and_integrity_validation():
    text = _text()
    for required in [
        "accept structured input",
        "fixture_root",
        "target_file",
        "expected_fixture_id",
        "expected_bytes",
        "expected_sha256",
        "compute SHA256 using Python standard library only",
        "redact private absolute paths",
        "return relative paths under fixture root",
    ]:
        assert required in text


def test_implementation_readiness_gate_requires_safety_flags():
    text = _text()
    for invariant in [
        "read_only` must be `true`",
        "scanner_used` must be `false`",
        "external_media_tool_used` must be `false`",
        "subprocess_used` must be `false`",
        "shell_used` must be `false`",
        "fixture_mutated` must be `false`",
        "customer_material_used` must be `false`",
        "real_production_material_used` must be `false`",
    ]:
        assert invariant in text
    assert "READ_ONLY_SINGLE_FILE_METADATA_VERIFIED" in text


def test_implementation_readiness_gate_preserves_failure_modes():
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


def test_implementation_readiness_gate_forbids_external_tools_runtime_and_product_expansion():
    text = _text()
    for forbidden in [
        "implementation code",
        "installed command exposure",
        "execution of ffprobe",
        "execution of FFmpeg",
        "subprocess usage",
        "shell execution",
        "scanner implementation",
        "recursive folder traversal",
        "glob expansion",
        "batch media processing",
        "fixture mutation",
        "new fixture creation",
        "customer material",
        "real production material",
        "SaaS integration",
        "database integration",
        "backend or frontend changes",
        "installer work",
        "pyproject or dependency changes",
        "runtime command changes",
    ]:
        assert forbidden in text


def test_implementation_readiness_gate_documents_readiness_constraints():
    text = _text()
    for constraint in [
        "single-file only",
        "fixture-bound only",
        "read-only only",
        "Python standard library only",
        "no scanner",
        "no external media tool",
        "no command exposure",
        "no product integration",
    ]:
        assert constraint in text


def test_implementation_readiness_gate_documents_future_safe_chain_order():
    text = _text()
    expected_order = [
        "Read-only single-file metadata implementation readiness gate.",
        "Read-only single-file metadata implementation gate using Python standard library only.",
        "Read-only single-file metadata implementation QA gate.",
        "Visible report over controlled fixture metadata.",
        "Scanner minimum limited to the controlled fixture root, only after separate gates.",
    ]
    positions = [text.index(item) for item in expected_order]
    assert positions == sorted(positions)
