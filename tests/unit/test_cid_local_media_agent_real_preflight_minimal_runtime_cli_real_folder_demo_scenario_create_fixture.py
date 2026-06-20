from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_create_fixture_v1.md")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_contract_v1.md")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CREATE.FIXTURE.V1"


def read(path: Path) -> str:
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_fixture_creation_doc_exists_and_names_phase():
    text = read(DOC)
    assert PHASE in text
    assert "Demo Scenario Create Fixture v1" in text


def test_fixture_creation_depends_on_contract():
    text = read(DOC)
    contract = read(CONTRACT_DOC)
    assert "DEMO.SCENARIO.CONTRACT.V1" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CONTRACT_PASS_SYNTHETIC_LOCAL_ONLY" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CONTRACT_PASS_SYNTHETIC_LOCAL_ONLY" in contract


def test_fixture_root_and_shape_are_recorded():
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
    ]:
        assert required in text


def test_fixture_content_and_creation_evidence_are_recorded():
    text = read(DOC)
    for required in [
        "synthetic placeholder only",
        "approved synthetic demo root: `PASS`",
        "file count: `7`",
        "placeholder content check: `PASS`",
        "forbidden path check: `PASS`",
        "scanner execution: `NOT_EXECUTED`",
        "ffprobe execution: `NOT_EXECUTED`",
        "ffmpeg execution: `NOT_EXECUTED`",
        "real client material: `NOT_USED`",
        "git status after fixture creation: `CLEAN`",
    ]:
        assert required in text


def test_no_goals_and_protected_scope_remain_blocked():
    text = read(DOC)
    for blocked in [
        "scanner execution",
        "public demo",
        "client-facing demo",
        "real client-material demo",
        "media probing",
        "media decoding",
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


def test_fixture_creation_result_and_next_phase_are_declared():
    text = read(DOC)
    assert "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CREATE_FIXTURE_PASS_SYNTHETIC_PLACEHOLDERS_ONLY" in text
    assert "DEMO.SCENARIO.FIXTURE.QA.GATE.V1" in text
