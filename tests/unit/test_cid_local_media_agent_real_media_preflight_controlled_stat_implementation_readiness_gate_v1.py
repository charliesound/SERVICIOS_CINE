from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_code_skeleton import (
    ControlledStatSkeletonInput,
    build_non_executing_controlled_stat_plan,
    describe_safety_boundary,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_readiness_gate_v1.md"
SKELETON = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_code_skeleton.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _skeleton_text() -> str:
    return SKELETON.read_text(encoding="utf-8")


def test_controlled_stat_implementation_readiness_doc_exists():
    assert DOC.exists()


def test_skeleton_module_exists():
    assert SKELETON.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_from_isolated_contract_qa():
    text = _doc_text()
    assert "CODE_SKELETON_ISOLATED_CONTRACT_QA_PASSED_READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_READINESS_GATE" in text


def test_target_state_is_ready_for_controlled_stat_implementation_gate():
    text = _doc_text()
    assert "READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_GATE" in text


def test_gate_purpose_is_readiness_only():
    text = _doc_text()
    assert "This readiness gate prepares the conditions for a later controlled stat implementation gate." in text
    assert "This gate does not implement real filesystem stat execution." in text
    assert "This gate does not modify the existing isolated skeleton module." in text
    assert "This gate is limited to documentation and tests." in text


def test_source_isolated_contract_qa_gate_is_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CODE_SKELETON.ISOLATED_CONTRACT_QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CODE_SKELETON_ISOLATED_CONTRACT_QA_GATE_V1_CLOSED" in text


def test_source_qa_record_values_are_preserved():
    text = _doc_text()
    required_values = [
        "code_skeleton_isolated_contract_qa_001",
        "code_skeleton_001",
        "CODE_SKELETON_HANDLE_001",
        "code_skeleton_readiness_001",
        "isolated_implementation_boundary_001",
        "ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        "real_stat_implementation_contract_001",
        "REAL_STAT_IMPLEMENTATION_CONTRACT_HANDLE_001",
        "scripts/local_media_agent/real_media_preflight_controlled_stat_code_skeleton.py",
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


def test_readiness_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_QA_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_SKELETON_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_SKELETON_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONTRACT_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONTRACT_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_STAT_EXECUTION_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_STAT_EXECUTION_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONTROLLED_STAT_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONTROLLED_STAT_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_REAL_FILE_ACCESS_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_REAL_FILE_ACCESS_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_LOCAL_PATH_DISCLOSURE_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_SELECTION_BOUNDARY_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_SELECTION_BOUNDARY_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONFIRMATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_CONFIRMATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_TOKEN_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_SOURCE_TOKEN_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_readiness_record_values_are_sanitized():
    text = _doc_text()
    required_values = [
        "controlled_stat_implementation_readiness_001",
        "CONTROLLED_STAT_IMPLEMENTATION_READINESS_HANDLE_001",
        "operator_local_selection_event_001",
        "OPERATOR_LOCAL_SELECTION_EVENT_HANDLE_001",
        "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN",
        "generic_video_file",
        "internal_operator_owned",
        "non_confidential_confirmed",
        "local_single_file_claimed",
        "single_file_claimed",
        "ready_for_controlled_stat_implementation_gate",
        "implementation_readiness_only",
        "no_code_changed_in_this_gate",
        "ready_for_controlled_stat_implementation_gate_without_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_skeleton_still_returns_non_execution_statuses():
    control_input = ControlledStatSkeletonInput(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
    )

    plan = build_non_executing_controlled_stat_plan(control_input)

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


def test_skeleton_safety_boundary_remains_non_executing():
    boundary = describe_safety_boundary()

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


def test_future_implementation_constraints_are_conservative():
    text = _doc_text()
    constraints = [
        "It must remain local-only.",
        "It must remain single-file only.",
        "It must use the sanitized selection token as the control input.",
        "It must use the manual confirmation handle as a control prerequisite.",
        "It must use the controlled real file selection boundary handle as a control prerequisite.",
        "It must use the local path disclosure boundary handle as a control prerequisite.",
        "It must use the real file access boundary handle as a control prerequisite.",
        "It must use the controlled stat boundary handle as a control prerequisite.",
        "It must use the stat execution boundary handle as a control prerequisite.",
        "It must use the real stat implementation contract handle as a control prerequisite.",
        "It must use the isolated implementation boundary handle as a control prerequisite.",
        "It must use the code skeleton handle as a source implementation shape.",
        "It must not commit local paths.",
        "It must not expose sensitive filenames in committed artifacts.",
        "It must not expose parent folder names in committed artifacts.",
        "It must not commit real file size.",
        "It must not commit real timestamps.",
        "It must not commit real hashes.",
        "It must not open the media file.",
        "It must not read file bytes.",
        "It must not execute FFmpeg.",
        "It must not execute ffprobe.",
        "It must not execute scanner logic.",
        "It must not create SaaS coupling.",
        "It must remain test-covered.",
        "It must pass repository safety guards before commit.",
    ]
    for constraint in constraints:
        assert constraint in text


def test_positive_assertions_are_documented():
    text = _doc_text()
    required_assertions = [
        "`controlled_stat_implementation_readiness_001` is created as a readiness record.",
        "`CONTROLLED_STAT_IMPLEMENTATION_READINESS_HANDLE_001` is a non-filesystem readiness handle.",
        "`code_skeleton_isolated_contract_qa_001` remains the source QA record.",
        "`code_skeleton_001` remains the source skeleton record.",
        "`CODE_SKELETON_HANDLE_001` remains a non-filesystem skeleton handle.",
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
        "The skeleton module remains present.",
        "The skeleton module remains compile-safe.",
        "The skeleton module still returns non-execution statuses.",
        "No source code is modified in this gate.",
    ]
    for assertion in required_assertions:
        assert assertion in text


def test_forbidden_file_and_metadata_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Creating runtime implementation.",
        "Modifying existing skeleton module code.",
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


def test_next_phase_boundary_is_controlled_stat_implementation_gate():
    text = _doc_text()
    assert "The next conservative phase may be a controlled stat implementation gate." in text
    assert "This readiness gate does not authorize filesystem stat execution." in text
    assert "This readiness gate does not authorize accessing a real file." in text
    assert "This readiness gate does not authorize opening media." in text
    assert "This readiness gate does not authorize reading file bytes." in text
    assert "This readiness gate does not authorize reading real metadata." in text
    assert "This readiness gate does not authorize media execution." in text
    assert "This readiness gate only prepares conditions for a later controlled stat implementation gate." in text


def test_required_checks_reference_previous_gates_and_generic_guards():
    text = _doc_text()
    required_checks = [
        "This controlled stat implementation readiness gate test.",
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


def test_skeleton_still_does_not_contain_runtime_invocation_patterns():
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


def test_closing_state_is_ready_for_controlled_stat_implementation_gate():
    text = _doc_text()
    assert "READY_FOR_CONTROLLED_STAT_IMPLEMENTATION_GATE" in text
