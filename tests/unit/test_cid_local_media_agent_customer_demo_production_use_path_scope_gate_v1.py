from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_production_use_path_scope_gate_v1.md"
)

PACK_DOC_PATH = Path(
    "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)

HUMAN_REVIEW_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md"
)


def _text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_production_use_path_scope_declares_phase_and_result() -> None:
    text = _text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PRODUCTION_USE_PATH.SCOPE.GATE.V1"
        in text
    )
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PRODUCTION_USE_PATH_SCOPE_GATE_V1_CLOSED" in text
    assert "LOCAL_MEDIA_AGENT_APPROVED_FOR_CONTROLLED_PRODUCTION_USE" in text


def test_production_use_path_scope_records_base_state() -> None:
    text = _text()

    assert "5614ff43c2d6e2f64b9abf95b4c4c1f950fdf8d2" in text
    assert "5614ff4 test: add CID Local Media Agent customer demo human review gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-human-review-gate-v1-20260701"
        in text
    )


def test_production_use_path_scope_references_existing_review_artifacts() -> None:
    text = _text()

    assert PACK_DOC_PATH.exists()
    assert HUMAN_REVIEW_DOC_PATH.exists()
    assert "CUSTOMER_DEMO_MEETING_PACK_HUMAN_REVIEW_ACCEPTED_WITH_RESERVATIONS" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text


def test_production_use_path_scope_prevents_direct_jump_to_production() -> None:
    text = _text()

    assert "This gate does not approve production use." in text
    assert "This gate does not approve paid delivery." in text
    assert "This gate does not approve private pilot execution." in text
    assert "This gate does not approve customer material processing." in text
    assert "This gate does not approve real media processing." in text
    assert "This gate prevents accidental promotion from controlled demo to production product." in text


def test_production_use_path_scope_defines_current_allowed_and_forbidden_use() -> None:
    text = _text()

    allowed = [
        "Private one-to-one trusted prospect conversation.",
        "Private producer conversation.",
        "Private executive producer conversation.",
        "Private requirements discussion.",
        "Private pilot-boundary discussion without customer files.",
    ]
    forbidden = [
        "Public sales deck.",
        "Public demo.",
        "Website launch material.",
        "Paid delivery proposal.",
        "Installer delivery.",
        "Binary distribution.",
        "Customer onboarding material.",
        "Real project execution.",
        "Customer file processing.",
        "Production workflow replacement.",
        "Private pilot execution.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_production_use_path_scope_defines_production_use() -> None:
    text = _text()

    markers = [
        "Production use means the product can be installed or operated for a real customer",
        "Production use means real customer material may be processed only within approved boundaries.",
        "Production use means operational risks, privacy risks, data-handling risks, support risks, and rollback risks have been accepted.",
        "Production use does not mean unlimited processing.",
        "Production use does not mean SaaS integration by default.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_lists_mandatory_path() -> None:
    text = _text()

    steps = [
        "01_PROSPECT_FEEDBACK_CAPTURE_READINESS_GATE",
        "02_PROSPECT_FEEDBACK_CAPTURE_GATE",
        "03_PRIVATE_PILOT_BOUNDARY_READINESS_GATE",
        "04_PRIVATE_PILOT_BOUNDARY_GATE",
        "05_REAL_MEDIA_PREFLIGHT_PLANNING_GATE",
        "06_REAL_MEDIA_PREFLIGHT_READINESS_GATE",
        "07_REAL_MEDIA_PREFLIGHT_CONTROLLED_EXECUTION_GATE",
        "08_REAL_MEDIA_PREFLIGHT_EXECUTION_QA_GATE",
        "09_SINGLE_FILE_REAL_METADATA_IMPLEMENTATION_SCOPE_GATE",
        "10_SINGLE_FILE_REAL_METADATA_IMPLEMENTATION_GATE",
        "11_SINGLE_FILE_REAL_METADATA_QA_GATE",
        "12_LOCAL_FOLDER_READ_ONLY_SCAN_SCOPE_GATE",
        "13_LOCAL_FOLDER_READ_ONLY_SCAN_IMPLEMENTATION_GATE",
        "14_LOCAL_FOLDER_READ_ONLY_SCAN_QA_GATE",
        "15_CUSTOMER_PRIVACY_AND_DATA_HANDLING_GATE",
        "16_INSTALLATION_AND_DEPENDENCY_STRATEGY_GATE",
        "17_LICENSE_AND_ACTIVATION_STRATEGY_GATE",
        "18_PACKAGING_READINESS_GATE",
        "19_PACKAGING_GATE",
        "20_PACKAGING_QA_GATE",
        "21_PRIVATE_BETA_OPERATIONAL_READINESS_GATE",
        "22_PRIVATE_BETA_EXECUTION_GATE",
        "23_PRIVATE_BETA_QA_GATE",
        "24_PRODUCTION_USE_READINESS_GATE",
        "25_PRODUCTION_USE_ACCEPTANCE_GATE",
    ]

    for step in steps:
        assert step in text


def test_production_use_path_scope_lists_non_negotiable_blockers() -> None:
    text = _text()

    blockers = [
        "No production use without a written customer/pilot boundary.",
        "No production use without explicit real-media approval.",
        "No production use without privacy and data-handling rules.",
        "No production use without installation or execution strategy.",
        "No production use without rollback strategy.",
        "No production use without support boundary.",
        "No production use without known limitations.",
        "No production use without validation on controlled real-media scenarios.",
        "No production use without explicit acceptance gate.",
    ]

    for blocker in blockers:
        assert blocker in text


def test_production_use_path_scope_lists_prospect_feedback_requirements() -> None:
    text = _text()

    markers = [
        "Capture producer pain points.",
        "Capture buyer/user/approver roles.",
        "Capture current workflow.",
        "Capture file volume expectations.",
        "Capture operating systems.",
        "Capture storage locations.",
        "Capture security/privacy concerns.",
        "Capture budget sensitivity.",
        "Capture deal blockers.",
        "Capture what the prospect would pay for.",
        "Capture what the prospect refuses to risk.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_lists_private_pilot_requirements() -> None:
    text = _text()

    markers = [
        "Define allowed customer.",
        "Define allowed operator.",
        "Define allowed machine.",
        "Define allowed material type.",
        "Define allowed file count.",
        "Define allowed folder count.",
        "Define forbidden operations.",
        "Define data retention rule.",
        "Define confidentiality expectations.",
        "Define success criteria.",
        "Define stop conditions.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_lists_real_media_requirements() -> None:
    text = _text()

    markers = [
        "Real media must be explicitly approved before execution.",
        "Real media path must be explicitly listed.",
        "Real media processing must be read-only.",
        "No recursive traversal unless explicitly approved.",
        "No batch traversal unless explicitly approved.",
        "No upload is allowed.",
        "No destructive write is allowed.",
        "No modification of source files is allowed.",
        "Output location must be controlled.",
        "Execution must be reproducible.",
        "Failure paths must be safe.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_lists_runtime_installation_licensing_support_requirements() -> None:
    text = _text()

    markers = [
        "Read-only source handling.",
        "Controlled output path.",
        "No hidden network access.",
        "No destructive file operations.",
        "No accidental recursive scan.",
        "Define whether product is CLI, desktop app, or packaged local agent.",
        "Define supported operating systems.",
        "Define dependency strategy for FFmpeg and ffprobe.",
        "Define commercial model.",
        "Define seat model.",
        "Define device activation model.",
        "Define support contact.",
        "Define failure escalation.",
        "Define version identification.",
        "Define rollback plan.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_lists_production_acceptance_requirements() -> None:
    text = _text()

    markers = [
        "Private beta evidence reviewed.",
        "Real-media controlled execution evidence reviewed.",
        "Privacy and data-handling gate closed.",
        "Installation and dependency strategy closed.",
        "Packaging QA closed.",
        "Known limitations documented.",
        "Support model documented.",
        "Rollback plan documented.",
        "Customer scope documented.",
        "Final production use acceptance gate explicitly closed.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_keeps_not_approved_items_explicit() -> None:
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
        "Transcription is not approved.",
        "Subtitles are not approved.",
        "Sync is not approved.",
        "DaVinci Resolve integration is not approved.",
        "Avid integration is not approved.",
        "SaaS integration is not approved.",
        "Installer delivery is not approved.",
        "Binary distribution is not approved.",
    ]

    for marker in markers:
        assert marker in text


def test_production_use_path_scope_keeps_safety_confirmation_explicit() -> None:
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


def test_production_use_path_scope_keeps_allowed_and_forbidden_scope_explicit() -> None:
    text = _text()

    allowed = [
        "Add this production use path scope document.",
        "Add one production use path scope unit test.",
        "Inspect existing customer demo meeting pack document.",
        "Inspect existing customer demo human review gate document.",
        "Run validation tests.",
        "Run WSL repo guard.",
        "Run PostgreSQL-only regression guard required by policy.",
    ]
    forbidden = [
        "No production approval.",
        "No paid delivery approval.",
        "No private pilot execution.",
        "No prospect data capture yet.",
        "No meeting pack edits.",
        "No implementation changes.",
        "No CLI behavior changes.",
        "No fixture modification.",
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


def test_production_use_path_scope_records_pass_criteria() -> None:
    text = _text()

    criteria = [
        "Production target final status is defined.",
        "Current allowed use is explicit.",
        "Current forbidden use is explicit.",
        "Production use definition is explicit.",
        "Mandatory path to production is listed.",
        "Non-negotiable production blockers are listed.",
        "Prospect feedback requirements are listed.",
        "Private pilot boundary requirements are listed.",
        "Real-media preflight requirements are listed.",
        "Product runtime requirements are listed.",
        "Installation requirements are listed.",
        "Licensing requirements are listed.",
        "Support and operations requirements are listed.",
        "Production acceptance requirements are listed.",
        "Currently not approved items are explicit.",
        "No implementation change is performed.",
        "No real media is used.",
        "No customer material is used.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_production_use_path_scope_has_next_phase_commit_and_tag_guidance() -> None:
    text = _text()

    assert "CID.LOCAL_MEDIA_AGENT.CUSTOMER_DEMO.PROSPECT_FEEDBACK_CAPTURE.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CUSTOMER_DEMO_PROSPECT_FEEDBACK_CAPTURE_READINESS_GATE_V1_CLOSED" in text
    assert "docs: add CID Local Media Agent production use path scope gate" in text
    assert "cid-dev-stable-local-media-agent-customer-demo-production-use-path-scope-gate-v1-20260701" in text
