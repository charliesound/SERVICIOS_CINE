from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_code_skeleton import (
    BOUNDARY_HANDLE,
    SANITIZED_SELECTION_TOKEN,
    ControlledStatSkeletonInput,
    ControlledStatSkeletonPlan,
    build_non_executing_controlled_stat_plan,
    describe_safety_boundary,
    redact_controlled_stat_plan,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_code_skeleton_isolated_contract_qa_gate_v1.md"
SKELETON = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_code_skeleton.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _skeleton_text() -> str:
    return SKELETON.read_text(encoding="utf-8")


def test_qa_gate_doc_exists():
    assert DOC.exists()


def test_skeleton_module_exists():
    assert SKELETON.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CODE_SKELETON.ISOLATED_CONTRACT_QA.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CODE_SKELETON_ISOLATED_CONTRACT_QA_GATE_V1_CLOSED" in text


def test_starting_state_is_from_code_skeleton_gate():
    text = _doc_text()
    assert "CODE_SKELETON_CREATED_READY_FOR_ISOLATED_CONTRACT_QA_GATE" in text


def test_target_state_is_controlled_stat_implementation_readiness():
    text = _doc_text()
    assert "CODE_SKELETON_ISOLATED_CONTRACT_QA_PASSED_READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_READINESS_GATE" in text


def test_gate_purpose_is_qa_only():
    text = _doc_text()
    assert "This QA gate validates the isolated controlled stat code skeleton contract." in text
    assert "This gate validates that the skeleton remains non-executing." in text
    assert "This gate validates that the skeleton remains pure and sanitized." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_code_skeleton_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CODE_SKELETON.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CODE_SKELETON_GATE_V1_CLOSED" in text


def test_source_code_skeleton_record_values_are_preserved():
    text = _doc_text()
    required_values = [
        "code_skeleton_001",
        "operator_input_001",
        "code_skeleton_readiness_001",
        "isolated_implementation_boundary_001",
        "ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        "real_stat_implementation_contract_001",
        "REAL_STAT_IMPLEMENTATION_CONTRACT_HANDLE_001",
        "stat_execution_boundary_001",
        "STAT_EXECUTION_BOUNDARY_HANDLE_001",
        "controlled_stat_boundary_001",
        "CONTROLLED_STAT_BOUNDARY_HANDLE_001",
        "real_file_access_boundary_001",
        "REAL_FILE_ACCESS_BOUNDARY_HANDLE_001",
        "local_path_disclosure_boundary_001",
        "LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001",
        "controlled_real_file_selection_boundary_001",
        "CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001",
        "manual_operator_confirmation_001",
        "MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        "REDACTED_MANUAL_OPERATOR_ACKNOWLEDGEMENT_FOR_NEXT_CONTROLLED_STEP",
        "sanitized_selection_token_001",
        "SANITIZED_SELECTION_TOKEN_HANDLE_001",
        "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN",
        "controlled_local_file_reference_001",
        "LOCAL_REFERENCE_HANDLE_001",
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "CODE_SKELETON_HANDLE_001",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "code_skeleton_created_without_runtime_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_qa_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_RECORD_ID",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_RECORD_ID",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_HANDLE",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_READINESS_RECORD_ID",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_BOUNDARY_RECORD_ID",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_BOUNDARY_HANDLE",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_CONTRACT_RECORD_ID",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_SOURCE_CONTRACT_HANDLE",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_MODULE_PATH",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_MODULE_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_IMPORT_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_PUBLIC_API_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_PLAN_HELPER_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_REDACTION_HELPER_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_BOUNDARY_HELPER_STATUS",
        "CODE_SKELETON_ISOLATED_CONTRACT_QA_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_qa_record_values_are_sanitized_and_passed():
    text = _doc_text()
    required_values = [
        "code_skeleton_isolated_contract_qa_001",
        "present_and_compile_checked",
        "import_safe_no_runtime_side_effects_detected",
        "expected_dataclasses_and_pure_helpers_present",
        "pure_non_executing_plan_helper_verified",
        "sanitized_token_redaction_verified",
        "non_execution_boundary_statuses_verified",
        "qa_passed_for_non_executing_isolated_skeleton_contract",
    ]
    for value in required_values:
        assert value in text


def test_skeleton_public_api_imports_are_available():
    assert BOUNDARY_HANDLE == "CODE_SKELETON_HANDLE_001"
    assert SANITIZED_SELECTION_TOKEN == "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
    assert ControlledStatSkeletonInput.__name__ == "ControlledStatSkeletonInput"
    assert ControlledStatSkeletonPlan.__name__ == "ControlledStatSkeletonPlan"
    assert callable(build_non_executing_controlled_stat_plan)
    assert callable(redact_controlled_stat_plan)
    assert callable(describe_safety_boundary)


def test_plan_helper_returns_expected_non_execution_contract():
    control_input = ControlledStatSkeletonInput(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
    )

    plan = build_non_executing_controlled_stat_plan(control_input)

    assert isinstance(plan, ControlledStatSkeletonPlan)
    assert plan.skeleton_record_id == "code_skeleton_001"
    assert plan.boundary_handle == "CODE_SKELETON_HANDLE_001"
    assert plan.input_record_id == "operator_input_001"
    assert plan.sanitized_selection_token == "LOCAL_TEST_TOKEN"
    assert plan.generic_file_category == "generic_video_file"
    assert plan.single_file_status == "single_file_claimed"
    assert plan.stat_status == "not_executed"
    assert plan.access_status == "not_accessed"
    assert plan.file_open_status == "not_opened"
    assert plan.file_bytes_status == "not_read"
    assert plan.filesystem_metadata_status == "not_read"
    assert plan.file_size_status == "not_recorded"
    assert plan.timestamp_status == "not_recorded"
    assert plan.hash_status == "not_recorded"
    assert plan.ffmpeg_status == "not_executed"
    assert plan.ffprobe_status == "not_executed"
    assert plan.scanner_status == "not_executed"
    assert plan.saas_status == "no_saas_integration"
    assert plan.verdict == "code_skeleton_plan_without_runtime_stat_open_or_metadata_read"


def test_redaction_helper_removes_local_test_token():
    control_input = ControlledStatSkeletonInput(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
    )

    plan = build_non_executing_controlled_stat_plan(control_input)
    redacted = redact_controlled_stat_plan(plan)

    assert redacted["sanitized_selection_token"] == "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
    assert "LOCAL_TEST_TOKEN" not in redacted.values()


def test_boundary_helper_reports_only_safe_statuses():
    boundary = describe_safety_boundary()

    expected = {
        "filesystem_stat": "not_executed",
        "file_access": "not_accessed",
        "file_open": "not_opened",
        "file_bytes": "not_read",
        "filesystem_metadata": "not_read",
        "file_size": "not_recorded",
        "timestamps": "not_recorded",
        "hashes": "not_recorded",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
    }
    assert boundary == expected


def test_qa_assertions_are_documented():
    text = _doc_text()
    required_assertions = [
        "The skeleton module exists at the expected isolated path.",
        "The skeleton module compiles.",
        "The skeleton module exposes a sanitized input dataclass.",
        "The skeleton module exposes a sanitized output dataclass.",
        "The skeleton module exposes a pure planning helper.",
        "The skeleton module exposes a pure redaction helper.",
        "The skeleton module exposes a pure safety boundary helper.",
        "The planning helper returns only non-execution statuses.",
        "The planning helper does not access a real file.",
        "The redaction helper replaces local test tokens with the fixed sanitized token.",
        "The safety boundary helper reports no filesystem stat execution.",
        "The safety boundary helper reports no FFmpeg execution.",
        "The safety boundary helper reports no ffprobe execution.",
        "The safety boundary helper reports no scanner execution.",
        "The safety boundary helper reports no SaaS integration.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_forbidden_file_and_metadata_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Creating runtime implementation.",
        "Modifying existing CLI runtime.",
        "Executing filesystem stat operations.",
        "Performing filesystem stat operations.",
        "Accessing a real file.",
        "Opening a media file.",
        "Reading file bytes.",
        "Reading real filesystem metadata.",
        "Recording real file size.",
        "Recording real file timestamps.",
        "Recording real file hashes.",
        "Committing a local filesystem path.",
        "Writing a local filesystem path to product documentation.",
        "Writing a local filesystem path to tests.",
        "Recording an absolute path.",
        "Recording a relative path.",
        "Recording a real filename.",
        "Recording a parent folder.",
    ]
    for item in forbidden_items:
        assert item in text


def test_forbidden_media_and_platform_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Executing real media preflight.",
        "Probing a media file.",
        "Scanning a media file.",
        "Decoding a media file.",
        "Transcribing a media file.",
        "Generating thumbnails.",
        "Generating waveforms.",
        "Executing FFmpeg.",
        "Executing ffprobe.",
        "Executing scanner logic.",
        "Touching SaaS backend.",
        "Touching SaaS frontend.",
        "Touching databases.",
        "Touching Docker.",
        "Touching Alembic.",
        "Touching Stripe.",
        "Touching AI Jobs.",
        "Touching credits or ledger.",
    ]
    for item in forbidden_items:
        assert item in text


def test_next_phase_boundary_is_readiness_only():
    text = _doc_text()
    assert "The next conservative phase may prepare a controlled stat implementation readiness gate." in text
    assert "This isolated contract QA gate does not authorize filesystem stat execution." in text
    assert "This isolated contract QA gate does not authorize accessing a real file." in text
    assert "This isolated contract QA gate does not authorize opening media." in text
    assert "This isolated contract QA gate does not authorize reading file bytes." in text
    assert "This isolated contract QA gate does not authorize reading real metadata." in text
    assert "This isolated contract QA gate does not authorize media execution." in text
    assert "This isolated contract QA gate only validates the non-executing isolated skeleton contract." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This code skeleton isolated contract QA gate test.",
        "The previous code skeleton gate test.",
        "The previous code skeleton readiness gate test.",
        "The previous isolated implementation gate test.",
        "The previous isolated implementation readiness gate test.",
        "The previous real stat implementation gate test.",
        "The previous real stat implementation readiness gate test.",
        "The previous stat execution gate test.",
        "The previous stat execution readiness gate test.",
        "The previous controlled stat gate test.",
        "The previous controlled stat readiness gate test.",
        "The previous real file access gate test.",
        "The previous real file access readiness gate test.",
        "The previous local path disclosure gate test.",
        "The previous local path disclosure readiness gate test.",
        "The previous controlled real file selection gate test.",
        "The previous controlled real file selection readiness gate test.",
        "The previous manual operator confirmation gate test.",
        "The previous manual operator confirmation readiness gate test.",
        "The previous real media preflight execution gate test.",
        "The previous real media preflight execution readiness gate test.",
        "The previous sanitized selection token gate test.",
        "The previous sanitized selection token readiness gate test.",
        "The previous operator local selection gate test.",
        "The previous operator local selection readiness gate test.",
        "The previous controlled local file reference gate test.",
        "The previous controlled local file reference readiness gate test.",
        "The previous real file binding gate test.",
        "The previous real file binding readiness gate test.",
        "The previous operator input materialization gate test.",
        "The previous operator input materialization readiness gate test.",
        "The previous safe operator value capture gate test.",
        "The previous safe operator value capture readiness gate test.",
        "The previous sanitized candidate input gate test.",
        "The previous sanitized single file candidate gate test.",
        "The previous real media preflight controlled execution gate test.",
        "The previous real media preflight readiness gate test.",
        "The WSL repo guard script.",
        "The PostgreSQL-only regression guard script.",
    ]
    for check in required_checks:
        assert check in text


def test_document_and_skeleton_do_not_contain_windows_or_mount_paths():
    combined = _doc_text() + "\n" + _skeleton_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_skeleton_does_not_contain_runtime_invocation_patterns():
    text = _skeleton_text()
    forbidden_runtime_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "Path(",
        "Path.",
        ".stat()",
        "stat(",
        "open(",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_runtime_patterns:
        assert pattern not in text


def test_document_does_not_contain_runtime_invocation_patterns():
    text = _doc_text()
    forbidden_runtime_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "Path.stat(",
        ".stat()",
        "open(",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_runtime_patterns:
        assert pattern not in text


def test_closing_state_is_controlled_stat_implementation_readiness():
    text = _doc_text()
    assert "CODE_SKELETON_ISOLATED_CONTRACT_QA_PASSED_READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_READINESS_GATE" in text
