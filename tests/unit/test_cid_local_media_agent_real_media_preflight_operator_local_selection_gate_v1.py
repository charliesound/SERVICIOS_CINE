from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_local_selection_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_operator_local_selection_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_LOCAL_SELECTION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_LOCAL_SELECTION_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_operator_selection_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_LOCAL_SELECTION_GATE" in text


def test_target_state_prepares_sanitized_selection_token_gate():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_READY_FOR_SANITIZED_SELECTION_TOKEN_GATE" in text


def test_gate_purpose_is_sanitized_control_event_only():
    text = _text()
    assert "This gate defines a controlled operator local selection event for `operator_input_001`." in text
    assert "The event is a sanitized control event only." in text
    assert "The event does not perform a real file selection." in text
    assert "The event does not select a real file." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_operator_local_selection_readiness_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_LOCAL_SELECTION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_LOCAL_SELECTION_READINESS_GATE_V1_CLOSED" in text


def test_source_operator_local_selection_readiness_record_values_are_preserved():
    text = _text()
    required_values = [
        "operator_local_selection_readiness_001",
        "operator_input_001",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "ready_for_operator_local_selection_gate_without_real_file_selection",
    ]
    for value in required_values:
        assert value in text


def test_controlled_operator_selection_event_is_declared():
    text = _text()
    required_fields = [
        "OPERATOR_LOCAL_SELECTION_EVENT_ID",
        "OPERATOR_LOCAL_SELECTION_EVENT_INPUT_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_EVENT_SOURCE_READINESS_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_EVENT_SOURCE_REFERENCE_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_EVENT_SOURCE_REFERENCE_HANDLE",
        "OPERATOR_LOCAL_SELECTION_EVENT_SANITIZED_INPUT_TOKEN",
        "OPERATOR_LOCAL_SELECTION_EVENT_CONTROLLED_REFERENCE_TOKEN",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE",
        "OPERATOR_LOCAL_SELECTION_EVENT_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_controlled_operator_selection_event_values_are_sanitized():
    text = _text()
    required_values = [
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "operator_local_selection_event_recorded_without_real_file_selection",
    ]
    for value in required_values:
        assert value in text


def test_no_real_file_selection_occurs():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_EVENT_REAL_SELECTION_STATUS" in text
    assert "not_selected" in text
    assert "No real file is selected." in text


def test_no_path_filename_or_parent_folder_is_recorded():
    text = _text()
    required_statuses = [
        "OPERATOR_LOCAL_SELECTION_EVENT_REAL_PATH_STATUS",
        "OPERATOR_LOCAL_SELECTION_EVENT_REAL_FILENAME_STATUS",
        "OPERATOR_LOCAL_SELECTION_EVENT_PARENT_FOLDER_STATUS",
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
        "OPERATOR_LOCAL_SELECTION_EVENT_FILE_SIZE_STATUS",
        "OPERATOR_LOCAL_SELECTION_EVENT_TIMESTAMP_STATUS",
        "OPERATOR_LOCAL_SELECTION_EVENT_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text
    assert "No file size is recorded." in text
    assert "No timestamps are recorded." in text
    assert "No hashes are recorded." in text


def test_no_filesystem_or_media_operations_occur():
    text = _text()
    required_statuses = [
        "OPERATOR_LOCAL_SELECTION_EVENT_FILESYSTEM_METADATA_STATUS",
        "not_read",
        "OPERATOR_LOCAL_SELECTION_EVENT_FILE_OPEN_STATUS",
        "not_opened",
        "OPERATOR_LOCAL_SELECTION_EVENT_MEDIA_TOOL_STATUS",
        "not_executed",
    ]
    for status in required_statuses:
        assert status in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_EVENT_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "OPERATOR_LOCAL_SELECTION_EVENT_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`operator_local_selection_event_001` is created as a sanitized control event.",
        "`operator_local_selection_readiness_001` remains the source readiness record.",
        "`controlled_local_file_reference_001` remains the source controlled local reference.",
        "`LOCAL_REFERENCE_HANDLE_001` remains a non-filesystem reference handle.",
        "`OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001` is a non-filesystem event handle.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_real_file_selection_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Selecting a real file.",
        "Selecting a file through a UI.",
        "Selecting a file through a CLI argument.",
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


def test_next_phase_boundary_is_sanitized_selection_token_readiness_only():
    text = _text()
    assert "The next conservative phase may prepare a sanitized selection token readiness gate." in text
    assert "This gate does not create that token." in text
    assert "This gate does not authorize a real file selection." in text
    assert "This gate only records a sanitized operator local selection control event." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This operator local selection gate test.",
        "The previous operator local selection readiness gate test.",
        "The previous controlled local file reference gate test.",
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


def test_closing_state_is_ready_for_sanitized_selection_token_gate():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_READY_FOR_SANITIZED_SELECTION_TOKEN_GATE" in text
