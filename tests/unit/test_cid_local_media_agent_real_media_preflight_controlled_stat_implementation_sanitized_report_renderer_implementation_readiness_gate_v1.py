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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_gate_v1.md"
GENERATOR = ROOT / "scripts/local_media_agent/gate_generator.py"
IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"
FUTURE_RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _generator_text() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _impl_text() -> str:
    return IMPL.read_text(encoding="utf-8")


def _rich_definition() -> RichGateDefinition:
    return RichGateDefinition(
        phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.RENDERER.READINESS.SAMPLE.GATE.V1",
        phase_slug="sanitized_report_renderer_readiness_sample_gate_v1",
        title="CID Local Media Agent — Sanitized Report Renderer Readiness Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_SANITIZED_REPORT_RENDERER_READINESS_SAMPLE_GATE_V1_CLOSED",
        starting_state="SANITIZED_REPORT_RENDERER_READINESS_SAMPLE_STARTING_STATE",
        target_next_state="SANITIZED_REPORT_RENDERER_READINESS_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Sample sanitized report renderer readiness generation.",
        source_phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.CONTRACT.GATE.V1",
        source_closure_result="LOCAL_MEDIA_AGENT_SANITIZED_REPORT_CONTRACT_SAMPLE_GATE_V1_CLOSED",
        source_state="SANITIZED_REPORT_CONTRACT_SAMPLE_STATE",
        record_id="sanitized_report_renderer_readiness_sample_001",
        record_handle="SANITIZED_REPORT_RENDERER_READINESS_SAMPLE_HANDLE_001",
        source_record_id="controlled_stat_implementation_sanitized_report_contract_001",
        source_record_handle="CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        doc_artifact_path="docs/product/local_media_agent/sanitized_report_renderer_readiness_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_sanitized_report_renderer_readiness_sample_gate_v1.py",
        implementation_artifact_paths=(
            "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py",
        ),
        created_artifacts=(
            "docs/product/local_media_agent/sanitized_report_renderer_readiness_sample_gate_v1.md",
            "tests/unit/test_sanitized_report_renderer_readiness_sample_gate_v1.py",
        ),
        required_checks=(
            "Sanitized report renderer readiness sample test.",
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
            "Sanitized report renderer readiness sample is deterministic.",
            "Source continuity is preserved.",
        ),
        closure_criteria=(
            "All sanitized report renderer readiness sample tests pass.",
            "Repository guards pass.",
        ),
        recommended_next_phase="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.RENDERER.IMPLEMENTATION.GATE.V1",
        commit_message="docs: add sanitized report renderer readiness sample gate",
        tag_name="cid-dev-stable-sanitized-report-renderer-readiness-sample-gate-v1",
    )


def test_renderer_implementation_readiness_doc_exists():
    assert DOC.exists()


def test_source_modules_exist_and_future_renderer_is_not_created_yet():
    assert GENERATOR.exists()
    assert IMPL.exists()
    assert not FUTURE_RENDERER.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.RENDERER_IMPLEMENTATION.READINESS.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_GATE_V1_CLOSED" in text


def test_starting_state_is_sanitized_report_contract_state():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_DEFINED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text


def test_acceleration_tooling_state_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_PRODUCT_GATES" in text


def test_target_state_is_renderer_implementation_gate_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_PASSED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text


def test_source_product_and_generator_phases_are_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTRACT.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_GATE_V1_CLOSED" in text
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_readiness_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SOURCE_CONTRACT_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SOURCE_IMPLEMENTATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SOURCE_IMPLEMENTATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SOURCE_GENERATOR_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SOURCE_GENERATOR_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_RENDERER_MODULE_PATH",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_RENDERER_MODULE_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_SCOPE_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_readiness_record_values_are_present():
    text = _doc_text()
    required_values = [
        "controlled_stat_implementation_sanitized_report_renderer_implementation_readiness_001",
        "controlled_stat_implementation_sanitized_report_contract_001",
        "controlled_stat_implementation_001",
        "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        "gate_generator_rich_template_qa_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py",
        "not_created_yet",
        "renderer_implementation_readiness_only",
        "no_product_code_changed",
        "ready_for_pure_sanitized_markdown_renderer_implementation_without_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_future_renderer_public_api_contract_is_defined():
    text = _doc_text()
    api_items = [
        "`SANITIZED_REPORT_RENDERER_RECORD_ID`",
        "`SANITIZED_REPORT_RENDERER_HANDLE`",
        "`SANITIZED_REPORT_SCHEMA_VERSION`",
        "`SANITIZED_REPORT_TITLE`",
        "`FIXED_SANITIZED_SELECTION_TOKEN`",
        "`SanitizedControlledStatReport`",
        "`build_sanitized_status_map`",
        "`build_sanitized_disclosure_boundary`",
        "`build_sanitized_media_tooling_boundary`",
        "`build_sanitized_saas_boundary`",
        "`build_controlled_stat_sanitized_markdown_report`",
        "`describe_sanitized_report_renderer_boundary`",
    ]
    for item in api_items:
        assert item in text


def test_future_renderer_input_contract_is_safe():
    text = _doc_text()
    required_items = [
        "The future renderer must accept only a `ControlledStatImplementationResult`.",
        "The future renderer must not accept a filesystem path.",
        "The future renderer must not accept a media path.",
        "The future renderer must not accept a folder path.",
        "The future renderer must not accept raw bytes.",
        "The future renderer must not accept file handles.",
        "The future renderer must not accept subprocess results.",
        "The future renderer must not accept ffprobe output.",
        "The future renderer must not accept FFmpeg output.",
        "The future renderer must not accept scanner output.",
    ]
    for item in required_items:
        assert item in text


def test_future_renderer_output_contract_is_text_only():
    text = _doc_text()
    required_items = [
        "The future renderer must return Markdown text only.",
        "The future renderer must not write files.",
        "The future renderer must not modify existing files.",
        "The future renderer must not create sidecar files.",
        "The future renderer must not create JSON output files.",
        "The future renderer must not create subtitle files.",
        "The future renderer must not create media derivatives.",
        "The future renderer must not create thumbnails.",
        "The future renderer must not create waveform files.",
    ]
    for item in required_items:
        assert item in text


def test_future_renderer_schema_contract_is_preserved_from_contract_gate():
    text = _doc_text()
    sections = [
        "Report title.",
        "Report record.",
        "Source implementation.",
        "Sanitized selection.",
        "Controlled stat status map.",
        "Non-execution boundary.",
        "Disclosure boundary.",
        "Media tooling boundary.",
        "SaaS boundary.",
        "Human-readable verdict.",
        "Machine-readable status map.",
        "Renderer closure criteria.",
    ]
    for section in sections:
        assert section in text


def test_future_renderer_allowed_values_are_defined():
    text = _doc_text()
    values = [
        "`not_executed`",
        "`not_accessed`",
        "`not_opened`",
        "`not_read`",
        "`not_recorded`",
        "`not_generated`",
        "`not_allowed`",
        "`no_saas_integration`",
        "`not_touched`",
        "`sanitized`",
        "`controlled`",
        "`markdown_report`",
        "`REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN`",
    ]
    for value in values:
        assert value in text


def test_future_renderer_forbidden_disclosures_are_defined():
    text = _doc_text()
    forbidden = [
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
        "Real codec metadata.",
        "Real stream metadata.",
        "Real camera metadata.",
        "Real media duration.",
        "Operator home directory text.",
        "Customer private names.",
        "Project private names.",
        "SaaS tenant identifiers.",
        "Database identifiers.",
        "Secrets.",
        "Access tokens.",
    ]
    for item in forbidden:
        assert item in text


def test_future_renderer_deterministic_behavior_contract_is_defined():
    text = _doc_text()
    required_items = [
        "The future renderer output must be deterministic for the same input result object.",
        "The future renderer must preserve the fixed sanitized selection token.",
        "The future renderer must redact any operator-provided token before rendering.",
        "The future renderer must preserve non-execution statuses from the result object.",
        "The future renderer must preserve `not_recorded` statuses for file size, timestamps, and hashes.",
        "The future renderer must preserve `no_saas_integration`.",
        "The future renderer must omit or reject any field outside the contract.",
    ]
    for item in required_items:
        assert item in text


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


def test_rich_generator_can_build_renderer_readiness_plan_without_writing():
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


def test_positive_assertions_are_documented():
    text = _doc_text()
    assertions = [
        "The sanitized report contract state is preserved as product source.",
        "The rich generator QA state remains available as acceleration tooling.",
        "The future renderer module path is defined.",
        "The future renderer module is not created in this gate.",
        "The future renderer public API is defined.",
        "The future renderer input contract is defined.",
        "The future renderer output contract is defined.",
        "The future renderer schema contract is defined.",
        "The future renderer allowed value contract is defined.",
        "The future renderer forbidden disclosure contract is defined.",
        "The future renderer deterministic behavior contract is defined.",
        "The controlled stat implementation module remains present.",
        "The gate generator module remains present.",
        "The rich generator can still produce deterministic rich plans.",
        "The controlled stat implementation still reports non-execution statuses.",
        "No filesystem stat execution is performed.",
        "No real file is accessed.",
        "No media file is opened.",
        "No file bytes are read.",
        "No real filesystem metadata is read.",
        "FFmpeg is not executed.",
        "ffprobe is not executed.",
        "Scanner logic is not executed.",
        "No SaaS integration is created.",
    ]
    for assertion in assertions:
        assert assertion in text


def test_explicitly_forbidden_actions_are_documented():
    text = _doc_text()
    forbidden_items = [
        "Implementing the report renderer.",
        "Creating the renderer module.",
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
        "Recording absolute local paths.",
        "Recording relative local paths.",
        "Recording Windows paths.",
        "Recording mount paths.",
        "Recording UNC paths.",
        "Recording real filenames.",
        "Recording parent folders.",
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


def test_next_phase_boundary_is_renderer_implementation_gate():
    text = _doc_text()
    assert "The next conservative phase may be a sanitized report renderer implementation gate." in text
    assert "That future implementation gate may create the pure renderer module." in text
    assert "That future implementation gate must preserve this readiness gate and the previous report contract." in text
    assert "That future implementation gate must return Markdown text only." in text
    assert "That future implementation gate must not write files." in text
    assert "That future implementation gate must not execute filesystem stat operations." in text
    assert "That future implementation gate must not access a real file." in text
    assert "That future implementation gate must not open media." in text
    assert "That future implementation gate must not read file bytes." in text
    assert "That future implementation gate must not read real metadata." in text
    assert "That future implementation gate must not execute media tooling." in text


def test_required_checks_reference_product_and_generator_chain():
    text = _doc_text()
    required_checks = [
        "This sanitized report renderer implementation readiness gate test.",
        "The previous sanitized report contract gate test.",
        "The previous sanitized report readiness gate test.",
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


def test_closing_state_is_renderer_implementation_gate_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_PASSED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text
