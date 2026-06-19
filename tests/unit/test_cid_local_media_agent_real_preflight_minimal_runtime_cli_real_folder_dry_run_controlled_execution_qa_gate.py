from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_qa_gate_v1.md")
RECORD_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_v1.md")

def read(path):
    return path.read_text(encoding="utf-8")

def test_qa_gate_docs_exist():
    assert QA_DOC.exists()
    assert RECORD_DOC.exists()

def test_qa_gate_phase_and_upstream_record_are_declared():
    t = read(QA_DOC)
    assert "CONTROLLED.EXECUTION.QA.GATE.V1" in t
    assert "CONTROLLED.EXECUTION.V1" in t

def test_qa_gate_validates_sanitized_result_against_record():
    qa = read(QA_DOC)
    record = read(RECORD_DOC)
    required = ["status=PREFLIGHT_PASS", "exit_code=0", "media_file_count=2", "accepted_extension_counts=.mov:1,.wav:1", "maximum_detected_scan_depth=3", "total_selected_media_size_bucket=LE_100MB"]
    for item in required:
        assert item in qa
        assert item in record

def test_qa_gate_requires_validation_chain():
    t = read(QA_DOC)
    required = ["controlled execution record test passes", "dry-run execution gate test passes", "dry-run readiness gate test passes", "real folder authorization QA gate test passes", "real folder authorization contract test passes", "WSL repository secrets guard passes", "PostgreSQL-only regression guard passes"]
    for item in required:
        assert item in t

def test_qa_gate_keeps_private_evidence_outside_repo():
    t = read(QA_DOC)
    assert "remains outside the repository" in t
    assert "raw evidence payload is copied into the repository" in t

def test_qa_gate_private_tokens_are_absent():
    t = read(QA_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t

def test_qa_gate_non_goals_are_explicit():
    t = read(QA_DOC)
    required = ["real client media", "sensitive media", "personal data processing", "scanner integration", "ffprobe or ffmpeg", "media decoding", "report generation", "transcription", "translation", "subtitles", "sync", "DaVinci Resolve integration", "Avid integration", "SaaS integration", "database changes", "Docker changes", "Alembic changes", "Stripe changes", "AI Jobs changes", "credits", "ledger changes"]
    for item in required:
        assert item in t
