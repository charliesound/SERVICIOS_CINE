from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_static_template_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_contract_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_static_template_doc_exists_and_source_exists() -> None:
    assert DOC.exists()
    assert SOURCE_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.TEMPLATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTRACT_PASS_READY_FOR_STATIC_REPORT_TEMPLATE" in text
    assert "116465adfebc8dfe36b1f523ffa362ea9f154a9f" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-contract-v1-20260620" in text


def test_report_identity_and_status_are_present() -> None:
    text = _text()
    for token in [
        "CID Local Media Agent - Internal Demo Visible Report",
        "Report audience: `producer_product_post_internal_review`",
        "Report status: `internal_demo_only`",
        "Privacy mode: `local_only`",
        "Scenario: `approved_synthetic_controlled_demo`",
    ]:
        assert token in text


def test_all_required_report_sections_are_present_in_order() -> None:
    text = _text()
    sections = [
        "## 1. Executive Summary",
        "## 2. Local-Only Privacy Confirmation",
        "## 3. Controlled Demo Input Summary",
        "## 4. Scanner Result Summary",
        "## 5. Accepted Media",
        "## 6. Rejected Non-Media",
        "## 7. Human Review Required",
        "## 8. Warnings",
        "## 9. Created Output Artifacts",
        "## 10. Roadmap Modules Not Yet Generated",
        "## 11. Producer Interpretation",
        "## 12. Next Technical Actions",
    ]
    positions = [text.index(section) for section in sections]
    assert positions == sorted(positions)


def test_executive_summary_and_privacy_content_are_present() -> None:
    text = _text()
    for token in [
        "completed the approved synthetic controlled demo with warnings",
        "The scan remained local-only.",
        "detected valid media candidates",
        "rejected non-media files",
        "raised one human review warning",
        "No audio synchronization, transcription, subtitle generation, translation, timeline export, or SaaS upload was executed",
        "Original media left client system: `false`",
        "Privacy event: `local_only_scan_completed`",
        "without uploading media to SaaS, cloud storage, or an external processing service",
    ]:
        assert token in text


def test_input_scanner_result_and_warning_content_are_present() -> None:
    text = _text()
    for token in [
        "Input type: approved synthetic placeholder fixture.",
        "Real client media used: `false`",
        "Public demo media used: `false`",
        "Production customer footage used: `false`",
        "Scanner status: `completed_with_warnings`",
        "Candidate media count: `5`",
        "Human review required count: `1`",
        "Warnings count: `1`",
        "Warning message: `unknown synthetic placeholder`",
        "ffprobe preflight: `skipped`",
        "the scanner did not silently accept ambiguous material",
    ]:
        assert token in text


def test_accepted_rejected_and_human_review_content_are_present() -> None:
    text = _text()
    for token in [
        "Accepted media are scanner candidates, not edited deliverables.",
        "`.mov = 1`",
        "`.mp4 = 2`",
        "`.wav = 1`",
        "`.exe = 1`",
        "`.txt = 2`",
        "rejecting non-media is expected and protects the media catalog",
        "Human review required items: `1`",
        "one synthetic unknown placeholder requires human review",
        "warning-path exit code is expected",
        "ambiguous material should be surfaced to a human",
    ]:
        assert token in text


def test_artifacts_roadmap_and_producer_interpretation_are_present() -> None:
    text = _text()
    for token in [
        "`00_project/` - project-level scanner artifacts",
        "`01_media_catalog/` - media catalog artifacts",
        "`99_logs/` - privacy and processing logs",
        "does not over-claim exact runtime filenames",
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "translation",
        "report generation runtime",
        "DaVinci Resolve export",
        "Avid export",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
        "must not present those roadmap modules as already implemented runtime outputs",
        "useful for organizing and validating local media intake",
        "does not yet synchronize external audio, transcribe dialogue, generate translated subtitles, or export Resolve timelines",
    ]:
        assert token in text


def test_next_actions_boundary_result_and_next_phase_are_present() -> None:
    text = _text()
    for token in [
        "Create a QA gate for this static visible report template.",
        "Define a future static report fixture using only approved synthetic evidence.",
        "authorize a separate report generation phase only after the static template and QA gates are accepted",
        "does not authorize runtime report generation",
        "does not authorize scanner implementation changes",
        "does not authorize real media scanning",
        "does not authorize public or client-facing demo use",
        "does not authorize ffprobe, ffmpeg, SaaS upload, database writes, network calls, Docker, Alembic, frontend/backend SaaS, Stripe, AI Jobs, credits, or ledger changes",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_STATIC_TEMPLATE_PASS_READY_FOR_STATIC_TEMPLATE_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.TEMPLATE.QA.GATE.V1",
    ]:
        assert token in text
