from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_controlled_execution_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_controlled_execution_doc_exists() -> None:
    assert DOC.exists()


def test_phase_authorization_and_result_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION" in text
    assert "b5a3bd23ee3851684cfc219fefb29dd0ae94a555" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION_PASS_WITH_DOCUMENTED_DELTAS_READY_FOR_QA_GATE" in text


def test_fixture_and_authorized_command_are_recorded() -> None:
    text = _text()
    assert "/tmp/cid_local_media_agent_synthetic_demo_001/input" in text
    assert "/tmp/cid_local_media_agent_synthetic_demo_001/output" in text
    assert "python scripts/cid_media_agent_scan.py --input-root /tmp/cid_local_media_agent_synthetic_demo_001/input --output-root /tmp/cid_local_media_agent_synthetic_demo_001/output --json" in text
    for fixture_file in [
        "camera/A001_SC001_TK001.mov",
        "camera/A001_SC001_TK002.mp4",
        "sound/A001_SC001_TK001.wav",
        "proxies/A001_SC001_TK001_PROXY.mp4",
        "non_media/notes.txt",
        "non_media/installer.exe",
        "UNKNOWN/UNKNOWN_ASSET.txt",
    ]:
        assert fixture_file in text


def test_runtime_result_is_recorded() -> None:
    text = _text()
    for token in [
        "`exit_code`: `1`",
        "`status`: `completed_with_warnings`",
        "`privacy_mode`: `local_only`",
        "`candidate_media_count`: `5`",
        "`files_seen`: `5`",
        "`human_review_required_count`: `1`",
        "`warnings_count`: `1`",
        "`warnings`: `unknown synthetic placeholder`",
        "`accepted_extension_counts`: `.mov=1`, `.mp4=2`, `.wav=1`",
        "`rejected_extension_counts`: `.exe=1`, `.txt=2`",
        "`ffprobe_preflight.status`: `skipped`",
    ]:
        assert token in text


def test_persisted_outputs_and_json_facts_are_recorded() -> None:
    text = _text()
    for output_file in [
        "00_project/project_manifest.json",
        "00_project/processing_status.json",
        "00_project/privacy_report.md",
        "00_project/human_review_index.md",
        "01_media_catalog/media_catalog.json",
        "01_media_catalog/media_catalog.csv",
        "01_media_catalog/media_catalog.md",
        "01_media_catalog/scan_warnings.json",
        "01_media_catalog/manual_media_review.csv",
        "99_logs/processing_log.md",
        "99_logs/errors.json",
        "99_logs/warnings.json",
        "99_logs/privacy_events.json",
    ]:
        assert output_file in text
    for fact in [
        "status = completed_with_warnings",
        "candidate_media_count = 5",
        "human_review_required_count = 1",
        "ffprobe_preflight.requested = false",
        "ffprobe_preflight.status = skipped",
        "warnings = [\"unknown synthetic placeholder\"]",
        "errors = []",
        "event = local_only_scan_completed",
        "original_media_left_client_system = false",
    ]:
        assert fact in text


def test_documented_deltas_privacy_and_non_goals_are_recorded() -> None:
    text = _text()
    for token in [
        "warnings_count` appears in stdout summary but is not persisted",
        "synthetic_project` appears in stdout summary but is not persisted",
        "02_audio_sync",
        "03_transcription",
        "04_subtitles",
        "05_reports",
        "06_exports",
        "privacy_events.json` is not empty",
        "Privacy token check passed",
        "real client media scanning",
        "public/client-facing demo",
        "ffprobe execution",
        "ffmpeg execution",
        "audio/video synchronization",
        "transcription",
        "subtitle generation",
        "DaVinci Resolve export",
        "SaaS upload",
        "database writes",
        "network calls",
        "frontend/backend SaaS changes",
        "Docker or Alembic changes",
        "Stripe, AI Jobs, credits, or ledger changes",
    ]:
        assert token in text


def test_next_phase_is_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in text
