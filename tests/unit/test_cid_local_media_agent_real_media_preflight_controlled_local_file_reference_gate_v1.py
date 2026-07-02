from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_local_file_reference_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_controlled_local_file_reference_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_LOCAL_FILE_REFERENCE.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_LOCAL_FILE_REFERENCE_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_controlled_reference_gate():
    text = _text()
    assert "READY_FOR_CONTROLLED_LOCAL_FILE_REFERENCE_GATE" in text


def test_target_state_prepares_operator_selection_readiness():
    text = _text()
    assert "CONTROLLED_LOCAL_FILE_REFERENCE_READY_FOR_OPERATOR_LOCAL_SELECTION_READINESS_GATE" in text


def test_gate_purpose_is_sanitized_control_record_only():
    text = _text()
    assert "This gate defines a controlled local file reference record for `operator_input_001`." in text
    assert "The reference is a sanitized control record only." in text
    assert "The reference is not a real path." in text
    assert "The reference is not a real filename." in text
    assert "The reference is not a parent folder." in text
    assert "The reference is not a filesystem pointer." in text


def test_reference_is_not_sufficient_to_touch_media():
    text = _text()
    assert "not sufficient to locate, read, open, inspect, probe, scan, decode, transcribe, thumbnail, waveform, copy, upload, or process a media file" in text


def test_source_readiness_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_LOCAL_FILE_REFERENCE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_LOCAL_FILE_REFERENCE_READINESS_GATE_V1_CLOSED" in text


def test_source_readiness_record_values_are_preserved():
    text = _text()
    required_values = [
        "controlled_local_file_reference_readiness_001",
        "operator_input_001",
        "operator_input_real_file_binding_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "ready_for_controlled_local_file_reference_gate_without_real_file_reference",
    ]
    for value in required_values:
        assert value in text


def test_controlled_local_reference_record_is_declared():
    text = _text()
    required_fields = [
        "CONTROLLED_LOCAL_REFERENCE_RECORD_ID",
        "CONTROLLED_LOCAL_REFERENCE_INPUT_RECORD_ID",
        "CONTROLLED_LOCAL_REFERENCE_SOURCE_READINESS_RECORD_ID",
        "CONTROLLED_LOCAL_REFERENCE_SOURCE_BINDING_RECORD_ID",
        "CONTROLLED_LOCAL_REFERENCE_SANITIZED_INPUT_TOKEN",
        "CONTROLLED_LOCAL_REFERENCE_TOKEN",
        "CONTROLLED_LOCAL_REFERENCE_HANDLE",
        "CONTROLLED_LOCAL_REFERENCE_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_controlled_local_reference_values_are_sanitized():
    text = _text()
    required_values = [
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "controlled_local_reference_created_without_disclosing_or_touching_real_file",
    ]
    for value in required_values:
        assert value in text


def test_no_real_path_filename_or_folder_is_recorded():
    text = _text()
    required_statuses = [
        "CONTROLLED_LOCAL_REFERENCE_REAL_PATH_STATUS",
        "CONTROLLED_LOCAL_REFERENCE_REAL_FILENAME_STATUS",
        "CONTROLLED_LOCAL_REFERENCE_PARENT_FOLDER_STATUS",
        "not_recorded",
    ]
    for status in required_statuses:
        assert status in text
    assert "No real path is recorded." in text
    assert "No real filename is recorded." in text
    assert "No parent folder is recorded." in text


def test_no_file_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "CONTROLLED_LOCAL_REFERENCE_FILE_SIZE_STATUS",
        "CONTROLLED_LOCAL_REFERENCE_TIMESTAMP_STATUS",
        "CONTROLLED_LOCAL_REFERENCE_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text
    assert "No file size is recorded." in text
    assert "No timestamps are recorded." in text
    assert "No hashes are recorded." in text


def test_no_filesystem_or_media_operations_occur():
    text = _text()
    required_statuses = [
        "CONTROLLED_LOCAL_REFERENCE_FILESYSTEM_METADATA_STATUS",
        "not_read",
        "CONTROLLED_LOCAL_REFERENCE_FILE_OPEN_STATUS",
        "not_opened",
        "CONTROLLED_LOCAL_REFERENCE_MEDIA_TOOL_STATUS",
        "not_executed",
    ]
    for status in required_statuses:
        assert status in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "CONTROLLED_LOCAL_REFERENCE_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "CONTROLLED_LOCAL_REFERENCE_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_real_file_selection_and_path_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Selecting a real file.",
        "Recording an absolute path.",
        "Recording a relative path.",
        "Recording a real filename.",
        "Recording a parent folder.",
    ]
    for item in forbidden_items:
        assert item in text


def test_file_metadata_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Recording file size.",
        "Recording file timestamps.",
        "Recording file hashes.",
        "Reading filesystem metadata.",
        "Opening a media file.",
    ]
    for item in forbidden_items:
        assert item in text


def test_media_processing_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Probing a media file.",
        "Scanning a media file.",
        "Decoding a media file.",
        "Transcribing a media file.",
        "Generating thumbnails.",
        "Generating waveforms.",
        "Executing FFmpeg.",
        "Executing ffprobe.",
        "Executing scanner logic.",
    ]
    for item in forbidden_items:
        assert item in text


def test_platform_boundaries_are_forbidden():
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


def test_next_phase_boundary_is_operator_selection_readiness_only():
    text = _text()
    assert "The next conservative phase may prepare an operator local selection readiness gate." in text
    assert "This gate does not authorize that selection." in text
    assert "This gate only prepares a sanitized controlled reference record." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This controlled local file reference gate test.",
        "The previous controlled local file reference readiness gate test.",
        "The previous real file binding gate test.",
        "The previous real file binding readiness gate test.",
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


def test_closing_state_is_ready_for_operator_selection_readiness_gate():
    text = _text()
    assert "CONTROLLED_LOCAL_FILE_REFERENCE_READY_FOR_OPERATOR_LOCAL_SELECTION_READINESS_GATE" in text
