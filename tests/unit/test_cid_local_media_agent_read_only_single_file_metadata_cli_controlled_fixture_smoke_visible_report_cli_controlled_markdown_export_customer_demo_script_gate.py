from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_script_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_script_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.SCRIPT.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_SCRIPT_GATE_V1_CLOSED"
        in text
    )
    assert "READY_FOR_CONTROLLED_CUSTOMER_DEMO_SCRIPTED_PRESENTATION_ONLY" in text


def test_customer_demo_script_gate_records_base_state() -> None:
    text = _doc_text()

    assert "18febf1ddb65b286c5aecd5dba837799cf8f8adc" in text
    assert "18febf1 test: add CID Local Media Agent customer demo readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-readiness-gate-v1-20260701"
        in text
    )


def test_customer_demo_script_gate_defines_demo_type_owner_and_audience() -> None:
    text = _doc_text()

    assert "Controlled customer-facing technical preview." in text
    assert "Owner/operator only." in text
    assert "Trusted producer." in text
    assert "Trusted executive producer." in text
    assert "Trusted postproduction supervisor." in text
    assert "Public launch." in text
    assert "Paid delivery." in text
    assert "Customer file processing." in text


def test_customer_demo_script_gate_contains_opening_script() -> None:
    text = _doc_text()

    assert "I want to show you a controlled preview of CID Local Media Agent." in text
    assert "local-first: the files stay on the customer machine" in text
    assert "not going to process real footage or real sound" in text
    assert "safe internal fixture" in text
    assert "wrapper command, metadata validation, visible Markdown report" in text


def test_customer_demo_script_gate_contains_value_proposition() -> None:
    text = _doc_text()

    assert "lack of fast, local, auditable visibility over audiovisual material" in text
    assert "folders with mixed, unclear, or poorly documented assets" in text
    assert "before they start organizing, syncing, transcribing, editing, or delivering" in text
    assert "safe local command can inspect one allowed file" in text


def test_customer_demo_script_gate_defines_what_to_show_and_not_show() -> None:
    text = _doc_text()

    show_markers = [
        "Show the repository is at the expected stable base.",
        "Show the workspace is clean.",
        "Show the controlled fixture path.",
        "Run the stdout visible report command.",
        "Run the controlled Markdown export command.",
        "Verify the exported report exists inside the controlled temporary root.",
        "Clean the temporary export root.",
    ]

    not_show_markers = [
        "Do not show real camera files.",
        "Do not show real sound files.",
        "Do not show confidential project folders.",
        "Do not show customer material.",
        "Do not show SaaS internals.",
        "Do not show future features as if they already work.",
    ]

    for marker in show_markers + not_show_markers:
        assert marker in text


def test_customer_demo_script_gate_records_safe_commands() -> None:
    text = _doc_text()

    assert "STDOUT_REPORT:" in text
    assert "EXPORT_PREP:" in text
    assert "EXPORT_REPORT:" in text
    assert "VERIFY_REPORT:" in text
    assert "CLEANUP:" in text
    assert "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt" in text
    assert "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "--expected-bytes 239" in text
    assert "--allowed-relative-path media/controlled_plain_text_marker.txt" in text
    assert "--visible-report-markdown" in text
    assert "customer_demo_visible_report.md" in text
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text


def test_customer_demo_script_gate_records_fixture_identity() -> None:
    text = _doc_text()

    assert "controlled_plain_text_marker_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text


def test_customer_demo_script_gate_has_timing_guide() -> None:
    text = _doc_text()

    assert "Minute 0: Explain local-first product direction." in text
    assert "Minute 3: Run visible report to stdout." in text
    assert "Minute 5: Run controlled Markdown export." in text
    assert "Minute 9: Ask discovery questions." in text
    assert "Minute 10: Agree next safe step." in text


def test_customer_demo_script_gate_has_discovery_questions() -> None:
    text = _doc_text()

    questions = [
        "How many productions do you usually supervise at the same time?",
        "Where do you currently lose time when receiving camera, sound, or postproduction material?",
        "Who is responsible for checking whether folders are complete and understandable?",
        "Would a local report before upload or handoff reduce risk for your team?",
        "Would you prefer this as a local app, CLI tool, or integrated CID module?",
        "Who would approve a paid pilot inside your company?",
    ]

    for question in questions:
        assert question in text


def test_customer_demo_script_gate_defines_allowed_and_forbidden_roadmap_language() -> None:
    text = _doc_text()

    assert "Each step must be gated separately before it is presented as working functionality." in text
    assert "Do not say real media processing is ready." in text
    assert "Do not say folder scanning is ready." in text
    assert "Do not say transcription is ready." in text
    assert "Do not say sync is ready." in text
    assert "Do not say DaVinci Resolve integration is ready." in text
    assert "Do not say licensing or installer delivery is ready." in text


def test_customer_demo_script_gate_contains_safe_close_script() -> None:
    text = _doc_text()

    assert "This is not yet a production product." in text
    assert "whether this local-first direction solves a real operational pain" in text
    assert "The current working proof is the controlled report chain" in text
    assert "private pilot with strict boundaries" in text
    assert "no cloud upload of sensitive files" in text


def test_customer_demo_script_gate_records_stop_conditions() -> None:
    text = _doc_text()

    stop_conditions = [
        "Stop if the repository is not at the expected stable base.",
        "Stop if the workspace is not clean before the demo.",
        "Stop if the target path is not the controlled fixture path.",
        "Stop if the output path is not inside the controlled temporary export root.",
        "Stop if any customer or real media path appears.",
        "Stop if the audience asks to process real material during this gate.",
        "Stop if the audience interprets the demo as production-ready.",
    ]

    for condition in stop_conditions:
        assert condition in text


def test_customer_demo_script_gate_keeps_safety_scope_explicit() -> None:
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
    ]

    for marker in safety_markers:
        assert marker in text


def test_customer_demo_script_gate_keeps_forbidden_scope_explicit() -> None:
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
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_customer_demo_script_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_customer_demo_script_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo script gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-script-gate-v1-20260701"
        in text
    )
