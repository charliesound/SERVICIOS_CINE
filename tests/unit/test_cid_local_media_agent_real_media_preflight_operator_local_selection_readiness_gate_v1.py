from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_local_selection_readiness_gate_v1.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_operator_local_selection_readiness_gate_doc_exists():
    assert DOC.exists()


def test_phase_identifier_is_present():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_LOCAL_SELECTION.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_LOCAL_SELECTION_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_controlled_local_reference_gate():
    text = _text()
    assert "CONTROLLED_LOCAL_FILE_REFERENCE_READY_FOR_OPERATOR_LOCAL_SELECTION_READINESS_GATE" in text


def test_target_state_is_ready_for_operator_local_selection_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_LOCAL_SELECTION_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _text()
    assert "This readiness gate prepares the conditions for a later operator local selection gate." in text
    assert "This gate does not perform an operator file selection." in text
    assert "This gate does not select a real file." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_controlled_local_reference_gate_is_referenced():
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_LOCAL_FILE_REFERENCE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_LOCAL_FILE_REFERENCE_GATE_V1_CLOSED" in text


def test_source_controlled_local_reference_record_values_are_preserved():
    text = _text()
    required_values = [
        "controlled_local_file_reference_001",
        "operator_input_001",
        "controlled_local_file_reference_readiness_001",
        "operator_input_real_file_binding_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "LOCAL_REFERENCE_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "controlled_local_reference_created_without_disclosing_or_touching_real_file",
    ]
    for value in required_values:
        assert value in text


def test_operator_local_selection_readiness_record_is_declared():
    text = _text()
    required_fields = [
        "OPERATOR_LOCAL_SELECTION_READINESS_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_INPUT_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_SOURCE_REFERENCE_RECORD_ID",
        "OPERATOR_LOCAL_SELECTION_SOURCE_REFERENCE_HANDLE",
        "OPERATOR_LOCAL_SELECTION_SANITIZED_INPUT_TOKEN",
        "OPERATOR_LOCAL_SELECTION_CONTROLLED_REFERENCE_TOKEN",
        "OPERATOR_LOCAL_SELECTION_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_operator_local_selection_readiness_values_are_sanitized():
    text = _text()
    required_values = [
        "operator_local_selection_readiness_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "REDACTED_CONTROLLED_LOCAL_SINGLE_VIDEO_REFERENCE",
        "ready_for_operator_local_selection_gate_without_real_file_selection",
    ]
    for value in required_values:
        assert value in text


def test_no_real_selection_occurs_in_this_gate():
    text = _text()
    assert "not_selected_in_this_gate" in text
    assert "not_recorded_in_this_gate" in text
    assert "not_read_in_this_gate" in text
    assert "not_opened_in_this_gate" in text
    assert "not_executed_in_this_gate" in text


def test_no_real_path_filename_folder_or_metadata_is_recorded():
    text = _text()
    required_statuses = [
        "OPERATOR_LOCAL_SELECTION_REAL_PATH_STATUS",
        "OPERATOR_LOCAL_SELECTION_REAL_FILENAME_STATUS",
        "OPERATOR_LOCAL_SELECTION_PARENT_FOLDER_STATUS",
        "OPERATOR_LOCAL_SELECTION_FILE_SIZE_STATUS",
        "OPERATOR_LOCAL_SELECTION_TIMESTAMP_STATUS",
        "OPERATOR_LOCAL_SELECTION_HASH_STATUS",
    ]
    for status in required_statuses:
        assert status in text


def test_no_filesystem_or_media_operations_occur():
    text = _text()
    required_statuses = [
        "OPERATOR_LOCAL_SELECTION_FILESYSTEM_METADATA_STATUS",
        "not_read_in_this_gate",
        "OPERATOR_LOCAL_SELECTION_FILE_OPEN_STATUS",
        "not_opened_in_this_gate",
        "OPERATOR_LOCAL_SELECTION_MEDIA_TOOL_STATUS",
        "not_executed_in_this_gate",
    ]
    for status in required_statuses:
        assert status in text


def test_no_runtime_is_created():
    text = _text()
    assert "OPERATOR_LOCAL_SELECTION_RUNTIME_STATUS" in text
    assert "no_runtime_created" in text
    assert "No runtime is created in this gate." in text


def test_positive_assertions_preserve_scope():
    text = _text()
    required_assertions = [
        "`operator_input_001` remains the only input in scope.",
        "`controlled_local_file_reference_001` remains the source controlled local reference.",
        "`LOCAL_REFERENCE_HANDLE_001` remains a non-filesystem control handle.",
        "The locality claim remains `local_single_file_claimed`.",
        "The single-file claim remains `single_file_claimed`.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_future_operator_local_selection_constraints_are_conservative():
    text = _text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
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


def test_next_phase_boundary_is_operator_local_selection_gate_only():
    text = _text()
    assert "The next conservative phase may define an operator local selection gate." in text
    assert "This readiness gate does not authorize the selection event itself." in text
    assert "This readiness gate only prepares the conditions for that later controlled gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _text()
    required_checks = [
        "This operator local selection readiness gate test.",
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


def test_closing_state_is_ready_for_operator_local_selection_gate():
    text = _text()
    assert "READY_FOR_OPERATOR_LOCAL_SELECTION_GATE" in text
