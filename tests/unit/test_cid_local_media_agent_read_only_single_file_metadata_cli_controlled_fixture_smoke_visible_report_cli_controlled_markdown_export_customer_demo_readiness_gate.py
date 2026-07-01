from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_readiness_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_readiness_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.READINESS.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_READINESS_GATE_V1_CLOSED"
        in text
    )
    assert "READY_FOR_CONTROLLED_CUSTOMER_DEMO_SCRIPT_REVIEW" in text


def test_customer_demo_readiness_gate_records_base_state() -> None:
    text = _doc_text()

    assert "6c02de7ae0fe7d7c3effb144b4f3683fc6278949" in text
    assert "6c02de7 test: add CID Local Media Agent manual demo execution QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-qa-gate-v1-20260701"
        in text
    )


def test_customer_demo_readiness_gate_defines_positioning() -> None:
    text = _doc_text()

    assert "controlled technical preview" in text
    assert "local-first media utility" in text
    assert "non-customer controlled fixture" in text
    assert "does not approve real media usage" in text
    assert "does not approve customer material usage" in text
    assert "does not approve production use" in text


def test_customer_demo_readiness_gate_defines_allowed_customer_message() -> None:
    text = _doc_text()

    assert "early controlled preview" in text
    assert "safe internal fixture" in text
    assert "wrapper, validation path, visible report rendering" in text
    assert "controlled export policy" in text
    assert "verification commands, cleanup, and evidence chain" in text


def test_customer_demo_readiness_gate_forbids_overclaiming() -> None:
    text = _doc_text()

    forbidden_claims = [
        "Do not claim that real camera media is supported yet.",
        "Do not claim that real sound files are supported yet.",
        "Do not claim that full folder scanning is supported yet.",
        "Do not claim that batch processing is supported yet.",
        "Do not claim that recursive traversal is supported yet.",
        "Do not claim that audiovisual metadata extraction is supported yet.",
        "Do not claim that transcription is supported yet.",
        "Do not claim that sync by waveform, timecode, or slate is supported yet.",
        "Do not claim that DaVinci Resolve or Avid integration is supported yet.",
        "Do not claim that cloud upload is supported.",
        "Do not claim that customer files can already be processed.",
        "Do not claim that this is a production-ready release.",
    ]

    for claim in forbidden_claims:
        assert claim in text


def test_customer_demo_readiness_gate_defines_allowed_and_forbidden_audience() -> None:
    text = _doc_text()

    assert "Trusted prospective producer." in text
    assert "Trusted production executive." in text
    assert "Trusted postproduction supervisor." in text
    assert "Owner/operator controlled presentation only." in text
    assert "Public launch audience." in text
    assert "Unsupervised customer user." in text
    assert "Paid customer delivery." in text
    assert "Any audience requiring support for confidential media." in text


def test_customer_demo_readiness_gate_records_fixture_identity() -> None:
    text = _doc_text()

    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "controlled_plain_text_marker_v1" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_readiness_gate_records_safe_commands() -> None:
    text = _doc_text()

    assert "CUSTOMER_DEMO_STDOUT_COMMAND:" in text
    assert "CUSTOMER_DEMO_EXPORT_COMMAND:" in text
    assert "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt" in text
    assert "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "--expected-bytes 239" in text
    assert "--allowed-relative-path media/controlled_plain_text_marker.txt" in text
    assert "--visible-report-markdown" in text
    assert (
        "--visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/"
        "customer_demo_visible_report.md"
        in text
    )
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text


def test_customer_demo_readiness_gate_records_verification_targets() -> None:
    text = _doc_text()

    assert "CUSTOMER_DEMO_VERIFICATION_TARGETS:" in text
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text
    assert "controlled_plain_text_marker_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_readiness_gate_records_talk_track() -> None:
    text = _doc_text()

    assert "Step 1: Explain that this is a controlled local-only preview." in text
    assert "Step 3: Run the public wrapper command." in text
    assert "Step 6: Verify that the exported Markdown report exists inside the controlled temporary root." in text
    assert "Step 10: Show that the workspace is clean." in text


def test_customer_demo_readiness_gate_records_stop_conditions() -> None:
    text = _doc_text()

    stop_conditions = [
        "Stop if the repository is not at the expected stable base.",
        "Stop if the workspace is not clean before the demo.",
        "Stop if the target path is not the controlled fixture path.",
        "Stop if the output path is not inside the controlled temporary export root.",
        "Stop if the output suffix is not .md.",
        "Stop if any customer or real media path appears.",
        "Stop if the wrapper does not return the expected export success marker.",
        "Stop if report verification fails.",
        "Stop if cleanup fails.",
        "Stop if workspace final status is not clean.",
    ]

    for condition in stop_conditions:
        assert condition in text


def test_customer_demo_readiness_gate_records_previous_evidence_chain() -> None:
    text = _doc_text()

    assert "Manual demo execution stdout: CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text
    assert "Manual demo report size: 1795 bytes" in text
    assert (
        "Manual demo report digest: "
        "b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd"
        in text
    )
    assert "Manual demo execution QA stable head: 6c02de7ae0fe7d7c3effb144b4f3683fc6278949" in text


def test_customer_demo_readiness_gate_keeps_safety_scope_explicit() -> None:
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


def test_customer_demo_readiness_gate_keeps_forbidden_scope_explicit() -> None:
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


def test_customer_demo_readiness_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_customer_demo_readiness_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-readiness-gate-v1-20260701"
        in text
    )
