from pathlib import Path


DOC_PATH = Path(
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

SELECTION_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_explicit_single_file_selection_readiness_gate_v1.md"
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


def test_candidate_gate_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_SINGLE_FILE_CANDIDATE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SANITIZED_SINGLE_FILE_CANDIDATE_GATE_V1_CLOSED" in text
    assert "READY_FOR_SANITIZED_SINGLE_FILE_CANDIDATE_GATE" in text
    assert "SANITIZED_SINGLE_FILE_CANDIDATE_DEFERRED_PENDING_OPERATOR_CANDIDATE_RECORD" in text


def test_candidate_gate_records_base_state() -> None:
    text = _text()

    assert "b3f7a0455f1c31c721467b0fc7a009c32d75f683" in text
    assert "b3f7a04 docs: add CID Local Media Agent sanitized single file candidate readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-sanitized-single-file-candidate-readiness-gate-v1-20260702" in text


def test_candidate_gate_references_upstream_documents() -> None:
    text = _text()

    assert CANDIDATE_READINESS_DOC.exists()
    assert SELECTION_GATE_DOC.exists()
    assert SELECTION_READINESS_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_sanitized_single_file_candidate_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_candidate_gate_does_not_create_or_execute_anything() -> None:
    text = _text()

    markers = [
        "This gate does not create a candidate.",
        "This gate does not invent a selection id.",
        "This gate does not invent a sanitized input token.",
        "This gate does not invent a generic file category.",
        "This gate does not invent a material owner category.",
        "This gate does not invent a confidentiality status.",
        "This gate does not select a real file.",
        "This gate does not record a real file path.",
        "This gate does not record a real filename.",
        "This gate does not stat a real file.",
        "This gate does not open a real file.",
        "This gate does not execute real media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_gate_explains_safe_deferral() -> None:
    text = _text()

    markers = [
        "A candidate gate must not fabricate a candidate record.",
        "A candidate gate must not fabricate a selection id.",
        "A candidate gate must not fabricate a redacted input token.",
        "A candidate gate must not fabricate a file category.",
        "A candidate gate must not fabricate ownership or confidentiality confirmations.",
        "A candidate gate must not commit real absolute paths.",
        "A candidate gate must not commit sensitive filenames.",
        "A candidate gate must stop if the operator has not provided the sanitized candidate record.",
        "Deferring candidate creation is the correct safe decision when candidate values are missing.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_gate_records_decision_fields() -> None:
    text = _text()

    fields = [
        "CANDIDATE_DECISION_RECORD_ID:",
        "sanitized_single_file_candidate_deferred_v1",
        "CANDIDATE_RECORD_TYPE:",
        "candidate_decision_no_candidate_created",
        "CANDIDATE_DECISION:",
        "DEFERRED_NO_OPERATOR_PROVIDED_SANITIZED_CANDIDATE_RECORD",
        "CANDIDATE_STATUS:",
        "NOT_CREATED",
        "CANDIDATE_CREATION_ALLOWED:",
        "no",
        "CANDIDATE_CREATION_ATTEMPTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_candidate_gate_records_no_created_candidate_values() -> None:
    text = _text()

    fields = [
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
        "READ_ONLY_STATUS_CREATED:",
        "no",
        "NETWORK_NO_UPLOAD_STATUS_CREATED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_candidate_gate_records_no_file_no_customer_no_dependency() -> None:
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


def test_candidate_gate_records_deferral_reasons() -> None:
    text = _text()

    reasons = [
        "No operator-provided sanitized candidate record exists.",
        "No placeholder selection id has been provided.",
        "No redacted input token has been provided.",
        "No generic file category has been provided.",
        "No material owner category has been provided.",
        "No confidentiality status has been provided.",
        "No locality status has been provided.",
        "No single-file confirmation has been provided.",
        "No read-only confirmation has been provided.",
        "No no-upload confirmation has been provided.",
        "No stop-condition confirmation has been provided.",
    ]

    for reason in reasons:
        assert reason in text


def test_candidate_gate_lists_required_operator_candidate_record() -> None:
    text = _text()

    fields = [
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
        "stop_condition_status",
        "candidate_verdict",
    ]

    for field in fields:
        assert field in text


def test_candidate_gate_lists_required_confirmations_and_redaction() -> None:
    text = _text()

    markers = [
        "Confirm the candidate represents exactly one local file.",
        "Confirm the candidate is not a folder.",
        "Confirm the candidate is not a batch list.",
        "Confirm the candidate is not recursive.",
        "Confirm the candidate is not a wildcard.",
        "Confirm the candidate is not a glob pattern.",
        "Confirm the candidate is operator-owned or explicitly approved.",
        "Confirm the candidate is non-confidential.",
        "Confirm no real absolute path will be committed.",
        "Confirm no sensitive filename will be committed.",
        "Confirm no customer identity will be committed.",
        "Confirm source policy remains read-only.",
        "Confirm no upload will occur.",
        "Confirm no dependency execution is requested.",
        "Use a placeholder selection id.",
        "Use a redacted input token.",
        "Use a generic file category.",
        "Do not commit a real absolute path.",
        "Do not commit a sensitive real filename.",
        "Do not commit customer names.",
        "Do not commit project titles.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_gate_defines_deferred_boundary() -> None:
    text = _text()

    markers = [
        "The gate is closed as a safe candidate decision record.",
        "candidate creation is not allowed without operator-provided sanitized candidate values",
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


def test_candidate_gate_records_validated_and_not_validated_scope() -> None:
    text = _text()

    validated = [
        "Candidate creation cannot proceed without operator-provided sanitized values.",
        "The safe stop condition works.",
        "The candidate readiness policy is respected.",
        "No selection id is invented.",
        "No sanitized input token is invented.",
        "No generic file category is invented.",
        "No owner category is invented.",
        "No confidentiality status is invented.",
        "No file path is invented.",
        "No filename is invented.",
        "No real file is touched.",
        "No dependency command is run.",
        "No customer data is captured.",
        "No production claim is made.",
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


def test_candidate_gate_defines_safe_next_step() -> None:
    text = _text()

    markers = [
        "Provide an operator-supplied sanitized candidate record in a separate gate.",
        "The record must use a placeholder selection id.",
        "The record must use a redacted input token.",
        "The record must use a generic file category.",
        "The record must state material owner category.",
        "The record must state confidentiality status.",
        "The record must state local single-file status.",
        "The record must confirm folder rejection.",
        "The record must confirm batch rejection.",
        "The record must confirm recursive rejection.",
        "The record must confirm read-only intent.",
        "The record must confirm no upload.",
        "The record must confirm execution is not requested.",
        "The record must confirm stop conditions.",
        "The record must not commit the real absolute path.",
        "The record must not commit a sensitive filename.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_gate_confirms_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop because no operator-provided sanitized candidate record exists.",
        "Stop because no placeholder selection id exists.",
        "Stop because no redacted input token exists.",
        "Stop because no generic file category exists.",
        "Stop because no material owner category exists.",
        "Stop because no confidentiality status exists.",
        "Stop because no locality status exists.",
        "Stop because no single-file confirmation exists.",
        "Stop because no read-only confirmation exists.",
        "Stop because no no-upload confirmation exists.",
        "Stop because no stop-condition confirmation exists.",
        "Stop because no real candidate should be invented.",
        "Stop because no real path should be committed.",
        "Stop because no real filename should be committed.",
        "Stop because no customer material is allowed.",
        "Stop because no dependency execution is allowed.",
    ]

    for condition in conditions:
        assert condition in text


def test_candidate_gate_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Sanitized single-file candidate gate phase is defined.",
        "Base state is recorded.",
        "Candidate readiness gate is referenced.",
        "Explicit single-file selection gate is referenced.",
        "Explicit single-file selection readiness gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Production path scope gate is referenced.",
        "Candidate decision record id is present.",
        "Candidate record type is no candidate created.",
        "Candidate decision is deferred.",
        "Candidate status is not created.",
        "Candidate creation allowed is no.",
        "Candidate creation attempted is no.",
        "Selection id created is no.",
        "Sanitized input token created is no.",
        "Generic file category created is no.",
        "Material owner category created is no.",
        "Confidentiality status created is no.",
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
        "Required operator candidate record is explicit.",
        "Required confirmations are explicit.",
        "Required redaction is explicit.",
        "Deferred candidate boundary is explicit.",
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


def test_candidate_gate_keeps_limitations_and_safety_active() -> None:
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


def test_candidate_gate_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this sanitized single-file candidate decision document.",
        "Add one sanitized single-file candidate decision unit test.",
        "Inspect existing sanitized single-file candidate readiness document.",
        "Inspect existing explicit single-file selection gate document.",
        "Inspect existing explicit single-file selection readiness document.",
        "Inspect existing real-media preflight controlled execution document.",
        "Inspect existing real-media preflight readiness document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
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


def test_candidate_gate_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.OPERATOR_SANITIZED_CANDIDATE_INPUT.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_OPERATOR_SANITIZED_CANDIDATE_INPUT_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent sanitized single file candidate gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-sanitized-single-file-candidate-gate-v1-20260702" in text
