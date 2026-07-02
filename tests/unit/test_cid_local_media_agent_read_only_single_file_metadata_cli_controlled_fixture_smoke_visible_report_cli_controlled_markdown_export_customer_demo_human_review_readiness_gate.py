from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_readiness_gate_v1.md"
)

PACK_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)

PACK_TEST_PATH = Path(
    "tests/unit/test_cid_local_media_agent_customer_demo_meeting_pack_v1.py"
)

PACKAGING_QA_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_packaging_qa_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def _pack_text() -> str:
    assert PACK_DOC_PATH.exists()
    return PACK_DOC_PATH.read_text(encoding="utf-8")


def test_human_review_readiness_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.HUMAN_REVIEW.READINESS.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_"
        "CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_HUMAN_REVIEW_READINESS_GATE_V1_CLOSED"
        in text
    )
    assert "READY_FOR_HUMAN_COMMERCIAL_REVIEW_OF_SAFE_MEETING_PACK" in text


def test_human_review_readiness_gate_records_base_state() -> None:
    text = _doc_text()

    assert "c433175db80a9e58a969a0aeded5006d2eb77b27" in text
    assert "c433175 test: add CID Local Media Agent customer demo packaging QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-qa-gate-v1-20260701"
        in text
    )


def test_human_review_readiness_gate_references_existing_pack_artifacts() -> None:
    text = _doc_text()

    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_customer_demo_meeting_pack_v1.py" in text
    assert PACK_DOC_PATH.exists()
    assert PACK_TEST_PATH.exists()
    assert PACKAGING_QA_DOC_PATH.exists()
    assert "SAFE_CUSTOMER_DEMO_MEETING_PACK_QA_VERIFIED" in text


def test_human_review_readiness_gate_defines_goal_and_reviewer_role() -> None:
    text = _doc_text()

    assert "Read the customer demo meeting pack as a producer would read or hear it." in text
    assert "Confirm that it creates interest without overpromising." in text
    assert "Owner/operator with producer judgment." in text
    assert "senior audiovisual producer" in text


def test_human_review_readiness_gate_defines_review_mode_and_inputs() -> None:
    text = _doc_text()

    assert "Manual read-through only." in text
    assert "No code changes during review." in text
    assert "No pack edits during this readiness gate." in text
    assert "No customer meeting during this readiness gate." in text
    assert "Customer demo meeting pack document." in text
    assert "Known controlled demo execution evidence." in text


def test_human_review_readiness_gate_defines_expected_later_output() -> None:
    text = _doc_text()

    markers = [
        "Human review decision record.",
        "List of wording issues if any.",
        "List of overpromise risks if any.",
        "List of commercial clarity issues if any.",
        "List of missing producer questions if any.",
        "Decision: accepted, accepted with edits required, or rejected.",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_readiness_gate_contains_commercial_review_checklist() -> None:
    text = _doc_text()

    markers = [
        "Does the first paragraph make sense to a producer?",
        "Does the pitch explain value without sounding like a generic AI tool?",
        "Does the pack explain local-first clearly?",
        "Does the pack avoid claiming production readiness?",
        "Does the pack avoid claiming installer availability?",
        "Does the pack keep the demo interesting despite being controlled?",
        "Does the pack connect the technical demo to producer pain",
        "Does the pack ask useful discovery questions?",
        "Does the pack give a safe next step?",
        "Does the pack support a private pilot conversation?",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_readiness_gate_contains_technical_review_checklist() -> None:
    text = _doc_text()

    markers = [
        "Does the pack reference only the controlled fixture?",
        "Does the pack include the expected fixture SHA256?",
        "Does the pack include the expected success marker?",
        "Does the pack include the safe stdout report command?",
        "Does the pack include the safe export report command?",
        "Does the pack include safe verification commands?",
        "Does the pack include cleanup?",
        "Does the pack forbid real media paths?",
        "Does the pack forbid customer paths?",
        "Does the pack forbid production paths?",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_readiness_gate_contains_wording_risk_checklist() -> None:
    text = _doc_text()

    markers = [
        "Flag any wording that sounds like the product is finished.",
        "Flag any wording that sounds like it can process client media today.",
        "Flag any wording that sounds like it supports FFmpeg or ffprobe today.",
        "Flag any wording that sounds like it supports folder scanning today.",
        "Flag any wording that sounds like it supports transcription today.",
        "Flag any wording that sounds like it supports sync today.",
        "Flag any wording that sounds too technical for a producer.",
        "Flag any wording that weakens commercial interest too much.",
        "Flag any missing buyer, user, or approver question.",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_readiness_gate_defines_decision_options() -> None:
    text = _doc_text()

    assert "ACCEPTED_FOR_PRIVATE_PROSPECT_REVIEW" in text
    assert "ACCEPTED_WITH_WORDING_EDITS_REQUIRED" in text
    assert "REJECTED_NEEDS_REWRITE" in text


def test_human_review_readiness_gate_records_pass_criteria() -> None:
    text = _doc_text()

    criteria = [
        "Human review target document exists.",
        "Human review target test exists.",
        "Packaging QA gate is the current base.",
        "Review goal is explicit.",
        "Reviewer role is explicit.",
        "Review mode is manual only.",
        "Review inputs are explicit.",
        "Expected later output is explicit.",
        "Commercial review checklist is present.",
        "Technical review checklist is present.",
        "Wording risk checklist is present.",
        "Review decision options are present.",
        "No meeting pack modification is performed.",
        "No real media execution is performed.",
        "No customer material is used.",
        "No installer is created.",
        "No binary is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_human_review_readiness_gate_contains_stop_conditions() -> None:
    text = _doc_text()

    markers = [
        "Stop if the reviewer wants to edit the pack during this readiness phase.",
        "Stop if the reviewer wants to run real material.",
        "Stop if the reviewer wants to process customer files.",
        "Stop if the reviewer wants to promise production readiness.",
        "Stop if the reviewer wants to use the pack publicly.",
        "Stop if the reviewer cannot explain current limitations clearly.",
        "Stop if the reviewer finds a serious overpromise risk.",
        "Stop if the reviewer finds that the producer value is unclear.",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_readiness_gate_keeps_limitations_active() -> None:
    text = _doc_text()

    limitations = [
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
        "Production readiness is not approved.",
        "Paid delivery is not approved.",
    ]

    for limitation in limitations:
        assert limitation in text


def test_human_review_readiness_gate_keeps_safety_scope_explicit() -> None:
    text = _doc_text()

    safety_markers = [
        "No real media is allowed.",
        "No customer material is allowed.",
        "No production material is allowed.",
        "No confidential material is allowed.",
        "No FFmpeg is allowed.",
        "No ffprobe is allowed.",
        "No scanner integration is allowed.",
        "No batch traversal is allowed.",
        "No recursive traversal is allowed.",
        "No SaaS module is allowed.",
        "No database is allowed.",
        "No backend change is allowed.",
        "No frontend change is allowed.",
        "No Docker change is allowed.",
        "No Alembic change is allowed.",
        "No Stripe change is allowed.",
        "No AI Jobs change is allowed.",
        "No credits or ledger change is allowed.",
        "No committed customer demo export artifact is allowed.",
        "No installer is created.",
        "No binary is created.",
    ]

    for marker in safety_markers:
        assert marker in text


def test_human_review_readiness_gate_keeps_forbidden_scope_explicit() -> None:
    text = _doc_text()

    forbidden_markers = [
        "No meeting pack edits.",
        "No implementation changes.",
        "No parser changes.",
        "No CLI behavior changes.",
        "No wrapper changes.",
        "No renderer changes.",
        "No in-memory integration changes.",
        "No fixture modification.",
        "No committed export artifact.",
        "No execution against real media.",
        "No execution against customer material.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive traversal.",
        "No unsafe shell execution.",
        "No pyproject modification.",
        "No console script registration.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No installer work.",
        "No binary packaging.",
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_human_review_readiness_gate_verifies_pack_contains_commercial_core() -> None:
    pack_text = _pack_text()

    markers = [
        "CID Local Media Agent - Demo controlada para productores audiovisuales",
        "CID Local Media Agent está pensado para ayudar",
        "Esto es una demo técnica controlada, no una versión comercial final.",
        "La demo actual no procesa material real.",
        "La demo actual no procesa material de cliente.",
        "What kind of first real-media preflight would be worth paying for?",
        "Define a written private pilot boundary.",
        "Do not promise production readiness.",
        "Stop if the prospect asks to process real material during the meeting.",
    ]

    for marker in markers:
        assert marker in pack_text


def test_human_review_readiness_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
        "Customer demo human review readiness gate test.",
        "Customer demo packaging QA gate test.",
        "Customer demo meeting pack test.",
        "Customer demo packaging readiness gate test.",
        "Customer demo execution QA gate test.",
        "Customer demo execution gate test.",
        "Customer demo execution readiness gate test.",
        "Customer demo script gate test.",
        "Customer demo readiness gate test.",
        "Manual demo execution QA gate test.",
        "Manual demo execution gate test.",
        "Manual demo readiness gate test.",
        "Controlled demo execution QA gate test.",
        "Controlled demo execution gate test.",
        "Wrapper smoke execution QA gate test.",
        "Wrapper smoke execution gate test.",
        "Implementation QA gate test.",
        "Implementation gate test.",
        "In-memory wrapper smoke execution QA gate test.",
        "In-memory wrapper smoke execution gate test.",
        "Visible report contract test.",
        "CLI contract gate test.",
        "WSL repo guard.",
        "PostgreSQL-only regression guard required by policy.",
    ]

    for validation_target in validation_targets:
        assert validation_target in text


def test_human_review_readiness_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo human review readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-human-review-readiness-gate-v1-20260701"
        in text
    )
