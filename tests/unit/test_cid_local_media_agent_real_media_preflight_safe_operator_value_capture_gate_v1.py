from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_safe_operator_value_capture_gate_v1.md"
)

VALUE_CAPTURE_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_safe_operator_value_capture_readiness_gate_v1.md"
)

OPERATOR_INPUT_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_gate_v1.md"
)

OPERATOR_INPUT_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_readiness_gate_v1.md"
)

CANDIDATE_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md"
)

CONTROLLED_EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_readiness_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_safe_capture_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SAFE_OPERATOR_VALUE_CAPTURE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SAFE_OPERATOR_VALUE_CAPTURE_GATE_V1_CLOSED" in text
    assert "READY_FOR_SAFE_OPERATOR_VALUE_CAPTURE_GATE" in text
    assert "SAFE_OPERATOR_VALUE_CAPTURE_ACCEPTED_FOR_OPERATOR_INPUT_MATERIALIZATION_GATE" in text


def test_safe_capture_records_base_state() -> None:
    text = _text()

    assert "4ffebf9dd53d79193e6e190cc3791ea8e9b7d0b3" in text
    assert "4ffebf9 docs: add CID Local Media Agent safe operator value capture readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-safe-operator-value-capture-readiness-gate-v1-20260702" in text


def test_safe_capture_references_upstream_documents() -> None:
    text = _text()

    assert VALUE_CAPTURE_READINESS_DOC.exists()
    assert OPERATOR_INPUT_GATE_DOC.exists()
    assert OPERATOR_INPUT_READINESS_DOC.exists()
    assert CANDIDATE_GATE_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_safe_operator_value_capture_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text


def test_safe_capture_records_sanitized_values() -> None:
    text = _text()

    values = [
        "CAPTURE_RECORD_ID:",
        "safe_capture_001",
        "INPUT_RECORD_ID:",
        "operator_input_001",
        "SELECTION_ID:",
        "local_single_file_candidate_001",
        "SANITIZED_INPUT_TOKEN:",
        "REDACTED_LOCAL_SINGLE_VIDEO_FILE",
        "GENERIC_FILE_CATEGORY:",
        "generic_video_file",
        "MATERIAL_OWNER_CATEGORY:",
        "internal_operator_owned",
        "CONFIDENTIALITY_STATUS:",
        "non_confidential_confirmed",
        "LOCALITY_STATUS:",
        "local_single_file_claimed",
        "SINGLE_FILE_STATUS:",
        "single_file_claimed",
        "CAPTURE_VERDICT:",
        "accepted_for_operator_input_materialization_gate",
    ]

    for value in values:
        assert value in text


def test_safe_capture_records_rejections_and_safety_statuses() -> None:
    text = _text()

    statuses = [
        "FOLDER_REJECTION_STATUS:",
        "folder_rejected",
        "BATCH_REJECTION_STATUS:",
        "batch_rejected",
        "RECURSIVE_REJECTION_STATUS:",
        "recursive_rejected",
        "WILDCARD_REJECTION_STATUS:",
        "wildcard_rejected",
        "GLOB_PATTERN_REJECTION_STATUS:",
        "glob_pattern_rejected",
        "SOURCE_READ_ONLY_STATUS:",
        "source_read_only_confirmed",
        "OUTPUT_PATH_CONTROL_STATUS:",
        "controlled_output_required_later",
        "NETWORK_NO_UPLOAD_STATUS:",
        "no_upload_confirmed",
        "CLOUD_PROCESSING_REJECTION_STATUS:",
        "no_cloud_processing_confirmed",
        "EXTERNAL_API_REJECTION_STATUS:",
        "no_external_api_confirmed",
        "EXECUTION_NOT_REQUESTED_STATUS:",
        "execution_not_requested",
        "STOP_CONDITION_STATUS:",
        "stop_conditions_confirmed",
    ]

    for status in statuses:
        assert status in text


def test_safe_capture_commits_no_sensitive_or_real_file_values() -> None:
    text = _text()

    fields = [
        "REAL_ABSOLUTE_PATH_COMMITTED:",
        "no",
        "REAL_FILENAME_COMMITTED:",
        "no",
        "CUSTOMER_IDENTITY_COMMITTED:",
        "no",
        "COMPANY_IDENTITY_COMMITTED:",
        "no",
        "PROJECT_IDENTITY_COMMITTED:",
        "no",
        "PERSONAL_DATA_COMMITTED:",
        "no",
        "CONFIDENTIAL_DESCRIPTION_COMMITTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_safe_capture_records_no_file_execution_dependency_or_scanner() -> None:
    text = _text()

    fields = [
        "REAL_FILE_SELECTED:",
        "no",
        "REAL_FILE_PATH_RECORDED:",
        "no",
        "REAL_FILENAME_RECORDED:",
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


def test_safe_capture_lists_what_was_captured_and_not_captured() -> None:
    text = _text()

    captured = [
        "A safe placeholder capture record id.",
        "A safe placeholder input record id.",
        "A safe placeholder selection id.",
        "A redacted local single video file token.",
        "A generic video file category.",
        "A neutral internal operator-owned category.",
        "A non-confidential confirmation.",
        "A local single-file claim.",
        "Execution-not-requested confirmation.",
        "Operator attestation.",
        "Stop-condition confirmation.",
    ]
    not_captured = [
        "No real absolute path.",
        "No real filename.",
        "No customer name.",
        "No company name.",
        "No project title.",
        "No person name.",
        "No email.",
        "No phone number.",
        "No home directory.",
        "No external drive name.",
        "No cloud sync folder name.",
        "No network share name.",
        "No scene identifier.",
        "No take identifier.",
        "No roll identifier.",
        "No camera-card identifier.",
        "No confidential description.",
        "No media-derived sensitive description.",
    ]

    for marker in captured + not_captured:
        assert marker in text


def test_safe_capture_records_validated_and_not_validated_scope() -> None:
    text = _text()

    validated = [
        "Safe operator values were captured using placeholders and redacted tokens.",
        "No real absolute path was committed.",
        "No sensitive filename was committed.",
        "No customer identity was committed.",
        "No production identity was committed.",
        "The input is represented as one local single video file.",
        "Folder input is rejected.",
        "Batch input is rejected.",
        "Recursive traversal is rejected.",
        "Source read-only intent is confirmed.",
        "No upload is confirmed.",
        "Execution is not requested.",
        "Stop conditions are confirmed.",
        "The record is accepted for operator input materialization gate.",
    ]
    not_validated = [
        "Real file existence.",
        "Real file readability.",
        "Real file ownership beyond operator attestation.",
        "Real file confidentiality beyond operator attestation.",
        "Real file extension.",
        "Real file size.",
        "Real media metadata.",
        "Real FFmpeg behavior.",
        "Real ffprobe behavior.",
        "Real scanner behavior.",
        "Real output report from media.",
    ]

    for marker in validated + not_validated:
        assert marker in text


def test_safe_capture_defines_safe_next_step() -> None:
    text = _text()

    markers = [
        "Materialize these sanitized values into an operator input record in a separate gate.",
        "Do not add a real path in the next committed artifact.",
        "Do not add a real filename in the next committed artifact.",
        "Do not execute, open, or stat the real file in the next materialization gate.",
        "Keep execution separated until an explicit real-media preflight execution gate.",
    ]

    for marker in markers:
        assert marker in text


def test_safe_capture_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Safe operator value capture phase is defined.",
        "Base state is recorded.",
        "Value capture readiness gate is referenced.",
        "Operator sanitized candidate input gate is referenced.",
        "Operator sanitized candidate input readiness gate is referenced.",
        "Sanitized single-file candidate gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Capture record id is safe.",
        "Input record id is safe.",
        "Selection id is safe.",
        "Sanitized input token is redacted.",
        "Generic file category is generic video file.",
        "Material owner category is internal operator owned.",
        "Confidentiality status is non-confidential confirmed.",
        "Locality status is local single file claimed.",
        "Single-file status is claimed.",
        "Folder input is rejected.",
        "Batch input is rejected.",
        "Recursive traversal is rejected.",
        "No real absolute path is committed.",
        "No real filename is committed.",
        "No customer identity is committed.",
        "No dependency command is run.",
        "No real media is executed.",
        "No production use is approved.",
        "No paid delivery is approved.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_safe_capture_keeps_limitations_and_safety_active() -> None:
    text = _text()

    markers = [
        "Production use is not approved.",
        "Paid delivery is not approved.",
        "Private pilot execution is not approved.",
        "Real media processing is not approved.",
        "Customer material processing is not approved.",
        "Folder scanning is not approved.",
        "Batch processing is not approved.",
        "Recursive traversal is not approved.",
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
        "No installer is created in this gate.",
        "No binary is created in this gate.",
    ]

    for marker in markers:
        assert marker in text


def test_safe_capture_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this safe operator value capture document.",
        "Add one safe operator value capture unit test.",
        "Inspect existing safe operator value capture readiness document.",
        "Inspect existing operator sanitized candidate input gate document.",
        "Inspect existing real-media preflight controlled execution document.",
        "Inspect existing real-media preflight readiness document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real path capture.",
        "No real filename capture.",
        "No real-media execution.",
        "No real file selection.",
        "No real file path recording.",
        "No real filename recording.",
        "No customer media.",
        "No customer files.",
        "No production approval.",
        "No paid delivery approval.",
        "No private pilot execution.",
        "No implementation changes.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive traversal.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No installer work.",
        "No binary packaging.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_safe_capture_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_INPUT_MATERIALIZATION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_INPUT_MATERIALIZATION_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent safe operator value capture gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-safe-operator-value-capture-gate-v1-20260702" in text
