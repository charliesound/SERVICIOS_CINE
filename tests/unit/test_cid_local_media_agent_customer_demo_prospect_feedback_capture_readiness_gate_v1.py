from pathlib import Path


DOC_PATH = Path(
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


def test_prospect_feedback_readiness_declares_phase_result_and_status() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PROSPECT_FEEDBACK_CAPTURE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PROSPECT_FEEDBACK_CAPTURE_READINESS_GATE_V1_CLOSED" in text
    assert "PRODUCTION_USE_PATH_SCOPED" in text
    assert "READY_FOR_SAFE_PROSPECT_FEEDBACK_CAPTURE" in text


def test_prospect_feedback_readiness_records_base_state() -> None:
    text = _text()

    assert "2906a69672040b31e026101da90506079ebd980d" in text
    assert "2906a69 docs: add CID Local Media Agent production use path scope gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-production-use-path-scope-gate-v1-20260701" in text


def test_prospect_feedback_readiness_references_upstream_documents() -> None:
    text = _text()

    assert PRODUCTION_PATH_DOC.exists()
    assert HUMAN_REVIEW_DOC.exists()
    assert MEETING_PACK_DOC.exists()
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md" in text
    assert "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text


def test_prospect_feedback_readiness_does_not_capture_real_feedback() -> None:
    text = _text()

    markers = [
        "This gate prepares feedback capture only.",
        "This gate does not capture real prospect feedback.",
        "This gate does not include prospect names.",
        "This gate does not include company names.",
        "This gate does not include emails.",
        "This gate does not include phone numbers.",
        "This gate does not include confidential project details.",
        "This gate does not request real media.",
        "This gate does not process real media.",
        "This gate does not approve private pilot execution.",
        "This gate does not approve production use.",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_readiness_explains_why_gate_exists() -> None:
    text = _text()

    markers = [
        "The production path requires prospect feedback before private pilot boundaries.",
        "Feedback must be captured without leaking private project information.",
        "Feedback must separate commercial interest from technical approval.",
        "Feedback must separate what a prospect wants from what the product is allowed to do.",
        "Feedback must avoid accidental commitment to production use.",
        "Feedback must avoid requesting or storing customer files.",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_readiness_defines_safe_capture_principles() -> None:
    text = _text()

    markers = [
        "Capture problems, not confidential project details.",
        "Capture workflow patterns, not production secrets.",
        "Capture role categories, not personal identities.",
        "Capture file-volume ranges, not actual file lists.",
        "Capture operating-system needs, not machine identifiers.",
        "Capture storage patterns, not private paths.",
        "Capture budget signals, not binding commercial terms.",
        "Capture requested features, not delivery commitments.",
        "Capture pilot interest, not pilot approval.",
    ]

    for marker in markers:
        assert marker in text


def test_prospect_feedback_readiness_lists_forbidden_feedback_content() -> None:
    text = _text()

    forbidden = [
        "No prospect full names.",
        "No company legal names unless separately approved.",
        "No email addresses.",
        "No phone numbers.",
        "No project titles.",
        "No script titles.",
        "No confidential film details.",
        "No cast names.",
        "No crew names.",
        "No locations.",
        "No budgets.",
        "No schedules.",
        "No legal terms.",
        "No contract language.",
        "No file paths from customer machines.",
        "No media filenames from customer material.",
        "No uploaded files.",
        "No screenshots of customer systems.",
        "No passwords.",
        "No license keys.",
        "No API keys.",
        "No personal data.",
        "No sensitive business data.",
    ]

    for marker in forbidden:
        assert marker in text


def test_prospect_feedback_readiness_defines_safe_template_fields() -> None:
    text = _text()

    fields = [
        "Feedback record id: controlled_prospect_feedback_placeholder_v1",
        "Meeting type: private prospect conversation",
        "Prospect category: producer | executive producer | postproduction supervisor | school | other",
        "Conversation date: YYYY-MM-DD",
        "Confidentiality level: non-confidential notes only",
        "Primary production pain:",
        "Current workflow summary:",
        "Current handoff problem:",
        "Current media organization problem:",
        "Who would approve a pilot:",
        "Who would use the tool:",
        "Expected file volume range:",
        "Expected operating systems:",
        "Privacy concerns:",
        "Offline/local-first importance:",
        "Must-have capability:",
        "Deal blocker:",
        "Budget signal:",
        "Pilot interest level:",
        "Pilot acceptable boundary:",
        "Requested proof before pilot:",
        "Main objection:",
        "Recommended next step:",
        "Do not promise:",
        "Stop condition triggered:",
        "Follow-up allowed: yes | no | unclear",
    ]

    for field in fields:
        assert field in text


def test_prospect_feedback_readiness_defines_classification_options() -> None:
    text = _text()

    options = [
        "INTEREST_HIGH_WITH_CLEAR_PAIN",
        "INTEREST_MEDIUM_NEEDS_MORE_CONTEXT",
        "INTEREST_LOW_NO_CLEAR_PAIN",
        "INTEREST_BLOCKED_BY_TRUST_OR_PRIVACY",
        "INTEREST_BLOCKED_BY_PRICE",
        "INTEREST_BLOCKED_BY_MISSING_FEATURE",
        "INTEREST_BLOCKED_BY_TIMING",
        "NOT_A_FIT",
    ]

    for option in options:
        assert option in text


def test_prospect_feedback_readiness_defines_pilot_interest_options() -> None:
    text = _text()

    options = [
        "NO_PILOT_INTEREST",
        "PILOT_CURIOSITY_ONLY",
        "PILOT_INTEREST_WITHOUT_FILES",
        "PILOT_INTEREST_REQUIRES_SCOPE",
        "PILOT_INTEREST_REQUIRES_REAL_MEDIA_PLAN",
        "PILOT_INTEREST_REQUIRES_INSTALLER",
        "PILOT_INTEREST_REQUIRES_PRIVACY_APPROVAL",
        "PILOT_INTEREST_REQUIRES_PRICE",
    ]

    for option in options:
        assert option in text


def test_prospect_feedback_readiness_defines_safe_next_steps() -> None:
    text = _text()

    options = [
        "NO_FOLLOW_UP",
        "SEND_NON_CONFIDENTIAL_SUMMARY",
        "REQUEST_SECOND_DISCOVERY_MEETING",
        "CREATE_PRIVATE_PILOT_BOUNDARY_READINESS_GATE",
        "CREATE_REAL_MEDIA_PREFLIGHT_PLANNING_GATE",
        "CREATE_COMMERCIAL_OFFER_SCOPE_GATE",
        "WAIT_FOR_PROSPECT_TIMING",
        "REJECT_AS_NOT_FIT",
    ]

    for option in options:
        assert option in text


def test_prospect_feedback_readiness_lists_allowed_questions() -> None:
    text = _text()

    questions = [
        "What problem are you trying to solve before postproduction starts?",
        "Where does material organization usually break?",
        "Who loses time when material is not well described?",
        "How many projects do you usually manage at the same time?",
        "What kind of first report would be valuable?",
        "What would make this safe enough to test?",
        "What should never leave your machine?",
        "What would make this unacceptable?",
        "Who would need to approve a pilot?",
        "What would you need to see before paying?",
        "What would be a small safe first step?",
    ]

    for question in questions:
        assert question in text


def test_prospect_feedback_readiness_lists_forbidden_questions() -> None:
    text = _text()

    questions = [
        "Can you send me the material?",
        "Can you upload the folder?",
        "Can I run this on your project now?",
        "Can I have your exact file paths?",
        "Can I have your client names?",
        "Can I have your production budget?",
        "Can I have your shooting schedule?",
        "Can I have your cast or crew list?",
        "Can I have confidential project documents?",
        "Can I keep your media for testing?",
    ]

    for question in questions:
        assert question in text


def test_prospect_feedback_readiness_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Feedback readiness phase is defined.",
        "Base state is recorded.",
        "Production path scope is referenced.",
        "Human review gate is referenced.",
        "Meeting pack is referenced.",
        "Safe feedback principles are defined.",
        "Forbidden feedback content is defined.",
        "Safe feedback template is defined.",
        "Classification options are defined.",
        "Pilot interest options are defined.",
        "Safe next-step options are defined.",
        "Allowed questions are defined.",
        "Forbidden questions are defined.",
        "No actual prospect feedback is captured.",
        "No real prospect identity is captured.",
        "No confidential project data is captured.",
        "No customer file request is made.",
        "No private pilot is approved.",
        "No production use is approved.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_prospect_feedback_readiness_keeps_limitations_active() -> None:
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


def test_prospect_feedback_readiness_keeps_safety_confirmation_explicit() -> None:
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


def test_prospect_feedback_readiness_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this prospect feedback capture readiness document.",
        "Add one prospect feedback capture readiness unit test.",
        "Inspect existing production use path scope document.",
        "Inspect existing customer demo human review gate document.",
        "Inspect existing customer demo meeting pack document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No actual prospect feedback capture.",
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


def test_prospect_feedback_readiness_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PROSPECT_FEEDBACK_CAPTURE.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PROSPECT_FEEDBACK_CAPTURE_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent prospect feedback capture readiness gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-prospect-feedback-capture-readiness-gate-v1-20260701" in text
