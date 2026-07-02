from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_private_pilot_boundary_readiness_gate_v1.md"
)

FEEDBACK_CAPTURE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)

MEETING_PACK_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_private_pilot_boundary_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PRIVATE_PILOT_BOUNDARY.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRIVATE_PILOT_BOUNDARY_GATE_V1_CLOSED" in text
    assert "READY_FOR_SAFE_PRIVATE_PILOT_BOUNDARY_DRAFTING" in text
    assert "SAFE_PRIVATE_PILOT_BOUNDARY_PLACEHOLDER_DEFINED" in text


def test_private_pilot_boundary_records_base_state() -> None:
    text = _text()

    assert "3934e145b58c7ce908327abcb6086bf566e9d018" in text
    assert "3934e14 docs: add CID Local Media Agent private pilot boundary readiness gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-private-pilot-boundary-readiness-gate-v1-20260701" in text


def test_private_pilot_boundary_references_upstream_documents() -> None:
    text = _text()

    assert READINESS_DOC.exists()
    assert FEEDBACK_CAPTURE_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert MEETING_PACK_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_private_pilot_boundary_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text


def test_private_pilot_boundary_is_placeholder_only() -> None:
    text = _text()

    markers = [
        "This gate defines a placeholder boundary only.",
        "This gate does not approve private pilot execution.",
        "This gate does not define a real customer.",
        "This gate does not include customer names.",
        "This gate does not request customer files.",
        "This gate does not process real media.",
        "This gate does not approve production use.",
        "This gate does not approve paid delivery.",
        "BOUNDARY_RECORD_TYPE:",
        "non_customer_placeholder_boundary",
        "BOUNDARY_DECISION:",
        "ACCEPTED_FOR_STRUCTURE_ONLY_NOT_FOR_EXECUTION",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_records_core_boundary_fields() -> None:
    text = _text()

    fields = [
        "BOUNDARY_RECORD_ID:",
        "controlled_private_pilot_boundary_placeholder_v1",
        "BOUNDARY_STATUS:",
        "DRAFT_BOUNDARY_DEFINED_WITHOUT_REAL_CUSTOMER",
        "PILOT_STATUS:",
        "NOT_APPROVED_FOR_EXECUTION",
        "CUSTOMER_CATEGORY:",
        "producer_or_executive_producer_placeholder",
        "CUSTOMER_IDENTITY:",
        "not_recorded",
        "COMPANY_IDENTITY:",
        "not_recorded",
        "CONTACT_DETAILS:",
        "not_recorded",
        "OPERATOR:",
        "internal_operator_only",
    ]

    for field in fields:
        assert field in text


def test_private_pilot_boundary_records_machine_network_and_material_policy() -> None:
    text = _text()

    markers = [
        "MACHINE:",
        "placeholder_local_operator_machine_to_be_defined_later",
        "EXECUTION_LOCATION:",
        "local_only",
        "NETWORK_POLICY:",
        "no_upload_by_default",
        "no_hidden_network_access",
        "no_customer_media_transfer",
        "MATERIAL_CATEGORY:",
        "placeholder_only_until_separate_real_media_preflight_planning_gate",
        "ALLOWED_MATERIAL_TYPE:",
        "non_customer_controlled_fixture_or_future_explicitly_scoped_non_confidential_real_media_after_separate_approval",
        "FORBIDDEN_MATERIAL_TYPE:",
        "confidential_customer_material",
        "unapproved_media_folders",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_blocks_files_folders_recursion_and_batch() -> None:
    text = _text()

    markers = [
        "ALLOWED_FILE_COUNT:",
        "zero_customer_files_in_this_gate",
        "ALLOWED_FOLDER_COUNT:",
        "zero_customer_folders_in_this_gate",
        "RECURSIVE_TRAVERSAL:",
        "forbidden",
        "BATCH_PROCESSING:",
        "forbidden",
        "ALLOWED_OUTPUT:",
        "controlled_human_readable_report_placeholder_only",
        "FORBIDDEN_OUTPUT:",
        "customer_media_copy",
        "hidden_upload",
        "destructive_write",
        "source_file_modification",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_records_source_retention_support_and_execution_policy() -> None:
    text = _text()

    markers = [
        "SOURCE_FILE_POLICY:",
        "read_only_required_for_any_future_pilot",
        "OUTPUT_PATH_POLICY:",
        "controlled_output_path_required_for_any_future_pilot",
        "RETENTION_RULE:",
        "no_customer_data_retained_in_this_gate",
        "DELETION_RULE:",
        "no_customer_data_exists_in_this_gate",
        "SUPPORT_OWNER:",
        "internal_operator_placeholder",
        "ROLLBACK_RULE:",
        "stop_execution_and_preserve_source_files_untouched",
        "APPROVAL_REQUIRED_BEFORE_EXECUTION:",
        "yes",
        "NEXT_EXECUTION_ALLOWED:",
        "none_in_this_gate",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_records_failure_criteria_and_stop_conditions() -> None:
    text = _text()

    markers = [
        "Any ambiguity that could be interpreted as approval for customer material",
        "Stop if a real customer name is introduced.",
        "Stop if a company name is introduced.",
        "Stop if a customer file path is introduced.",
        "Stop if a customer media filename is introduced.",
        "Stop if real material is requested.",
        "Stop if customer material is requested.",
        "Stop if recursive scan is requested.",
        "Stop if batch processing is requested.",
        "Stop if upload is requested.",
        "Stop if source file modification is requested.",
        "Stop if the pilot is interpreted as production use.",
        "Stop if paid delivery is discussed as approved.",
        "Stop if installer or binary delivery is assumed.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_records_commercial_and_production_status() -> None:
    text = _text()

    assert "COMMERCIAL_STATUS:" in text
    assert "not_paid_delivery" in text
    assert "PRODUCTION_STATUS:" in text
    assert "not_production_use" in text
    assert "APPROVAL_REQUIRED_BEFORE_EXECUTION:" in text
    assert "yes" in text


def test_private_pilot_boundary_explains_accepted_and_limited_scope() -> None:
    text = _text()

    markers = [
        "The boundary is accepted because it records the required shape of a future private pilot",
        "without naming a customer, requesting customer files, processing real media, or approving execution.",
        "The boundary is limited because it is not connected to a real prospect",
        "real machine, real material path, real support window, real commercial agreement",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_defines_supported_and_unsupported_next_use() -> None:
    text = _text()

    supported = [
        "Future private pilot planning.",
        "Future real-media preflight planning.",
        "Future privacy and data-handling discussion.",
        "Future installation/dependency planning.",
        "Future commercial scope discussion.",
        "Expectation control before any real customer execution.",
    ]
    unsupported = [
        "Private pilot execution.",
        "Real media processing.",
        "Customer material processing.",
        "Folder scanning.",
        "Batch processing.",
        "Recursive traversal.",
        "Production use.",
        "Paid delivery.",
        "Public demo.",
        "Installer delivery.",
        "Binary distribution.",
        "Customer onboarding.",
    ]

    for marker in supported + unsupported:
        assert marker in text


def test_private_pilot_boundary_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Private pilot boundary phase is defined.",
        "Base state is recorded.",
        "Private pilot boundary readiness gate is referenced.",
        "Feedback capture gate is referenced.",
        "Production use path scope gate is referenced.",
        "Meeting pack is referenced.",
        "Boundary record id is present.",
        "Boundary record type is non-customer placeholder.",
        "Boundary decision is structure only.",
        "Pilot status is not approved for execution.",
        "Customer identity is not recorded.",
        "Company identity is not recorded.",
        "Contact details are not recorded.",
        "Operator is internal only.",
        "Execution location is local-only.",
        "Network policy forbids upload by default.",
        "Material category remains placeholder only.",
        "Allowed file count is zero customer files.",
        "Allowed folder count is zero customer folders.",
        "Recursive traversal is forbidden.",
        "Batch processing is forbidden.",
        "Allowed output is controlled report placeholder only.",
        "Source file policy is read-only for future pilot.",
        "Retention rule avoids customer data.",
        "Stop conditions are explicit.",
        "Commercial status is not paid delivery.",
        "Production status is not production use.",
        "Execution approval is required later.",
        "No real customer is named.",
        "No customer material is requested.",
        "No real media is processed.",
        "No private pilot execution is approved.",
        "No production use is approved.",
        "No paid delivery is approved.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_private_pilot_boundary_keeps_limitations_active() -> None:
    text = _text()

    limitations = [
        "Production use is not approved.",
        "Paid delivery is not approved.",
        "Private pilot execution is not approved.",
        "Real media processing is not approved.",
        "Customer material processing is not approved.",
        "Folder scanning is not approved.",
        "Batch processing is not approved.",
        "Recursive traversal is not approved.",
        "Transcription is not approved.",
        "Subtitles are not approved.",
        "Sync is not approved.",
        "DaVinci Resolve integration is not approved.",
        "Avid integration is not approved.",
        "SaaS integration is not approved.",
        "Installer delivery is not approved.",
        "Binary distribution is not approved.",
    ]

    for limitation in limitations:
        assert limitation in text


def test_private_pilot_boundary_keeps_safety_confirmation_explicit() -> None:
    text = _text()

    markers = [
        "No real media is allowed in this gate.",
        "No customer material is allowed in this gate.",
        "No production material is allowed in this gate.",
        "No confidential material is allowed in this gate.",
        "No FFmpeg is allowed in this gate.",
        "No ffprobe is allowed in this gate.",
        "No scanner integration is allowed in this gate.",
        "No batch traversal is allowed in this gate.",
        "No recursive traversal is allowed in this gate.",
        "No SaaS module is allowed in this gate.",
        "No database is allowed in this gate.",
        "No backend change is allowed in this gate.",
        "No frontend change is allowed in this gate.",
        "No Docker change is allowed in this gate.",
        "No Alembic change is allowed in this gate.",
        "No Stripe change is allowed in this gate.",
        "No AI Jobs change is allowed in this gate.",
        "No credits or ledger change is allowed in this gate.",
        "No installer is created in this gate.",
        "No binary is created in this gate.",
    ]

    for marker in markers:
        assert marker in text


def test_private_pilot_boundary_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this private pilot boundary document.",
        "Add one private pilot boundary unit test.",
        "Inspect existing private pilot boundary readiness document.",
        "Inspect existing prospect feedback capture document.",
        "Inspect existing production use path scope document.",
        "Inspect existing customer demo meeting pack document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No actual private pilot execution.",
        "No real customer names.",
        "No company names.",
        "No emails.",
        "No phone numbers.",
        "No confidential project details.",
        "No customer file paths.",
        "No media filenames from customer material.",
        "No customer files.",
        "No production approval.",
        "No paid delivery approval.",
        "No meeting pack edits.",
        "No implementation changes.",
        "No execution against real media.",
        "No execution against customer material.",
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


def test_private_pilot_boundary_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.PLANNING.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_PLANNING_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent private pilot boundary gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-private-pilot-boundary-gate-v1-20260701" in text
