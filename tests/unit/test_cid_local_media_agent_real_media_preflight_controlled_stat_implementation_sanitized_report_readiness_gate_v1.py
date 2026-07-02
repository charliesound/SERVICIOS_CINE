from pathlib import Path

from scripts.local_media_agent.gate_generator import (
    RichGateDefinition,
    build_rich_gate_artifact_plan,
    describe_rich_gate_template_contract,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationRequest,
    build_controlled_stat_implementation_result,
    describe_controlled_stat_implementation_boundary,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_readiness_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"
IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _impl_text() -> str:
    return IMPL.read_text(encoding="utf-8")


def _rich_definition() -> RichGateDefinition:
    return RichGateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.SAMPLE.GATE.V1",
        phase_slug="sanitized_report_sample_gate_v1",
        title="CID Local Media Agent — Sanitized Report Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_SANITIZED_REPORT_SAMPLE_GATE_V1_CLOSED",
        starting_state="SANITIZED_REPORT_SAMPLE_STARTING_STATE",
        target_next_state="SANITIZED_REPORT_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Sample sanitized report readiness generation.",
        source_phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SOURCE.GATE.V1",
        source_closure_result="LOCAL_MEDIA_AGENT_SOURCE_GATE_V1_CLOSED",
        source_state="SOURCE_SAMPLE_STATE",
        record_id="sanitized_report_sample_001",
        record_handle="SANITIZED_REPORT_SAMPLE_HANDLE_001",
        source_record_id="controlled_stat_implementation_dry_run_qa_001",
        source_record_handle="CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        doc_artifact_path="docs/product/local_media_agent/sanitized_report_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_sanitized_report_sample_gate_v1.py",
        implementation_artifact_paths=(
            "scripts/local_media_agent/gate_generator.py",
        ),
        created_artifacts=(
            "docs/product/local_media_agent/sanitized_report_sample_gate_v1.md",
            "tests/unit/test_sanitized_report_sample_gate_v1.py",
        ),
        required_checks=(
            "Sanitized report sample test.",
            "The WSL repo guard script.",
            "The PostgreSQL-only regression guard script.",
        ),
        forbidden_changes=(
            "Reading local media files.",
            "Executing FFmpeg.",
            "Executing ffprobe.",
            "Touching databases.",
        ),
        safety_boundaries=(
            "text_only",
            "non_writing",
            "non_executing",
            "no_media_access",
            "no_saas_integration",
        ),
        positive_assertions=(
            "Sanitized report sample is deterministic.",
            "Source continuity is preserved.",
        ),
        closure_criteria=(
            "All sanitized report sample tests pass.",
            "Repository guards pass.",
        ),
        recommended_next_phase="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.SAMPLE.QA.GATE.V1",
        commit_message="test: add sanitized report sample gate",
        tag_name="cid-dev-stable-sanitized-report-sample-gate-v1",
    )


def test_sanitized_report_readiness_doc_exists():
    assert DOC.exists()


def test_source_modules_exist():
    assert GENERATOR.exists()
    assert IMPL.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_product_source_state():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_DRY_RUN_QA_PASSED_READY_FOR_SANITIZED_REPORT_READINESS_GATE" in text


def test_acceleration_tooling_state_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_PRODUCT_GATES" in text


def test_target_state_is_report_contract_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_PASSED_READY_FOR_REPORT_CONTRACT_GATE" in text


def test_source_product_and_generator_phases_are_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.DRY_RUN_QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_DRY_RUN_QA_GATE_V1_CLOSED" in text
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_readiness_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SOURCE_PRODUCT_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SOURCE_IMPLEMENTATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SOURCE_IMPLEMENTATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SOURCE_GENERATOR_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SOURCE_GENERATOR_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_MODULE_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_SCOPE_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_REPORT_RENDERER_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_readiness_record_values_are_present():
    text = _doc_text()
    required_values = [
        "controlled_stat_implementation_sanitized_report_readiness_001",
        "controlled_stat_implementation_dry_run_qa_001",
        "controlled_stat_implementation_001",
        "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        "gate_generator_rich_template_qa_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "no_report_module_created_yet",
        "sanitized_report_readiness_only",
        "not_implemented",
        "no_product_code_changed",
        "ready_for_sanitized_report_contract_without_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_rich_generator_support_remains_available_and_safe():
    boundary = describe_rich_gate_template_contract()

    assert boundary["filesystem_write"] == "not_performed"
    assert boundary["command_execution"] == "not_performed"
    assert boundary["subprocess_execution"] == "not_performed"
    assert boundary["media_access"] == "not_performed"
    assert boundary["ffmpeg"] == "not_executed"
    assert boundary["ffprobe"] == "not_executed"
    assert boundary["scanner"] == "not_executed"
    assert boundary["saas"] == "no_saas_integration"
    assert boundary["database"] == "not_touched"


def test_rich_generator_can_build_sanitized_report_readiness_plan_without_writing():
    definition = _rich_definition()

    first = build_rich_gate_artifact_plan(definition)
    second = build_rich_gate_artifact_plan(definition)

    assert first == second
    assert definition.phase_identifier in first.document_text
    assert definition.phase_identifier in first.test_stub_text
    assert first.validation_plan["forbidden_changes"] == definition.forbidden_changes
    assert first.validation_plan["safety_boundaries"] == definition.safety_boundaries


def test_controlled_stat_implementation_still_reports_non_execution():
    request = ControlledStatImplementationRequest(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_TEST_TOKEN",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        skeleton_handle="CODE_SKELETON_HANDLE_001",
    )

    result = build_controlled_stat_implementation_result(request)

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


def test_controlled_stat_implementation_boundary_is_still_safe():
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


def test_future_report_contract_requirements_are_defined():
    text = _doc_text()
    required_items = [
        "A sanitized report schema.",
        "A sanitized report title.",
        "A sanitized report summary section.",
        "A sanitized implementation result section.",
        "A non-execution boundary section.",
        "A no-local-path disclosure section.",
        "A no-sensitive-filename disclosure section.",
        "A no-parent-folder disclosure section.",
        "A no-file-size disclosure section.",
        "A no-timestamp disclosure section.",
        "A no-hash disclosure section.",
        "A no-media-execution section.",
        "A no-SaaS-integration section.",
        "A machine-readable status map.",
        "A human-readable verdict.",
        "A fixed sanitized token representation.",
        "Explicit allowed fields.",
        "Explicit forbidden fields.",
        "Markdown output contract.",
        "Future renderer acceptance criteria.",
    ]
    for item in required_items:
        assert item in text


def test_allowed_future_report_fields_are_safe():
    text = _doc_text()
    allowed_fields = [
        "Phase identifier.",
        "Report record ID.",
        "Implementation record ID.",
        "Implementation handle.",
        "Generic file category.",
        "Single-file status.",
        "Sanitized selection token.",
        "Filesystem stat status.",
        "File access status.",
        "File open status.",
        "File bytes status.",
        "Filesystem metadata status.",
        "File size status value as `not_recorded`.",
        "Timestamp status value as `not_recorded`.",
        "Hash status value as `not_recorded`.",
        "FFmpeg status.",
        "ffprobe status.",
        "Scanner status.",
        "SaaS status.",
        "Human-readable sanitized verdict.",
    ]
    for item in allowed_fields:
        assert item in text


def test_forbidden_future_report_fields_are_documented():
    text = _doc_text()
    forbidden_fields = [
        "Absolute local paths.",
        "Relative local paths.",
        "Windows paths.",
        "Mount paths.",
        "UNC paths.",
        "Sensitive filenames.",
        "Parent folders.",
        "Real file sizes.",
        "Real timestamps.",
        "Real hashes.",
        "File bytes.",
        "Media duration from real probing.",
        "Codec metadata from real probing.",
        "Stream metadata from real probing.",
        "Camera metadata from real probing.",
        "Operator home directory.",
        "Customer/project private names.",
        "SaaS tenant identifiers.",
        "Database identifiers.",
        "Secrets or tokens other than the fixed sanitized placeholder.",
    ]
    for item in forbidden_fields:
        assert item in text


def test_positive_assertions_are_documented():
    text = _doc_text()
    assertions = [
        "The controlled stat dry-run QA state is preserved as product source.",
        "The rich generator QA state is available as acceleration tooling.",
        "The future sanitized report contract has a defined readiness record.",
        "The future report renderer is not implemented in this gate.",
        "The controlled stat implementation module remains present.",
        "The gate generator module remains present.",
        "The rich generator can still produce deterministic rich plans.",
        "The controlled stat implementation still reports non-execution statuses.",
        "No filesystem stat execution is performed.",
        "No real file is accessed.",
        "No media file is opened.",
        "No file bytes are read.",
        "No real filesystem metadata is read.",
        "No local path is committed.",
        "No sensitive filename is recorded.",
        "No parent folder is recorded.",
        "FFmpeg is not executed.",
        "ffprobe is not executed.",
        "Scanner logic is not executed.",
        "No SaaS integration is created.",
    ]
    for item in assertions:
        assert item in text


def test_explicitly_forbidden_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Implementing a report renderer.",
        "Modifying the controlled stat implementation module.",
        "Modifying the gate generator module.",
        "Creating runtime filesystem execution.",
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


def test_next_phase_boundary_is_report_contract_gate():
    text = _doc_text()
    assert "The next conservative phase may be a sanitized report contract gate." in text
    assert "That future contract gate may define report schema and acceptance criteria." in text
    assert "That future contract gate must remain doc and test-only unless explicitly scoped otherwise." in text
    assert "That future contract gate must not execute filesystem stat operations." in text
    assert "That future contract gate must not access a real file." in text
    assert "That future contract gate must not open media." in text
    assert "That future contract gate must not read file bytes." in text
    assert "That future contract gate must not read real metadata." in text
    assert "That future contract gate must not execute media tooling." in text


def test_required_checks_reference_product_and_generator_chain():
    text = _doc_text()
    required_checks = [
        "This sanitized report readiness gate test.",
        "The previous rich template QA gate test.",
        "The previous rich template implementation gate test.",
        "The previous rich template contract gate test.",
        "The previous gate generator template QA gate test.",
        "The previous gate generator isolated implementation gate test.",
        "The previous controlled stat implementation dry-run QA gate test.",
        "The previous controlled stat implementation gate test.",
        "The previous controlled stat implementation readiness gate test.",
        "The previous code skeleton isolated contract QA gate test.",
        "The previous code skeleton gate test.",
        "The previous code skeleton readiness gate test.",
        "The previous real media preflight readiness gate test.",
        "The WSL repo guard script.",
        "The PostgreSQL-only regression guard script.",
    ]
    for check in required_checks:
        assert check in text


def test_document_generator_and_implementation_do_not_contain_windows_or_mount_paths():
    combined = _doc_text() + "\n" + _generator_text() + "\n" + _impl_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_generator_and_implementation_do_not_contain_runtime_or_write_patterns():
    combined = _generator_text() + "\n" + _impl_text()
    forbidden_patterns = [
        "subprocess.run",
        "subprocess.Popen",
        "os.system",
        "shell=True",
        "open(",
        ".write(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "ffmpeg -",
        "ffprobe -",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in combined


def test_closing_state_is_report_contract_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_PASSED_READY_FOR_REPORT_CONTRACT_GATE" in text
