from pathlib import Path


DOC_PATH = Path(
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


def test_operator_input_gate_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_SANITIZED_CANDIDATE_INPUT.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_SANITIZED_CANDIDATE_INPUT_GATE_V1_CLOSED" in text
    assert "READY_FOR_OPERATOR_SANITIZED_CANDIDATE_INPUT_GATE" in text
    assert "OPERATOR_SANITIZED_CANDIDATE_INPUT_DEFERRED_PENDING_SAFE_OPERATOR_VALUES" in text


def test_operator_input_gate_records_base_state() -> None:
    text = _text()

    assert "48b2b3abadc0355dc8f391add2c54d816609a5d3" in text
    assert "48b2b3a docs: add CID Local Media Agent operator sanitized candidate input readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-operator-sanitized-candidate-input-readiness-gate-v1-20260702" in text


def test_operator_input_gate_references_upstream_documents() -> None:
    text = _text()

    assert OPERATOR_INPUT_READINESS_DOC.exists()
    assert CANDIDATE_GATE_DOC.exists()
    assert CANDIDATE_READINESS_DOC.exists()
    assert SELECTION_GATE_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_operator_sanitized_candidate_input_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_operator_input_gate_does_not_collect_invent_or_execute() -> None:
    text = _text()

    markers = [
        "This gate does not collect operator values.",
        "This gate does not invent operator values.",
        "This gate does not create a candidate.",
        "This gate does not invent an input record id.",
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


def test_operator_input_gate_explains_safe_deferral() -> None:
    text = _text()

    markers = [
        "An operator input gate must not fabricate values.",
        "An operator input gate must not fabricate a selection id.",
        "An operator input gate must not fabricate a redacted token.",
        "An operator input gate must not fabricate file category, ownership, confidentiality, or locality.",
        "An operator input gate must not commit real absolute paths.",
        "An operator input gate must not commit sensitive filenames.",
        "An operator input gate must not expose customer, company, project, person, scene, take, roll, or camera-card identifiers.",
        "An operator input gate must stop when no safe operator values have been provided.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_gate_records_decision_fields() -> None:
    text = _text()

    fields = [
        "OPERATOR_INPUT_DECISION_RECORD_ID:",
        "operator_sanitized_candidate_input_deferred_v1",
        "OPERATOR_INPUT_RECORD_TYPE:",
        "operator_input_decision_no_values_collected",
        "OPERATOR_INPUT_DECISION:",
        "DEFERRED_NO_SAFE_OPERATOR_SANITIZED_VALUES_PROVIDED",
        "OPERATOR_INPUT_STATUS:",
        "NOT_COLLECTED",
        "OPERATOR_INPUT_COLLECTION_ALLOWED:",
        "no",
        "OPERATOR_INPUT_COLLECTION_ATTEMPTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_operator_input_gate_records_no_created_values() -> None:
    text = _text()

    fields = [
        "CANDIDATE_CREATION_ALLOWED:",
        "no",
        "CANDIDATE_CREATION_ATTEMPTED:",
        "no",
        "INPUT_RECORD_ID_CREATED:",
        "no",
        "SELECTION_ID_CREATED:",
        "no",
        "SANITIZED_INPUT_TOKEN_CREATED:",
        "no",
        "GENERIC_FILE_CATEGORY_CREATED:",
        "no",
        "MATERIAL_OWNER_CATEGORY_CREATED:",
        "no",
        "CONFIDENTIALITY_STATUS_CREATED:",
        "no",
        "LOCALITY_STATUS_CREATED:",
        "no",
        "SINGLE_FILE_STATUS_CREATED:",
        "no",
        "OPERATOR_ATTESTATION_CREATED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_operator_input_gate_records_no_file_no_customer_no_dependency() -> None:
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


def test_operator_input_gate_records_deferral_reasons() -> None:
    text = _text()

    reasons = [
        "No safe operator values were provided.",
        "No input record id was provided.",
        "No placeholder selection id was provided.",
        "No redacted input token was provided.",
        "No generic file category was provided.",
        "No material owner category was provided.",
        "No confidentiality status was provided.",
        "No locality status was provided.",
        "No single-file status was provided.",
        "No folder rejection status was provided.",
        "No batch rejection status was provided.",
        "No recursive rejection status was provided.",
        "No read-only confirmation was provided.",
        "No no-upload confirmation was provided.",
        "No operator attestation was provided.",
        "No stop-condition confirmation was provided.",
        "No input verdict was provided.",
    ]

    for reason in reasons:
        assert reason in text


def test_operator_input_gate_lists_required_safe_values_and_example_shape() -> None:
    text = _text()

    required = [
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
    examples = [
        "input_record_id: operator_input_001",
        "selection_id: local_single_file_candidate_001",
        "sanitized_input_token: REDACTED_LOCAL_SINGLE_MEDIA_FILE",
        "generic_file_category: generic_video_file",
        "material_owner_category: internal_operator_owned",
        "confidentiality_status: non_confidential_confirmed",
        "locality_status: local_single_file_claimed",
        "single_file_status: single_file_claimed",
        "network_no_upload_status: no_upload_confirmed",
        "execution_not_requested_status: execution_not_requested",
        "input_verdict: accepted_for_candidate_creation_gate",
    ]

    for marker in required + examples:
        assert marker in text


def test_operator_input_gate_blocks_forbidden_content() -> None:
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


def test_operator_input_gate_defines_deferred_boundary() -> None:
    text = _text()

    markers = [
        "The gate is closed as a safe operator input decision record.",
        "operator input collection is not allowed without safe operator values",
        "The gate does not claim operator input was collected.",
        "The gate does not claim a candidate was created.",
        "The gate does not claim a real file was selected.",
        "The gate does not claim a real path was validated.",
        "The gate does not claim a real filename was accepted.",
        "The gate does not claim media readiness.",
        "The gate does not claim real-media execution readiness.",
        "The gate does not claim production readiness.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_gate_records_validated_and_not_validated_scope() -> None:
    text = _text()

    validated = [
        "Operator input collection cannot proceed without safe operator values.",
        "The safe stop condition works.",
        "The operator input readiness policy is respected.",
        "No input record id is invented.",
        "No selection id is invented.",
        "No sanitized input token is invented.",
        "No generic file category is invented.",
        "No material owner category is invented.",
        "No confidentiality status is invented.",
        "No locality status is invented.",
        "No single-file status is invented.",
        "No operator attestation is invented.",
        "No file path is invented.",
        "No filename is invented.",
        "No real file is touched.",
        "No dependency command is run.",
    ]
    not_validated = [
        "Real file existence.",
        "Real file readability.",
        "Real file ownership.",
        "Real file confidentiality.",
        "Real file extension.",
        "Real file size.",
        "Real media metadata.",
        "Real FFmpeg behavior.",
        "Real ffprobe behavior.",
        "Real scanner behavior.",
        "Real output report from media.",
        "Real dependency availability.",
    ]

    for marker in validated + not_validated:
        assert marker in text


def test_operator_input_gate_defines_safe_next_step() -> None:
    text = _text()

    markers = [
        "Provide safe operator values in a separate gate.",
        "The values must use placeholder identifiers.",
        "The values must use a redacted input token.",
        "The values must use a generic file category.",
        "The values must use neutral ownership and confidentiality statuses.",
        "The values must confirm local single-file shape.",
        "The values must reject folder, batch, and recursive traversal.",
        "The values must confirm read-only intent.",
        "The values must confirm no upload.",
        "The values must confirm execution is not requested.",
        "The values must confirm stop conditions.",
        "The values must not commit a real absolute path.",
        "The values must not commit a sensitive filename.",
        "The values must not expose customer, company, project, person, scene, take, roll, or camera-card identifiers.",
    ]

    for marker in markers:
        assert marker in text


def test_operator_input_gate_confirms_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop because no safe operator values were provided.",
        "Stop because no input record id exists.",
        "Stop because no placeholder selection id exists.",
        "Stop because no redacted input token exists.",
        "Stop because no generic file category exists.",
        "Stop because no material owner category exists.",
        "Stop because no confidentiality status exists.",
        "Stop because no locality status exists.",
        "Stop because no single-file confirmation exists.",
        "Stop because no read-only confirmation exists.",
        "Stop because no no-upload confirmation exists.",
        "Stop because no operator attestation exists.",
        "Stop because no stop-condition confirmation exists.",
        "Stop because no input verdict exists.",
        "Stop because no real operator input should be invented.",
        "Stop because no real path should be committed.",
        "Stop because no real filename should be committed.",
        "Stop because no customer material is allowed.",
        "Stop because no dependency execution is allowed.",
    ]

    for condition in conditions:
        assert condition in text


def test_operator_input_gate_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Operator sanitized candidate input gate phase is defined.",
        "Base state is recorded.",
        "Operator input readiness gate is referenced.",
        "Sanitized single-file candidate gate is referenced.",
        "Sanitized single-file candidate readiness gate is referenced.",
        "Explicit single-file selection gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Production path scope gate is referenced.",
        "Operator input decision record id is present.",
        "Operator input record type is no values collected.",
        "Operator input decision is deferred.",
        "Operator input status is not collected.",
        "Operator input collection allowed is no.",
        "Operator input collection attempted is no.",
        "Candidate creation allowed is no.",
        "Candidate creation attempted is no.",
        "Input record id created is no.",
        "Selection id created is no.",
        "Sanitized input token created is no.",
        "Generic file category created is no.",
        "Material owner category created is no.",
        "Confidentiality status created is no.",
        "Locality status created is no.",
        "Single-file status created is no.",
        "Operator attestation created is no.",
        "Real file selected is no.",
        "Real file path recorded is no.",
        "Real filename recorded is no.",
        "Real file stat run is no.",
        "Real file open run is no.",
        "Customer file selected is no.",
        "Customer media used is no.",
        "Dependency command run is no.",
        "FFmpeg run is no.",
        "ffprobe run is no.",
        "Scanner run is no.",
        "Deferral reason is explicit.",
        "Required safe operator values are explicit.",
        "Safe example shape is explicit.",
        "Forbidden operator value content is explicit.",
        "Deferred operator input boundary is explicit.",
        "Validated scope is explicit.",
        "Non-validated scope is explicit.",
        "Safe next step is explicit.",
        "Stop conditions are confirmed.",
        "No real media is executed.",
        "No real file is selected.",
        "No customer material is requested.",
        "No dependency command is run.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_operator_input_gate_keeps_limitations_and_safety_active() -> None:
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
        "No operator values are invented in this gate.",
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


def test_operator_input_gate_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this operator sanitized candidate input decision document.",
        "Add one operator sanitized candidate input decision unit test.",
        "Inspect existing operator sanitized candidate input readiness document.",
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
        "No operator value invention.",
        "No candidate creation.",
        "No candidate value invention.",
        "No input record id invention.",
        "No selection id invention.",
        "No sanitized token invention.",
        "No generic category invention.",
        "No owner category invention.",
        "No confidentiality status invention.",
        "No locality status invention.",
        "No single-file status invention.",
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


def test_operator_input_gate_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SAFE_OPERATOR_VALUE_CAPTURE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SAFE_OPERATOR_VALUE_CAPTURE_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent operator sanitized candidate input gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-operator-sanitized-candidate-input-gate-v1-20260702" in text
