from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_gate_v1.md"
)

READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_prospect_feedback_capture_readiness_gate_v1.md"
)

PRODUCTION_PATH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)

HUMAN_REVIEW_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md"
)

MEETING_PACK_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_prospect_feedback_capture_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PROSPECT_FEEDBACK_CAPTURE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PROSPECT_FEEDBACK_CAPTURE_GATE_V1_CLOSED" in text
    assert "READY_FOR_SAFE_PROSPECT_FEEDBACK_CAPTURE" in text
    assert "SAFE_PLACEHOLDER_PROSPECT_FEEDBACK_CAPTURED" in text


def test_prospect_feedback_capture_records_base_state() -> None:
    text = _text()

    assert "b69babb1ecb06235d8de10d28a8f980bad36e48f" in text
    assert "b69babb docs: add CID Local Media Agent prospect feedback capture readiness gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-prospect-feedback-capture-readiness-gate-v1-20260701" in text


def test_prospect_feedback_capture_references_upstream_documents() -> None:
    text = _text()

    assert READINESS_DOC.exists()
    assert PRODUCTION_PATH_DOC.exists()
    assert HUMAN_REVIEW_DOC.exists()
    assert MEETING_PACK_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_prospect_feedback_capture_readiness_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text
    assert "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text


def test_prospect_feedback_capture_is_placeholder_only() -> None:
    text = _text()

    markers = [
        "This gate captures placeholder feedback only.",
        "This gate does not capture real prospect feedback.",
        "CAPTURE_MODE:",
        "CONTROLLED_PLACEHOLDER_ONLY",
        "MARKET_VALIDATION_STATUS:",
        "NOT_MARKET_VALIDATION",
        "No real anonymized prospect feedback has been provided.",
        "No real meeting notes have been provided.",
        "validates the feedback capture structure but does not validate commercial demand",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_does_not_include_sensitive_content() -> None:
    text = _text()

    markers = [
        "This gate does not contain prospect names.",
        "This gate does not contain company names.",
        "This gate does not contain emails.",
        "This gate does not contain phone numbers.",
        "This gate does not contain project titles.",
        "This gate does not contain budgets.",
        "This gate does not contain schedules.",
        "This gate does not contain confidential film details.",
        "This gate does not contain customer file paths.",
        "This gate does not contain customer media filenames.",
        "This gate does not request customer files.",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_populates_safe_template_core_fields() -> None:
    text = _text()

    fields = [
        "FEEDBACK_RECORD_ID:",
        "controlled_prospect_feedback_placeholder_v1",
        "FEEDBACK_RECORD_TYPE:",
        "non_confidential_placeholder",
        "MEETING_TYPE:",
        "private prospect conversation placeholder",
        "PROSPECT_CATEGORY:",
        "producer",
        "CONFIDENTIALITY_LEVEL:",
        "non-confidential notes only",
        "PRIMARY_PRODUCTION_PAIN:",
        "OPERATIONAL_CONTEXT:",
        "CURRENT_WORKFLOW_SUMMARY:",
        "CURRENT_HANDOFF_PROBLEM:",
        "CURRENT_MEDIA_ORGANIZATION_PROBLEM:",
        "CURRENT_POSTPRODUCTION_DELAY_PROBLEM:",
        "CURRENT_ARCHIVE_OR_DELIVERY_RISK:",
    ]

    for field in fields:
        assert field in text


def test_prospect_feedback_capture_populates_roles_volume_privacy_and_capability_fields() -> None:
    text = _text()

    fields = [
        "WHO_FEELS_THE_PROBLEM:",
        "WHO_WOULD_APPROVE_A_PILOT:",
        "WHO_WOULD_USE_THE_TOOL:",
        "EXPECTED_FILE_VOLUME_RANGE:",
        "small_to_medium_initial_test",
        "EXPECTED_FOLDER_COMPLEXITY_RANGE:",
        "single_folder_or_limited_subfolder_scope_after_future_approval",
        "EXPECTED_OPERATING_SYSTEMS:",
        "Windows first, macOS later, Linux possible for technical operators.",
        "EXPECTED_STORAGE_PATTERN:",
        "local disk or attached external drive, no upload required.",
        "PRIVACY_CONCERNS:",
        "Material should remain local and should not be uploaded by default.",
        "OFFLINE_LOCAL_FIRST_IMPORTANCE:",
        "high",
        "MUST_HAVE_CAPABILITY:",
        "NICE_TO_HAVE_CAPABILITY:",
        "EXPLICITLY_NOT_NEEDED:",
    ]

    for field in fields:
        assert field in text


def test_prospect_feedback_capture_populates_commercial_and_pilot_fields() -> None:
    text = _text()

    fields = [
        "DEAL_BLOCKER:",
        "Any requirement to upload confidential production media before trust is established.",
        "BUDGET_SIGNAL:",
        "unknown_placeholder",
        "PURCHASE_MODEL_PREFERENCE:",
        "subscription_or_private_pilot_to_be_validated",
        "PILOT_INTEREST_LEVEL:",
        "PILOT_INTEREST_REQUIRES_SCOPE",
        "PILOT_ACCEPTABLE_BOUNDARY:",
        "PILOT_UNACCEPTABLE_BOUNDARY:",
        "REQUESTED_PROOF_BEFORE_PILOT:",
        "MAIN_OBJECTION:",
        "MAIN_RISK_CONCERN:",
        "MOST_COMPELLING_PHRASE_USED_BY_PROSPECT:",
        "placeholder_not_real_quote_do_not_use_as_testimonial",
    ]

    for field in fields:
        assert field in text


def test_prospect_feedback_capture_records_interpretation_and_next_step() -> None:
    text = _text()

    markers = [
        "OPERATOR_COMMERCIAL_INTERPRETATION:",
        "commercially plausible if it is positioned as local-first production risk reduction",
        "OPERATOR_TECHNICAL_INTERPRETATION:",
        "progress toward explicitly scoped real-media preflight",
        "RECOMMENDED_NEXT_STEP:",
        "CREATE_PRIVATE_PILOT_BOUNDARY_READINESS_GATE",
        "FOLLOW_UP_ALLOWED:",
        "unclear",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_records_do_not_promise_list() -> None:
    text = _text()

    markers = [
        "Do not promise production readiness.",
        "Do not promise real-media processing today.",
        "Do not promise folder scanning today.",
        "Do not promise transcription today.",
        "Do not promise subtitles today.",
        "Do not promise sync today.",
        "Do not promise DaVinci Resolve integration today.",
        "Do not promise Avid integration today.",
        "Do not promise SaaS integration today.",
        "Do not promise installer delivery today.",
        "Do not promise delivery dates without scoped plan.",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_records_classifications() -> None:
    text = _text()

    markers = [
        "CLASSIFICATION:",
        "INTEREST_MEDIUM_NEEDS_MORE_CONTEXT",
        "PILOT_INTEREST_CLASSIFICATION:",
        "PILOT_INTEREST_REQUIRES_SCOPE",
        "SAFE_NEXT_STEP_CLASSIFICATION:",
        "CREATE_PRIVATE_PILOT_BOUNDARY_READINESS_GATE",
        "CAPTURE_VERDICT:",
        "PLACEHOLDER_CAPTURE_VALID_FOR_STRUCTURE_ONLY",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_records_capture_limitations() -> None:
    text = _text()

    markers = [
        "This is not real prospect feedback.",
        "This is not customer validation.",
        "This is not a sales commitment.",
        "This is not a private pilot approval.",
        "This is not production acceptance.",
        "only a safe structure validation for future sanitized prospect feedback",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_capture_defines_supported_and_unsupported_claims() -> None:
    text = _text()

    supported = [
        "Testing the feedback capture structure.",
        "Preparing a future real anonymized feedback record.",
        "Preparing a future private pilot boundary discussion.",
        "Maintaining separation between commercial interest and technical approval.",
    ]
    unsupported = [
        "Claiming market validation.",
        "Claiming customer demand.",
        "Claiming customer approval.",
        "Claiming product-market fit.",
        "Claiming pilot approval.",
        "Claiming production readiness.",
        "Claiming paid delivery readiness.",
    ]

    for marker in supported + unsupported:
        assert marker in text


def test_prospect_feedback_capture_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Prospect feedback capture phase is defined.",
        "Base state is recorded.",
        "Readiness gate is referenced.",
        "Production path scope is referenced.",
        "Human review gate is referenced.",
        "Meeting pack is referenced.",
        "Capture mode is controlled placeholder only.",
        "Market validation status is not market validation.",
        "Feedback record id is present.",
        "Feedback record type is non-confidential placeholder.",
        "Safe template fields are populated.",
        "No real prospect identity is captured.",
        "No company identity is captured.",
        "No confidential project data is captured.",
        "No customer file path is captured.",
        "No media filename is captured.",
        "No customer file request is made.",
        "Classification is present.",
        "Pilot interest classification is present.",
        "Safe next-step classification is present.",
        "Capture limitation is explicit.",
        "No private pilot is approved.",
        "No production use is approved.",
        "No paid delivery is approved.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_prospect_feedback_capture_keeps_limitations_active() -> None:
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


def test_prospect_feedback_capture_keeps_safety_confirmation_explicit() -> None:
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


def test_prospect_feedback_capture_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this prospect feedback capture document.",
        "Add one prospect feedback capture unit test.",
        "Inspect existing prospect feedback capture readiness document.",
        "Inspect existing production use path scope document.",
        "Inspect existing customer demo human review gate document.",
        "Inspect existing customer demo meeting pack document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No real prospect feedback capture.",
        "No prospect names.",
        "No company names.",
        "No emails.",
        "No phone numbers.",
        "No confidential project details.",
        "No customer file paths.",
        "No media filenames from customer material.",
        "No customer files.",
        "No production approval.",
        "No paid delivery approval.",
        "No private pilot execution.",
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


def test_prospect_feedback_capture_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PRIVATE_PILOT_BOUNDARY.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRIVATE_PILOT_BOUNDARY_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent prospect feedback capture gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-prospect-feedback-capture-gate-v1-20260701" in text
