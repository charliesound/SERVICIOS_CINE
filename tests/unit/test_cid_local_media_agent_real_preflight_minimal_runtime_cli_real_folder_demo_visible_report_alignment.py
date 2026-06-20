from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_alignment_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_post_execution_alignment_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_visible_report_alignment_doc_exists_and_source_exists() -> None:
    assert DOC.exists()
    assert SOURCE_DOC.exists()


def test_phase_source_result_head_and_tag_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.ALIGNMENT.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.POST.EXECUTION.ALIGNMENT.V1" in text
    assert "LOCAL_MEDIA_AGENT_POST_EXECUTION_ALIGNMENT_PASS_CURRENT_SCANNER_BASELINE_ACCEPTED_WITH_ROADMAP_OUTPUT_DELTAS" in text
    assert "b7465b28d6450f1f736e4a41f0ebf7b485adea03" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-scenario-post-execution-alignment-v1-20260620" in text


def test_current_accepted_scanner_baseline_is_recorded() -> None:
    text = _text()
    for token in [
        "`00_project/`",
        "`01_media_catalog/`",
        "`99_logs/`",
        "audio sync",
        "transcription",
        "subtitle generation",
        "translation",
        "DaVinci Resolve export",
        "Avid export",
        "client-facing delivery",
    ]:
        assert token in text


def test_required_visible_sections_are_recorded() -> None:
    text = _text()
    for token in [
        "Executive summary",
        "Local-only privacy confirmation",
        "Input fixture summary",
        "Media candidate summary",
        "Accepted media by extension",
        "Rejected non-media by extension",
        "Human review required items",
        "Warning path summary",
        "Created output files summary",
        "Roadmap outputs not yet generated",
        "Producer interpretation",
        "Next recommended technical actions",
    ]:
        assert token in text


def test_required_data_points_are_recorded() -> None:
    text = _text()
    for token in [
        "status = completed_with_warnings",
        "privacy_mode = local_only",
        "candidate_media_count = 5",
        "human_review_required_count = 1",
        "warnings_count = 1",
        "unknown synthetic placeholder",
        ".mov=1", "`.mp4=2`", ".wav=1",
        ".exe=1", "`.txt=2`",
        "ffprobe preflight `skipped`",
        "local_only_scan_completed",
        "original_media_left_client_system = false",
    ]:
        assert token in text


def test_producer_interpretation_and_roadmap_rules_are_recorded() -> None:
    text = _text()
    for token in [
        "The scanner found valid media candidates.",
        "The scanner rejected non-media files instead of treating them as assets.",
        "The scanner raised a human review warning for ambiguous material.",
        "The scanner remained local-only.",
        "The warning-path exit code is expected for this controlled demo.",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
        "must not present those directories as already implemented runtime outputs",
    ]:
        assert token in text


def test_privacy_rules_and_forbidden_tokens_are_recorded() -> None:
    text = _text()
    for token in [
        "must not leak local user names",
        "machine names",
        "Windows paths",
        "WSL paths outside approved synthetic demo context",
        "real client material",
        "`/mnt/`",
        "Windows drive paths",
        "UNC paths",
        "`DESKTOP-`",
        "`harliesound`",
        "`SERVICIOS_CINE`",
        "approved synthetic demo context",
    ]:
        assert token in text


def test_non_goals_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "runtime report generation",
        "scanner code changes",
        "real media scanning",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "SaaS upload",
        "database writes",
        "network calls",
        "Stripe, AI Jobs, credits, or ledger changes",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_ALIGNMENT_PASS_READY_FOR_VISIBLE_REPORT_CONTRACT",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.CONTRACT.V1",
    ]:
        assert token in text
