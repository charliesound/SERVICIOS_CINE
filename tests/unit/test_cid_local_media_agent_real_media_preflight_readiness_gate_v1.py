from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_readiness_gate_v1.md"
)

PLANNING_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_planning_gate_v1.md"
)

PRIVATE_PILOT_BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_real_media_preflight_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_READINESS_GATE_V1_CLOSED" in text
    assert "REAL_MEDIA_PREFLIGHT_PLANNING_SCOPED" in text
    assert "READY_FOR_SINGLE_FILE_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE" in text


def test_real_media_preflight_readiness_records_base_state() -> None:
    text = _text()

    assert "9e8b194484e2a8caf6556ff9ac1fb8c36229c00c" in text
    assert "9e8b194 docs: add CID Local Media Agent real media preflight planning gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-planning-gate-v1-20260701" in text


def test_real_media_preflight_readiness_references_upstream_documents() -> None:
    text = _text()

    assert PLANNING_DOC.exists()
    assert PRIVATE_PILOT_BOUNDARY_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_planning_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_real_media_preflight_readiness_is_readiness_only() -> None:
    text = _text()

    markers = [
        "This gate is readiness only.",
        "This gate does not execute real media.",
        "This gate does not select a real media file.",
        "This gate does not request customer media.",
        "This gate does not process customer media.",
        "This gate does not approve private pilot execution.",
        "This gate does not approve production use.",
        "This gate does not approve paid delivery.",
        "This gate does not approve folder scanning.",
        "This gate does not approve batch processing.",
        "This gate does not approve recursive traversal.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "Before any execution gate, the readiness conditions must be explicit.",
        "A future execution gate must not invent scope at runtime.",
        "A future execution gate must not accept folders.",
        "A future execution gate must not accept customer media without written scope.",
        "A future execution gate must not run batch or recursive behavior.",
        "must not write, rename, move, delete, transcode, extract, upload, or commit media-derived customer information",
        "must preserve product trust by remaining local-first and read-only",
        "must remain auditable",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_records_core_readiness_fields() -> None:
    text = _text()

    fields = [
        "READINESS_RECORD_ID:",
        "controlled_real_media_preflight_readiness_v1",
        "READINESS_RECORD_TYPE:",
        "readiness_only_no_execution",
        "READINESS_DECISION:",
        "ACCEPTED_FOR_CONTROLLED_EXECUTION_GATE_DRAFTING_ONLY",
        "READINESS_STATUS:",
        "SINGLE_FILE_REAL_MEDIA_PREFLIGHT_READINESS_DEFINED_WITHOUT_EXECUTION",
        "FUTURE_EXECUTION_GATE_ALLOWED_TO_BE_DRAFTED:",
        "yes",
        "FUTURE_EXECUTION_ALLOWED_IN_THIS_GATE:",
        "no",
        "FUTURE_PREFLIGHT_TYPE:",
        "single_file_read_only_metadata_preflight",
    ]

    for field in fields:
        assert field in text


def test_real_media_preflight_readiness_defines_input_selection_policy() -> None:
    text = _text()

    markers = [
        "The future input must be one explicit local file path.",
        "The future input must not be a folder.",
        "The future input must not be recursive.",
        "The future input must not be a wildcard.",
        "The future input must not be a glob pattern.",
        "The future input must not be a batch list.",
        "The future input must not be a cloud sync folder.",
        "The future input must not be a customer drive without written scope.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_defines_material_ownership_policy() -> None:
    text = _text()

    markers = [
        "The future material must be internal-operator-owned or separately approved non-confidential material.",
        "Customer material is forbidden without a written private pilot boundary.",
        "Third-party confidential material is forbidden.",
        "Production-sensitive material is forbidden.",
        "Legal or contractual material is forbidden.",
        "Personal data material is forbidden.",
        "Unapproved media folders are forbidden.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_blocks_folders_batch_recursion_and_network() -> None:
    text = _text()

    markers = [
        "FUTURE_FILE_COUNT_POLICY:",
        "exactly_one_file_after_future_execution_gate_approval",
        "FUTURE_FOLDER_COUNT_POLICY:",
        "zero_folders",
        "FUTURE_BATCH_POLICY:",
        "forbidden",
        "FUTURE_RECURSION_POLICY:",
        "forbidden",
        "FUTURE_NETWORK_POLICY:",
        "no_upload",
        "no_hidden_network_access",
        "no_customer_media_transfer",
        "no_cloud_processing",
        "no_external_api_call",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_defines_source_output_and_forbidden_outputs() -> None:
    text = _text()

    markers = [
        "FUTURE_SOURCE_FILE_POLICY:",
        "read_only_no_write_no_rename_no_move_no_delete",
        "controlled_human_readable_report_only",
        "metadata_summary_only",
        "risk_notes_only",
        "operator_review_notes_only",
        "media_copy",
        "transcoded_media",
        "proxy_media",
        "thumbnail_export",
        "frame_export",
        "audio_extract",
        "subtitle_file",
        "transcript_file",
        "timeline_file",
        "database_write",
        "cloud_upload",
        "repository_committed_media_data",
        "customer_identity_in_report",
        "project_title_in_report",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_defines_redaction_policy() -> None:
    text = _text()

    markers = [
        "Redact absolute paths before any committed artifact.",
        "Do not commit filenames from customer material.",
        "Do not commit customer names.",
        "Do not commit company names.",
        "Do not commit project titles.",
        "Do not commit personal data.",
        "Do not commit media-derived confidential descriptions.",
        "Use placeholder identifiers in committed docs and tests.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_lists_future_operator_checklist() -> None:
    text = _text()

    markers = [
        "Confirm execution gate exists and is approved.",
        "Confirm input is exactly one local file.",
        "Confirm input is not a folder.",
        "Confirm input is not recursive.",
        "Confirm input is not a batch list.",
        "Confirm material owner is known.",
        "Confirm material is non-confidential or separately approved.",
        "Confirm customer material is not used unless explicitly scoped later.",
        "Confirm source file will remain read-only.",
        "Confirm output path is controlled.",
        "Confirm report redaction policy is understood.",
        "Confirm network behavior is local-only.",
        "Confirm no customer promise is made.",
        "Confirm limitations are visible.",
        "Confirm stop conditions are understood.",
        "Confirm no installer or binary expectation exists.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_allows_only_planning_pre_execution_checks() -> None:
    text = _text()

    allowed = [
        "planned_path_shape_review",
        "planned_material_owner_review",
        "planned_confidentiality_review",
        "planned_output_path_review",
        "planned_redaction_review",
        "planned_stop_condition_review",
        "planned_operator_scope_review",
    ]
    forbidden = [
        "real_file_stat_execution",
        "real_file_open_execution",
        "FFmpeg_execution",
        "ffprobe_execution",
        "scanner_execution",
        "media_decode",
        "media_transcode",
        "audio_extraction",
        "frame_extraction",
        "thumbnail_generation",
        "waveform_analysis",
        "transcription",
        "subtitle_generation",
        "sync_analysis",
        "database_write",
        "network_transfer",
        "dependency_execution",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_real_media_preflight_readiness_lists_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop if the input is a folder.",
        "Stop if the input is recursive.",
        "Stop if the input is a batch list.",
        "Stop if the file count is not exactly one.",
        "Stop if ownership is unclear.",
        "Stop if confidentiality is unclear.",
        "Stop if material belongs to a customer without written scope.",
        "Stop if customer identity appears.",
        "Stop if company identity appears.",
        "Stop if project title appears.",
        "Stop if a customer file path appears.",
        "Stop if a customer filename appears.",
        "Stop if source file modification could occur.",
        "Stop if output path is uncontrolled.",
        "Stop if output path is inside source media folder without approval.",
        "Stop if network transfer is requested.",
        "Stop if dependency behavior is unclear.",
        "Stop if operator cannot explain limitations.",
        "Stop if prospect interprets the test as production use.",
        "Stop if paid delivery is discussed as approved.",
        "Stop if installer or binary delivery is assumed.",
    ]

    for condition in conditions:
        assert condition in text


def test_real_media_preflight_readiness_defines_future_success_and_failure_criteria() -> None:
    text = _text()

    success = [
        "A single local file is explicitly selected in the future execution gate.",
        "The selected file is not customer material unless separately approved later.",
        "The selected file is not confidential material.",
        "The source file remains untouched.",
        "The output is a controlled report only.",
        "No upload occurs.",
        "No batch processing occurs.",
        "No recursive traversal occurs.",
        "No customer data is committed.",
        "No media file is committed.",
        "The result is auditable.",
        "The limitations are visible.",
    ]
    failure = [
        "Any write to source media.",
        "Any rename of source media.",
        "Any move of source media.",
        "Any delete of source media.",
        "Any unapproved upload.",
        "Any batch behavior.",
        "Any recursive behavior.",
        "Any customer data committed to repository.",
        "Any media committed to repository.",
        "Any unclear ownership.",
        "Any unclear confidentiality.",
        "Any expectation that this is production use.",
        "Any inability to audit what happened.",
    ]

    for marker in success + failure:
        assert marker in text


def test_real_media_preflight_readiness_defines_approval_boundary() -> None:
    text = _text()

    markers = [
        "This readiness gate only allows drafting a separate controlled execution gate.",
        "This readiness gate does not allow actual execution.",
        "This readiness gate does not allow selecting or naming a real file.",
        "This readiness gate does not allow collecting customer media.",
        "This readiness gate does not allow running dependency commands.",
        "This readiness gate does not allow changing implementation.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_readiness_defines_supported_and_unsupported_next_use() -> None:
    text = _text()

    supported = [
        "Future controlled execution gate drafting.",
        "Future one-file real-media preflight proof.",
        "Future local-first read-only validation.",
        "Future operator checklist enforcement.",
        "Future stop-condition enforcement.",
        "Future redaction policy enforcement.",
        "Future auditability.",
    ]
    unsupported = [
        "Executing real media now.",
        "Selecting a real file now.",
        "Processing customer material now.",
        "Running FFmpeg now.",
        "Running ffprobe now.",
        "Running scanner behavior now.",
        "Scanning folders now.",
        "Batch processing now.",
        "Recursive traversal now.",
        "Private pilot execution now.",
        "Production use now.",
        "Paid delivery now.",
        "Installer creation now.",
        "Binary distribution now.",
    ]

    for marker in supported + unsupported:
        assert marker in text


def test_real_media_preflight_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Real-media preflight readiness phase is defined.",
        "Base state is recorded.",
        "Real-media preflight planning gate is referenced.",
        "Private pilot boundary gate is referenced.",
        "Production path scope gate is referenced.",
        "Readiness record id is present.",
        "Readiness record type is readiness only.",
        "Readiness decision allows controlled execution gate drafting only.",
        "Readiness status is defined without execution.",
        "Future execution is not allowed in this gate.",
        "Future preflight type remains single-file read-only metadata preflight.",
        "Future input selection policy is explicit.",
        "Future material ownership policy is explicit.",
        "Future file count policy is exactly one after later approval.",
        "Future folder count policy is zero folders.",
        "Future batch policy is forbidden.",
        "Future recursion policy is forbidden.",
        "Future network policy forbids upload.",
        "Future source file policy is read-only.",
        "Future allowed output policy is report-only.",
        "Future forbidden output policy is explicit.",
        "Future redaction policy is explicit.",
        "Future operator checklist is explicit.",
        "Future allowed pre-execution checks are planning-only.",
        "Forbidden execution checks in this gate are explicit.",
        "Future stop conditions are listed.",
        "Future success criteria are listed.",
        "Future failure criteria are listed.",
        "Readiness approval boundary is explicit.",
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


def test_real_media_preflight_readiness_keeps_limitations_and_safety_active() -> None:
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
        "No real media is allowed to be executed in this gate.",
        "No real media file is selected in this gate.",
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


def test_real_media_preflight_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this real-media preflight readiness document.",
        "Add one real-media preflight readiness unit test.",
        "Inspect existing real-media preflight planning document.",
        "Inspect existing private pilot boundary document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real-media execution.",
        "No real file selection.",
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


def test_real_media_preflight_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_EXECUTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent real media preflight readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-readiness-gate-v1-20260702" in text
