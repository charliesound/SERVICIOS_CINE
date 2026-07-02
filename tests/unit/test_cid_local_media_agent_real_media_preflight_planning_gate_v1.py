from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_planning_gate_v1.md"
)

PRIVATE_PILOT_BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md"
)

PRIVATE_PILOT_BOUNDARY_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_readiness_gate_v1.md"
)

PROSPECT_FEEDBACK_CAPTURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_real_media_preflight_planning_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.PLANNING.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_PLANNING_GATE_V1_CLOSED" in text
    assert "SAFE_PRIVATE_PILOT_BOUNDARY_PLACEHOLDER_DEFINED" in text
    assert "REAL_MEDIA_PREFLIGHT_PLANNING_SCOPED" in text


def test_real_media_preflight_planning_records_base_state() -> None:
    text = _text()

    assert "cf0aa0d2834f01930f088cbd7a5e284159a30301" in text
    assert "cf0aa0d docs: add CID Local Media Agent private pilot boundary gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-private-pilot-boundary-gate-v1-20260701" in text


def test_real_media_preflight_planning_references_upstream_documents() -> None:
    text = _text()

    assert PRIVATE_PILOT_BOUNDARY_DOC.exists()
    assert PRIVATE_PILOT_BOUNDARY_READINESS_DOC.exists()
    assert PROSPECT_FEEDBACK_CAPTURE_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_private_pilot_boundary_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_real_media_preflight_planning_is_planning_only() -> None:
    text = _text()

    markers = [
        "This gate is planning only.",
        "This gate does not execute real media.",
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


def test_real_media_preflight_planning_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "Before touching any real audiovisual file, the exact allowed scope must be planned.",
        "A future real-media preflight must remain read-only.",
        "A future real-media preflight must be single-file first.",
        "must use explicit operator-owned material or separately approved non-confidential material",
        "must not start with customer folders",
        "must not start with recursive scan",
        "must not start with batch processing",
        "must not promise production readiness",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_planning_records_core_planning_fields() -> None:
    text = _text()

    fields = [
        "PLANNING_RECORD_ID:",
        "controlled_real_media_preflight_planning_v1",
        "PLANNING_RECORD_TYPE:",
        "planning_only_no_execution",
        "PLANNING_DECISION:",
        "ACCEPTED_FOR_SCOPE_PLANNING_ONLY_NOT_FOR_EXECUTION",
        "PLANNING_STATUS:",
        "REAL_MEDIA_PREFLIGHT_SCOPE_DEFINED_WITHOUT_EXECUTION",
        "FUTURE_PREFLIGHT_TYPE:",
        "single_file_read_only_metadata_preflight",
        "FUTURE_EXECUTION_STATUS:",
        "not_approved_in_this_gate",
    ]

    for field in fields:
        assert field in text


def test_real_media_preflight_planning_defines_future_material_ownership() -> None:
    text = _text()

    markers = [
        "FUTURE_ALLOWED_MATERIAL_OWNER:",
        "internal_operator_owned_material_or_separately_approved_non_confidential_material",
        "FUTURE_FORBIDDEN_MATERIAL_OWNER:",
        "customer_material_without_written_scope",
        "third_party_confidential_material",
        "production_sensitive_material",
        "legal_or_contractual_material",
        "personal_data",
        "unapproved_media_folders",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_planning_limits_input_shape_file_count_folder_count() -> None:
    text = _text()

    markers = [
        "FUTURE_ALLOWED_INPUT_SHAPE:",
        "one_explicit_file_path_only_after_future_readiness_gate",
        "FUTURE_FORBIDDEN_INPUT_SHAPE:",
        "folder_path",
        "recursive_path",
        "wildcard_path",
        "glob_pattern",
        "batch_list",
        "FUTURE_ALLOWED_FILE_COUNT:",
        "one_file_only_after_future_readiness_gate",
        "FUTURE_ALLOWED_FOLDER_COUNT:",
        "zero_folders",
        "FUTURE_RECURSIVE_TRAVERSAL:",
        "forbidden",
        "FUTURE_BATCH_PROCESSING:",
        "forbidden",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_planning_defines_allowed_and_forbidden_outputs() -> None:
    text = _text()

    markers = [
        "FUTURE_ALLOWED_OUTPUT:",
        "human_readable_preflight_report",
        "explicit_metadata_summary",
        "risk_notes_without_media_copy",
        "operator_review_notes",
        "FUTURE_FORBIDDEN_OUTPUT:",
        "media_copy",
        "transcoded_media",
        "proxy_media",
        "thumbnail_export",
        "audio_extract",
        "subtitle_file",
        "transcript_file",
        "timeline_file",
        "database_write",
        "cloud_upload",
        "public_artifact",
        "repository_committed_media_data",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_planning_defines_source_output_privacy_and_redaction_policy() -> None:
    text = _text()

    markers = [
        "FUTURE_SOURCE_FILE_POLICY:",
        "read_only_no_write_no_rename_no_move_no_delete",
        "FUTURE_OUTPUT_PATH_POLICY:",
        "controlled_temp_or_reports_path_outside_customer_source_folder",
        "FUTURE_PRIVACY_POLICY:",
        "no_upload",
        "no_hidden_network_access",
        "no_customer_identity_in_report",
        "no_project_title_in_report",
        "no_absolute_customer_path_in_committed_artifact",
        "FUTURE_REDACTION_POLICY:",
        "Redact absolute paths before any committed artifact.",
        "Do not commit filenames from customer material.",
        "Do not commit customer names.",
        "Do not commit company names.",
        "Do not commit project titles.",
        "Do not commit personal data.",
    ]

    for marker in markers:
        assert marker in text


def test_real_media_preflight_planning_defines_technical_checks_and_forbidden_execution() -> None:
    text = _text()

    allowed = [
        "file_exists_check",
        "file_is_regular_check",
        "file_size_check",
        "extension_observation",
        "read_permission_observation",
        "planned_metadata_preflight_only_after_future_gate",
    ]
    forbidden = [
        "real_file_execution",
        "FFmpeg_execution",
        "ffprobe_execution",
        "scanner_execution",
        "media_decode",
        "media_transcode",
        "audio_extraction",
        "frame_extraction",
        "waveform_analysis",
        "transcription",
        "subtitle_generation",
        "sync_analysis",
        "database_write",
        "network_transfer",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_real_media_preflight_planning_lists_future_operator_prechecks() -> None:
    text = _text()

    prechecks = [
        "Confirm material owner.",
        "Confirm material is non-confidential.",
        "Confirm file count is one.",
        "Confirm input is a file, not a folder.",
        "Confirm source file remains read-only.",
        "Confirm output path is controlled.",
        "Confirm network behavior is disabled or irrelevant.",
        "Confirm report redaction rules.",
        "Confirm stop conditions.",
        "Confirm no customer promises.",
    ]

    for marker in prechecks:
        assert marker in text


def test_real_media_preflight_planning_lists_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop if input is a folder.",
        "Stop if input is recursive.",
        "Stop if input is a batch list.",
        "Stop if file ownership is unclear.",
        "Stop if material confidentiality is unclear.",
        "Stop if material belongs to a customer without written scope.",
        "Stop if project title or customer identity appears.",
        "Stop if source file could be modified.",
        "Stop if output path is inside source media folder without approval.",
        "Stop if dependency behavior is unclear.",
        "Stop if network transfer is requested.",
        "Stop if operator cannot explain limitations.",
        "Stop if prospect interprets preflight as production use.",
        "Stop if paid delivery is discussed as approved.",
        "Stop if installer or binary delivery is assumed.",
    ]

    for condition in conditions:
        assert condition in text


def test_real_media_preflight_planning_defines_future_success_and_failure_criteria() -> None:
    text = _text()

    success = [
        "One explicitly scoped local file is selected.",
        "Material owner is known.",
        "Material is non-confidential or separately approved.",
        "Source file remains untouched.",
        "Output is a controlled report only.",
        "No upload occurs.",
        "No batch processing occurs.",
        "No recursive traversal occurs.",
        "No customer data is committed.",
        "Result is auditable.",
        "Limitations are visible.",
    ]
    failure = [
        "Any write to source media.",
        "Any unapproved upload.",
        "Any batch or recursive behavior.",
        "Any customer data committed to repository.",
        "Any unclear ownership.",
        "Any unclear confidentiality.",
        "Any expectation that this is production use.",
        "Any inability to audit what happened.",
    ]

    for marker in success + failure:
        assert marker in text


def test_real_media_preflight_planning_defines_supported_and_unsupported_next_use() -> None:
    text = _text()

    supported = [
        "Future readiness gate for one-file real-media preflight.",
        "Future explicit operator prechecks.",
        "Future safe redaction policy.",
        "Future stop-condition enforcement.",
        "Future transition from placeholder-only demo toward controlled real-media proof.",
    ]
    unsupported = [
        "Executing real media now.",
        "Processing customer material now.",
        "Running FFmpeg now.",
        "Running ffprobe now.",
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


def test_real_media_preflight_planning_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Real-media preflight planning phase is defined.",
        "Base state is recorded.",
        "Private pilot boundary gate is referenced.",
        "Production path scope gate is referenced.",
        "Planning record id is present.",
        "Planning record type is planning only.",
        "Planning decision is not execution.",
        "Future preflight type is single-file read-only metadata preflight.",
        "Future execution status is not approved in this gate.",
        "Future allowed material owner is defined.",
        "Future forbidden material owner is defined.",
        "Future allowed input shape is one explicit file path only after later readiness.",
        "Future forbidden input shapes are listed.",
        "Future allowed file count is one after later readiness.",
        "Future allowed folder count is zero.",
        "Future recursive traversal is forbidden.",
        "Future batch processing is forbidden.",
        "Future allowed output is report-only.",
        "Future forbidden outputs are listed.",
        "Future source file policy is read-only.",
        "Future output path policy is controlled.",
        "Future privacy policy is explicit.",
        "Future redaction policy is explicit.",
        "Future technical checks are planned.",
        "Forbidden technical checks in this gate are explicit.",
        "Future operator prechecks are listed.",
        "Future stop conditions are listed.",
        "Future success criteria are listed.",
        "Future failure criteria are listed.",
        "No real media is executed.",
        "No customer material is requested.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_real_media_preflight_planning_keeps_limitations_and_safety_confirmation_active() -> None:
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


def test_real_media_preflight_planning_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this real-media preflight planning document.",
        "Add one real-media preflight planning unit test.",
        "Inspect existing private pilot boundary document.",
        "Inspect existing private pilot boundary readiness document.",
        "Inspect existing prospect feedback capture document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real-media execution.",
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


def test_real_media_preflight_planning_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent real media preflight planning gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-planning-gate-v1-20260701" in text
