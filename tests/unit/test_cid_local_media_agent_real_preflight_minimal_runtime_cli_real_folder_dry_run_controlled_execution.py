from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_v1.md")

def text():
    return DOC.read_text(encoding="utf-8")

def test_record_exists():
    assert DOC.exists()

def test_phase_and_result_are_recorded():
    t = text()
    assert "CONTROLLED.EXECUTION.V1" in t
    assert "status=PREFLIGHT_PASS" in t
    assert "exit_code=0" in t
    assert "media_file_count=2" in t
    assert "accepted_extension_counts=.mov:1,.wav:1" in t
    assert "maximum_detected_scan_depth=3" in t
    assert "total_selected_media_size_bucket=LE_100MB" in t

def test_private_evidence_is_not_copied():
    t = text()
    assert "remains outside the repository" in t
    assert "raw evidence payload is copied into this repository record" in t

def test_private_tokens_are_absent():
    t = text()
    forbidden = ["/home/", "/opt/", "/mnt/", "DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN", "C:\\\\", "\\\\\\\\wsl.localhost"]
    for token in forbidden:
        assert token not in t

def test_non_goals_are_explicit():
    t = text()
    required = ["real client media", "sensitive media", "personal data processing", "scanner integration", "ffprobe or ffmpeg", "media decoding", "report generation", "transcription", "translation", "subtitles", "sync", "DaVinci Resolve integration", "Avid integration", "SaaS integration", "database changes", "Docker changes", "Alembic changes", "Stripe changes", "AI Jobs changes", "credits", "ledger changes"]
    for item in required:
        assert item in t
