from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_post_execution_alignment_v1.md")
SOURCE_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_controlled_execution_qa_gate_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_post_execution_alignment_doc_exists_and_source_exists() -> None:
    assert DOC.exists()
    assert SOURCE_QA_DOC.exists()


def test_phase_source_gate_and_result_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.POST.EXECUTION.ALIGNMENT.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION_QA_GATE_PASS_READY_FOR_NEXT_DEMO_ALIGNMENT_PHASE" in text
    assert "a3f1e133f49fba0c95aa37065cc622335d26986d" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-scenario-controlled-execution-qa-gate-v1-20260620" in text


def test_alignment_inputs_are_recorded() -> None:
    text = _text()
    for token in [
        "local-only execution",
        "synthetic placeholder fixture only",
        "no real client media",
        "no public demo use",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no SaaS upload",
        "no database writes",
        "no network calls",
        "exit_code = 1",
        "status = completed_with_warnings",
        "privacy_mode = local_only",
        "candidate_media_count = 5",
        "human_review_required_count = 1",
        "warnings_count = 1",
        "unknown synthetic placeholder",
        "`.mov=1`, `.mp4=2`, `.wav=1`",
        "`.exe=1`, `.txt=2`",
        "ffprobe preflight skipped",
    ]:
        assert token in text


def test_output_set_alignment_decision_is_recorded() -> None:
    text = _text()
    for token in [
        "Current scanner output set is accepted for the minimal demo baseline",
        "`00_project/`",
        "`01_media_catalog/`",
        "`99_logs/`",
        "`02_audio_sync/`",
        "`03_transcription/`",
        "`04_subtitles/`",
        "`05_reports/`",
        "`06_exports/`",
        "product roadmap targets, not blockers",
    ]:
        assert token in text


def test_stdout_and_privacy_alignment_decisions_are_recorded() -> None:
    text = _text()
    for token in [
        "`warnings_count`",
        "`synthetic_project`",
        "stdout-only in the current scanner behavior",
        "not required as persisted JSON fields for this baseline",
        "`privacy_events.json` being non-empty is correct",
        "event = local_only_scan_completed",
        "original_media_left_client_system = false",
        "positive privacy evidence",
        "Exit code 1 remains correct for warning-path demo",
    ]:
        assert token in text


def test_demo_position_and_follow_up_options_are_recorded() -> None:
    text = _text()
    for token in [
        "internal technical demo of the scanner baseline",
        "not yet a client-facing product demo",
        "not yet a promotional sales demo",
        "not yet an audio sync, transcription, subtitles, reports, or DaVinci Resolve export demo",
        "visible report alignment phase",
        "future output directories contract phase",
        "persistence alignment phase for stdout-only fields",
    ]:
        assert token in text


def test_boundary_result_and_next_phase_are_recorded() -> None:
    text = _text()
    for token in [
        "docs/test-only",
        "must not create or modify runtime scanner code",
        "must not execute the scanner",
        "must not touch real media",
        "must not touch SaaS runtime",
        "LOCAL_MEDIA_AGENT_POST_EXECUTION_ALIGNMENT_PASS_CURRENT_SCANNER_BASELINE_ACCEPTED_WITH_ROADMAP_OUTPUT_DELTAS",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.ALIGNMENT.V1",
    ]:
        assert token in text
