from pathlib import Path

READINESS_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_readiness_gate_v1.md"
)
AUTH_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_authorization_qa_gate_v1.md"
)
AUTH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_authorization_contract_v1.md"
)
SCENARIO_READINESS_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_readiness_qa_gate_v1.md"
)
SCENARIO_READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_readiness_contract_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_execution_readiness_gate_docs_exist():
    assert READINESS_GATE_DOC.exists()
    assert AUTH_QA_DOC.exists()
    assert AUTH_DOC.exists()
    assert SCENARIO_READINESS_QA_DOC.exists()
    assert SCENARIO_READINESS_DOC.exists()


def test_second_controlled_scenario_execution_readiness_gate_phase_declared():
    t = read(READINESS_GATE_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.READINESS.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.CONTRACT.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1" in t


def test_second_controlled_scenario_execution_readiness_gate_preserves_previous_result():
    readiness = read(READINESS_GATE_DOC)
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
        assert item in readiness
        assert item in auth


def test_second_controlled_scenario_execution_readiness_gate_objective_is_bounded():
    t = read(READINESS_GATE_DOC)
    required = [
        "prepare a later execution gate",
        "require explicit human authorization evidence before any CLI command is run",
        "require a bounded second controlled scenario",
        "require synthetic non-sensitive local files only",
        "require local Linux-only folder only",
        "require dry-run-only CLI preflight",
        "preserve sanitized output expectations",
        "preserve abort conditions",
        "preserve repository evidence restrictions",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_candidate_requirements_are_explicit():
    t = read(READINESS_GATE_DOC)
    required = [
        "candidate folder is defined outside the repository",
        "candidate folder is local Linux-only",
        "candidate folder is synthetic",
        "candidate folder is non-sensitive",
        "candidate folder contains no client material",
        "candidate folder contains no personal data",
        "candidate folder is not a mounted Windows path",
        "candidate folder is not cloud-synced",
        "candidate folder is not a network share",
        "candidate folder contains multiple nested subfolders",
        "candidate folder contains at least two accepted media extensions",
        "candidate folder contains at least one ignored extension",
        "candidate folder contains at least one rejected extension",
        "candidate folder does not require symlink following",
        "candidate folder is small enough for bounded dry-run preflight",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_explicit_limits_are_required():
    t = read(READINESS_GATE_DOC)
    required = [
        "maximum file count must be declared",
        "maximum total size must be declared",
        "maximum scan depth must be declared",
        "accepted extensions must be declared",
        "symlink following must remain disabled",
        "output format must remain sanitized",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_allowed_command_shape_is_limited():
    t = read(READINESS_GATE_DOC)
    required = [
        "CLI preflight only",
        "dry-run behavior only",
        "explicit input folder",
        "optional explicit output folder only when synthetic and local Linux-only",
        "explicit accepted extensions",
        "explicit maximum file count",
        "explicit maximum total size",
        "explicit maximum scan depth",
        "symlink following disabled",
        "sanitized format only",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_sanitized_output_fields_are_explicit():
    t = read(READINESS_GATE_DOC)
    required = [
        "status",
        "sanitized_input_folder_label",
        "sanitized_output_folder_label",
        "media_file_count",
        "total_selected_media_size_bucket",
        "maximum_detected_scan_depth",
        "accepted_extension_counts",
        "ignored_extension_counts",
        "rejected_extension_counts",
        "failed_check_identifiers",
        "remediation_items",
        "exit_code",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_sanitized_output_restrictions_are_explicit():
    t = read(READINESS_GATE_DOC)
    required = [
        "no private path",
        "no machine name",
        "no user name",
        "no folder name",
        "no file name",
        "no project name",
        "no client name",
        "no raw evidence payload",
        "no stack trace",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_abort_conditions_are_explicit():
    t = read(READINESS_GATE_DOC)
    required = [
        "abort if explicit human authorization is missing",
        "abort if candidate folder is missing",
        "abort if candidate folder is not local Linux-only",
        "abort if candidate folder contains real client media",
        "abort if candidate folder contains sensitive media",
        "abort if candidate folder contains personal data",
        "abort if candidate folder is a mounted Windows path",
        "abort if candidate folder is cloud-synced",
        "abort if candidate folder is a network share",
        "abort if symlink following would be required",
        "abort if limits are not declared",
        "abort if accepted extensions are not declared",
        "abort if scanner integration is required",
        "abort if ffprobe or ffmpeg is required",
        "abort if media probing or decoding is required",
        "abort if report generation is required",
        "abort if output would expose private paths, machine names, user names, folder names, file names, project names, client names, or raw evidence",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_repository_policy_is_explicit():
    t = read(READINESS_GATE_DOC)
    required = [
        "human authorization evidence remains outside the repository",
        "candidate folder path remains outside the repository",
        "real command output remains outside the repository unless represented only as sanitized summary fields",
        "raw evidence payload may be copied into this repository",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_does_not_authorize_execution():
    t = read(READINESS_GATE_DOC)
    required = [
        "This readiness gate does not authorize execution",
        "This readiness gate does not run the CLI",
        "A later execution gate must still be created",
        "A separate controlled execution phase must still be explicitly authorized before any CLI command is run",
        "This readiness gate does not create, modify, scan, probe, decode, transcribe, translate, sync, export, or upload media",
        "second controlled scenario execution gate only, without running the CLI",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_readiness_gate_non_goals_are_explicit():
    t = read(READINESS_GATE_DOC)
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


def test_second_controlled_scenario_execution_readiness_gate_private_tokens_are_absent():
    t = read(READINESS_GATE_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
