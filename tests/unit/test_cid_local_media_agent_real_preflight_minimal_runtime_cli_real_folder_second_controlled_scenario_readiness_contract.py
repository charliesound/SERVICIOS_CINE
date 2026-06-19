from pathlib import Path

DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_readiness_contract_v1.md"
)
BOUNDARY_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_qa_gate_v1.md"
)
BOUNDARY_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_contract_v1.md"
)
CONTROLLED_EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_dry_run_controlled_execution_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_readiness_docs_exist():
    assert DOC.exists()
    assert BOUNDARY_QA_DOC.exists()
    assert BOUNDARY_DOC.exists()
    assert CONTROLLED_EXECUTION_DOC.exists()


def test_second_controlled_scenario_readiness_phase_declared():
    t = read(DOC)
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1" in t
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1" in t
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.CONTRACT.V1" in t
    assert "DRY_RUN.CONTROLLED.EXECUTION.V1" in t


def test_second_controlled_scenario_preserves_previous_result():
    t = read(DOC)
    required = [
        "status=PREFLIGHT_PASS",
        "exit_code=0",
        "media_file_count=2",
        "accepted_extension_counts=.mov:1,.wav:1",
        "maximum_detected_scan_depth=3",
        "total_selected_media_size_bucket=LE_100MB",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_shape_is_more_demanding_but_synthetic():
    t = read(DOC)
    required = [
        "Linux-only synthetic folder",
        "Non-sensitive local files only",
        "Multiple nested subfolders",
        "At least two accepted media extensions",
        "At least one ignored extension",
        "At least one rejected extension",
        "Explicit maximum file count limit",
        "Explicit maximum total size limit",
        "Explicit maximum scan depth limit",
        "Symlink following disabled",
        "Sanitized labels only",
        "Sanitized summary fields only",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_does_not_authorize_execution_yet():
    t = read(DOC)
    required = [
        "without authorizing execution",
        "This contract does not authorize execution",
        "later execution phase must provide separate human authorization evidence",
        "explicit candidate folder restrictions",
        "expected sanitized outcome",
        "abort conditions",
        "QA validation before any command is run",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_private_evidence_policy_is_explicit():
    t = read(DOC)
    required = [
        "Human authorization evidence remains outside the repository",
        "Execution output remains outside the repository",
        "sanitized summary fields",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_non_goals_are_explicit():
    t = read(DOC)
    required = [
        "real client media",
        "sensitive media",
        "personal data processing",
        "mounted Windows paths",
        "cloud-synced folders",
        "network shares",
        "scanner integration",
        "ffprobe or ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "edit decision output",
        "upload",
        "desktop app",
        "installer",
        "licensing",
        "SaaS integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits",
        "ledger changes",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_private_tokens_are_absent():
    t = read(DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
