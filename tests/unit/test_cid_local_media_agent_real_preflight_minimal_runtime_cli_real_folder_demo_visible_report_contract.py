from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_contract_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_alignment_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_visible_report_contract_doc_exists_and_source_exists() -> None:
    assert DOC.exists()
    assert SOURCE_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTRACT.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.ALIGNMENT.V1" in text
    assert "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_ALIGNMENT_PASS_READY_FOR_VISIBLE_REPORT_CONTRACT" in text
    assert "17511611a15dc94dd795bcd7b10b9509983bc413" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-alignment-v1-20260620" in text


def test_report_identity_is_contractual() -> None:
    text = _text()
    for token in [
        "CID Local Media Agent - Internal Demo Visible Report",
        "producer_product_post_internal_review",
        "internal_demo_only",
        "local_only",
        "internal demo report",
    ]:
        assert token in text


def test_input_scope_and_output_families_are_constrained() -> None:
    text = _text()
    for token in [
        "approved synthetic controlled demo scenario",
        "must not describe real client media",
        "must not describe public demo material",
        "must not claim SaaS upload or cloud processing",
        "`00_project/`",
        "`01_media_catalog/`",
        "`99_logs/`",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
        "roadmap modules",
    ]:
        assert token in text


def test_required_report_sections_are_exactly_specified() -> None:
    text = _text()
    for token in [
        "1. `Executive Summary`",
        "2. `Local-Only Privacy Confirmation`",
        "3. `Controlled Demo Input Summary`",
        "4. `Scanner Result Summary`",
        "5. `Accepted Media`",
        "6. `Rejected Non-Media`",
        "7. `Human Review Required`",
        "8. `Warnings`",
        "9. `Created Output Artifacts`",
        "10. `Roadmap Modules Not Yet Generated`",
        "11. `Producer Interpretation`",
        "12. `Next Technical Actions`",
    ]:
        assert token in text


def test_required_executive_summary_and_data_contract_are_recorded() -> None:
    text = _text()
    for token in [
        "the scanner completed with warnings",
        "the execution stayed local-only",
        "valid media candidates were detected",
        "non-media files were rejected",
        "at least one item requires human review",
        "no sync, transcription, subtitles, or export module was executed",
        "status = completed_with_warnings",
        "privacy_mode = local_only",
        "candidate_media_count = 5",
        "human_review_required_count = 1",
        "warnings_count = 1",
        "warning_message = unknown synthetic placeholder",
        "ffprobe_preflight = skipped",
        "original_media_left_client_system = false",
    ]:
        assert token in text


def test_media_rejection_human_review_and_artifacts_are_recorded() -> None:
    text = _text()
    for token in [
        "`.mov = 1`",
        "`.mp4 = 2`",
        "`.wav = 1`",
        "accepted media are scanner candidates, not edited deliverables",
        "`.exe = 1`",
        "`.txt = 2`",
        "non-media rejection is expected and protects the media catalog",
        "one synthetic unknown placeholder requires human review",
        "the warning-path exit code is expected",
        "ambiguous material is not silently accepted",
        "project-level scanner artifacts under `00_project/`",
        "media catalog artifacts under `01_media_catalog/`",
        "privacy and processing logs under `99_logs/`",
        "avoid over-claiming exact runtime filenames",
    ]:
        assert token in text


def test_roadmap_and_producer_interpretation_contract_are_recorded() -> None:
    text = _text()
    for token in [
        "audio synchronization",
        "transcription",
        "subtitle generation",
        "translation",
        "report generation runtime",
        "DaVinci Resolve export",
        "Avid export",
        "plain production language",
        "organizing and validating local media intake",
        "must not imply that the current baseline can already synchronize audio",
        "transcribe dialogue",
        "generate subtitles",
        "export Resolve timelines",
    ]:
        assert token in text


def test_privacy_non_goals_acceptance_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "local user names",
        "machine names",
        "Windows paths",
        "WSL paths outside approved synthetic demo context",
        "repository paths",
        "real client material",
        "private project titles",
        "private filenames from real shoots",
        "`/mnt/`",
        "`DESKTOP-`",
        "`harliesound`",
        "`SERVICIOS_CINE`",
        "runtime report generation",
        "scanner implementation changes",
        "client-facing demo use",
        "Stripe, AI Jobs, credits, or ledger changes",
        "all required sections are specified",
        "current scanner output families are the only accepted source families",
        "future modules are labelled as roadmap",
        "runtime implementation remains out of scope",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_CONTRACT_PASS_READY_FOR_STATIC_REPORT_TEMPLATE",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.STATIC.TEMPLATE.V1",
    ]:
        assert token in text
