from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_input_real_file_binding_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_operator_input_real_file_binding_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_REAL_FILE_BINDING.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_REAL_FILE_BINDING_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_binding_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_INPUT_REAL_FILE_BINDING_GATE" in text


def test_target_state_is_controlled_local_reference_gate():
    text = _text()
    assert "OPERATOR_INPUT_001_READY_FOR_CONTROLLED_LOCAL_FILE_REFERENCE_GATE" in text


def test_gate_purpose_defines_sanitized_binding_only():
    text = _text()
    assert "This gate defines a controlled, sanitized binding record for `operator_input_001`." in text
    assert "The binding is not a filesystem binding." in text
    assert "The binding is not a real path." in text
    assert "The binding is not a real filename." in text


def test_binding_is_not_sufficient_to_touch_media():
    text = _text()
    assert "not sufficient to locate, open, stat, decode, scan, probe, transcribe, thumbnail, waveform, copy, upload, or process any media file" in text


def test_source_readiness_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_REAL_FILE_BINDING.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_REAL_FILE_BINDING_READINESS_GATE_V1_CLOSED" in text


def test_source_materialized_input_values_are_preserved():
    text = _text()
    required_values = [
        "operator_input_materialization_001",
        "operator_input_001",
        "safe_capture_001",
        "local_single_file_candidate_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "materialized_from_sanitized_operator_capture_without_real_file_binding",
    ]
    for value in required_values:
        assert value in text


def test_controlled_binding_record_is_declared():
    text = _text()
    required_fields = [
        "BINDING_RECORD_ID",
        "BINDING_INPUT_RECORD_ID",
        "BINDING_SOURCE_MATERIALIZATION_RECORD_ID",
        "BINDING_SOURCE_READINESS_RECORD_ID",
        "BINDING_SANITIZED_INPUT_TOKEN",
        "BINDING_CONTROLLED_REFERENCE_TOKEN",
        "BINDING_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_controlled_binding_values_are_sanitized():
    text = _text()
    assert "operator_input_real_file_binding_001" in text
    assert "operator_input_real_file_binding_readiness_001" in text
    assert "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE" in text
    assert "controlled_reference_bound_without_disclosing_or_touching_real_file" in text


def test_no_path_or_filename_is_recorded():
    text = _text()
    assert "BINDING_REAL_PATH_STATUS" in text
    assert "BINDING_REAL_FILENAME_STATUS" in text
    assert "not_recorded" in text
    assert "No real path is recorded." in text
    assert "No real filename is recorded." in text


def test_no_filesystem_or_media_operation_is_performed():
    text = _text()
    assert "BINDING_FILESYSTEM_METADATA_STATUS" in text
    assert "not_read" in text
    assert "BINDING_FILE_OPEN_STATUS" in text
    assert "not_opened" in text
    assert "BINDING_MEDIA_TOOL_STATUS" in text
    assert "not_executed" in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "BINDING_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "BINDING_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_real_file_selection_remains_forbidden():
    text = _text()
    forbidden_items = [
        "Selecting a real file through a UI.",
        "Selecting a real file through a CLI argument.",
        "Recording an absolute path.",
        "Recording a relative path.",
        "Recording a real filename.",
        "Recording a parent folder.",
    ]
    for item in forbidden_items:
        assert item in text


def test_file_metadata_and_hashes_remain_forbidden():
    text = _text()
    forbidden_items = [
        "Recording file size.",
        "Recording file timestamps.",
        "Recording file hashes.",
        "Opening the file.",
    ]
    for item in forbidden_items:
        assert item in text


def test_media_processing_remains_forbidden():
    text = _text()
    forbidden_items = [
        "Probing the file.",
        "Scanning the file.",
        "Decoding the file.",
        "Transcribing the file.",
        "Generating thumbnails.",
        "Generating waveforms.",
        "Executing FFmpeg.",
        "Executing ffprobe.",
        "Executing scanner logic.",
    ]
    for item in forbidden_items:
        assert item in text


def test_platform_boundaries_remain_forbidden():
    text = _text()
    forbidden_items = [
        "Creating runtime implementation.",
        "Modifying existing CLI runtime.",
        "Touching SaaS backend.",
        "Touching SaaS frontend.",
        "Touching databases.",
        "Touching Docker.",
        "Touching Alembic.",
        "Touching Stripe.",
        "Touching AI Jobs.",
        "Touching credits or ledger.",
    ]
    for item in forbidden_items:
        assert item in text


def test_required_checks_reference_previous_gates_without_forbidden_literals():
    text = _text()
    required_checks = [
        "This binding gate test.",
        "The previous binding readiness gate test.",
        "The previous operator input materialization gate test.",
        "The previous operator input materialization readiness gate test.",
        "The previous safe operator value capture gate test.",
        "The previous safe operator value capture readiness gate test.",
        "The previous sanitized candidate input gate test.",
        "The previous sanitized single file candidate gate test.",
        "The previous real media preflight controlled execution gate test.",
        "The previous real media preflight readiness gate test.",
        "The WSL repo guard script.",
        "The PostgreSQL-only regression guard script.",
    ]
    for check in required_checks:
        assert check in text


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


def test_document_does_not_contain_runtime_invocation_patterns():
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


def test_closing_state_is_ready_for_controlled_local_file_reference_gate():
    text = _text()
    assert "OPERATOR_INPUT_001_READY_FOR_CONTROLLED_LOCAL_FILE_REFERENCE_GATE" in text
