from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_real_file_access_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_real_file_access_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.REAL_FILE_ACCESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_REAL_FILE_ACCESS_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_real_file_access_gate():
    text = _text()
    assert "READY_FOR_REAL_FILE_ACCESS_GATE" in text


def test_target_state_prepares_controlled_stat_readiness():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_READY_FOR_CONTROLLED_STAT_READINESS_GATE" in text


def test_gate_purpose_defines_boundary_only():
    text = _text()
    assert "This gate defines the controlled real file access boundary for a later controlled stat readiness phase." in text
    assert "This gate creates only a sanitized real file access boundary record." in text
    assert "This gate does not access a real file." in text
    assert "This gate does not perform filesystem stat operations." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_real_file_access_readiness_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.REAL_FILE_ACCESS.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_REAL_FILE_ACCESS_READINESS_GATE_V1_CLOSED" in text


def test_source_real_file_access_readiness_record_values_are_preserved():
    text = _text()
    required_values = [
        "real_file_access_readiness_001",
        "operator_input_001",
        "local_path_disclosure_boundary_001",
        "LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001",
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
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "ready_for_real_file_access_gate_without_file_access_or_filesystem_touch",
    ]
    for value in required_values:
        assert value in text


def test_real_file_access_boundary_record_is_declared():
    text = _text()
    required_fields = [
        "REAL_FILE_ACCESS_BOUNDARY_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_INPUT_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_READINESS_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_SELECTION_BOUNDARY_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_SELECTION_BOUNDARY_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_CONFIRMATION_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_CONFIRMATION_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_CONFIRMATION_VALUE",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_TOKEN_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_TOKEN_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_SANITIZED_SELECTION_TOKEN",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_REFERENCE_RECORD_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_REFERENCE_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_EVENT_ID",
        "REAL_FILE_ACCESS_BOUNDARY_SOURCE_EVENT_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_HANDLE",
        "REAL_FILE_ACCESS_BOUNDARY_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_real_file_access_boundary_values_are_sanitized():
    text = _text()
    required_values = [
        "real_file_access_boundary_001",
        "REAL_FILE_ACCESS_BOUNDARY_HANDLE_001",
        "defined_as_operator_local_file_access_boundary",
        "prepares_controlled_stat_readiness_only",
        "boundary_defined_without_file_access",
        "real_file_access_boundary_defined_without_stat_open_or_file_read",
    ]
    for value in required_values:
        assert value in text


def test_boundary_status_and_scope_are_limited():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_STATUS" in text
    assert "defined_as_operator_local_file_access_boundary" in text
    assert "REAL_FILE_ACCESS_BOUNDARY_SCOPE_STATUS" in text
    assert "prepares_controlled_stat_readiness_only" in text
    assert "The boundary status is `defined_as_operator_local_file_access_boundary`." in text
    assert "The boundary scope prepares controlled stat readiness only." in text


def test_no_real_file_access_occurs():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_ACCESS_STATUS" in text
    assert "boundary_defined_without_file_access" in text
    assert "No real file is accessed." in text


def test_no_stat_operation_occurs():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_STAT_STATUS" in text
    assert "not_performed" in text
    assert "No filesystem stat operation is performed." in text


def test_no_media_file_is_opened():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_FILE_OPEN_STATUS" in text
    assert "not_opened" in text
    assert "No media file is opened." in text


def test_no_file_bytes_or_filesystem_metadata_are_read():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_FILE_BYTES_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_FILESYSTEM_METADATA_STATUS",
        "not_read",
    ]
    for status in required_statuses:
        assert status in text
    assert "No file bytes are read." in text
    assert "No filesystem metadata is read." in text


def test_no_local_path_is_committed_or_recorded_in_artifacts():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_REAL_PATH_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_ABSOLUTE_PATH_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_RELATIVE_PATH_STATUS",
        "not_recorded_in_committed_artifacts",
    ]
    for status in required_statuses:
        assert status in text
    assert "No local path is committed." in text


def test_no_filename_parent_folder_size_timestamps_or_hashes_are_recorded():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_REAL_FILENAME_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_PARENT_FOLDER_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_FILE_SIZE_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_TIMESTAMP_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_HASH_STATUS",
        "not_recorded",
    ]
    for status in required_statuses:
        assert status in text


def test_no_media_decode_probe_scan_or_transcription_occurs():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_MEDIA_DECODE_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_MEDIA_PROBE_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_MEDIA_SCAN_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_TRANSCRIPTION_STATUS",
        "not_executed",
    ]
    for status in required_statuses:
        assert status in text
    assert "Media decode is not executed." in text
    assert "Media probe is not executed." in text
    assert "Media scan is not executed." in text
    assert "Transcription is not executed." in text


def test_no_thumbnails_or_waveforms_are_generated():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_THUMBNAIL_STATUS",
        "not_generated",
        "REAL_FILE_ACCESS_BOUNDARY_WAVEFORM_STATUS",
    ]
    for status in required_statuses:
        assert status in text
    assert "Thumbnails are not generated." in text
    assert "Waveforms are not generated." in text


def test_no_execution_or_media_tools_are_run():
    text = _text()
    required_statuses = [
        "REAL_FILE_ACCESS_BOUNDARY_EXECUTION_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_FFMPEG_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_FFPROBE_STATUS",
        "REAL_FILE_ACCESS_BOUNDARY_SCANNER_STATUS",
        "not_executed",
    ]
    for status in required_statuses:
        assert status in text
    assert "Real media preflight is not executed." in text
    assert "FFmpeg is not executed." in text
    assert "ffprobe is not executed." in text
    assert "Scanner logic is not executed." in text


def test_no_runtime_or_saas_integration_is_created():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "REAL_FILE_ACCESS_BOUNDARY_SAAS_STATUS" in text
    assert "no_saas_integration" in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`real_file_access_boundary_001` is created as a sanitized boundary record.",
        "`REAL_FILE_ACCESS_BOUNDARY_HANDLE_001` is a non-filesystem boundary handle.",
        "`real_file_access_readiness_001` remains the source readiness record.",
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


def test_later_controlled_stat_readiness_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must use the sanitized selection token as the control input.",
        "It must use the manual confirmation handle as a control prerequisite.",
        "It must use the controlled real file selection boundary handle as a control prerequisite.",
        "It must use the local path disclosure boundary handle as a control prerequisite.",
        "It must use the real file access boundary handle as a control prerequisite.",
        "It must not commit the local path to git.",
        "It must not write the local path to product documentation.",
        "It must not write the local path to tests.",
        "It must not expose a sensitive filename in committed artifacts.",
        "It must not expose parent folder names in committed artifacts.",
        "It must not commit file size.",
        "It must not commit timestamps.",
        "It must not commit hashes.",
        "It must not open the media file.",
        "It must not read file bytes.",
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


def test_next_phase_boundary_is_controlled_stat_readiness_only():
    text = _text()
    assert "The next conservative phase may prepare a controlled stat readiness gate." in text
    assert "This real file access gate does not authorize accessing a real file." in text
    assert "This real file access gate does not authorize filesystem stat operations." in text
    assert "This real file access gate does not authorize opening media." in text
    assert "This real file access gate does not authorize reading file bytes." in text
    assert "This real file access gate does not authorize media execution." in text
    assert "This real file access gate only defines the sanitized real file access boundary." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This real file access gate test.",
        "The previous real file access readiness gate test.",
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


def test_closing_state_is_ready_for_controlled_stat_readiness_gate():
    text = _text()
    assert "REAL_FILE_ACCESS_BOUNDARY_READY_FOR_CONTROLLED_STAT_READINESS_GATE" in text
