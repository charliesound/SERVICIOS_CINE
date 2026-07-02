from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_manual_operator_confirmation_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_manual_operator_confirmation_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.MANUAL_OPERATOR_CONFIRMATION.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_MANUAL_OPERATOR_CONFIRMATION_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_execution_gate():
    text = _text()
    assert "REAL_MEDIA_PREFLIGHT_EXECUTION_BOUNDARY_READY_FOR_MANUAL_OPERATOR_CONFIRMATION_READINESS_GATE" in text


def test_target_state_is_ready_for_manual_confirmation_gate():
    text = _text()
    assert "READY_FOR_MANUAL_OPERATOR_CONFIRMATION_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This readiness gate prepares the conditions for a later manual operator confirmation gate." in text
    assert "This gate does not collect a manual operator confirmation." in text
    assert "This gate does not authorize execution." in text
    assert "This gate does not execute real media preflight." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_execution_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.EXECUTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_EXECUTION_GATE_V1_CLOSED" in text


def test_source_execution_boundary_record_values_are_preserved():
    text = _text()
    required_values = [
        "real_media_preflight_execution_boundary_001",
        "operator_input_001",
        "real_media_preflight_execution_readiness_001",
        "sanitized_selection_token_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "controlled_execution_boundary_defined_without_execution_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_manual_operator_confirmation_readiness_record_is_declared():
    text = _text()
    required_fields = [
        "MANUAL_OPERATOR_CONFIRMATION_READINESS_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_INPUT_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_EXECUTION_BOUNDARY_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_READINESS_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_TOKEN_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_TOKEN_HANDLE",
        "MANUAL_OPERATOR_CONFIRMATION_SANITIZED_SELECTION_TOKEN",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_REFERENCE_RECORD_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_REFERENCE_HANDLE",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_EVENT_ID",
        "MANUAL_OPERATOR_CONFIRMATION_SOURCE_EVENT_HANDLE",
        "MANUAL_OPERATOR_CONFIRMATION_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_manual_operator_confirmation_readiness_values_are_sanitized():
    text = _text()
    required_values = [
        "manual_operator_confirmation_readiness_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN",
        "LOCAL_REFERENCE_HANDLE_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "ready_for_manual_operator_confirmation_gate_without_confirmation_or_execution",
    ]
    for value in required_values:
        assert value in text


def test_confirmation_is_not_collected_in_this_gate():
    text = _text()
    assert "MANUAL_OPERATOR_CONFIRMATION_STATUS" in text
    assert "not_collected_in_this_gate" in text
    assert "Manual operator confirmation is not collected in this gate." in text
    assert "Collecting manual operator confirmation." in text


def test_execution_is_not_performed_in_this_gate():
    text = _text()
    assert "MANUAL_OPERATOR_CONFIRMATION_EXECUTION_STATUS" in text
    assert "not_executed_in_this_gate" in text
    assert "Execution status remains `not_executed_in_this_gate`." in text


def test_no_real_file_selection_occurs_in_this_gate():
    text = _text()
    assert "MANUAL_OPERATOR_CONFIRMATION_REAL_SELECTION_STATUS" in text
    assert "not_selected_in_this_gate" in text
    assert "No real file is selected in this gate." in text


def test_no_path_filename_or_parent_folder_is_recorded():
    text = _text()
    required_statuses = [
        "MANUAL_OPERATOR_CONFIRMATION_REAL_PATH_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_REAL_FILENAME_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_PARENT_FOLDER_STATUS",
        "not_recorded_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_file_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "MANUAL_OPERATOR_CONFIRMATION_FILE_SIZE_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_TIMESTAMP_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text


def test_no_filesystem_or_file_open_operations_occur():
    text = _text()
    required_statuses = [
        "MANUAL_OPERATOR_CONFIRMATION_FILESYSTEM_METADATA_STATUS",
        "not_read_in_this_gate",
        "MANUAL_OPERATOR_CONFIRMATION_FILE_OPEN_STATUS",
        "not_opened_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_media_tools_are_executed():
    text = _text()
    required_statuses = [
        "MANUAL_OPERATOR_CONFIRMATION_FFMPEG_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_FFPROBE_STATUS",
        "MANUAL_OPERATOR_CONFIRMATION_SCANNER_STATUS",
        "not_executed_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text
    assert "FFmpeg is not executed in this gate." in text
    assert "ffprobe is not executed in this gate." in text
    assert "Scanner logic is not executed in this gate." in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "MANUAL_OPERATOR_CONFIRMATION_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "MANUAL_OPERATOR_CONFIRMATION_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`manual_operator_confirmation_readiness_001` is created as a readiness record.",
        "`real_media_preflight_execution_boundary_001` remains the source execution boundary record.",
        "`real_media_preflight_execution_readiness_001` remains the source execution readiness record.",
        "`sanitized_selection_token_001` remains the source token record.",
        "`SANITIZED_SELECTION_TOKEN_HANDLE_001` remains a non-filesystem token handle.",
        "`REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN` remains the sanitized selection token.",
        "`controlled_local_file_reference_001` remains the source controlled local reference.",
        "`LOCAL_REFERENCE_HANDLE_001` remains a non-filesystem reference handle.",
        "`operator_local_selection_event_001` remains the source operator local selection event.",
        "`OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001` remains a non-filesystem event handle.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_later_manual_confirmation_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must require explicit operator acknowledgement.",
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must use the sanitized selection token as the control input.",
        "It must not commit an absolute path.",
        "It must not commit a relative path.",
        "It must not commit a sensitive filename.",
        "It must not commit parent folder names.",
        "It must not commit file size.",
        "It must not commit timestamps.",
        "It must not commit hashes.",
        "It must not create SaaS coupling.",
        "It must remain test-covered.",
        "It must pass repository safety guards before commit.",
    ]
    for constraint in constraints:
        assert constraint in text


def test_confirmation_execution_and_file_selection_are_forbidden():
    text = _text()
    forbidden_items = [
        "Collecting manual operator confirmation.",
        "Executing real media preflight.",
        "Selecting a real file.",
        "Selecting a file through a UI.",
        "Selecting a file through a CLI argument.",
        "Resolving a real filesystem path.",
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


def test_next_phase_boundary_is_manual_confirmation_gate_only():
    text = _text()
    assert "The next conservative phase may define a manual operator confirmation gate." in text
    assert "This readiness gate does not authorize confirmation collection." in text
    assert "This readiness gate does not authorize execution." in text
    assert "This readiness gate does not authorize real file selection." in text
    assert "This readiness gate does not authorize filesystem access." in text
    assert "This readiness gate only prepares the conditions for a later manual operator confirmation gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This manual operator confirmation readiness gate test.",
        "The previous real media preflight execution gate test.",
        "The previous real media preflight execution readiness gate test.",
        "The previous sanitized selection token gate test.",
        "The previous sanitized selection token readiness gate test.",
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


def test_closing_state_is_ready_for_manual_operator_confirmation_gate():
    text = _text()
    assert "READY_FOR_MANUAL_OPERATOR_CONFIRMATION_GATE" in text
