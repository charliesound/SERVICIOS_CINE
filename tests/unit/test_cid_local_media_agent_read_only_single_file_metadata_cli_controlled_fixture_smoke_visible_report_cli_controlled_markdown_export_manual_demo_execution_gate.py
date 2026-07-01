from pathlib import Path


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_execution_gate_v1.md"
)


def _doc_text() -> str:
    assert DOC_PATH.exists()
    return DOC_PATH.read_text(encoding="utf-8")


def test_manual_demo_execution_gate_declares_phase_and_result() -> None:
    text = _doc_text()

    assert (
        "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE."
        "SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.MANUAL_DEMO.EXECUTION.GATE.V1"
        in text
    )
    assert (
        "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_"
        "VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_MANUAL_DEMO_EXECUTION_GATE_V1_CLOSED"
        in text
    )
    assert "MANUAL_CONTROLLED_FIXTURE_DEMO_EXECUTED_AND_VERIFIED" in text
    assert "EXECUTION_RESULT:\nPASS" in text


def test_manual_demo_execution_gate_records_stable_base() -> None:
    text = _doc_text()

    assert "437b906bc3dfe35404c321ec5d7eff7cac474500" in text
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-manual-demo-readiness-gate-v1-20260701"
        in text
    )


def test_manual_demo_execution_gate_records_controlled_fixture_identity() -> None:
    text = _doc_text()

    assert "controlled_plain_text_marker_v1" in text
    assert "media/controlled_plain_text_marker.txt" in text
    assert "EXPECTED_BYTES:\n239" in text
    assert (
        "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
        in text
    )


def test_manual_demo_execution_gate_records_public_wrapper_command() -> None:
    text = _doc_text()

    assert "scripts/local_media_agent/read_only_single_file_metadata_cli.py" in text
    assert "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt" in text
    assert "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1" in text
    assert "--expected-bytes 239" in text
    assert "--allowed-relative-path media/controlled_plain_text_marker.txt" in text
    assert "--visible-report-markdown" in text
    assert (
        "--visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/"
        "manual_demo_visible_report.md"
        in text
    )


def test_manual_demo_execution_gate_records_export_success_stdout() -> None:
    text = _doc_text()

    assert "MANUAL_EXECUTION_STDOUT:" in text
    assert "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK" in text


def test_manual_demo_execution_gate_records_generated_report_evidence() -> None:
    text = _doc_text()

    assert "GENERATED_REPORT_SIZE_BYTES:\n1795" in text
    assert (
        "GENERATED_REPORT_SHA256:\n"
        "b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd"
        in text
    )
    assert "CID Local Media Agent - Controlled Fixture Smoke Visible Report" in text
    assert "VERIFIED_REPORT_EVIDENCE:" in text


def test_manual_demo_execution_gate_records_cleanup_and_clean_workspace() -> None:
    text = _doc_text()

    assert "CLEANUP_COMMAND_EXECUTED:" in text
    assert "rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports" in text
    assert "FINAL_WORKSPACE_STATUS:\nclean" in text
    assert "No persistent manual demo artifact was committed." in text


def test_manual_demo_execution_gate_keeps_real_material_forbidden() -> None:
    text = _doc_text()

    assert "No real media was used." in text
    assert "No customer material was used." in text
    assert "No execution against real media." in text
    assert "No execution against customer material." in text


def test_manual_demo_execution_gate_keeps_runtime_and_saas_forbidden() -> None:
    text = _doc_text()

    forbidden_markers = [
        "No implementation changes.",
        "No parser changes.",
        "No CLI behavior changes.",
        "No wrapper changes.",
        "No renderer changes.",
        "No in-memory integration changes.",
        "No FFmpeg.",
        "No ffprobe.",
        "No scanner integration.",
        "No batch processing.",
        "No recursive traversal.",
        "No SaaS integration.",
        "No database access.",
        "No backend changes.",
        "No frontend changes.",
        "No Docker work.",
        "No Alembic work.",
        "No Stripe work.",
        "No AI Jobs work.",
        "No credits or ledger work.",
    ]

    for marker in forbidden_markers:
        assert marker in text


def test_manual_demo_execution_gate_lists_required_validations() -> None:
    text = _doc_text()

    assert (
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_"
        "controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_execution_gate.py"
        in text
    )
    assert "bash scripts/dev/guard_wsl_repo.sh" in text
    assert "PostgreSQL-only regression guard required by policy" in text


def test_manual_demo_execution_gate_has_commit_and_tag_guidance() -> None:
    text = _doc_text()

    assert (
        "test: add CID Local Media Agent manual controlled demo execution gate"
        in text
    )
    assert (
        "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-"
        "smoke-visible-report-cli-controlled-markdown-export-manual-demo-execution-gate-v1-20260701"
        in text
    )
