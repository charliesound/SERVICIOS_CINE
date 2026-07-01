from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_customer_demo_execution_qa_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_customer_demo_execution_qa_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.EXECUTION.QA.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_EXECUTION_QA_GATE_V1_CLOSED"
        in text
    )
    assert "CONTROLLED_CUSTOMER_DEMO_EXECUTION_QA_VERIFIED" in text


def test_customer_demo_execution_qa_gate_records_execution_gate_head() -> None:
    text = _doc_text()

    assert "9127a2f776fc9350cd1b99393524815fedc61a6a" in text
    assert "9127a2f test: add CID Local Media Agent customer demo execution gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-gate-v1-20260701"
        in text
    )


def test_customer_demo_execution_qa_gate_records_remote_tag_verification() -> None:
    text = _doc_text()

    assert "HEAD_SHA=9127a2f776fc9350cd1b99393524815fedc61a6a" in text
    assert "REMOTE_TAG_SHA=9127a2f776fc9350cd1b99393524815fedc61a6a" in text
    assert "REMOTE_TAG_POINTS_TO_CUSTOMER_DEMO_EXECUTION_GATE_HEAD" in text


def test_customer_demo_execution_qa_gate_records_execution_result() -> None:
    text = _doc_text()

    assert "LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS" in text
    assert "Execution result was PASS." in text
    assert "Execution evidence was recorded." in text
    assert "Final workspace was clean." in text


def test_customer_demo_execution_qa_gate_records_execution_base_and_closure() -> None:
    text = _doc_text()

    assert "Working directory was /opt/SERVICIOS_CINE." in text
    assert "Branch was main." in text
    assert "HEAD was ce417ff23af372e01cad66fd8d40e73d16519488 during execution." in text
    assert "Workspace was clean before execution." in text
    assert "Controlled export root was absent before execution." in text
    assert "Customer demo execution gate was committed." in text
    assert "Customer demo execution gate was pushed to main." in text
    assert "Remote tag verification matched execution gate HEAD." in text


def test_customer_demo_execution_qa_gate_records_fixture_identity() -> None:
    text = _doc_text()

    assert "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "controlled_plain_text_marker_v1" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_customer_demo_execution_qa_gate_records_stdout_visible_report_qa() -> None:
    text = _doc_text()

    markers = [
        "The stdout visible report was generated from the controlled fixture.",
        "The report title was present.",
        "The smoke status was PASS.",
        "The fixture id was present.",
        "The allowed relative path was present.",
        "The byte size was 239.",
        "The fixture digest matched the expected value.",
        "The execution mode was read_only_single_file_metadata_visible_report_markdown_in_memory.",
        "The exit code was 0.",
        "The fixture immutability status was PASS_READ_ONLY_METADATA_COLLECTION.",
        "The output file creation status was PASS_NONE_CREATED.",
        "The visible report stated no real material.",
        "The visible report stated no customer material.",
    ]

    for marker in markers:
        assert marker in text


def test_customer_demo_execution_qa_gate_records_controlled_export_qa() -> None:
    text = _doc_text()

    markers = [
        "The controlled Markdown export returned CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.",
        "The generated report path was inside the controlled temporary export root.",
        "The generated report file name was customer_demo_visible_report.md.",
        "The generated report size was 1795 bytes.",
        "The generated report digest was recorded.",
        "The generated report contained the expected title.",
        "The generated report contained the allowed relative path.",
        "The generated report contained the expected fixture digest.",
    ]

    for marker in markers:
        assert marker in text


def test_customer_demo_execution_qa_gate_records_generated_report_evidence() -> None:
    text = _doc_text()

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
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text


def test_customer_demo_execution_qa_gate_records_cleanup() -> None:
    text = _doc_text()

    assert "The controlled export root was removed after verification." in text
    assert "No generated customer demo report was committed." in text
    assert "Final workspace was clean." in text


def test_customer_demo_execution_qa_gate_records_pass_criteria() -> None:
    text = _doc_text()

    pass_items = [
        "Execution result was PASS.",
        "Execution evidence was recorded.",
        "Customer demo execution gate was committed and pushed.",
        "Execution gate stable tag was pushed.",
        "Remote tag verification matched the execution gate HEAD.",
        "Controlled fixture identity was preserved.",
        "Controlled fixture digest was preserved.",
        "Generated report digest was recorded.",
        "Controlled export root was removed.",
        "Final workspace was clean.",
        "No real media was used.",
        "No customer material was used.",
        "No production material was used.",
        "No confidential material was used.",
    ]

    for item in pass_items:
        assert item in text


def test_customer_demo_execution_qa_gate_keeps_limitations_active() -> None:
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


def test_customer_demo_execution_qa_gate_keeps_safety_scope_explicit() -> None:
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


def test_customer_demo_execution_qa_gate_keeps_forbidden_scope_explicit() -> None:
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


def test_customer_demo_execution_qa_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_customer_demo_execution_qa_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent customer demo execution QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-customer-demo-execution-qa-gate-v1-20260701"
        in text
    )
