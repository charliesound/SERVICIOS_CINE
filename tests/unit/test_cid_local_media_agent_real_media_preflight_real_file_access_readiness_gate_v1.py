from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_real_file_access_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_real_file_access_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.REAL_FILE_ACCESS.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_REAL_FILE_ACCESS_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_local_path_disclosure_gate():
    text = _text()
    assert "LOCAL_PATH_DISCLOSURE_BOUNDARY_READY_FOR_REAL_FILE_ACCESS_READINESS_GATE" in text


def test_target_state_is_ready_for_real_file_access_gate():
    text = _text()
    assert "READY_FOR_REAL_FILE_ACCESS_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This readiness gate prepares the conditions for a later controlled real file access gate." in text
    assert "This gate does not access a real file." in text
    assert "This gate does not perform filesystem stat operations." in text
    assert "This gate does not open a media file." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_local_path_disclosure_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.LOCAL_PATH_DISCLOSURE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_LOCAL_PATH_DISCLOSURE_GATE_V1_CLOSED" in text


def test_source_local_path_disclosure_boundary_record_values_are_preserved():
    text = _text()
    required_values = [
        "local_path_disclosure_boundary_001",
        "operator_input_001",
        "local_path_disclosure_readiness_001",
        "controlled_real_file_selection_boundary_001",
        "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001",
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
        "LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "local_path_disclosure_boundary_defined_without_committed_path_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_real_file_access_readiness_record_is_declared():
    text = _text()
    required_fields = [
        "REAL_FILE_ACCESS_READINESS_RECORD_ID",
        "REAL_FILE_ACCESS_INPUT_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE",
        "REAL_FILE_ACCESS_SOURCE_SELECTION_BOUNDARY_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_SELECTION_BOUNDARY_HANDLE",
        "REAL_FILE_ACCESS_SOURCE_CONFIRMATION_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_CONFIRMATION_HANDLE",
        "REAL_FILE_ACCESS_SOURCE_CONFIRMATION_VALUE",
        "REAL_FILE_ACCESS_SOURCE_TOKEN_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_TOKEN_HANDLE",
        "REAL_FILE_ACCESS_SANITIZED_SELECTION_TOKEN",
        "REAL_FILE_ACCESS_SOURCE_REFERENCE_RECORD_ID",
        "REAL_FILE_ACCESS_SOURCE_REFERENCE_HANDLE",
        "REAL_FILE_ACCESS_SOURCE_EVENT_ID",
        "REAL_FILE_ACCESS_SOURCE_EVENT_HANDLE",
        "REAL_FILE_ACCESS_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_real_file_access_readiness_values_are_sanitized():
    text = _text()
    required_values = [
        "real_file_access_readiness_001",
        "LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001",
        "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001",
        "MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "ready_for_real_file_access_gate_without_file_access_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_readiness_status_is_ready_for_real_file_access_gate():
    text = _text()
    assert "REAL_FILE_ACCESS_READINESS_STATUS" in text
    assert "ready_for_real_file_access_gate" in text
    assert "The readiness status is `ready_for_real_file_access_gate`." in text


def test_no_real_file_access_occurs_in_this_gate():
    text = _text()
    assert "REAL_FILE_ACCESS_ACCESS_STATUS" in text
    assert "not_accessed_in_this_gate" in text
    assert "No real file is accessed in this gate." in text


def test_no_stat_operation_occurs_in_this_gate():
    text = _text()
    assert "REAL_FILE_ACCESS_STAT_STATUS" in text
    assert "not_performed_in_this_gate" in text
    assert "No filesystem stat operation is performed in this gate." in text


def test_no_media_file_is_opened_in_this_gate():
    text = _text()
    assert "REAL_FILE_ACCESS_FILE_OPEN_STATUS" in text
    assert "not_opened_in_this_gate" in text
    assert "No media file is opened in this gate." in text


def test_no_file_bytes_or_filesystem_metadata_are_read():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_FILE_BYTES_STATUS",
        "REAL_FILE_ACCESS_FILESYSTEM_METADATA_STATUS",
        "not_read_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text
    assert "No file bytes are read in this gate." in text
    assert "No filesystem metadata is read in this gate." in text


def test_no_local_path_is_committed_or_recorded_in_artifacts():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_REAL_PATH_STATUS",
        "REAL_FILE_ACCESS_ABSOLUTE_PATH_STATUS",
        "REAL_FILE_ACCESS_RELATIVE_PATH_STATUS",
        "not_recorded_in_committed_artifacts",
    ]
    for status in required_statuses:
        assert status in text
    assert "No local path is committed in this gate." in text


def test_no_filename_parent_folder_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_REAL_FILENAME_STATUS",
        "REAL_FILE_ACCESS_PARENT_FOLDER_STATUS",
        "REAL_FILE_ACCESS_FILE_SIZE_STATUS",
        "REAL_FILE_ACCESS_TIMESTAMP_STATUS",
        "REAL_FILE_ACCESS_HASH_STATUS",
        "not_recorded_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_media_decode_probe_scan_or_transcription_occurs():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_MEDIA_DECODE_STATUS",
        "REAL_FILE_ACCESS_MEDIA_PROBE_STATUS",
        "REAL_FILE_ACCESS_MEDIA_SCAN_STATUS",
        "REAL_FILE_ACCESS_TRANSCRIPTION_STATUS",
        "not_executed_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text
    assert "Media decode is not executed in this gate." in text
    assert "Media probe is not executed in this gate." in text
    assert "Media scan is not executed in this gate." in text
    assert "Transcription is not executed in this gate." in text


def test_no_thumbnails_or_waveforms_are_generated():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_THUMBNAIL_STATUS",
        "not_generated_in_this_gate",
        "REAL_FILE_ACCESS_WAVEFORM_STATUS",
    ]
    for status in required_statuses:
        assert status in text
    assert "Thumbnails are not generated in this gate." in text
    assert "Waveforms are not generated in this gate." in text


def test_no_execution_or_media_tools_are_run():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_EXECUTION_STATUS",
        "REAL_FILE_ACCESS_FFMPEG_STATUS",
        "REAL_FILE_ACCESS_FFPROBE_STATUS",
        "REAL_FILE_ACCESS_SCANNER_STATUS",
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
    assert "REAL_FILE_ACCESS_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "REAL_FILE_ACCESS_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`real_file_access_readiness_001` is created as a readiness record.",
        "`local_path_disclosure_boundary_001` remains the source local path disclosure boundary.",
        "`LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001` remains a non-filesystem disclosure boundary handle.",
        "`controlled_real_file_selection_boundary_001` remains the source selection boundary record.",
        "`CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001` remains a non-filesystem selection boundary handle.",
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


def test_later_real_file_access_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must use the sanitized selection token as the control input.",
        "It must use the manual confirmation handle as a control prerequisite.",
        "It must use the controlled real file selection boundary handle as a control prerequisite.",
        "It must use the local path disclosure boundary handle as a control prerequisite.",
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
        "It must not decode media.",
        "It must not transcribe media.",
        "It must not generate thumbnails.",
        "It must not generate waveforms.",
        "It must not create SaaS coupling.",
        "It must remain test-covered.",
        "It must pass repository safety guards before commit.",
    ]
    for constraint in constraints:
        assert constraint in text


def test_real_file_access_and_stat_are_forbidden():
    text = _text()
    forbidden_items = [
        "Accessing a real file.",
        "Performing filesystem stat operations.",
        "Opening a media file.",
        "Reading file bytes.",
        "Reading filesystem metadata.",
    ]
    for item in forbidden_items:
        assert item in text


def test_committed_path_and_identity_metadata_are_forbidden():
    text = _text()
    forbidden_items = [
        "Committing a local filesystem path.",
        "Writing a local filesystem path to product documentation.",
        "Writing a local filesystem path to tests.",
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


def test_next_phase_boundary_is_real_file_access_gate_only():
    text = _text()
    assert "The next conservative phase may define a real file access gate." in text
    assert "This real file access readiness gate does not authorize accessing a real file." in text
    assert "This real file access readiness gate does not authorize filesystem stat operations." in text
    assert "This real file access readiness gate does not authorize opening media." in text
    assert "This real file access readiness gate does not authorize reading metadata." in text
    assert "This real file access readiness gate does not authorize reading file bytes." in text
    assert "This real file access readiness gate does not authorize media execution." in text
    assert "This real file access readiness gate only prepares conditions for a later real file access gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This real file access readiness gate test.",
        "The previous local path disclosure gate test.",
        "The previous local path disclosure readiness gate test.",
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


def test_closing_state_is_ready_for_real_file_access_gate():
    text = _text()
    assert "READY_FOR_REAL_FILE_ACCESS_GATE" in text
