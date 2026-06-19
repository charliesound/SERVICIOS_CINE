from pathlib import Path

QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_authorization_qa_gate_v1.md"
)
AUTH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_authorization_contract_v1.md"
)
READINESS_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_readiness_qa_gate_v1.md"
)
READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_readiness_contract_v1.md"
)
BOUNDARY_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_post_controlled_execution_boundary_qa_gate_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_execution_authorization_qa_gate_docs_exist():
    assert QA_GATE_DOC.exists()
    assert AUTH_DOC.exists()
    assert READINESS_QA_DOC.exists()
    assert READINESS_DOC.exists()
    assert BOUNDARY_QA_DOC.exists()


def test_second_controlled_scenario_execution_authorization_qa_gate_phase_declared():
    t = read(QA_GATE_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.CONTRACT.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1" in t
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1" in t


def test_second_controlled_scenario_execution_authorization_qa_gate_preserves_previous_result():
    qa = read(QA_GATE_DOC)
    auth = read(AUTH_DOC)
    required = [
        "status=PREFLIGHT_PASS",
        "exit_code=0",
        "media_file_count=2",
        "accepted_extension_counts=.mov:1,.wav:1",
        "maximum_detected_scan_depth=3",
        "total_selected_media_size_bucket=LE_100MB",
    ]
    for item in required:
        assert item in qa
        assert item in auth


def test_second_controlled_scenario_execution_authorization_qa_gate_requires_validation_chain():
    t = read(QA_GATE_DOC)
    required = [
        "second controlled scenario execution authorization contract test passes",
        "second controlled scenario readiness QA gate test passes",
        "second controlled scenario readiness contract test passes",
        "post controlled execution boundary QA gate test passes",
        "post controlled execution boundary contract test passes",
        "controlled execution QA gate test passes",
        "controlled execution record test passes",
        "dry-run execution gate test passes",
        "dry-run readiness gate test passes",
        "real folder authorization QA gate test passes",
        "real folder authorization contract test passes",
        "WSL repository secrets guard passes",
        "PostgreSQL-only regression guard passes",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_qa_gate_preserves_authorization_requirements():
    t = read(QA_GATE_DOC)
    required = [
        "human authorization evidence remains outside the repository",
        "authorization decision must be explicit",
        "authorization must name this phase",
        "authorization must name the second controlled scenario",
        "candidate folder restrictions are explicit",
        "allowed command shape is explicit",
        "expected sanitized outcome is explicit",
        "abort conditions are explicit",
        "repository evidence policy is explicit",
        "execution remains blocked until a later execution phase",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_qa_gate_preserves_candidate_restrictions():
    t = read(QA_GATE_DOC)
    required = [
        "candidate folder must be local Linux-only",
        "candidate folder must be synthetic",
        "candidate folder must be non-sensitive",
        "candidate folder must not contain client material",
        "candidate folder must not contain personal data",
        "candidate folder must not be a mounted Windows path",
        "candidate folder must not be cloud-synced",
        "candidate folder must not be a network share",
        "symlink following must remain disabled",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_qa_gate_preserves_sanitized_outcome():
    t = read(QA_GATE_DOC)
    required = [
        "status is one of PREFLIGHT_PASS, PREFLIGHT_FAIL, or PREFLIGHT_BLOCKED",
        "exit_code is one of 0, 2, or 3",
        "sanitized_input_folder_label is present",
        "sanitized_output_folder_label is present when output folder is provided",
        "media_file_count is present",
        "total_selected_media_size_bucket is present",
        "maximum_detected_scan_depth is present",
        "accepted_extension_counts is present",
        "ignored_extension_counts is present",
        "rejected_extension_counts is present",
        "failed_check_identifiers is present",
        "remediation_items is present",
        "no private path is emitted",
        "no machine name is emitted",
        "no user name is emitted",
        "no file name is emitted",
        "no raw evidence payload is emitted",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_qa_gate_does_not_authorize_execution():
    t = read(QA_GATE_DOC)
    required = [
        "This QA gate does not authorize execution",
        "This QA gate does not run the CLI",
        "A later execution readiness gate must still be created",
        "A later execution gate must still be created",
        "A separate controlled execution phase must still be explicitly authorized before any CLI command is run",
        "second controlled scenario execution readiness gate only, without running the CLI",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_qa_gate_non_goals_are_explicit():
    t = read(QA_GATE_DOC)
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


def test_second_controlled_scenario_execution_authorization_qa_gate_private_tokens_are_absent():
    t = read(QA_GATE_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
