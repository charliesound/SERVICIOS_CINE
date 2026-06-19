from pathlib import Path

EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_v1.md"
)
EXECUTION_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_gate_v1.md"
)
READINESS_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_readiness_gate_v1.md"
)
AUTH_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_execution_authorization_qa_gate_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_controlled_execution_docs_exist():
    assert EXECUTION_DOC.exists()
    assert EXECUTION_GATE_DOC.exists()
    assert READINESS_GATE_DOC.exists()
    assert AUTH_QA_DOC.exists()


def test_second_controlled_scenario_controlled_execution_phase_declared():
    t = read(EXECUTION_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.READINESS.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.QA.GATE.V1" in t


def test_second_controlled_scenario_controlled_execution_authorization_is_recorded_safely():
    t = read(EXECUTION_DOC)
    required = [
        "explicit human authorization was provided in chat before execution preparation",
        "authorization allowed only Linux-only synthetic non-sensitive dry-run-only execution",
        "authorization excluded real client media",
        "authorization excluded personal data",
        "authorization excluded mounted Windows paths",
        "authorization excluded cloud-synced folders",
        "authorization excluded network shares",
        "authorization excluded scanner integration",
        "authorization excluded ffprobe and ffmpeg",
        "authorization excluded media probing and decoding",
        "authorization excluded report generation",
        "authorization evidence itself remains outside the repository",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_scope_is_limited():
    t = read(EXECUTION_DOC)
    required = [
        "controlled dry-run only",
        "local Linux-only temporary scenario",
        "synthetic non-sensitive files only",
        "no real client media",
        "no personal data",
        "no mounted Windows paths",
        "no cloud-synced folders",
        "no network shares",
        "no scanner integration",
        "no ffprobe or ffmpeg",
        "no media probing",
        "no media decoding",
        "no report generation",
        "no transcription",
        "no translation",
        "no subtitles",
        "no sync",
        "no edit decision output",
        "no export",
        "no upload",
        "no SaaS integration",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_result_is_recorded():
    t = read(EXECUTION_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "media_file_count=2",
        "accepted_extension_counts=.mov:1,.wav:1",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "maximum_detected_scan_depth=3",
        "total_selected_media_size_bucket=LE_100MB",
        "failed_check_identifiers=[]",
        "remediation_items=[]",
        "sanitized_input_folder_label=selected_input_folder",
        "sanitized_output_folder_label=selected_output_folder",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_sanitization_passed():
    t = read(EXECUTION_DOC)
    required = [
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "sanitized_output_contains_no_private_path=true",
        "sanitized_output_contains_no_machine_name=true",
        "sanitized_output_contains_no_user_name=true",
        "sanitized_output_contains_no_folder_name=true",
        "sanitized_output_contains_no_file_name=true",
        "sanitized_output_contains_no_project_name=true",
        "sanitized_output_contains_no_client_name=true",
        "sanitized_output_contains_no_raw_evidence_payload=true",
        "sanitized_output_contains_no_stack_trace=true",
        "sanitized_output_keys_match_expected_contract=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_observation_is_explicit():
    t = read(EXECUTION_DOC)
    required = [
        "expected_ignored_extension_category=present",
        "actual_ignored_extension_counts={}",
        "observed_rejected_extension_counts=.exe:1,.txt:1",
        "observation=the current CLI classified the non-accepted synthetic extensions as rejected rather than ignored",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
        "Reason for PASS_WITH_OBSERVATION",
        "the CLI completed successfully",
        "the result status was PREFLIGHT_PASS",
        "the output was sanitized",
        "the output did not expose private or synthetic concrete names",
        "the output keys matched the contract",
        "the temporary scenario was cleaned up",
        "the repository remained clean after execution",
        "the ignored extension bucket was empty",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_repository_policy_is_sanitized():
    t = read(EXECUTION_DOC)
    required = [
        "this file records only sanitized summary fields",
        "raw command output remains outside the repository",
        "temporary scenario path remains outside the repository",
        "synthetic concrete folder names remain outside the repository",
        "synthetic concrete file names remain outside the repository",
        "human authorization evidence remains outside the repository",
        "raw evidence payload may be copied into this repository",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_post_execution_status_is_clean():
    t = read(EXECUTION_DOC)
    required = [
        "temporary_folder_cleanup=PASS",
        "repository_status_after_execution=CLEAN",
        "no_runtime_code_changed=true",
        "no_scanner_integration_added=true",
        "no_media_tooling_added=true",
        "no_backend_frontend_database_or_saas_changes=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_boundary_blocks_expansion():
    t = read(EXECUTION_DOC)
    required = [
        "this record does not authorize real client media",
        "this record does not authorize personal data processing",
        "this record does not authorize scanner integration",
        "this record does not authorize ffprobe or ffmpeg",
        "this record does not authorize media probing or decoding",
        "this record does not authorize report generation",
        "this record does not authorize transcription, translation, subtitles, sync, edit decision output, export, upload, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_controlled_execution_non_goals_are_explicit():
    t = read(EXECUTION_DOC)
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


def test_second_controlled_scenario_controlled_execution_private_tokens_are_absent():
    t = read(EXECUTION_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["clip_alpha", "sound_alpha", "readme.txt", "reject_alpha"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in t
