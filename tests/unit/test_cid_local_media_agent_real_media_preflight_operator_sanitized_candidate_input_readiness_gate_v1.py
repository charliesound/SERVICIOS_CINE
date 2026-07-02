from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_readiness_gate_v1.md"
)

CANDIDATE_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md"
)

CANDIDATE_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_readiness_gate_v1.md"
)

SELECTION_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md"
)

CONTROLLED_EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_readiness_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_operator_input_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_SANITIZED_CANDIDATE_INPUT.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_SANITIZED_CANDIDATE_INPUT_READINESS_GATE_V1_CLOSED" in text
    assert "SANITIZED_SINGLE_FILE_CANDIDATE_DEFERRED_PENDING_OPERATOR_CANDIDATE_RECORD" in text
    assert "READY_FOR_OPERATOR_SANITIZED_CANDIDATE_INPUT_GATE" in text


def test_operator_input_readiness_records_base_state() -> None:
    text = _text()

    assert "ecd9eaf1464347f67d36fd4c8804d7bfb3707e73" in text
    assert "ecd9eaf docs: add CID Local Media Agent sanitized single file candidate gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-sanitized-single-file-candidate-gate-v1-20260702" in text


def test_operator_input_readiness_references_upstream_documents() -> None:
    text = _text()

    assert CANDIDATE_GATE_DOC.exists()
    assert CANDIDATE_READINESS_DOC.exists()
    assert SELECTION_GATE_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_operator_input_readiness_is_readiness_only() -> None:
    text = _text()

    markers = [
        "This gate is operator input readiness only.",
        "This gate does not collect real operator input.",
        "This gate does not create a candidate.",
        "This gate does not invent a selection id.",
        "This gate does not invent a sanitized input token.",
        "This gate does not invent a generic file category.",
        "This gate does not invent material ownership.",
        "This gate does not invent confidentiality status.",
        "This gate does not select a real file.",
        "This gate does not record a real file path.",
        "This gate does not record a real filename.",
        "This gate does not stat a real file.",
        "This gate does not open a real file.",
        "This gate does not execute real media.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "The sanitized candidate gate was correctly deferred because no operator-provided sanitized candidate record existed.",
        "Before collecting operator input, the accepted input shape must be explicit.",
        "Operator input must not expose real absolute paths.",
        "Operator input must not expose sensitive filenames.",
        "Operator input must not expose customer identity.",
        "Operator input must not expose project identity.",
        "Operator input must not expose personal data.",
        "Operator input must not imply that media execution is approved.",
        "Operator input must be reviewable before candidate creation.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_readiness_records_core_fields() -> None:
    text = _text()

    fields = [
        "READINESS_RECORD_ID:",
        "operator_sanitized_candidate_input_readiness_v1",
        "READINESS_RECORD_TYPE:",
        "operator_input_readiness_only_no_input_collected",
        "READINESS_DECISION:",
        "ACCEPTED_FOR_OPERATOR_SANITIZED_CANDIDATE_INPUT_GATE_DRAFTING_ONLY",
        "READINESS_STATUS:",
        "OPERATOR_SANITIZED_INPUT_SCHEMA_DEFINED_WITHOUT_VALUES",
        "FUTURE_OPERATOR_INPUT_GATE_ALLOWED_TO_BE_DRAFTED:",
        "yes",
        "OPERATOR_INPUT_COLLECTION_ALLOWED_IN_THIS_GATE:",
        "no",
        "CANDIDATE_CREATION_ALLOWED_IN_THIS_GATE:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_operator_input_readiness_records_no_file_no_customer_no_dependency() -> None:
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


def test_operator_input_readiness_lists_required_fields() -> None:
    text = _text()

    fields = [
        "input_record_id",
        "selection_id",
        "sanitized_input_token",
        "generic_file_category",
        "material_owner_category",
        "confidentiality_status",
        "locality_status",
        "single_file_status",
        "folder_rejection_status",
        "batch_rejection_status",
        "recursive_rejection_status",
        "source_read_only_status",
        "output_path_control_status",
        "network_no_upload_status",
        "redaction_status",
        "execution_not_requested_status",
        "operator_attestation_status",
        "stop_condition_status",
        "input_verdict",
    ]

    for field in fields:
        assert field in text


def test_operator_input_readiness_defines_id_and_selection_policies() -> None:
    text = _text()

    markers = [
        "Use a generated placeholder input record id.",
        "Do not use a real path fragment.",
        "Do not use a real filename.",
        "Do not use a customer name.",
        "Do not use a company name.",
        "Do not use a project title.",
        "Do not use a person name.",
        "Use a generated placeholder selection id.",
        "Allowed example shape: candidate_input_001.",
        "Allowed example shape: local_single_file_candidate_001.",
        "Forbidden: customer names.",
        "Forbidden: company names.",
        "Forbidden: project titles.",
        "Forbidden: real filenames.",
        "Forbidden: real path fragments.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_readiness_defines_token_and_category_values() -> None:
    text = _text()

    markers = [
        "The token must be redacted.",
        "The token may state that the candidate is local.",
        "The token may state that the candidate is a single file.",
        "The token may state generic media type.",
        "The token must not include an absolute path.",
        "The token must not include home directory details.",
        "The token must not include mounted drive details.",
        "The token must not include customer folder names.",
        "The token must not include project titles.",
        "The token must not include real filenames.",
        "generic_video_file",
        "generic_audio_file",
        "generic_image_file",
        "generic_unknown_media_file",
        "unknown_stop_required",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_readiness_defines_allowed_status_values() -> None:
    text = _text()

    values = [
        "internal_operator_owned",
        "separately_approved_non_confidential",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "folder_rejected",
        "batch_rejected",
        "recursive_rejected",
        "wildcard_rejected",
        "glob_pattern_rejected",
        "source_read_only_confirmed",
        "controlled_output_required_later",
        "no_upload_confirmed",
        "no_cloud_processing_confirmed",
        "no_external_api_confirmed",
        "execution_not_requested",
        "operator_attests_non_confidential_single_local_file",
        "operator_attestation_missing_stop_required",
        "accepted_for_candidate_creation_gate",
        "rejected_stop_required",
        "deferred_missing_operator_data",
    ]

    for value in values:
        assert value in text


def test_operator_input_readiness_blocks_forbidden_values() -> None:
    text = _text()

    values = [
        "real_absolute_path",
        "real_sensitive_filename",
        "customer_name",
        "company_name",
        "project_title",
        "person_name",
        "email",
        "phone_number",
        "home_directory",
        "external_drive_name",
        "cloud_sync_folder_name",
        "network_share_name",
        "scene_identifier",
        "take_identifier",
        "roll_identifier",
        "camera_card_identifier",
        "confidential_description",
        "media_derived_sensitive_description",
    ]

    for value in values:
        assert value in text


def test_operator_input_readiness_defines_redaction_rules() -> None:
    text = _text()

    rules = [
        "Replace real path with redacted token.",
        "Replace real filename with generic category if filename is sensitive.",
        "Replace customer identity with neutral ownership category.",
        "Replace project identity with neutral category.",
        "Replace personal identifiers with neutral category.",
        "Do not persist actual file path in committed artifacts.",
        "Do not persist actual filename if sensitive.",
        "Do not persist production identifiers.",
        "Do not persist customer identifiers.",
        "Do not persist personal data.",
    ]

    for rule in rules:
        assert rule in text


def test_operator_input_readiness_lists_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop if the operator provides an absolute path for commit.",
        "Stop if the operator provides a sensitive filename for commit.",
        "Stop if the operator provides customer identity.",
        "Stop if the operator provides company identity.",
        "Stop if the operator provides project title.",
        "Stop if the operator provides personal data.",
        "Stop if the operator cannot confirm ownership.",
        "Stop if the operator cannot confirm non-confidentiality.",
        "Stop if the operator cannot confirm single-file shape.",
        "Stop if the operator provides a folder.",
        "Stop if the operator provides a batch list.",
        "Stop if the operator implies recursive traversal.",
        "Stop if the operator requests dependency execution.",
        "Stop if the operator requests real media execution.",
        "Stop if the operator requests upload.",
        "Stop if the operator implies production use.",
        "Stop if the operator implies paid delivery.",
    ]

    for condition in conditions:
        assert condition in text


def test_operator_input_readiness_lists_future_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Input record id is present and safe.",
        "Selection id is present and safe.",
        "Sanitized input token is present and redacted.",
        "Generic file category is present.",
        "Material owner category is present.",
        "Confidentiality status is present.",
        "Locality status is present.",
        "Single-file status is present.",
        "Folder rejection is confirmed.",
        "Batch rejection is confirmed.",
        "Recursive rejection is confirmed.",
        "Read-only status is confirmed.",
        "Controlled output path requirement is confirmed.",
        "No-upload status is confirmed.",
        "Redaction status is confirmed.",
        "Execution-not-requested status is confirmed.",
        "Operator attestation is present.",
        "Stop-condition status is present.",
        "Input verdict is present.",
        "No real absolute path is committed.",
        "No sensitive filename is committed.",
        "No customer identity is committed.",
        "No production identity is committed.",
        "No dependency execution is requested.",
        "No real media execution is requested.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_operator_input_readiness_defines_supported_and_unsupported_scope() -> None:
    text = _text()

    supported = [
        "Future operator sanitized candidate input gate drafting.",
        "Future safe manual input shape.",
        "Future redacted candidate input.",
        "Future stop-condition enforcement before candidate creation.",
        "Future separation between operator input and candidate creation.",
        "Future candidate creation only after explicit sanitized input.",
    ]
    unsupported = [
        "Collecting operator input now.",
        "Creating a candidate now.",
        "Selecting a real file now.",
        "Recording a real path now.",
        "Recording a real filename now.",
        "Stating a real file now.",
        "Opening a real file now.",
        "Executing real media now.",
        "Running FFmpeg now.",
        "Running ffprobe now.",
        "Running scanner behavior now.",
        "Processing customer material now.",
        "Folder scanning now.",
        "Batch processing now.",
        "Recursive traversal now.",
        "Production use now.",
        "Paid delivery now.",
    ]

    for marker in supported + unsupported:
        assert marker in text


def test_operator_input_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Operator sanitized candidate input readiness phase is defined.",
        "Base state is recorded.",
        "Sanitized single-file candidate gate is referenced.",
        "Sanitized single-file candidate readiness gate is referenced.",
        "Explicit single-file selection gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Production path scope gate is referenced.",
        "Readiness record id is present.",
        "Readiness record type is operator input readiness only.",
        "Readiness decision allows operator input gate drafting only.",
        "Readiness status is defined without values.",
        "Operator input collection is not allowed in this gate.",
        "Candidate creation is not allowed in this gate.",
        "No real file is selected.",
        "No real file path is recorded.",
        "No real filename is recorded.",
        "No real file stat is run.",
        "No real file open is run.",
        "No customer file is selected.",
        "No customer media is used.",
        "No dependency command is run.",
        "FFmpeg run is no.",
        "ffprobe run is no.",
        "Scanner run is no.",
        "Future operator input record type is defined.",
        "Required operator input fields are listed.",
        "Input record id policy is explicit.",
        "Selection id policy is explicit.",
        "Sanitized input token policy is explicit.",
        "Allowed status values are explicit.",
        "Forbidden operator input values are explicit.",
        "Redaction rules are explicit.",
        "Stop conditions are listed.",
        "Future operator input pass criteria are listed.",
        "Supported scope is explicit.",
        "Unsupported scope is explicit.",
        "No real media is executed.",
        "No customer material is requested.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_operator_input_readiness_keeps_limitations_and_safety_active() -> None:
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
        "No operator input is collected in this gate.",
        "No candidate is created in this gate.",
        "No real media is executed in this gate.",
        "No real media file is selected in this gate.",
        "No real file path is recorded in this gate.",
        "No real filename is recorded in this gate.",
        "No real file stat is run in this gate.",
        "No real file open is run in this gate.",
        "No customer material is allowed in this gate.",
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


def test_operator_input_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this operator sanitized candidate input readiness document.",
        "Add one operator sanitized candidate input readiness unit test.",
        "Inspect existing sanitized single-file candidate gate document.",
        "Inspect existing sanitized single-file candidate readiness document.",
        "Inspect existing explicit single-file selection gate document.",
        "Inspect existing real-media preflight controlled execution document.",
        "Inspect existing real-media preflight readiness document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No operator input collection.",
        "No candidate creation.",
        "No candidate value invention.",
        "No selection id invention.",
        "No sanitized token invention.",
        "No generic category invention.",
        "No owner category invention.",
        "No confidentiality status invention.",
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


def test_operator_input_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_SANITIZED_CANDIDATE_INPUT.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_SANITIZED_CANDIDATE_INPUT_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent operator sanitized candidate input readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-operator-sanitized-candidate-input-readiness-gate-v1-20260702" in text
