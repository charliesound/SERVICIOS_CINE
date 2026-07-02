from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    CONTROLLED_STAT_IMPLEMENTATION_HANDLE,
    CONTROLLED_STAT_IMPLEMENTATION_RECORD_ID,
    SANITIZED_SELECTION_TOKEN,
    ControlledStatImplementationRequest,
    ControlledStatImplementationResult,
    build_controlled_stat_implementation_result,
    describe_controlled_stat_implementation_boundary,
    redact_controlled_stat_implementation_result,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_gate_v1.md"
IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _impl_text() -> str:
    return IMPL.read_text(encoding="utf-8")


def test_controlled_stat_implementation_gate_doc_exists():
    assert DOC.exists()


def test_controlled_stat_implementation_module_exists():
    assert IMPL.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_starting_state_is_ready_for_controlled_stat_implementation_gate():
    text = _doc_text()
    assert "READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_GATE" in text


def test_target_state_is_ready_for_dry_run_qa_gate():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_CREATED_READY_FOR_DRY_RUN_QA_GATE" in text


def test_gate_purpose_creates_non_executing_wrapper_only():
    text = _doc_text()
    assert "This gate creates a controlled stat implementation module." in text
    assert "This implementation module is intentionally non-executing." in text
    assert "This implementation module wraps the validated isolated skeleton." in text
    assert "This implementation module does not execute filesystem stat operations." in text


def test_created_artifacts_are_declared():
    text = _doc_text()
    assert "real_media_preflight_controlled_stat_implementation.py" in text
    assert "cid_local_media_agent_real_media_preflight_controlled_stat_implementation_gate_v1.py" in text


def test_implementation_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CONTROLLED_STAT_IMPLEMENTATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_READINESS_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_SKELETON_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_SKELETON_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_QA_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONTRACT_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONTRACT_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_STAT_EXECUTION_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_STAT_EXECUTION_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONTROLLED_STAT_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONTROLLED_STAT_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_REAL_FILE_ACCESS_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_REAL_FILE_ACCESS_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_SELECTION_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_SELECTION_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONFIRMATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_CONFIRMATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_TOKEN_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SOURCE_TOKEN_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_implementation_record_values_are_sanitized():
    text = _doc_text()
    required_values = [
        "controlled_stat_implementation_001",
        "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        "created_as_non_executing_controlled_implementation_wrapper",
        "controlled_stat_planning_only",
        "new_non_executing_module_added",
        "controlled_stat_implementation_created_without_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_implementation_module_defines_expected_public_shapes():
    assert CONTROLLED_STAT_IMPLEMENTATION_HANDLE == "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001"
    assert CONTROLLED_STAT_IMPLEMENTATION_RECORD_ID == "controlled_stat_implementation_001"
    assert SANITIZED_SELECTION_TOKEN == "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
    assert ControlledStatImplementationRequest.__name__ == "ControlledStatImplementationRequest"
    assert ControlledStatImplementationResult.__name__ == "ControlledStatImplementationResult"
    assert callable(build_controlled_stat_implementation_result)
    assert callable(redact_controlled_stat_implementation_result)
    assert callable(describe_controlled_stat_implementation_boundary)


def test_controlled_implementation_result_is_non_executing():
    request = ControlledStatImplementationRequest(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        skeleton_handle="CODE_SKELETON_HANDLE_001",
    )

    result = build_controlled_stat_implementation_result(request)

    assert isinstance(result, ControlledStatImplementationResult)
    assert result.implementation_record_id == "controlled_stat_implementation_001"
    assert result.implementation_handle == "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001"
    assert result.skeleton_handle == "CODE_SKELETON_HANDLE_001"
    assert result.input_record_id == "operator_input_001"
    assert result.sanitized_selection_token == "LOCAL_TEST_TOKEN"
    assert result.generic_file_category == "generic_video_file"
    assert result.single_file_status == "single_file_claimed"
    assert result.filesystem_stat_status == "not_executed"
    assert result.file_access_status == "not_accessed"
    assert result.file_open_status == "not_opened"
    assert result.file_bytes_status == "not_read"
    assert result.filesystem_metadata_status == "not_read"
    assert result.file_size_status == "not_recorded"
    assert result.timestamp_status == "not_recorded"
    assert result.hash_status == "not_recorded"
    assert result.ffmpeg_status == "not_executed"
    assert result.ffprobe_status == "not_executed"
    assert result.scanner_status == "not_executed"
    assert result.saas_status == "no_saas_integration"


def test_implementation_redaction_removes_local_test_token():
    request = ControlledStatImplementationRequest(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        skeleton_handle="CODE_SKELETON_HANDLE_001",
    )

    result = build_controlled_stat_implementation_result(request)
    redacted = redact_controlled_stat_implementation_result(result)

    assert redacted["sanitized_selection_token"] == "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
    assert "LOCAL_TEST_TOKEN" not in redacted.values()


def test_implementation_boundary_reports_only_safe_statuses():
    boundary = describe_controlled_stat_implementation_boundary()

    assert boundary["filesystem_stat"] == "not_executed"
    assert boundary["file_access"] == "not_accessed"
    assert boundary["file_open"] == "not_opened"
    assert boundary["file_bytes"] == "not_read"
    assert boundary["filesystem_metadata"] == "not_read"
    assert boundary["file_size"] == "not_recorded"
    assert boundary["timestamps"] == "not_recorded"
    assert boundary["hashes"] == "not_recorded"
    assert boundary["ffmpeg"] == "not_executed"
    assert boundary["ffprobe"] == "not_executed"
    assert boundary["scanner"] == "not_executed"
    assert boundary["saas"] == "no_saas_integration"
    assert boundary["implementation"] == "non_executing_wrapper"


def test_implementation_behavior_is_documented():
    text = _doc_text()
    requirements = [
        "A sanitized implementation request dataclass.",
        "A sanitized implementation result dataclass.",
        "A pure implementation planning helper.",
        "A pure implementation redaction helper.",
        "A pure implementation safety boundary helper.",
        "A bridge from the validated skeleton plan.",
        "No filesystem operation.",
        "No media operation.",
        "No subprocess operation.",
        "No SaaS coupling.",
    ]
    for requirement in requirements:
        assert requirement in text


def test_positive_assertions_preserve_source_scope():
    text = _doc_text()
    required_assertions = [
        "`controlled_stat_implementation_001` is created as a sanitized implementation record.",
        "`CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001` is a non-filesystem implementation handle.",
        "`controlled_stat_implementation_readiness_001` remains the source readiness record.",
        "`code_skeleton_001` remains the source skeleton record.",
        "`CODE_SKELETON_HANDLE_001` remains a non-filesystem skeleton handle.",
        "`code_skeleton_isolated_contract_qa_001` remains the source QA record.",
        "`isolated_implementation_boundary_001` remains the source isolated implementation boundary.",
        "`ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001` remains a non-filesystem boundary handle.",
        "`real_stat_implementation_contract_001` remains the source real stat implementation contract.",
        "`REAL_STAT_IMPLEMENTATION_CONTRACT_HANDLE_001` remains a non-filesystem contract handle.",
        "`stat_execution_boundary_001` remains the source stat execution boundary.",
        "`STAT_EXECUTION_BOUNDARY_HANDLE_001` remains a non-filesystem stat execution boundary handle.",
        "`controlled_stat_boundary_001` remains the source controlled stat boundary.",
        "`CONTROLLED_STAT_BOUNDARY_HANDLE_001` remains a non-filesystem stat boundary handle.",
        "`real_file_access_boundary_001` remains the source real file access boundary.",
        "`REAL_FILE_ACCESS_BOUNDARY_HANDLE_001` remains a non-filesystem access boundary handle.",
        "`local_path_disclosure_boundary_001` remains the source local path disclosure boundary.",
        "`LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE_001` remains a non-filesystem disclosure boundary handle.",
        "`controlled_real_file_selection_boundary_001` remains the source selection boundary record.",
        "`CONTROLLED_REAL_FILE_SELECTION_BOUNDARY_HANDLE_001` remains a non-filesystem selection boundary handle.",
        "`manual_operator_confirmation_001` remains the source confirmation record.",
        "`MANUAL_OPERATOR_CONFIRMATION_HANDLE_001` remains a non-filesystem confirmation handle.",
        "`sanitized_selection_token_001` remains the source token record.",
        "`SANITIZED_SELECTION_TOKEN_HANDLE_001` remains a non-filesystem token handle.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_forbidden_file_and_metadata_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
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


def test_next_phase_boundary_is_dry_run_qa_gate():
    text = _doc_text()
    assert "The next conservative phase may be a dry-run QA gate for the controlled implementation module." in text
    assert "This controlled stat implementation gate does not authorize filesystem stat execution." in text
    assert "This controlled stat implementation gate does not authorize accessing a real file." in text
    assert "This controlled stat implementation gate does not authorize opening media." in text
    assert "This controlled stat implementation gate does not authorize reading file bytes." in text
    assert "This controlled stat implementation gate does not authorize reading real metadata." in text
    assert "This controlled stat implementation gate does not authorize media execution." in text
    assert "This controlled stat implementation gate only creates a non-executing implementation wrapper." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This controlled stat implementation gate test.",
        "The previous controlled stat implementation readiness gate test.",
        "The previous code skeleton isolated contract QA gate test.",
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


def test_document_and_implementation_do_not_contain_windows_or_mount_paths():
    combined = _doc_text() + "\n" + _impl_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_implementation_does_not_contain_runtime_invocation_patterns():
    text = _impl_text()
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


def test_closing_state_is_ready_for_dry_run_qa_gate():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_CREATED_READY_FOR_DRY_RUN_QA_GATE" in text
