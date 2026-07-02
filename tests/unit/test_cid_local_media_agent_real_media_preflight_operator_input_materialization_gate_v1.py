from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_input_materialization_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_operator_input_materialization_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_MATERIALIZATION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_MATERIALIZATION_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE" in text


def test_source_safe_capture_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SAFE_OPERATOR_VALUE_CAPTURE.GATE.V1" in text
    assert "SAFE_OPERATOR_VALUE_CAPTURE_ACCEPTED_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE" in text


def test_sanitized_source_values_are_preserved():
    text = _text()
    required_values = [
        "safe_capture_001",
        "operator_input_001",
        "local_single_file_candidate_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "accepted_for_operator_input_materialization_gate",
    ]
    for value in required_values:
        assert value in text


def test_materialization_record_is_declared():
    text = _text()
    assert "operator_input_materialization_001" in text
    assert "MATERIALIZED_INPUT_RECORD_ID" in text
    assert "SOURCE_CAPTURE_RECORD_ID" in text
    assert "SOURCE_SELECTION_ID" in text


def test_materialized_values_remain_sanitized_only():
    text = _text()
    assert "MATERIALIZED_SANITIZED_INPUT_TOKEN" in text
    assert "REDACTED_LOCAL_SINGLE_VIDEO_FILE" in text
    assert "MATERIALIZED_GENERIC_FILE_CATEGORY" in text
    assert "generic_video_file" in text


def test_no_real_file_binding_is_recorded():
    text = _text()
    assert "no_real_file_selected" in text
    assert "no_path_recorded" in text
    assert "no_filename_recorded" in text
    assert "materialized_from_sanitized_operator_capture_without_real_file_binding" in text


def test_runtime_remains_forbidden():
    text = _text()
    assert "no_runtime_created" in text
    assert "no_execution" in text
    assert "No implementation runtime is created by this gate." in text
    assert "No CLI runtime is modified by this gate." in text


def test_media_tool_execution_remains_forbidden():
    text = _text()
    forbidden_intents = [
        "FFmpeg execution",
        "ffprobe execution",
        "Scanner execution",
        "Media decoding",
        "Media transcription",
    ]
    for intent in forbidden_intents:
        assert intent in text


def test_sensitive_file_data_remains_forbidden():
    text = _text()
    assert "Real file selection" in text
    assert "Real filename recording" in text
    assert "Absolute path recording" in text
    assert "File stat/open operations" in text


def test_saas_and_database_boundaries_remain_forbidden():
    text = _text()
    forbidden_boundaries = [
        "SaaS backend integration",
        "SaaS frontend integration",
        "Database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "Credits or ledger changes",
    ]
    for boundary in forbidden_boundaries:
        assert boundary in text


def test_closing_state_is_non_runtime_materialized_state():
    text = _text()
    assert "OPERATOR_INPUT_001_MATERIALIZED_FROM_SANITIZED_VALUES_WITHOUT_REAL_FILE_BINDING" in text


def test_document_does_not_contain_windows_or_mount_paths():
    text = _text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in text


def test_document_does_not_create_runtime_or_process_invocation_patterns():
    text = _text()
    forbidden_runtime_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "Path.stat(",
        ".stat()",
        "open(",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_runtime_patterns:
        assert pattern not in text
