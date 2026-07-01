from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_execution_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_execution_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.EXECUTION.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_EXECUTION_GATE_V1_CLOSED"
        in text
    )
    assert "CONTROLLED_CUSTOMER_DEMO_EXECUTED_AND_VERIFIED" in text


def test_customer_demo_execution_gate_records_base_state() -> None:
    text = _doc_text()

    assert "ce417ff23af372e01cad66fd8d40e73d16519488" in text
    assert "ce417ff test: add CID Local Media Agent customer demo execution readiness gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-readiness-gate-v1-20260701"
        in text
    )


def test_customer_demo_execution_gate_records_execution_result() -> None:
    text = _doc_text()

    assert "LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS" in text
    assert "Workspace before execution: clean" in text
    assert "Controlled export root before execution: absent" in text
    assert "FINAL_WORKSPACE_STATUS:\nclean" in text


def test_customer_demo_execution_gate_records_operator_boundary() -> None:
    text = _doc_text()

    assert "controlled local-first technical preview" in text
    assert "internal non-customer fixture only" in text
    assert "No real footage, real sound, confidential files, or customer material" in text


def test_customer_demo_execution_gate_records_controlled_fixture_identity() -> None:
    text = _doc_text()

    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "controlled_plain_text_marker_v1" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_execution_gate_records_stdout_visible_report_evidence() -> None:
    text = _doc_text()

    assert "STDOUT_VISIBLE_REPORT_EXECUTION:" in text
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text
    assert "Smoke status: PASS" in text
    assert "CLI execution mode: read_only_single_file_metadata_visible_report_markdown_in_memory" in text
    assert "Exit code: 0" in text
    assert "Fixture immutability status: PASS_READ_ONLY_METADATA_COLLECTION" in text
    assert "Output file creation status: PASS_NONE_CREATED" in text


def test_customer_demo_execution_gate_records_controlled_export_evidence() -> None:
    text = _doc_text()

    assert "CONTROLLED_EXPORT_STDOUT:" in text
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text
    assert (
        "GENERATED_REPORT_PATH:\n"
        "tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md"
        in text
    )
    assert "GENERATED_REPORT_SIZE_BYTES:\n1795" in text
    assert (
        "GENERATED_REPORT_SHA256:\n"
        "b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd"
        in text
    )


def test_customer_demo_execution_gate_records_report_verification() -> None:
    text = _doc_text()

    assert "VERIFIED_REPORT_EVIDENCE:" in text
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_execution_gate_records_cleanup() -> None:
    text = _doc_text()

    assert "CLEANUP_EVIDENCE:" in text
    assert "Controlled export root removed after verification." in text
    assert "No customer demo export artifact was committed." in text


def test_customer_demo_execution_gate_records_pass_criteria() -> None:
    text = _doc_text()

    pass_items = [
        "Repository was at expected stable base.",
        "Workspace was clean before execution.",
        "Only controlled fixture path was used.",
        "Controlled fixture digest matched expected value.",
        "Stdout visible report was generated.",
        "Stdout visible report showed PASS status.",
        "Controlled Markdown export returned the expected success marker.",
        "Exported report existed inside the controlled temporary export root.",
        "Report title was verified.",
        "Allowed relative path was verified.",
        "Controlled fixture digest was verified in the report.",
        "Generated report digest was recorded.",
        "Controlled temporary export root was removed.",
        "Workspace was clean after execution.",
        "No customer material appeared.",
        "No real media appeared.",
        "No production path appeared.",
    ]

    for item in pass_items:
        assert item in text


def test_customer_demo_execution_gate_keeps_limitations_active() -> None:
    text = _doc_text()

    limitations = [
        "This does not approve real media processing.",
        "This does not approve customer material processing.",
        "This does not approve folder scanning.",
        "This does not approve batch processing.",
        "This does not approve recursive traversal.",
        "This does not approve transcription.",
        "This does not approve subtitles.",
        "This does not approve sync.",
        "This does not approve DaVinci Resolve integration.",
        "This does not approve Avid integration.",
        "This does not approve SaaS integration.",
        "This does not approve installer delivery.",
        "This does not approve production readiness.",
    ]

    for limitation in limitations:
        assert limitation in text


def test_customer_demo_execution_gate_keeps_safety_scope_explicit() -> None:
    text = _doc_text()

    safety_markers = [
        "No real media was used.",
        "No customer material was used.",
        "No production material was used.",
        "No confidential material was used.",
        "No FFmpeg was used.",
        "No ffprobe was used.",
        "No scanner integration was used.",
        "No batch traversal was used.",
        "No recursive traversal was used.",
        "No SaaS module was used.",
        "No database was used.",
        "No backend change was made.",
        "No frontend change was made.",
        "No Docker change was made.",
        "No Alembic change was made.",
        "No Stripe change was made.",
        "No AI Jobs change was made.",
        "No credits or ledger change was made.",
    ]

    for marker in safety_markers:
        assert marker in text


def test_customer_demo_execution_gate_keeps_forbidden_scope_explicit() -> None:
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


def test_customer_demo_execution_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_customer_demo_execution_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo execution gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-gate-v1-20260701"
        in text
    )
