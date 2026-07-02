from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_selection_token_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_sanitized_selection_token_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_SELECTION_TOKEN.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SANITIZED_SELECTION_TOKEN_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_operator_local_selection_gate():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_READY_FOR_SANITIZED_SELECTION_TOKEN_GATE" in text


def test_target_state_is_ready_for_sanitized_selection_token_gate():
    text = _text()
    assert "READY_FOR_SANITIZED_SELECTION_TOKEN_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This readiness gate prepares the conditions for a later sanitized selection token gate." in text
    assert "This gate does not create the final sanitized selection token." in text
    assert "This gate does not perform a real file selection." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_operator_local_selection_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_LOCAL_SELECTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_LOCAL_SELECTION_GATE_V1_CLOSED" in text


def test_source_operator_local_selection_event_values_are_preserved():
    text = _text()
    required_values = [
        "operator_local_selection_event_001",
        "operator_input_001",
        "operator_local_selection_readiness_001",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "operator_local_selection_event_recorded_without_real_file_selection",
    ]
    for value in required_values:
        assert value in text


def test_sanitized_selection_token_readiness_record_is_declared():
    text = _text()
    required_fields = [
        "SANITIZED_SELECTION_TOKEN_READINESS_RECORD_ID",
        "SANITIZED_SELECTION_TOKEN_INPUT_RECORD_ID",
        "SANITIZED_SELECTION_TOKEN_SOURCE_EVENT_ID",
        "SANITIZED_SELECTION_TOKEN_SOURCE_EVENT_HANDLE",
        "SANITIZED_SELECTION_TOKEN_SOURCE_REFERENCE_RECORD_ID",
        "SANITIZED_SELECTION_TOKEN_SOURCE_REFERENCE_HANDLE",
        "SANITIZED_SELECTION_TOKEN_SOURCE_INPUT_TOKEN",
        "SANITIZED_SELECTION_TOKEN_SOURCE_REFERENCE_TOKEN",
        "SANITIZED_SELECTION_TOKEN_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_sanitized_selection_token_readiness_values_are_sanitized():
    text = _text()
    required_values = [
        "sanitized_selection_token_readiness_001",
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "ready_for_sanitized_selection_token_gate_without_final_token_or_real_file_selection",
    ]
    for value in required_values:
        assert value in text


def test_final_token_is_not_created_in_this_gate():
    text = _text()
    assert "SANITIZED_SELECTION_TOKEN_FINAL_TOKEN_STATUS" in text
    assert "not_created_in_this_gate" in text
    assert "No final sanitized selection token is created in this gate." in text


def test_no_real_file_selection_occurs_in_this_gate():
    text = _text()
    assert "SANITIZED_SELECTION_TOKEN_REAL_SELECTION_STATUS" in text
    assert "not_selected_in_this_gate" in text
    assert "No real file is selected in this gate." in text


def test_no_path_filename_or_parent_folder_is_recorded():
    text = _text()
    required_statuses = [
        "SANITIZED_SELECTION_TOKEN_REAL_PATH_STATUS",
        "SANITIZED_SELECTION_TOKEN_REAL_FILENAME_STATUS",
        "SANITIZED_SELECTION_TOKEN_PARENT_FOLDER_STATUS",
        "not_recorded_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_file_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "SANITIZED_SELECTION_TOKEN_FILE_SIZE_STATUS",
        "SANITIZED_SELECTION_TOKEN_TIMESTAMP_STATUS",
        "SANITIZED_SELECTION_TOKEN_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text


def test_no_filesystem_or_media_operations_occur():
    text = _text()
    required_statuses = [
        "SANITIZED_SELECTION_TOKEN_FILESYSTEM_METADATA_STATUS",
        "not_read_in_this_gate",
        "SANITIZED_SELECTION_TOKEN_FILE_OPEN_STATUS",
        "not_opened_in_this_gate",
        "SANITIZED_SELECTION_TOKEN_MEDIA_TOOL_STATUS",
        "not_executed_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_runtime_is_created():
    text = _text()
    assert "SANITIZED_SELECTION_TOKEN_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "No runtime is created in this gate." in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`operator_local_selection_event_001` remains the source operator local selection event.",
        "`OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001` remains a non-filesystem event handle.",
        "`controlled_local_file_reference_001` remains the source controlled local reference.",
        "`LOCAL_REFERENCE_HANDLE_001` remains a non-filesystem reference handle.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_future_token_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must create only a sanitized token.",
        "It must not commit an absolute path.",
        "It must not commit a relative path.",
        "It must not commit a sensitive filename.",
        "It must not commit parent folder names.",
        "It must not commit file size.",
        "It must not commit timestamps.",
        "It must not commit hashes.",
        "It must not read filesystem metadata.",
        "It must not open media files.",
        "It must not run media tools.",
        "It must not create runtime implementation.",
        "It must not create SaaS coupling.",
        "It must remain test-covered.",
        "It must pass repository safety guards before commit.",
    ]
    for constraint in constraints:
        assert constraint in text


def test_real_file_selection_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Creating the final sanitized selection token.",
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


def test_next_phase_boundary_is_sanitized_selection_token_gate_only():
    text = _text()
    assert "The next conservative phase may define a sanitized selection token gate." in text
    assert "This readiness gate does not create that final token." in text
    assert "This readiness gate does not authorize a real file selection." in text
    assert "This readiness gate only prepares the conditions for that later controlled token gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This sanitized selection token readiness gate test.",
        "The previous operator local selection gate test.",
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
    assert "READY_FOR_SANITIZED_SELECTION_TOKEN_GATE" in text
