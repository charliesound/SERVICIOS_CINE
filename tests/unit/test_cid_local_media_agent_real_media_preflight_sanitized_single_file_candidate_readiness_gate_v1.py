from pathlib import Path


DOC_PATH = Path(
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


def test_candidate_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_SINGLE_FILE_CANDIDATE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SANITIZED_SINGLE_FILE_CANDIDATE_READINESS_GATE_V1_CLOSED" in text
    assert "EXPLICIT_SINGLE_FILE_SELECTION_DEFERRED_PENDING_SANITIZED_LOCAL_FILE_CANDIDATE" in text
    assert "READY_FOR_SANITIZED_SINGLE_FILE_CANDIDATE_GATE" in text


def test_candidate_readiness_records_base_state() -> None:
    text = _text()

    assert "9b30379ea5feb1b36f7235380ca651fa1902c396" in text
    assert "9b30379 docs: add CID Local Media Agent explicit single file selection gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-explicit-single-file-selection-gate-v1-20260702" in text


def test_candidate_readiness_references_upstream_documents() -> None:
    text = _text()

    assert SELECTION_GATE_DOC.exists()
    assert SELECTION_READINESS_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_explicit_single_file_selection_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_candidate_readiness_is_readiness_only() -> None:
    text = _text()

    markers = [
        "This gate is candidate readiness only.",
        "This gate does not create a real candidate.",
        "This gate does not select a real file.",
        "This gate does not record a real file path.",
        "This gate does not record a real filename.",
        "This gate does not stat a real file.",
        "This gate does not open a real file.",
        "This gate does not execute real media.",
        "This gate does not request customer media.",
        "This gate does not process customer media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "The explicit selection gate was correctly deferred because no sanitized eligible local file candidate existed.",
        "Before any candidate record is created, the candidate schema must be explicit.",
        "A candidate record must not commit real absolute paths.",
        "A candidate record must not commit sensitive filenames.",
        "A candidate record must not identify a customer, company, person, project, scene, take, or unreleased title.",
        "A candidate record must not imply execution approval.",
        "A candidate record must separate sanitized description from real file access.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_records_core_readiness_fields() -> None:
    text = _text()

    fields = [
        "READINESS_RECORD_ID:",
        "sanitized_single_file_candidate_readiness_v1",
        "READINESS_RECORD_TYPE:",
        "candidate_readiness_only_no_candidate_created",
        "READINESS_DECISION:",
        "ACCEPTED_FOR_SANITIZED_SINGLE_FILE_CANDIDATE_GATE_DRAFTING_ONLY",
        "READINESS_STATUS:",
        "SANITIZED_SINGLE_FILE_CANDIDATE_SCHEMA_DEFINED_WITHOUT_REAL_FILE",
        "FUTURE_CANDIDATE_GATE_ALLOWED_TO_BE_DRAFTED:",
        "yes",
        "CANDIDATE_CREATION_ALLOWED_IN_THIS_GATE:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_candidate_readiness_records_no_file_no_customer_no_dependency() -> None:
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


def test_candidate_readiness_lists_required_candidate_fields() -> None:
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


def test_candidate_readiness_defines_selection_id_policy() -> None:
    text = _text()

    markers = [
        "Use a generated placeholder selection id.",
        "Do not use a customer name in the selection id.",
        "Do not use a company name in the selection id.",
        "Do not use a project title in the selection id.",
        "Do not use a real filename in the selection id.",
        "Do not use a real path fragment in the selection id.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_defines_sanitized_token_and_generic_category_policy() -> None:
    text = _text()

    markers = [
        "Use a redacted input token only.",
        "The token may describe that the candidate is local.",
        "The token may describe that the candidate is a single file.",
        "The token may describe a generic category.",
        "The token must not contain an absolute path.",
        "The token must not contain a customer path.",
        "The token must not contain a personal path.",
        "The token must not contain a project title.",
        "The token must not contain a real filename.",
        "generic_video_file",
        "generic_audio_file",
        "generic_image_file",
        "generic_unknown_media_file",
        "Do not include scene names.",
        "Do not include take numbers.",
        "Do not include project names.",
        "Do not include customer names.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_defines_owner_confidentiality_and_locality_policies() -> None:
    text = _text()

    markers = [
        "internal_operator_owned",
        "separately_approved_non_confidential",
        "unknown_stop_required",
        "customer_named_owner",
        "company_named_owner",
        "project_named_owner",
        "personal_named_owner",
        "confidential_named_owner",
        "non_confidential_confirmed",
        "customer_confidential",
        "production_sensitive",
        "legal_sensitive",
        "personal_data",
        "unreleased_project_identifying",
        "local_single_file_claimed",
        "folder",
        "recursive_folder",
        "batch_list",
        "network_share_without_scope",
        "cloud_sync_folder_without_scope",
        "customer_drive_without_scope",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_defines_read_only_output_network_and_redaction_policies() -> None:
    text = _text()

    markers = [
        "The candidate record must confirm read-only intent.",
        "must not authorize write, rename, move, delete, transcode, extract, upload",
        "The candidate record must confirm a controlled output path will be required later.",
        "must not include a real output path if it contains personal, customer, project, or confidential information.",
        "The candidate record must confirm no upload.",
        "The candidate record must confirm no hidden network access.",
        "The candidate record must confirm no cloud processing.",
        "The candidate record must confirm no external API call.",
        "Use placeholder identifiers.",
        "Use redacted tokens.",
        "Use generic categories.",
        "Do not commit absolute paths.",
        "Do not commit real filenames if sensitive.",
        "Do not commit customer names.",
        "Do not commit project titles.",
    ]

    for marker in markers:
        assert marker in text


def test_candidate_readiness_lists_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop if a real absolute path would be committed.",
        "Stop if a real filename would be committed and it is sensitive.",
        "Stop if customer material is proposed without written scope.",
        "Stop if material ownership is unclear.",
        "Stop if confidentiality is unclear.",
        "Stop if the candidate is a folder.",
        "Stop if the candidate is a batch list.",
        "Stop if recursive traversal is implied.",
        "Stop if the candidate requires upload.",
        "Stop if the candidate requires source modification.",
        "Stop if the candidate requires dependency execution inside the candidate gate.",
        "Stop if execution is requested before a candidate gate is closed.",
        "Stop if production use is implied.",
        "Stop if paid delivery is implied.",
        "Stop if installer or binary delivery is assumed.",
    ]

    for condition in conditions:
        assert condition in text


def test_candidate_readiness_lists_future_candidate_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Candidate has a placeholder selection id.",
        "Candidate has a redacted input token.",
        "Candidate has a generic file category.",
        "Candidate has material owner category.",
        "Candidate has confidentiality status.",
        "Candidate confirms local single-file shape.",
        "Candidate rejects folder input.",
        "Candidate rejects batch input.",
        "Candidate rejects recursive input.",
        "Candidate confirms read-only intent.",
        "Candidate confirms controlled output path requirement.",
        "Candidate confirms no upload.",
        "Candidate confirms redaction.",
        "Candidate confirms execution is not requested.",
        "Candidate confirms stop conditions.",
        "Candidate does not expose path.",
        "Candidate does not expose filename.",
        "Candidate does not expose customer data.",
        "Candidate does not approve execution.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_candidate_readiness_defines_supported_and_unsupported_scope() -> None:
    text = _text()

    supported = [
        "Future sanitized single-file candidate gate drafting.",
        "Future placeholder selection id structure.",
        "Future redacted input token structure.",
        "Future generic file category structure.",
        "Future non-confidentiality confirmation.",
        "Future local-only and read-only confirmation.",
        "Future stop-condition enforcement.",
        "Future separation between candidate record and execution.",
    ]
    unsupported = [
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


def test_candidate_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Sanitized single-file candidate readiness phase is defined.",
        "Base state is recorded.",
        "Explicit single-file selection gate is referenced.",
        "Explicit single-file selection readiness gate is referenced.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Production path scope gate is referenced.",
        "Readiness record id is present.",
        "Readiness record type is candidate readiness only.",
        "Readiness decision allows candidate gate drafting only.",
        "Readiness status is defined without real file.",
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
        "Future candidate record type is defined.",
        "Required candidate fields are listed.",
        "Selection id policy is explicit.",
        "Sanitized input token policy is explicit.",
        "Generic file category policy is explicit.",
        "Material owner category policy is explicit.",
        "Confidentiality status policy is explicit.",
        "Locality status policy is explicit.",
        "Source read-only policy is explicit.",
        "Output path control policy is explicit.",
        "Network policy is explicit.",
        "Redaction policy is explicit.",
        "Stop conditions are listed.",
        "Future candidate pass criteria are listed.",
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


def test_candidate_readiness_keeps_limitations_and_safety_active() -> None:
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


def test_candidate_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this sanitized single-file candidate readiness document.",
        "Add one sanitized single-file candidate readiness unit test.",
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
        "No real-media execution.",
        "No real file selection.",
        "No real file path recording.",
        "No real filename recording.",
        "No real file stat.",
        "No real file open.",
        "No customer media.",
        "No customer files.",
        "No production material.",
        "No confidential material.",
        "No customer file paths.",
        "No media filenames from customer material.",
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


def test_candidate_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_SINGLE_FILE_CANDIDATE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_SANITIZED_SINGLE_FILE_CANDIDATE_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent sanitized single file candidate readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-sanitized-single-file-candidate-readiness-gate-v1-20260702" in text
