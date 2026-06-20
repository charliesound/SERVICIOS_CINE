from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_controlled_execution_qa_gate_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_controlled_execution_v1.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_qa_gate_doc_exists_and_source_record_exists() -> None:
    assert DOC.exists()
    assert SOURCE_DOC.exists()


def test_phase_source_result_and_commit_are_recorded() -> None:
    text = _text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.V1" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION_PASS_WITH_DOCUMENTED_DELTAS_READY_FOR_QA_GATE" in text
    assert "8582b4a7726cfd4cf74dcce7d1ad78ecd2f18e3c" in text
    assert "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-scenario-controlled-execution-v1-20260620" in text


def test_qa_scope_preserves_no_runtime_and_no_saas_boundaries() -> None:
    text = _text()
    for token in [
        "does not execute the scanner again",
        "does not inspect or commit `/tmp` runtime outputs",
        "real client media",
        "public demo use",
        "ffprobe",
        "ffmpeg",
        "transcription",
        "subtitles",
        "sync",
        "SaaS upload",
        "database writes",
        "network calls",
        "Docker",
        "Alembic",
        "frontend/backend SaaS",
        "Stripe",
        "AI Jobs",
        "credits",
        "ledger changes",
    ]:
        assert token in text


def test_required_execution_evidence_is_recorded() -> None:
    text = _text()
    for token in [
        "authorized HEAD `b5a3bd23ee3851684cfc219fefb29dd0ae94a555`",
        "only the authorized scanner command was executed",
        "fixture root was `/tmp/cid_local_media_agent_synthetic_demo_001`",
        "fixture was synthetic placeholder only",
        "exit_code = 1",
        "status = completed_with_warnings",
        "privacy_mode = local_only",
        "candidate_media_count = 5",
        "human_review_required_count = 1",
        "warnings_count = 1",
        "unknown synthetic placeholder",
        "`.mov=1`, `.mp4=2`, `.wav=1`",
        "`.exe=1`, `.txt=2`",
        "ffprobe preflight was skipped",
        "local_only_scan_completed",
        "original_media_left_client_system = false",
        "final privacy token check passed",
        "repository remained clean after runtime execution and verification",
    ]:
        assert token in text


def test_required_deltas_are_recorded() -> None:
    text = _text()
    for token in [
        "`warnings_count` is stdout-only",
        "`synthetic_project` is stdout-only",
        "`02_audio_sync`",
        "`03_transcription`",
        "`04_subtitles`",
        "`05_reports`",
        "`06_exports`",
        "`privacy_events.json` is not empty",
    ]:
        assert token in text


def test_qa_decision_result_and_next_phase_are_recorded() -> None:
    text = _text()
    assert "bounded, local-only, synthetic-only" in text
    assert "not blockers for this gate" in text
    assert "LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION_QA_GATE_PASS_READY_FOR_NEXT_DEMO_ALIGNMENT_PHASE" in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.POST.EXECUTION.ALIGNMENT.V1" in text
