from pathlib import Path


QA_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_packaging_qa_gate_v1.md"
)

PACK_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_customer_demo_meeting_pack_v1.md"
)

PACK_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_customer_demo_meeting_pack_v1.py"
)


def _qa_text() -> str:
    assert QA_DOC_PATH.exists()
    return QA_DOC_PATH.read_text(encoding="utf-8")


def _pack_text() -> str:
    assert PACK_DOC_PATH.exists()
    return PACK_DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_packaging_qa_gate_declares_phase_and_result() -> None:
    text = _qa_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PACKAGING.QA.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_PACKAGING_QA_GATE_V1_CLOSED"
        in text
    )
    assert "SAFE_CUSTOMER_DEMO_MEETING_PACK_QA_VERIFIED" in text


def test_customer_demo_packaging_qa_gate_records_base_state() -> None:
    text = _qa_text()

    assert "2cb9a5ef62f35e6099646329d659e40188cdb21f" in text
    assert "2cb9a5e docs: add CID Local Media Agent customer demo meeting pack" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-gate-v1-20260701"
        in text
    )


def test_customer_demo_packaging_qa_gate_references_pack_artifact_and_test() -> None:
    text = _qa_text()

    assert "docs/product/local_media_agent/cid_local_media_agent_customer_demo_meeting_pack_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_customer_demo_meeting_pack_v1.py" in text
    assert PACK_DOC_PATH.exists()
    assert PACK_TEST_PATH.exists()
    assert "SAFE_CUSTOMER_DEMO_MEETING_PACK_CREATED" in text


def test_customer_demo_packaging_qa_gate_records_qa_verdict() -> None:
    text = _qa_text()

    assert "MEETING_PACK_READY_FOR_HUMAN_REVIEW_BEFORE_PRIVATE_PROSPECT_USE" in text
    assert "The meeting pack is usable as a private controlled-demo guide." in text
    assert "The meeting pack must be reviewed by the operator before a real meeting." in text
    assert "The meeting pack is not a public sales deck." in text
    assert "The meeting pack is not a downloadable product." in text
    assert "The meeting pack is not an installer package." in text
    assert "The meeting pack is not approval for customer material processing." in text


def test_customer_demo_packaging_qa_gate_lists_required_pack_sections() -> None:
    text = _qa_text()

    sections = [
        "MEETING_TITLE",
        "ONE_SENTENCE_PITCH",
        "EXECUTIVE_SUMMARY_FOR_PRODUCER",
        "OPENING_SCRIPT",
        "DEMO_BOUNDARY_SCRIPT",
        "WHAT_TO_SHOW_ON_SCREEN",
        "SAFE_PRE_MEETING_PREFLIGHT",
        "SAFE_STDOUT_REPORT_COMMAND",
        "SAFE_EXPORT_REPORT_COMMAND",
        "SAFE_VERIFY_COMMANDS",
        "SAFE_CLEANUP_COMMAND",
        "BUSINESS_VALUE_HYPOTHESES",
        "PRODUCER_DISCOVERY_QUESTIONS",
        "PRIVATE_PILOT_DISCUSSION_BOUNDARY",
        "SAFE_FOLLOW_UP_OPTIONS",
        "DO_NOT_PROMISE",
        "STOP_CONDITIONS",
        "MEETING_CLOSE_OPTIONS",
    ]

    for section in sections:
        assert section in text
        assert section in _pack_text()


def test_customer_demo_packaging_qa_gate_verifies_commercial_safety() -> None:
    text = _qa_text()

    markers = [
        "The pack frames the demo as controlled and private.",
        "The pack says the demo is not a commercial final version.",
        "The pack says the current demo does not process real material.",
        "The pack says the current demo does not process customer material.",
        "The pack explains local-first positioning.",
        "The pack contains discovery questions instead of hard selling.",
        "The pack contains private pilot boundaries.",
        "The pack contains safe follow-up options.",
        "The pack contains do-not-promise constraints.",
        "The pack contains stop conditions.",
        "The pack contains meeting close options.",
    ]

    for marker in markers:
        assert marker in text


def test_customer_demo_packaging_qa_gate_verifies_technical_safety() -> None:
    text = _qa_text()

    markers = [
        "The pack uses only the controlled non-customer fixture path.",
        "The pack records the controlled fixture id.",
        "The pack records the allowed relative path.",
        "The pack records the expected byte size.",
        "The pack records the expected fixture SHA256.",
        "The pack records the expected success marker.",
        "The pack records the last verified execution evidence.",
        "The pack includes cleanup.",
        "The pack requires clean workspace.",
        "The pack forbids real media paths.",
        "The pack forbids customer paths.",
        "The pack forbids production paths.",
    ]

    for marker in markers:
        assert marker in text


def test_customer_demo_packaging_qa_gate_records_evidence() -> None:
    text = _qa_text()

    assert "Last stable packaging gate HEAD: 2cb9a5ef62f35e6099646329d659e40188cdb21f" in text
    assert "Customer demo execution result: LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS" in text
    assert "Generated report size: 1795 bytes" in text
    assert "Generated report SHA256: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd" in text
    assert "Controlled fixture SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" in text
    assert "Final workspace after packaging gate: clean" in text


def test_customer_demo_packaging_qa_gate_validates_pack_core_content() -> None:
    pack_text = _pack_text()

    markers = [
        "CID Local Media Agent - Demo controlada para productores audiovisuales",
        "CID Local Media Agent está pensado para ayudar",
        "Esto es una demo técnica controlada, no una versión comercial final.",
        "La demo actual no procesa material real.",
        "La demo actual no procesa material de cliente.",
        "No real media path may be used.",
        "No customer path may be used.",
        "No production path may be used.",
        "Do not promise production readiness.",
        "Stop if the prospect asks to process real material during the meeting.",
        "Option 3: Define private pilot boundary.",
    ]

    for marker in markers:
        assert marker in pack_text


def test_customer_demo_packaging_qa_gate_validates_pack_safe_commands() -> None:
    pack_text = _pack_text()

    markers = [
        "SAFE_STDOUT_REPORT_COMMAND:",
        "SAFE_EXPORT_REPORT_COMMAND:",
        "SAFE_VERIFY_COMMANDS:",
        "SAFE_CLEANUP_COMMAND:",
        "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt",
        "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1",
        "--expected-bytes 239",
        "--allowed-relative-path media/controlled_plain_text_marker.txt",
        "--visible-report-markdown",
        "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK",
    ]

    for marker in markers:
        assert marker in pack_text


def test_customer_demo_packaging_qa_gate_records_pass_criteria() -> None:
    text = _qa_text()

    criteria = [
        "Meeting pack artifact exists.",
        "Meeting pack unit test exists.",
        "Meeting pack phase is correct.",
        "Meeting pack expected result is correct.",
        "Meeting pack base state is recorded.",
        "Meeting pack status is safe customer demo meeting pack created.",
        "Meeting pack title is present.",
        "Meeting pack pitch is present.",
        "Meeting pack executive summary is present.",
        "Meeting pack opening script is present.",
        "Meeting pack boundary script is present.",
        "Meeting pack screen order is present.",
        "Meeting pack safe preflight is present.",
        "Meeting pack safe commands are present.",
        "Meeting pack controlled fixture identity is present.",
        "Meeting pack last execution evidence is present.",
        "Meeting pack business value hypotheses are present.",
        "Meeting pack producer discovery questions are present.",
        "Meeting pack private pilot boundary is present.",
        "Meeting pack safe follow-up options are present.",
        "Meeting pack do-not-promise list is present.",
        "Meeting pack stop conditions are present.",
        "Meeting pack close options are present.",
        "Meeting pack safety confirmation is present.",
        "Meeting pack forbidden scope is present.",
        "No installer is created.",
        "No binary package is created.",
        "No real material is included.",
        "No customer material is included.",
        "No generated report artifact is committed.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_customer_demo_packaging_qa_gate_keeps_limitations_active() -> None:
    text = _qa_text()

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


def test_customer_demo_packaging_qa_gate_keeps_safety_scope_explicit() -> None:
    text = _qa_text()

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


def test_customer_demo_packaging_qa_gate_keeps_forbidden_scope_explicit() -> None:
    text = _qa_text()

    forbidden_markers = [
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


def test_customer_demo_packaging_qa_gate_lists_required_validation_targets() -> None:
    text = _qa_text()

    validation_targets = [
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


def test_customer_demo_packaging_qa_gate_has_commit_and_tag_guidance() -> None:
    text = _qa_text()

    assert "test: add CID Local Media Agent customer demo packaging QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-qa-gate-v1-20260701"
        in text
    )
