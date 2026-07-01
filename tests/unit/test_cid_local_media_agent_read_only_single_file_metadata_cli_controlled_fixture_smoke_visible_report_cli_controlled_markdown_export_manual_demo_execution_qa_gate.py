from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_execution_qa_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_manual_demo_execution_qa_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.MANUAL_DEMO.EXECUTION.QA.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_MANUAL_DEMO_EXECUTION_QA_GATE_V1_CLOSED"
        in text
    )
    assert "MANUAL_DEMO_EXECUTION_CORRECTED_AND_QA_VERIFIED" in text


def test_manual_demo_execution_qa_gate_records_corrected_stable_head() -> None:
    text = _doc_text()

    assert "f1411d5287bfe73dc7571c309dab79678a9be44e" in text
    assert "f1411d5 fix: keep manual demo execution gate PostgreSQL-only guard compliant" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-gate-v1-20260701"
        in text
    )


def test_manual_demo_execution_qa_gate_records_previous_non_stable_commit() -> None:
    text = _doc_text()

    assert "954e0ba test: add CID Local Media Agent manual controlled demo execution gate" in text
    assert "previously published manual execution gate needed a minimal doc/test compliance correction" in text
    assert "The stable tag must point to the corrected HEAD" in text


def test_manual_demo_execution_qa_gate_records_remote_tag_verification() -> None:
    text = _doc_text()

    assert "HEAD_SHA=f1411d5287bfe73dc7571c309dab79678a9be44e" in text
    assert "REMOTE_TAG_SHA=f1411d5287bfe73dc7571c309dab79678a9be44e" in text
    assert "REMOTE_TAG_POINTS_TO_CORRECTED_HEAD" in text


def test_manual_demo_execution_qa_gate_records_execution_evidence() -> None:
    text = _doc_text()

    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text
    assert "tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md" in text
    assert "GENERATED_REPORT_SIZE_BYTES:\n1795" in text
    assert (
        "GENERATED_REPORT_SHA256:\n"
        "b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd"
        in text
    )


def test_manual_demo_execution_qa_gate_records_fixture_evidence() -> None:
    text = _doc_text()

    assert "controlled_plain_text_marker_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_manual_demo_execution_qa_gate_records_cleanup_and_workspace() -> None:
    text = _doc_text()

    assert "CONTROLLED_TEMP_EXPORT_ROOT_REMOVED_AFTER_VERIFICATION" in text
    assert "FINAL_WORKSPACE_STATUS:\nclean" in text
    assert "No persistent manual demo artifact was committed." in text


def test_manual_demo_execution_qa_gate_records_validation_summary() -> None:
    text = _doc_text()

    expected_lines = [
        "Manual demo execution gate: 11 PASS",
        "Manual demo readiness gate: 10 PASS",
        "Controlled demo execution QA gate: 8 PASS",
        "Controlled demo execution gate: 6 PASS",
        "Wrapper smoke execution QA gate: 10 PASS",
        "Wrapper smoke execution gate: 10 PASS",
        "Implementation QA gate: 15 PASS",
        "Implementation gate: 18 PASS",
        "In-memory wrapper smoke execution QA gate: 13 PASS",
        "In-memory wrapper smoke execution gate: 14 PASS",
        "Visible report contract: 9 PASS",
        "CLI contract gate: 12 PASS",
        "WSL repo guard: PASS",
        "PostgreSQL-only regression guard required by policy: PASS",
        "Push main: PASS",
        "Stable tag update: PASS",
        "Remote tag verification: PASS",
        "Workspace final: clean",
    ]

    for expected_line in expected_lines:
        assert expected_line in text


def test_manual_demo_execution_qa_gate_keeps_safety_scope_explicit() -> None:
    text = _doc_text()

    safety_markers = [
        "No real media was used.",
        "No customer material was used.",
        "No FFmpeg was used.",
        "No ffprobe was used.",
        "No scanner integration was used.",
        "No batch traversal was used.",
        "No recursive traversal was used.",
        "No SaaS module was touched.",
        "No database was touched.",
        "No backend was touched.",
        "No frontend was touched.",
        "No Docker file was touched.",
        "No Alembic migration was touched.",
        "No Stripe code was touched.",
        "No AI Jobs code was touched.",
        "No credits or ledger code was touched.",
    ]

    for marker in safety_markers:
        assert marker in text


def test_manual_demo_execution_qa_gate_keeps_forbidden_scope_explicit() -> None:
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


def test_manual_demo_execution_qa_gate_lists_required_validation_targets() -> None:
    text = _doc_text()

    validation_targets = [
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


def test_manual_demo_execution_qa_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert "test: add CID Local Media Agent manual demo execution QA gate" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-qa-gate-v1-20260701"
        in text
    )
