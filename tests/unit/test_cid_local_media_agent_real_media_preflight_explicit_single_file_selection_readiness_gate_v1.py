from pathlib import Path


DOC_PATH = Path(
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

PLANNING_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_media_preflight_planning_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_selection_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.EXPLICIT_SINGLE_FILE_SELECTION.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_EXPLICIT_SINGLE_FILE_SELECTION_READINESS_GATE_V1_CLOSED" in text
    assert "CONTROLLED_EXECUTION_DEFERRED_PENDING_EXPLICIT_SINGLE_LOCAL_FILE" in text
    assert "READY_FOR_EXPLICIT_SINGLE_FILE_SELECTION_GATE" in text


def test_selection_readiness_records_base_state() -> None:
    text = _text()

    assert "35e61ed9c891b61e078fbd459d34861b88dd6a9b" in text
    assert "35e61ed docs: add CID Local Media Agent real media preflight controlled execution gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-controlled-execution-gate-v1-20260702" in text


def test_selection_readiness_references_upstream_documents() -> None:
    text = _text()

    assert CONTROLLED_EXECUTION_DOC.exists()
    assert READINESS_DOC.exists()
    assert PLANNING_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_execution_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_planning_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text


def test_selection_readiness_is_readiness_only() -> None:
    text = _text()

    markers = [
        "This gate is selection readiness only.",
        "This gate does not select a real file.",
        "This gate does not record a real file path.",
        "This gate does not record a real filename.",
        "This gate does not execute real media.",
        "This gate does not open real media.",
        "This gate does not stat real media.",
        "This gate does not request customer media.",
        "This gate does not process customer media.",
        "This gate does not run FFmpeg.",
        "This gate does not run ffprobe.",
        "This gate does not run scanner behavior.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "The controlled execution gate was correctly deferred because no explicit eligible single local file existed.",
        "Before selecting any real file, the selection rules must be explicit.",
        "The system must not invent a path.",
        "The system must not silently choose a file.",
        "The system must not accept a folder.",
        "The system must not accept a batch list.",
        "The system must not accept a recursive pattern.",
        "must not record sensitive file paths in committed artifacts",
        "must not record customer or project-identifying filenames in committed artifacts",
        "must separate selection readiness from real execution",
    ]

    for marker in markers:
        assert marker in text


def test_selection_readiness_records_core_readiness_fields() -> None:
    text = _text()

    fields = [
        "READINESS_RECORD_ID:",
        "explicit_single_file_selection_readiness_v1",
        "READINESS_RECORD_TYPE:",
        "selection_readiness_only_no_file_selected",
        "READINESS_DECISION:",
        "ACCEPTED_FOR_EXPLICIT_SINGLE_FILE_SELECTION_GATE_DRAFTING_ONLY",
        "READINESS_STATUS:",
        "SINGLE_FILE_SELECTION_RULES_DEFINED_WITHOUT_SELECTION",
        "FUTURE_SELECTION_GATE_ALLOWED_TO_BE_DRAFTED:",
        "yes",
        "FILE_SELECTION_ALLOWED_IN_THIS_GATE:",
        "no",
        "REAL_FILE_SELECTED:",
        "no",
    ]

    for field in fields:
        assert field in text


def test_selection_readiness_records_no_path_no_filename_no_customer_no_dependency() -> None:
    text = _text()

    fields = [
        "REAL_FILE_PATH_RECORDED:",
        "no",
        "REAL_FILENAME_RECORDED:",
        "no",
        "CUSTOMER_FILE_SELECTED:",
        "no",
        "DEPENDENCY_COMMAND_RUN:",
        "no",
        "FUTURE_SELECTION_TYPE:",
        "one_explicit_local_file_selection",
    ]

    for field in fields:
        assert field in text


def test_selection_readiness_defines_allowed_and_forbidden_sources() -> None:
    text = _text()

    markers = [
        "operator_owned_non_confidential_local_file",
        "separately_approved_non_confidential_local_file",
        "customer_material_without_written_scope",
        "confidential_customer_material",
        "production_sensitive_material",
        "third_party_confidential_material",
        "legal_or_contractual_material",
        "personal_data_material",
        "cloud_sync_folder",
        "network_share_without_scope",
        "unapproved_media_folder",
    ]

    for marker in markers:
        assert marker in text


def test_selection_readiness_lists_required_selection_fields() -> None:
    text = _text()

    fields = [
        "selection_record_id",
        "selection_status",
        "operator_confirmation",
        "material_owner_category",
        "confidentiality_confirmation",
        "locality_confirmation",
        "file_shape_confirmation",
        "folder_rejection_confirmation",
        "batch_rejection_confirmation",
        "recursive_rejection_confirmation",
        "source_read_only_confirmation",
        "output_path_control_confirmation",
        "network_no_upload_confirmation",
        "redaction_confirmation",
        "stop_condition_confirmation",
    ]

    for field in fields:
        assert field in text


def test_selection_readiness_blocks_sensitive_committed_fields() -> None:
    text = _text()

    fields = [
        "absolute_personal_path",
        "absolute_customer_path",
        "customer_filename",
        "project_title",
        "company_name",
        "customer_name",
        "email",
        "phone_number",
        "confidential_scene_description",
        "media_derived_sensitive_description",
    ]

    for field in fields:
        assert field in text


def test_selection_readiness_defines_path_and_filename_representation() -> None:
    text = _text()

    markers = [
        "placeholder_identifier_only",
        "redacted_path_token",
        "non_sensitive_operator_label",
        "home_directory_path",
        "external_drive_real_path",
        "customer_drive_real_path",
        "network_share_real_path",
        "cloud_sync_real_path",
        "project_named_path",
        "person_named_path",
        "placeholder_filename_token",
        "generic_extension_category",
        "customer_original_filename",
        "project_original_filename",
        "scene_or_take_identifying_filename",
        "personal_name_in_filename",
        "company_name_in_filename",
        "unreleased_title_in_filename",
    ]

    for marker in markers:
        assert marker in text


def test_selection_readiness_defines_future_input_shape_requirements() -> None:
    text = _text()

    requirements = [
        "The future input must be exactly one local file.",
        "The future input must not be a folder.",
        "The future input must not be recursive.",
        "The future input must not be a wildcard.",
        "The future input must not be a glob pattern.",
        "The future input must not be a batch list.",
        "The future input must not be a directory tree.",
        "The future input must not be a customer drive.",
        "The future input must not be a cloud sync folder.",
    ]

    for requirement in requirements:
        assert requirement in text


def test_selection_readiness_lists_future_operator_confirmations_and_redaction() -> None:
    text = _text()

    markers = [
        "Confirm the file is one explicit local file.",
        "Confirm the file is operator-owned or separately approved.",
        "Confirm the file is non-confidential.",
        "Confirm the file is not customer material unless later written scope exists.",
        "Confirm no customer identity will be committed.",
        "Confirm no absolute path will be committed.",
        "Confirm no sensitive filename will be committed.",
        "Confirm source policy is read-only.",
        "Confirm output path will be controlled.",
        "Confirm no upload will occur.",
        "Use a placeholder selection id.",
        "Use a redacted input token.",
        "Use a generic file category.",
        "Do not commit the real absolute path.",
        "Do not commit customer names.",
        "Do not commit project titles.",
    ]

    for marker in markers:
        assert marker in text


def test_selection_readiness_lists_stop_conditions() -> None:
    text = _text()

    conditions = [
        "Stop if more than one file is proposed.",
        "Stop if a folder is proposed.",
        "Stop if a wildcard is proposed.",
        "Stop if a glob is proposed.",
        "Stop if a batch list is proposed.",
        "Stop if recursive traversal is implied.",
        "Stop if material ownership is unclear.",
        "Stop if confidentiality is unclear.",
        "Stop if customer material is proposed without written scope.",
        "Stop if a customer path would be committed.",
        "Stop if a customer filename would be committed.",
        "Stop if a project title would be committed.",
        "Stop if network transfer is requested.",
        "Stop if source modification is possible.",
        "Stop if output path is uncontrolled.",
        "Stop if operator cannot explain limitations.",
        "Stop if execution is requested before selection gate closure.",
        "Stop if production use is implied.",
        "Stop if paid delivery is implied.",
    ]

    for condition in conditions:
        assert condition in text


def test_selection_readiness_defines_supported_and_unsupported_scope() -> None:
    text = _text()

    supported = [
        "Future explicit single-file selection gate drafting.",
        "Future safe placeholder representation of a selected file.",
        "Future redaction enforcement before any real execution.",
        "Future operator confirmation checklist.",
        "Future stop-condition enforcement.",
        "Future separation between selection and execution.",
    ]
    unsupported = [
        "Selecting a real file now.",
        "Recording a real path now.",
        "Recording a real filename now.",
        "Executing real media now.",
        "Opening real media now.",
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


def test_selection_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Explicit single-file selection readiness phase is defined.",
        "Base state is recorded.",
        "Controlled execution gate is referenced.",
        "Real-media preflight readiness gate is referenced.",
        "Real-media preflight planning gate is referenced.",
        "Production path scope gate is referenced.",
        "Readiness record id is present.",
        "Readiness record type is selection readiness only.",
        "Readiness decision allows selection gate drafting only.",
        "Readiness status is defined without selection.",
        "File selection is not allowed in this gate.",
        "No real file is selected.",
        "No real file path is recorded.",
        "No real filename is recorded.",
        "No customer file is selected.",
        "No dependency command is run.",
        "Future selection type is one explicit local file.",
        "Future allowed selection source is defined.",
        "Future forbidden selection source is defined.",
        "Future required selection fields are listed.",
        "Forbidden committed selection fields are listed.",
        "Allowed path representation is placeholder/redacted only.",
        "Forbidden path representation is listed.",
        "Allowed filename representation is placeholder/generic only.",
        "Forbidden filename representation is listed.",
        "Future input shape requirements are listed.",
        "Future operator confirmations are listed.",
        "Future redaction requirements are listed.",
        "Future stop conditions are listed.",
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


def test_selection_readiness_keeps_limitations_and_safety_active() -> None:
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


def test_selection_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this explicit single-file selection readiness document.",
        "Add one explicit single-file selection readiness unit test.",
        "Inspect existing real-media preflight controlled execution document.",
        "Inspect existing real-media preflight readiness document.",
        "Inspect existing real-media preflight planning document.",
        "Inspect existing production use path scope document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real-media execution.",
        "No real file selection.",
        "No real file path recording.",
        "No real filename recording.",
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


def test_selection_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.EXPLICIT_SINGLE_FILE_SELECTION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_EXPLICIT_SINGLE_FILE_SELECTION_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent explicit single file selection readiness gate" in text
    assert "cid-dev-stable-local-media-agent-real-media-preflight-explicit-single-file-selection-readiness-gate-v1-20260702" in text
