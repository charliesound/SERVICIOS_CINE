from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_packaging_readiness_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_packaging_readiness_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PACKAGING.READINESS.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_PACKAGING_READINESS_GATE_V1_CLOSED"
        in text
    )
    assert "READY_FOR_SAFE_CUSTOMER_DEMO_MEETING_PACK_ONLY" in text


def test_customer_demo_packaging_readiness_gate_records_base_state() -> None:
    text = _doc_text()

    assert "a13d20b89beb39f5468785d93767c76edd3eefb7" in text
    assert "a13d20b test: add CID Local Media Agent customer demo execution QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-qa-gate-v1-20260701"
        in text
    )


def test_customer_demo_packaging_readiness_gate_defines_scope() -> None:
    text = _doc_text()

    assert "Controlled customer demo meeting pack." in text
    assert "Owner/operator only." in text
    assert "This gate does not create an installer." in text
    assert "This gate does not create binaries." in text
    assert "This gate does not package customer files." in text
    assert "This gate does not approve production use." in text


def test_customer_demo_packaging_readiness_gate_defines_allowed_and_forbidden_use() -> None:
    text = _doc_text()

    allowed = [
        "One-to-one trusted prospect meeting.",
        "Private producer meeting.",
        "Private executive producer meeting.",
        "Private postproduction supervisor meeting.",
        "Private distributor or exhibitor technical discussion.",
        "Private school decision-maker meeting without participant files.",
    ]
    forbidden = [
        "Public launch.",
        "Paid delivery.",
        "Downloadable product distribution.",
        "Unsupervised installation.",
        "Workshop with participant media.",
        "Real project ingestion.",
        "Customer file processing.",
        "Production workflow replacement.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_customer_demo_packaging_readiness_gate_contains_executive_summary_and_pitch() -> None:
    text = _doc_text()

    assert "CID Local Media Agent is being prepared as a local-first utility for audiovisual teams." in text
    assert "one safe command can inspect one allowed internal fixture" in text
    assert "The current demo is not a production product." in text
    assert "The current demo is not a real-media processor." in text
    assert "CID Local Media Agent aims to help film and postproduction teams" in text


def test_customer_demo_packaging_readiness_gate_contains_short_script() -> None:
    text = _doc_text()

    assert "This is a controlled preview, not a production release." in text
    assert "files stay on the client machine" in text
    assert "I will only show a safe internal fixture" in text
    assert "I will not process real footage, real sound, confidential files, or customer material." in text
    assert "controlled report chain: validation, visible report, controlled export, verification, cleanup, and evidence" in text


def test_customer_demo_packaging_readiness_gate_records_what_demo_proves() -> None:
    text = _doc_text()

    proves = [
        "The public wrapper can be executed safely.",
        "The controlled fixture can be validated by path, size, and digest.",
        "A visible Markdown report can be generated.",
        "A Markdown report can be exported only into a controlled temporary root.",
        "The report can be verified.",
        "The generated report digest can be recorded.",
        "The temporary export root can be removed.",
        "The workspace can remain clean.",
        "The evidence chain can be audited.",
    ]

    for item in proves:
        assert item in text


def test_customer_demo_packaging_readiness_gate_records_what_demo_does_not_prove() -> None:
    text = _doc_text()

    not_proves = [
        "It does not prove real camera media processing.",
        "It does not prove real sound file processing.",
        "It does not prove folder scanning.",
        "It does not prove batch processing.",
        "It does not prove recursive traversal.",
        "It does not prove audiovisual metadata extraction.",
        "It does not prove transcription.",
        "It does not prove subtitles.",
        "It does not prove sync.",
        "It does not prove DaVinci Resolve integration.",
        "It does not prove Avid integration.",
        "It does not prove SaaS integration.",
        "It does not prove installer delivery.",
        "It does not prove production readiness.",
    ]

    for item in not_proves:
        assert item in text


def test_customer_demo_packaging_readiness_gate_includes_safe_commands() -> None:
    text = _doc_text()

    assert "STDOUT_REPORT_COMMAND:" in text
    assert "EXPORT_REPORT_COMMAND:" in text
    assert "VERIFY_REPORT_COMMANDS:" in text
    assert "CLEANUP_COMMAND:" in text
    assert "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt" in text
    assert "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "--expected-bytes 239" in text
    assert "--allowed-relative-path media/controlled_plain_text_marker.txt" in text
    assert "--visible-report-markdown" in text
    assert "customer_demo_visible_report.md" in text
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text


def test_customer_demo_packaging_readiness_gate_records_fixture_and_execution_evidence() -> None:
    text = _doc_text()

    assert "controlled_plain_text_marker_v1" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "EXPECTED_FIXTURE_SHA256:\n"
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )
    assert "Controlled customer demo execution result: LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS" in text
    assert "Generated report size: 1795 bytes" in text
    assert "Generated report digest: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd" in text
    assert "Final workspace: clean" in text


def test_customer_demo_packaging_readiness_gate_defines_assets_allowed_and_forbidden() -> None:
    text = _doc_text()

    allowed = [
        "Executive summary text.",
        "One-sentence pitch.",
        "Short meeting script.",
        "Safe demo command sequence.",
        "Demo limitation list.",
        "Discovery questions.",
        "Go/no-go checklist.",
        "Follow-up options.",
        "Evidence summary from the controlled execution QA gate.",
    ]
    forbidden = [
        "Installer package.",
        "Executable package.",
        "Binary distribution.",
        "Customer media sample.",
        "Real camera file.",
        "Real sound file.",
        "Confidential project folder.",
        "SaaS credentials.",
        "Database access.",
        "Backend screen.",
        "Frontend screen.",
        "Cloud upload workflow.",
        "Production-ready claim.",
    ]

    for marker in allowed + forbidden:
        assert marker in text


def test_customer_demo_packaging_readiness_gate_includes_discovery_questions() -> None:
    text = _doc_text()

    questions = [
        "How many productions do you supervise at the same time?",
        "Where do you currently lose time when receiving camera, sound, or postproduction material?",
        "Who checks whether folders are complete and understandable?",
        "Would a local report before upload or handoff reduce operational risk?",
        "What would be the first useful real-media preflight your team would pay for?",
        "Who would approve a private pilot?",
        "What cannot leave your premises under any circumstance?",
    ]

    for question in questions:
        assert question in text


def test_customer_demo_packaging_readiness_gate_includes_follow_up_and_stop_conditions() -> None:
    text = _doc_text()

    follow_up = [
        "Schedule a requirements call.",
        "Define a private pilot boundary.",
        "Identify first real-media preflight requirements.",
        "Collect requirements without taking customer files.",
        "Ask for non-sensitive synthetic examples only.",
        "Define success criteria for a future paid pilot.",
    ]
    stop_conditions = [
        "Stop if the prospect asks to process real material during this controlled pack stage.",
        "Stop if the prospect asks to send customer files.",
        "Stop if the prospect interprets the demo as production-ready.",
        "Stop if the operator cannot explain current limitations clearly.",
        "Stop if the workspace is not clean.",
        "Stop if the repo is not at the expected stable state.",
        "Stop if the controlled fixture path is changed.",
        "Stop if the export path leaves the controlled temporary root.",
        "Stop if the report verification fails.",
        "Stop if cleanup fails.",
    ]

    for marker in follow_up + stop_conditions:
        assert marker in text


def test_customer_demo_packaging_readiness_gate_records_pass_criteria() -> None:
    text = _doc_text()

    criteria = [
        "Executive summary is present.",
        "One-sentence pitch is present.",
        "Short meeting script is present.",
        "Safe command sequence is present.",
        "Controlled fixture identity is present.",
        "Last execution evidence is present.",
        "Limitations are explicit.",
        "Allowed meeting assets are explicit.",
        "Forbidden meeting assets are explicit.",
        "Discovery questions are present.",
        "Safe follow-up options are present.",
        "Stop conditions are present.",
        "No real material is included.",
        "No customer material is included.",
        "No generated report artifact is committed.",
        "No installer or binary package is created.",
    ]

    for criterion in criteria:
        assert criterion in text


def test_customer_demo_packaging_readiness_gate_keeps_safety_scope_explicit() -> None:
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


def test_customer_demo_packaging_readiness_gate_keeps_forbidden_scope_explicit() -> None:
    text = _doc_text()

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


def test_customer_demo_packaging_readiness_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_customer_demo_packaging_readiness_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo packaging readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-readiness-gate-v1-20260701"
        in text
    )
