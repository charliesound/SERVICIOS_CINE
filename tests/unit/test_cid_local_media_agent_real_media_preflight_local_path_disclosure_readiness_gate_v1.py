from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_local_path_disclosure_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_local_path_disclosure_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.LOCAL_PATH_DISCLOSURE.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_LOCAL_PATH_DISCLOSURE_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_controlled_real_file_selection_gate():
    text = _text()
    assert "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_READY_FOR_LOCAL_PATH_DISCLOSURE_READINESS_GATE" in text


def test_target_state_is_ready_for_local_path_disclosure_gate():
    text = _text()
    assert "READY_FOR_LOCAL_PATH_DISCLOSURE_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This readiness gate prepares the conditions for a later local path disclosure gate." in text
    assert "This gate does not disclose a local filesystem path." in text
    assert "This gate does not record a real path." in text
    assert "This gate does not execute real media preflight." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_controlled_real_file_selection_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_REAL_FILE_SELECTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_REAL_FILE_SELECTION_GATE_V1_CLOSED" in text


def test_source_selection_boundary_record_values_are_preserved():
    text = _text()
    required_values = [
        "controlled_real_file_selection_boundary_001",
        "operator_input_001",
        "controlled_real_file_selection_readiness_001",
        "manual_operator_confirmation_001",
        "MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        "REDACTED_MANUAL_OPERATOR_ACKNOWLEDGEMENT_FOR_NEXT_CONTROLLED_STEP",
        "sanitized_selection_token_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "controlled_real_file_selection_boundary_defined_without_path_disclosure_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_local_path_disclosure_readiness_record_is_declared():
    text = _text()
    required_fields = [
        "LOCAL_PATH_DISCLOSURE_READINESS_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_INPUT_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_SELECTION_BOUNDARY_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_SELECTION_BOUNDARY_HANDLE",
        "LOCAL_PATH_DISCLOSURE_SOURCE_CONFIRMATION_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_CONFIRMATION_HANDLE",
        "LOCAL_PATH_DISCLOSURE_SOURCE_CONFIRMATION_VALUE",
        "LOCAL_PATH_DISCLOSURE_SOURCE_TOKEN_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_TOKEN_HANDLE",
        "LOCAL_PATH_DISCLOSURE_SANITIZED_SELECTION_TOKEN",
        "LOCAL_PATH_DISCLOSURE_SOURCE_REFERENCE_RECORD_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_REFERENCE_HANDLE",
        "LOCAL_PATH_DISCLOSURE_SOURCE_EVENT_ID",
        "LOCAL_PATH_DISCLOSURE_SOURCE_EVENT_HANDLE",
        "LOCAL_PATH_DISCLOSURE_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_local_path_disclosure_readiness_values_are_sanitized():
    text = _text()
    required_values = [
        "local_path_disclosure_readiness_001",
        "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001",
        "MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "ready_for_local_path_disclosure_gate_without_path_disclosure_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_readiness_status_is_ready_for_local_path_disclosure_gate():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_READINESS_STATUS" in text
    assert "ready_for_local_path_disclosure_gate" in text
    assert "The readiness status is `ready_for_local_path_disclosure_gate`." in text


def test_local_path_is_not_disclosed_in_this_gate():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_DISCLOSURE_STATUS" in text
    assert "not_disclosed_in_this_gate" in text
    assert "Local path disclosure is not performed in this gate." in text


def test_no_real_file_selection_occurs_in_this_gate():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_REAL_SELECTION_STATUS" in text
    assert "not_selected_in_this_gate" in text
    assert "No real file is selected in this gate." in text


def test_no_real_path_is_resolved_or_recorded():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_REAL_PATH_STATUS" in text
    assert "not_resolved_or_recorded_in_this_gate" in text
    assert "No real path is resolved or recorded in this gate." in text


def test_no_absolute_or_relative_path_is_recorded():
    text = _text()
    required_statuses = [
        "LOCAL_PATH_DISCLOSURE_ABSOLUTE_PATH_STATUS",
        "LOCAL_PATH_DISCLOSURE_RELATIVE_PATH_STATUS",
        "not_recorded_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text
    assert "No absolute path is recorded in this gate." in text
    assert "No relative path is recorded in this gate." in text


def test_no_filename_or_parent_folder_is_recorded():
    text = _text()
    required_statuses = [
        "LOCAL_PATH_DISCLOSURE_REAL_FILENAME_STATUS",
        "LOCAL_PATH_DISCLOSURE_PARENT_FOLDER_STATUS",
        "not_recorded_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_file_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "LOCAL_PATH_DISCLOSURE_FILE_SIZE_STATUS",
        "LOCAL_PATH_DISCLOSURE_TIMESTAMP_STATUS",
        "LOCAL_PATH_DISCLOSURE_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text


def test_no_filesystem_or_file_open_operations_occur():
    text = _text()
    required_statuses = [
        "LOCAL_PATH_DISCLOSURE_FILESYSTEM_METADATA_STATUS",
        "not_read_in_this_gate",
        "LOCAL_PATH_DISCLOSURE_FILE_OPEN_STATUS",
        "not_opened_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_execution_or_media_tools_are_run():
    text = _text()
    required_statuses = [
        "LOCAL_PATH_DISCLOSURE_EXECUTION_STATUS",
        "LOCAL_PATH_DISCLOSURE_FFMPEG_STATUS",
        "LOCAL_PATH_DISCLOSURE_FFPROBE_STATUS",
        "LOCAL_PATH_DISCLOSURE_SCANNER_STATUS",
        "not_executed_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text
    assert "Real media preflight is not executed in this gate." in text
    assert "FFmpeg is not executed in this gate." in text
    assert "ffprobe is not executed in this gate." in text
    assert "Scanner logic is not executed in this gate." in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "LOCAL_PATH_DISCLOSURE_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`local_path_disclosure_readiness_001` is created as a readiness record.",
        "`controlled_real_file_selection_boundary_001` remains the source selection boundary record.",
        "`CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001` remains a non-filesystem boundary handle.",
        "`manual_operator_confirmation_001` remains the source confirmation record.",
        "`MANUAL_OPERATOR_CONFIRMATION_HANDLE_001` remains a non-filesystem confirmation handle.",
        "`REDACTED_MANUAL_OPERATOR_ACKNOWLEDGEMENT_FOR_NEXT_CONTROLLED_STEP` remains the sanitized acknowledgement value.",
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


def test_later_local_path_disclosure_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must use the sanitized selection token as the control input.",
        "It must use the manual confirmation handle as a control prerequisite.",
        "It must use the controlled real file selection boundary handle as a control prerequisite.",
        "It must disclose only to the local operator context.",
        "It must not commit the local path to git.",
        "It must not write the local path to product documentation.",
        "It must not write the local path to tests.",
        "It must not expose a sensitive filename in committed artifacts.",
        "It must not expose parent folder names in committed artifacts.",
        "It must not commit file size.",
        "It must not commit timestamps.",
        "It must not commit hashes.",
        "It must not execute real media preflight.",
        "It must not run FFmpeg.",
        "It must not run ffprobe.",
        "It must not run scanner logic.",
        "It must not create SaaS coupling.",
        "It must remain test-covered.",
        "It must pass repository safety guards before commit.",
    ]
    for constraint in constraints:
        assert constraint in text


def test_path_disclosure_and_path_recording_are_forbidden():
    text = _text()
    forbidden_items = [
        "Disclosing a local filesystem path.",
        "Recording an absolute path.",
        "Recording a relative path.",
        "Recording a real filename.",
        "Recording a parent folder.",
    ]
    for item in forbidden_items:
        assert item in text


def test_file_selection_and_path_resolution_are_forbidden():
    text = _text()
    forbidden_items = [
        "Selecting a real file.",
        "Selecting a file through a UI.",
        "Selecting a file through a CLI argument.",
        "Resolving a real filesystem path.",
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


def test_execution_and_media_processing_actions_are_forbidden():
    text = _text()
    forbidden_items = [
        "Executing real media preflight.",
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


def test_next_phase_boundary_is_local_path_disclosure_gate_only():
    text = _text()
    assert "The next conservative phase may define a local path disclosure gate." in text
    assert "This readiness gate does not authorize local path disclosure." in text
    assert "This readiness gate does not authorize real file selection." in text
    assert "This readiness gate does not authorize path resolution." in text
    assert "This readiness gate does not authorize filesystem access." in text
    assert "This readiness gate does not authorize media execution." in text
    assert "This readiness gate only prepares the conditions for a later local path disclosure gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This local path disclosure readiness gate test.",
        "The previous controlled real file selection gate test.",
        "The previous controlled real file selection readiness gate test.",
        "The previous manual operator confirmation gate test.",
        "The previous manual operator confirmation readiness gate test.",
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


def test_closing_state_is_ready_for_local_path_disclosure_gate():
    text = _text()
    assert "READY_FOR_LOCAL_PATH_DISCLOSURE_GATE" in text
