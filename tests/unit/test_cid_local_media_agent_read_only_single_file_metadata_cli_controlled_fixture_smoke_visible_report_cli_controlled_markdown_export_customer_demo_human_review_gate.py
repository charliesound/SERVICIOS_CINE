from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_gate_v1.md"
)

PACK_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)

READINESS_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_readiness_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def _pack_text() -> str:
    assert PACK_DOC_PATH.exists()
    return PACK_DOC_PATH.read_text(encoding="utf-8")


def test_human_review_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.HUMAN_REVIEW.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_"
        "CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_HUMAN_REVIEW_GATE_V1_CLOSED"
        in text
    )
    assert "CUSTOMER_DEMO_MEETING_PACK_HUMAN_REVIEW_ACCEPTED_WITH_RESERVATIONS" in text


def test_human_review_gate_records_base_state() -> None:
    text = _doc_text()

    assert "1fc59b496ab02e8d9ece292fcd735f6c4be29897" in text
    assert "1fc59b4 test: add CID Local Media Agent customer demo human review readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-human-review-readiness-gate-v1-20260701"
        in text
    )


def test_human_review_gate_references_targets() -> None:
    text = _doc_text()

    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_customer_demo_meeting_pack_v1.py" in text
    assert "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_human_review_readiness_gate_v1.md" in text
    assert PACK_DOC_PATH.exists()
    assert READINESS_DOC_PATH.exists()


def test_human_review_gate_records_decision() -> None:
    text = _doc_text()

    assert "HUMAN_REVIEW_DECISION:" in text
    assert "ACCEPTED_FOR_PRIVATE_PROSPECT_REVIEW_WITH_RESERVATIONS" in text
    assert "The meeting pack may be used as an internal guide for a private one-to-one conversation" in text
    assert "The meeting pack may not be used as a public launch asset." in text
    assert "The meeting pack may not be used to process real or customer material." in text
    assert "The meeting pack may not be used to close paid delivery" in text


def test_human_review_gate_records_reviewer_perspective_and_summary() -> None:
    text = _doc_text()

    assert "Senior audiovisual producer perspective." in text
    assert "Commercial usefulness perspective." in text
    assert "Risk control perspective." in text
    assert "The pack is commercially usable for a private producer conversation" in text
    assert "The pack keeps the local-first direction visible." in text
    assert "The pack should still be presented verbally with discipline" in text


def test_human_review_gate_records_commercial_strengths() -> None:
    text = _doc_text()

    strengths = [
        "The pack has a clear one-sentence pitch.",
        "The pack has a producer-facing title.",
        "The pack explains local-first value.",
        "The pack connects the demo to producer pain",
        "The pack includes producer discovery questions.",
        "The pack includes safe follow-up options.",
        "The pack includes private pilot discussion boundaries.",
        "The pack avoids hard-selling a finished product.",
    ]

    for strength in strengths:
        assert strength in text


def test_human_review_gate_records_commercial_reservations() -> None:
    text = _doc_text()

    reservations = [
        "The current demo remains narrow and controlled.",
        "The operator must explain why a fixture demo matters.",
        "The operator must not let the prospect believe real media processing is already approved.",
        "The operator should translate technical evidence into production risk language.",
        "The operator should focus on the producer problem before showing commands.",
        "The operator should ask discovery questions before discussing a pilot.",
        "The operator should not mention delivery dates without a scoped plan.",
    ]

    for reservation in reservations:
        assert reservation in text


def test_human_review_gate_records_technical_strengths_and_reservations() -> None:
    text = _doc_text()

    markers = [
        "The pack references the controlled fixture only.",
        "The pack preserves the expected fixture SHA256.",
        "The pack preserves the expected byte size.",
        "The pack preserves the expected success marker.",
        "The pack includes stdout report command.",
        "The pack includes controlled Markdown export command.",
        "The pack includes verification commands.",
        "The pack includes cleanup command.",
        "The current demo does not approve FFmpeg.",
        "The current demo does not approve ffprobe.",
        "The current demo does not approve scanner integration.",
        "The current demo does not approve folder scanning.",
        "The current demo does not approve production readiness.",
    ]

    for marker in markers:
        assert marker in text


def test_human_review_gate_records_wording_risk_review() -> None:
    text = _doc_text()

    risks = [
        "No wording should be interpreted as public product launch.",
        "No wording should be interpreted as production-ready claim.",
        "No wording should be interpreted as installer availability.",
        "No wording should be interpreted as real-media processing approval.",
        "No wording should be interpreted as customer-data processing approval.",
        "No wording should be interpreted as FFmpeg or ffprobe approval.",
        "No wording should be interpreted as scanning, transcription, sync, subtitles, DaVinci Resolve, Avid, or SaaS availability.",
        "The human presenter must reinforce these boundaries orally.",
    ]

    for risk in risks:
        assert risk in text


def test_human_review_gate_records_approved_and_not_approved_use() -> None:
    text = _doc_text()

    approved = [
        "Private one-to-one trusted prospect conversation.",
        "Private producer conversation.",
        "Private executive producer conversation.",
        "Private postproduction supervisor conversation.",
        "Private requirements discussion.",
        "Private pilot-boundary discussion without customer files.",
    ]
    not_approved = [
        "Public sales deck.",
        "Public demo.",
        "Website launch material.",
        "Paid delivery proposal.",
        "Installer delivery.",
        "Binary distribution.",
        "Workshop material.",
        "Customer onboarding material.",
        "Real project execution.",
        "Customer file processing.",
        "Production workflow replacement.",
        "Private pilot execution.",
    ]

    for marker in approved + not_approved:
        assert marker in text


def test_human_review_gate_records_operator_presentation_rules() -> None:
    text = _doc_text()

    rules = [
        "Start with the production problem, not with the terminal.",
        "Explain that the demo is controlled and intentionally limited.",
        "State clearly that no real or customer material will be processed.",
        "Use the report chain as proof of disciplined local-first development.",
        "Translate SHA256, fixture, and workspace evidence into trust, repeatability, and auditability.",
        "Ask discovery questions before proposing next steps.",
        "Stop if the prospect asks to process real files.",
        "Do not promise dates, features, integrations, or production delivery without a scoped plan.",
    ]

    for rule in rules:
        assert rule in text


def test_human_review_gate_records_approved_next_step() -> None:
    text = _doc_text()

    assert "Use the pack for private prospect review only after the operator reads it before the meeting." in text
    assert "Record prospect feedback separately." in text
    assert "create a future private pilot boundary readiness gate" in text
    assert "create a separate explicit real-media preflight planning/readiness phase before any execution" in text


def test_human_review_gate_records_decision_record() -> None:
    text = _doc_text()

    assert "Decision: ACCEPTED_FOR_PRIVATE_PROSPECT_REVIEW_WITH_RESERVATIONS" in text
    assert "Reason: commercially understandable, technically bounded, and safe for private discussion." in text
    assert "Main reservation: the presenter must actively control expectations" in text
    assert "Next allowed use: private prospect discussion only." in text
    assert "Next forbidden use: public launch, paid delivery, customer material processing, real-media execution, installer or binary distribution." in text


def test_human_review_gate_records_pass_criteria() -> None:
    text = _doc_text()

    criteria = [
        "Review target document exists.",
        "Review target test exists.",
        "Human review readiness gate is the base.",
        "Meeting pack QA status is recorded.",
        "Human review decision is recorded.",
        "Decision meaning is explicit.",
        "Reviewer perspective is explicit.",
        "Human review summary is present.",
        "Commercial strengths are recorded.",
        "Commercial reservations are recorded.",
        "Technical strengths are recorded.",
        "Technical reservations are recorded.",
        "Wording risk review is present.",
        "Approved private meeting use is present.",
        "Not-approved use is present.",
        "Operator presentation rules are present.",
        "Approved next step is present.",
        "Review decision record is present.",
        "No meeting pack edit was performed.",
        "No real media was used.",
        "No customer material was used.",
        "No installer was created.",
        "No binary was created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_human_review_gate_verifies_pack_core_content() -> None:
    pack_text = _pack_text()

    markers = [
        "CID Local Media Agent - Demo controlada para productores audiovisuales",
        "CID Local Media Agent está pensado para ayudar",
        "Esto es una demo técnica controlada, no una versión comercial final.",
        "La demo actual no procesa material real.",
        "La demo actual no procesa material de cliente.",
        "Do not promise production readiness.",
        "Stop if the prospect asks to process real material during the meeting.",
        "Option 3: Define private pilot boundary.",
    ]

    for marker in markers:
        assert marker in pack_text


def test_human_review_gate_keeps_limitations_active() -> None:
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
        "Private pilot execution is not approved.",
    ]

    for limitation in limitations:
        assert limitation in text


def test_human_review_gate_keeps_safety_scope_explicit() -> None:
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


def test_human_review_gate_keeps_forbidden_scope_explicit() -> None:
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


def test_human_review_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
        "Customer demo human review gate test.",
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


def test_human_review_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo human review gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-human-review-gate-v1-20260701"
        in text
    )
