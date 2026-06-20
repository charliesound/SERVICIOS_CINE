from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_execution_authorization_gate_v1.md")
FIXTURE_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_fixture_qa_gate_v1.md")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1"


def read(path: Path) -> str:
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_execution_authorization_doc_exists_and_names_phase():
    text = read(DOC)
    assert PHASE in text
    assert "Demo Scenario Execution Authorization Gate v1" in text


def test_execution_authorization_depends_on_fixture_qa_gate():
    text = read(DOC)
    fixture_qa = read(FIXTURE_QA_DOC)
    assert "DEMO.SCENARIO.FIXTURE.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_FIXTURE_QA_GATE_PASS_READY_FOR_EXECUTION_AUTHORIZATION_GATE" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_FIXTURE_QA_GATE_PASS_READY_FOR_EXECUTION_AUTHORIZATION_GATE" in fixture_qa


def test_authorization_evidence_is_recorded():
    text = read(DOC)
    for required in [
        "repo status before authorization gate: `CLEAN`",
        "HEAD approved lineage: `73070f5b74c932ce9f64b04c35818490bca20518`",
        "origin/main alignment: `PASS`",
        "fixture QA gate tag alignment: `PASS`",
        "fixture root exists: `PASS`",
        "expected fixture tree exists: `PASS`",
        "scanner execution before this gate: `NOT_EXECUTED`",
        "ffprobe execution before this gate: `NOT_EXECUTED`",
        "ffmpeg execution before this gate: `NOT_EXECUTED`",
        "real client material: `NOT_USED`",
    ]:
        assert required in text


def test_authorized_roots_and_command_are_declared():
    text = read(DOC)
    for required in [
        "/tmp/cid_local_media_agent_synthetic_demo_001/",
        "/tmp/cid_local_media_agent_synthetic_demo_001/input",
        "/tmp/cid_local_media_agent_synthetic_demo_001/output",
        "python scripts/cid_media_agent_scan.py --input-root /tmp/cid_local_media_agent_synthetic_demo_001/input --output-root /tmp/cid_local_media_agent_synthetic_demo_001/output --json",
        "No `--ffprobe-preflight` flag is authorized.",
        "No ffmpeg command is authorized.",
        "No network call is authorized.",
        "No SaaS call is authorized.",
        "No database write is authorized.",
    ]:
        assert required in text


def test_expected_future_result_and_outputs_are_declared():
    text = read(DOC)
    for required in [
        "exit_code=1",
        "status=completed_with_warnings",
        "candidate_media_count=5",
        "warnings_count=1",
        "human_review_required_count=1",
        'accepted_extension_counts={".mov":1,".mp4":2,".wav":1}',
        'rejected_extension_counts={".exe":1,".txt":2}',
        "ignored_extension_counts={}",
        "ffprobe_preflight.requested=false",
        "ffprobe_preflight.status=skipped",
        "00_project/processing_status.json",
        "01_media_catalog/media_catalog.json",
        "02_audio_sync/README.txt",
        "03_transcription/README.txt",
        "04_subtitles/README.txt",
        "05_reports/README.txt",
        "06_exports/README.txt",
    ]:
        assert required in text


def test_future_abort_conditions_are_declared():
    text = read(DOC)
    for required in [
        "repo is not clean",
        "HEAD is not approved lineage",
        "fixture root is missing",
        "fixture root is outside",
        "input root is missing",
        "output root is missing",
        "real media is detected",
        "real client material is detected",
        "Windows paths are detected",
        "`/mnt/` paths are detected",
        "scanner exits with code `2`",
        "required JSON fields are missing",
        "semantic counts differ",
        "scanner writes outside output root",
        "privacy checks fail",
    ]:
        assert required in text


def test_no_goals_and_protected_scope_remain_blocked():
    text = read(DOC)
    for blocked in [
        "public demo",
        "client-facing demo",
        "sales demo",
        "real client-material demo",
        "media probing",
        "media decoding",
        "ffprobe execution",
        "ffmpeg execution",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "NLE export",
        "SaaS calls",
        "database writes",
        "network calls",
        "report-expansion scope",
        "Docker",
        "Alembic",
        "Stripe",
        "AI Jobs",
        "credits",
        "ledger",
    ]:
        assert blocked in text


def test_authorization_result_and_next_phase_are_declared():
    text = read(DOC)
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION" in text
    assert "DEMO.SCENARIO.CONTROLLED.EXECUTION.V1" in text
