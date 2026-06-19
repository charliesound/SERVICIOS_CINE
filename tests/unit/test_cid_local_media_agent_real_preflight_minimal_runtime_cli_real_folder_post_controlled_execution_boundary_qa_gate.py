from pathlib import Path

QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_qa_gate_v1.md")
BOUNDARY_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_contract_v1.md")
EXECUTION_QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_qa_gate_v1.md")
EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_v1.md")

def read(path):
    return path.read_text(encoding="utf-8")

def test_boundary_qa_gate_docs_exist():
    assert QA_GATE_DOC.exists()
    assert BOUNDARY_DOC.exists()
    assert EXECUTION_QA_DOC.exists()
    assert EXECUTION_DOC.exists()

def test_boundary_qa_gate_phase_declared():
    t = read(QA_GATE_DOC)
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1" in t
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.CONTRACT.V1" in t
    assert "CONTROLLED.EXECUTION.QA.GATE.V1" in t
    assert "CONTROLLED.EXECUTION.V1" in t

def test_boundary_qa_gate_preserves_validated_result():
    qa = read(QA_GATE_DOC)
    boundary = read(BOUNDARY_DOC)
    required = ["status=PREFLIGHT_PASS", "exit_code=0", "media_file_count=2", "accepted_extension_counts=.mov:1,.wav:1", "maximum_detected_scan_depth=3", "total_selected_media_size_bucket=LE_100MB"]
    for item in required:
        assert item in qa
        assert item in boundary

def test_boundary_qa_gate_requires_validation_chain():
    t = read(QA_GATE_DOC)
    required = ["post controlled execution boundary contract test passes", "controlled execution QA gate test passes", "controlled execution record test passes", "dry-run execution gate test passes", "dry-run readiness gate test passes", "real folder authorization QA gate test passes", "real folder authorization contract test passes", "WSL repository secrets guard passes", "PostgreSQL-only regression guard passes"]
    for item in required:
        assert item in t

def test_boundary_qa_gate_keeps_boundaries_closed():
    t = read(QA_GATE_DOC)
    required = ["does not authorize broader execution", "does not authorize new folder classes", "does not authorize media analysis", "does not authorize scanner integration", "does not authorize client material handling"]
    for item in required:
        assert item in t

def test_boundary_qa_gate_non_goals_are_explicit():
    t = read(QA_GATE_DOC)
    required = ["real client media", "sensitive media", "personal data processing", "mounted Windows paths", "cloud-synced folders", "network shares", "scanner integration", "ffprobe or ffmpeg", "media probing", "media decoding", "report generation", "transcription", "translation", "subtitles", "sync", "edit decision output", "upload", "desktop app", "installer", "licensing", "SaaS integration", "backend changes", "frontend changes", "database changes", "Docker changes", "Alembic changes", "Stripe changes", "AI Jobs changes", "credits", "ledger changes"]
    for item in required:
        assert item in t

def test_boundary_qa_gate_private_tokens_are_absent():
    t = read(QA_GATE_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
