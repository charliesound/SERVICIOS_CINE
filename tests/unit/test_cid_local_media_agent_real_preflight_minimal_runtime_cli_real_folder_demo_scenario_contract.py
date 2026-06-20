from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_scenario_contract_v1.md")
READINESS_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_readiness_gate_v1.md")
SCANNER_SCRIPT = Path("scripts/cid_media_agent_scan.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTRACT.V1"


def read(path: Path) -> str:
    assert path.exists()
    return path.read_text(encoding="utf-8")


def test_contract_doc_exists_and_names_phase():
    text = read(DOC)
    assert PHASE in text
    assert "Real Folder Demo Scenario Contract v1" in text


def test_contract_depends_on_demo_readiness_gate():
    text = read(DOC)
    readiness = read(READINESS_DOC)
    assert "LOCAL_MEDIA_AGENT_DEMO_READINESS_GATE_PASS_CONTROLLED_LOCAL_SYNTHETIC_ONLY" in text
    assert "LOCAL_MEDIA_AGENT_DEMO_READINESS_GATE_PASS_CONTROLLED_LOCAL_SYNTHETIC_ONLY" in readiness


def test_contract_result_and_demo_boundaries_are_declared():
    text = read(DOC)
    for required in [
        "LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CONTRACT_PASS_SYNTHETIC_LOCAL_ONLY",
        "CID_LOCAL_MEDIA_AGENT_SYNTHETIC_DEMO_001",
        "/tmp/cid_local_media_agent_synthetic_demo_001/",
        "does not execute the scanner",
        "does not use real client material",
        "The demo itself is not yet created.",
        "No real client-material demo is authorized.",
    ]:
        assert required in text


def test_synthetic_input_expected_command_and_counts_are_declared():
    text = read(DOC)
    for required in [
        "A001_SC001_TK001.mov",
        "A001_SC001_TK002.mp4",
        "A001_SC001_TK001.wav",
        "A001_SC001_TK001_PROXY.mp4",
        "notes.txt",
        "installer.exe",
        "UNKNOWN_ASSET.txt",
        "python scripts/cid_media_agent_scan.py",
        "candidate_media_count=5",
        "warnings_count=1",
        "human_review_required_count=1",
        "accepted_extension_counts=",
        "rejected_extension_counts=",
        "ignored_extension_counts={}",
        "exit_code=1",
    ]:
        assert required in text


def test_outputs_privacy_abort_and_no_goals_are_declared():
    text = read(DOC)
    for required in [
        "00_project/processing_status.json",
        "01_media_catalog/media_catalog.json",
        "no absolute input path leak",
        "no absolute output path leak",
        "no Windows path leak",
        "no `/mnt/` leak",
        "repo is not clean",
        "semantic counts differ",
        "public demo",
        "client-facing demo",
        "ffmpeg execution",
        "transcription",
        "SaaS calls",
        "database writes",
    ]:
        assert required in text


def test_runtime_boundary_and_scanner_dependencies_exist():
    text = read(DOC)
    source = read(SCANNER_SCRIPT)
    assert "This contract changes no runtime files" in text
    assert "does not authorize scanner, report, or CLI behavior changes" in text
    for required in ["SAFE_OUTPUTS", "accepted_extension_counts", "rejected_extension_counts", "ignored_extension_counts", "NON_MEDIA_REJECTED_EXTENSIONS", "UNKNOWN_ASSET", "ffprobe_preflight"]:
        assert required in source


def test_validation_chain_and_next_phase_are_declared():
    text = read(DOC)
    for required in [
        "demo scenario contract test",
        "demo readiness gate",
        "bounded implementation QA gate",
        "scanner safe baseline",
        "scanner execution hardening",
        "scanner CLI contract",
        "guard_wsl_repo.sh",
        "guard_no_sqlite_regressions.sh",
        "DEMO.SCENARIO.CREATE.FIXTURE.V1",
    ]:
        assert required in text
