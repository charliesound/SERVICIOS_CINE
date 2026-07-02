from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_operator_input_materialization_readiness_gate_v1.md"
)

SAFE_CAPTURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_safe_operator_value_capture_gate_v1.md"
)

SAFE_CAPTURE_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_safe_operator_value_capture_readiness_gate_v1.md"
)

OPERATOR_INPUT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_gate_v1.md"
)

SANITIZED_CANDIDATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md"
)

CONTROLLED_EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_operator_input_materialization_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_MATERIALIZATION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_MATERIALIZATION_READINESS_GATE_V1_CLOSED" in text
    assert "SAFE_OPERATOR_VALUE_CAPTURE_ACCEPTED_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE" in text
    assert "READY_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE" in text


def test_operator_input_materialization_readiness_records_base_state() -> None:
    text = _text()

    assert "85fd7d5a5753684d1deb4fd72c9617fb0d21d701" in text
    assert "85fd7d5 docs: add CID Local Media Agent safe operator value capture gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-safe-operator-value-capture-gate-v1-20260702" in text


def test_operator_input_materialization_readiness_references_upstream_documents() -> None:
    text = _text()

    assert SAFE_CAPTURE_DOC.exists()
    assert SAFE_CAPTURE_READINESS_DOC.exists()
    assert OPERATOR_INPUT_DOC.exists()
    assert SANITIZED_CANDIDATE_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_safe_operator_value_capture_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_safe_operator_value_capture_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text


def test_operator_input_materialization_readiness_is_readiness_only() -> None:
    text = _text()

    markers = [
        "This gate is materialization readiness only.",
        "This gate does not create the operator input record.",
        "This gate does not select a real file.",
        "This gate does not commit a real absolute path.",
        "This gate does not commit a real filename.",
        "This gate does not stat a real file.",
        "This gate does not open a real file.",
        "This gate does not execute real media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_materialization_readiness_records_core_decision_fields() -> None:
    text = _text()

    fields = [
        "READINESS_RECORD_ID:",
        "operator_input_materialization_readiness_v1",
        "READINESS_RECORD_TYPE:",
        "operator_input_materialization_readiness_only_no_record_created",
        "READINESS_DECISION:",
        "ACCEPTED_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE_DRAFTING_ONLY",
        "READINESS_STATUS:",
        "OPERATOR_INPUT_MATERIALIZATION_SCHEMA_DEFINED_WITHOUT_RECORD_CREATION",
        "FUTURE_MATERIALIZATION_GATE_ALLOWED_TO_BE_DRAFTED:",
        "yes",
        "OPERATOR_INPUT_RECORD_CREATED_IN_THIS_GATE:",
        "no",
        "CANDIDATE_RECORD_CREATED_IN_THIS_GATE:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_operator_input_materialization_readiness_records_no_real_file_or_dependency() -> None:
    text = _text()

    fields = [
        "REAL_FILE_SELECTED:",
        "no",
        "REAL_ABSOLUTE_PATH_COMMITTED:",
        "no",
        "REAL_FILENAME_COMMITTED:",
        "no",
        "REAL_FILE_STAT_RUN:",
        "no",
        "REAL_FILE_OPEN_RUN:",
        "no",
        "REAL_MEDIA_EXECUTED:",
        "no",
        "CUSTOMER_FILE_SELECTED:",
        "no",
        "CUSTOMER_MEDIA_USED:",
        "no",
        "CONFIDENTIAL_MATERIAL_USED:",
        "no",
        "DEPENDENCY_COMMAND_RUN:",
        "no",
        "FFMPEG_RUN:",
        "no",
        "FFPROBE_RUN:",
        "no",
        "SCANNER_RUN:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_operator_input_materialization_readiness_lists_sanitized_values() -> None:
    text = _text()

    values = [
        "capture_record_id=safe_capture_001",
        "input_record_id=operator_input_001",
        "selection_id=local_single_file_candidate_001",
        "sanitized_input_token=REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "generic_file_category=generic_video_file",
        "material_owner_category=internal_operator_owned",
        "confidentiality_status=non_confidential_confirmed",
        "locality_status=local_single_file_claimed",
        "single_file_status=single_file_claimed",
        "folder_rejection_status=folder_rejected",
        "batch_rejection_status=batch_rejected",
        "recursive_rejection_status=recursive_rejected",
        "network_no_upload_status=no_upload_confirmed",
        "execution_not_requested_status=execution_not_requested",
        "capture_verdict=accepted_for_operator_input_materialization_gate",
    ]

    for value in values:
        assert value in text


def test_operator_input_materialization_readiness_lists_future_record_fields_and_values() -> None:
    text = _text()

    markers = [
        "operator_input_record_id",
        "source_capture_record_id",
        "source_selection_id",
        "sanitized_input_token",
        "generic_file_category",
        "material_owner_category",
        "confidentiality_status",
        "locality_status",
        "single_file_status",
        "traversal_rejection_status",
        "materialization_status",
        "materialization_verdict",
        "operator_input_record_id=operator_input_001",
        "source_capture_record_id=safe_capture_001",
        "source_selection_id=local_single_file_candidate_001",
        "materialization_status=materialized_from_sanitized_capture_only",
        "materialization_verdict=accepted_for_sanitized_candidate_materialization_readiness_gate",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_materialization_readiness_blocks_forbidden_values() -> None:
    text = _text()

    forbidden = [
        "real_absolute_path",
        "real_filename",
        "sensitive_filename",
        "customer_name",
        "company_name",
        "project_title",
        "person_name",
        "home_directory",
        "external_drive_name",
        "network_share_name",
        "scene_identifier",
        "take_identifier",
        "roll_identifier",
        "camera_card_identifier",
        "confidential_description",
        "media_derived_sensitive_description",
    ]

    for marker in forbidden:
        assert marker in text


def test_operator_input_materialization_readiness_defines_rules_and_stop_conditions() -> None:
    text = _text()

    markers = [
        "The future operator input record must copy only sanitized values from the safe capture gate.",
        "The future operator input record must not add a real absolute path.",
        "The future operator input record must not add a real filename.",
        "The future operator input record must not add customer identity.",
        "The future operator input record must not execute, stat, open, or probe media.",
        "Stop if the safe capture gate is missing.",
        "Stop if the safe capture verdict is not accepted for operator input materialization.",
        "Stop if any required sanitized value is missing.",
        "Stop if any real absolute path would be committed.",
        "Stop if any real filename would be committed.",
        "Stop if FFmpeg execution is requested.",
        "Stop if ffprobe execution is requested.",
        "Stop if scanner execution is requested.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_materialization_readiness_defines_supported_and_unsupported_scope() -> None:
    text = _text()

    markers = [
        "Future operator input materialization gate.",
        "Future operator input record contract.",
        "Future sanitized candidate materialization readiness.",
        "Future separation between sanitized input record and real execution.",
        "Creating the operator input record now.",
        "Creating a sanitized candidate now.",
        "Selecting a real file now.",
        "Recording a real path now.",
        "Recording a real filename now.",
        "Executing real media now.",
        "Running FFmpeg now.",
        "Running ffprobe now.",
        "Running scanner behavior now.",
        "Production use now.",
        "Paid delivery now.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_materialization_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Operator input materialization readiness phase is defined.",
        "Base state is recorded.",
        "Safe operator value capture gate is referenced.",
        "Safe operator value capture readiness gate is referenced.",
        "Operator sanitized candidate input gate is referenced.",
        "Sanitized single-file candidate gate is referenced.",
        "Controlled execution gate is referenced.",
        "Readiness record id is present.",
        "Readiness record type is materialization readiness only.",
        "Readiness decision allows materialization gate drafting only.",
        "Readiness status is defined without record creation.",
        "Future materialization gate is allowed to be drafted.",
        "Operator input record created in this gate is no.",
        "Candidate record created in this gate is no.",
        "No real file is selected.",
        "No real absolute path is committed.",
        "No real filename is committed.",
        "No dependency command is run.",
        "FFmpeg run is no.",
        "ffprobe run is no.",
        "Scanner run is no.",
        "Sanitized safe capture values are listed.",
        "Future operator input required fields are listed.",
        "Future operator input allowed values are listed.",
        "Future forbidden values are listed.",
        "Materialization readiness rules are explicit.",
        "Materialization stop conditions are explicit.",
        "No production use is approved.",
        "No paid delivery is approved.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_operator_input_materialization_readiness_keeps_safety_and_scope_explicit() -> None:
    text = _text()

    markers = [
        "No operator input record is created in this gate.",
        "No candidate is created in this gate.",
        "No real path is committed in this gate.",
        "No real filename is committed in this gate.",
        "No real media is executed in this gate.",
        "No real media file is selected in this gate.",
        "No real file stat is run in this gate.",
        "No real file open is run in this gate.",
        "No FFmpeg is allowed in this gate.",
        "No ffprobe is allowed in this gate.",
        "No scanner integration is allowed in this gate.",
        "No SaaS module is allowed in this gate.",
        "No database is allowed in this gate.",
        "Add this operator input materialization readiness document.",
        "Add one operator input materialization readiness unit test.",
        "No operator input record creation.",
        "No candidate creation.",
        "No implementation changes.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_materialization_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_MATERIALIZATION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_MATERIALIZATION_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent operator input materialization readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-operator-input-materialization-readiness-gate-v1-20260702" in text
