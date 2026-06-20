from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_fixture_qa_gate_v1.md")
CREATE_FIXTURE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_create_fixture_v1.md")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.FIXTURE.QA.GATE.V1"


def read(path: Path) -> str:
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_fixture_qa_gate_doc_exists_and_names_phase():
    text = read(DOC)
    assert PHASE in text
    assert "Demo Scenario Fixture QA Gate v1" in text


def test_fixture_qa_gate_depends_on_create_fixture_phase():
    text = read(DOC)
    create_fixture = read(CREATE_FIXTURE_DOC)
    assert "DEMO.SCENARIO.CREATE.FIXTURE.V1" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CREATE_FIXTURE_PASS_SYNTHETIC_PLACEHOLDERS_ONLY" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CREATE_FIXTURE_PASS_SYNTHETIC_PLACEHOLDERS_ONLY" in create_fixture


def test_fixture_qa_evidence_is_recorded():
    text = read(DOC)
    for required in [
        "repo status before QA gate: `CLEAN`",
        "HEAD approved lineage: `72d2031de2c1d34a1d95e9d5fba2e3eb1263f5b2`",
        "origin/main alignment: `PASS`",
        "create fixture tag alignment: `PASS`",
        "fixture root exists: `PASS`",
        "expected directory tree exists: `PASS`",
        "expected file count: `7`",
        "placeholder-only content policy: `PASS`",
        "forbidden path policy: `PASS`",
        "scanner execution: `NOT_EXECUTED`",
        "ffprobe execution: `NOT_EXECUTED`",
        "ffmpeg execution: `NOT_EXECUTED`",
        "real client material: `NOT_USED`",
    ]:
        assert required in text


def test_required_fixture_files_and_content_policy_are_declared():
    text = read(DOC)
    for required in [
        "/tmp/cid_local_media_agent_synthetic_demo_001/",
        "input/camera/A001_SC001_TK001.mov",
        "input/camera/A001_SC001_TK002.mp4",
        "input/sound/A001_SC001_TK001.wav",
        "input/proxies/A001_SC001_TK001_PROXY.mp4",
        "input/non_media/notes.txt",
        "input/non_media/installer.exe",
        "input/UNKNOWN/UNKNOWN_ASSET.txt",
        "output/",
        "synthetic placeholder only",
    ]:
        assert required in text


def test_execution_authorization_boundary_is_explicit():
    text = read(DOC)
    for required in [
        "This QA gate does not authorize scanner execution by itself.",
        "A later execution authorization gate is still required",
        "python scripts/cid_media_agent_scan.py",
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


def test_fixture_qa_gate_result_and_next_phase_are_declared():
    text = read(DOC)
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_FIXTURE_QA_GATE_PASS_READY_FOR_EXECUTION_AUTHORIZATION_GATE" in text
    assert "DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1" in text
