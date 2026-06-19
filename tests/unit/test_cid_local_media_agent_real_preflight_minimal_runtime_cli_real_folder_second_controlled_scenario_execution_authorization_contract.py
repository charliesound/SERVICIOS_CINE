from pathlib import Path

DOC = Path(
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


def test_second_controlled_scenario_execution_authorization_docs_exist():
    assert DOC.exists()
    assert READINESS_QA_DOC.exists()
    assert READINESS_DOC.exists()
    assert BOUNDARY_QA_DOC.exists()


def test_second_controlled_scenario_execution_authorization_phase_declared():
    t = read(DOC)
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.CONTRACT.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1" in t
    assert "POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1" in t


def test_second_controlled_scenario_execution_authorization_preserves_previous_result():
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


def test_second_controlled_scenario_execution_authorization_scope_is_limited():
    t = read(DOC)
    required = [
        "local Linux-only synthetic folder",
        "non-sensitive local files only",
        "dry-run-only CLI preflight",
        "no real client media",
        "no personal data",
        "multiple nested subfolders",
        "at least two accepted media extensions",
        "at least one ignored extension",
        "at least one rejected extension",
        "explicit maximum file count limit",
        "explicit maximum total size limit",
        "explicit maximum scan depth limit",
        "symlink following disabled",
        "sanitized labels only",
        "sanitized summary fields only",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_requires_human_evidence():
    t = read(DOC)
    required = [
        "authorization decision must be explicit",
        "authorization must name this phase",
        "authorization must name the second controlled scenario",
        "authorization must confirm synthetic non-sensitive files only",
        "authorization must confirm local Linux-only folder only",
        "authorization must confirm no real client media",
        "authorization must confirm no personal data",
        "authorization must confirm no mounted Windows paths",
        "authorization must confirm no cloud-synced folders",
        "authorization must confirm no network shares",
        "authorization must confirm no scanner integration",
        "authorization must confirm no ffprobe or ffmpeg",
        "authorization must confirm no media probing",
        "authorization must confirm no media decoding",
        "authorization must confirm no report generation",
        "authorization must remain outside the repository",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_candidate_restrictions_are_explicit():
    t = read(DOC)
    required = [
        "candidate folder must be created specifically for this second controlled scenario",
        "candidate folder must be local Linux-only",
        "candidate folder must be synthetic",
        "candidate folder must be non-sensitive",
        "candidate folder must not contain client material",
        "candidate folder must not contain personal data",
        "candidate folder must not be a mounted Windows path",
        "candidate folder must not be cloud-synced",
        "candidate folder must not be a network share",
        "candidate folder must not contain symlink-dependent media selection",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_allowed_command_shape_is_explicit():
    t = read(DOC)
    required = [
        "CLI dry-run invocation only",
        "input folder must be explicitly provided",
        "output folder may be explicitly provided only if synthetic and local Linux-only",
        "accepted extensions must be explicitly declared",
        "maximum file count must be explicitly declared",
        "maximum total size must be explicitly declared",
        "maximum scan depth must be explicitly declared",
        "symlink following must remain disabled",
        "format must remain sanitized",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_expected_sanitized_outcome_is_explicit():
    t = read(DOC)
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


def test_second_controlled_scenario_execution_authorization_abort_conditions_are_explicit():
    t = read(DOC)
    required = [
        "abort if candidate folder is missing",
        "abort if candidate folder is not local Linux-only",
        "abort if candidate folder contains real client media",
        "abort if candidate folder contains personal data",
        "abort if candidate folder is cloud-synced",
        "abort if candidate folder is a network share",
        "abort if mounted Windows path is detected",
        "abort if symlink following would be required",
        "abort if scanner integration is required",
        "abort if ffprobe or ffmpeg is required",
        "abort if media probing or decoding is required",
        "abort if report generation is required",
        "abort if output would expose private path, machine name, user name, folder name, file name, or raw evidence payload",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_repo_evidence_policy_is_explicit():
    t = read(DOC)
    required = [
        "human authorization evidence remains outside the repository",
        "candidate path remains outside the repository",
        "command output remains outside the repository unless represented only as sanitized summary fields",
        "raw evidence payload may be copied into this repository",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_does_not_run_cli():
    t = read(DOC)
    required = [
        "It does not run the CLI and does not authorize execution by itself",
        "This authorization contract does not authorize execution",
        "A later QA gate must validate this authorization contract before any execution phase is prepared",
        "A separate execution phase must still be created before any CLI command is run",
        "execution authorization QA gate only, without running the CLI",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_authorization_non_goals_are_explicit():
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


def test_second_controlled_scenario_execution_authorization_private_tokens_are_absent():
    t = read(DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
