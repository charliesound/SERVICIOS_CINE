from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_contract_v1.md")
EXECUTION_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_v1.md")
QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_qa_gate_v1.md")

def read(path):
    return path.read_text(encoding="utf-8")

def test_boundary_contract_docs_exist():
    assert DOC.exists()
    assert EXECUTION_DOC.exists()
    assert QA_DOC.exists()

def test_boundary_contract_phase_declared():
    t = read(DOC)
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.CONTRACT.V1" in t
    assert "CONTROLLED.EXECUTION.V1" in t
    assert "CONTROLLED.EXECUTION.QA.GATE.V1" in t

def test_boundary_contract_preserves_controlled_result_only():
    t = read(DOC)
    required = ["status=PREFLIGHT_PASS", "exit_code=0", "media_file_count=2", "accepted_extension_counts=.mov:1,.wav:1", "maximum_detected_scan_depth=3", "total_selected_media_size_bucket=LE_100MB"]
    for item in required:
        assert item in t

def test_boundary_contract_does_not_expand_capabilities():
    t = read(DOC)
    required = ["does not authorize broader execution", "new folder classes", "media analysis", "scanner integration", "client material handling"]
    for item in required:
        assert item in t

def test_boundary_contract_hard_boundary_rules_are_explicit():
    t = read(DOC)
    required = ["real client media", "sensitive media", "personal data processing", "mounted Windows paths", "cloud-synced folders", "network shares", "scanner integration", "ffprobe or ffmpeg", "media probing", "media decoding", "report generation", "transcription", "translation", "subtitles", "sync", "edit decision output", "upload", "desktop app", "installer", "licensing", "SaaS integration", "backend changes", "frontend changes", "database changes", "Docker changes", "Alembic changes", "Stripe changes", "AI Jobs changes", "credits", "ledger changes"]
    for item in required:
        assert item in t

def test_boundary_contract_keeps_private_evidence_outside_repo():
    t = read(DOC)
    assert "Local authorization evidence remains outside the repository" in t
    assert "raw evidence payload may be copied into this repository" in t

def test_boundary_contract_private_tokens_are_absent():
    t = read(DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
