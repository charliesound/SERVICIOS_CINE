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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_contract_gate_v1.md"
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
        phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.CONTRACT.SAMPLE.GATE.V1",
        phase_slug="sanitized_report_contract_sample_gate_v1",
        title="CID Local Media Agent — Sanitized Report Contract Sample Gate V1",
        expected_closure_result="LOCAL_MEDIA_AGENT_SANITIZED_REPORT_CONTRACT_SAMPLE_GATE_V1_CLOSED",
        starting_state="SANITIZED_REPORT_CONTRACT_SAMPLE_STARTING_STATE",
        target_next_state="SANITIZED_REPORT_CONTRACT_SAMPLE_TARGET_NEXT_STATE",
        gate_purpose="Sample sanitized report contract generation.",
        source_phase_identifier="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.READINESS.GATE.V1",
        source_closure_result="LOCAL_MEDIA_AGENT_SANITIZED_REPORT_READINESS_SAMPLE_GATE_V1_CLOSED",
        source_state="SANITIZED_REPORT_READINESS_SAMPLE_STATE",
        record_id="sanitized_report_contract_sample_001",
        record_handle="SANITIZED_REPORT_CONTRACT_SAMPLE_HANDLE_001",
        source_record_id="controlled_stat_implementation_sanitized_report_readiness_001",
        source_record_handle="CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        doc_artifact_path="docs/product/local_media_agent/sanitized_report_contract_sample_gate_v1.md",
        test_artifact_path="tests/unit/test_sanitized_report_contract_sample_gate_v1.py",
        implementation_artifact_paths=(
            "scripts/local_media_agent/gate_generator.py",
        ),
        created_artifacts=(
            "docs/product/local_media_agent/sanitized_report_contract_sample_gate_v1.md",
            "tests/unit/test_sanitized_report_contract_sample_gate_v1.py",
        ),
        required_checks=(
            "Sanitized report contract sample test.",
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
            "Sanitized report contract sample is deterministic.",
            "Source continuity is preserved.",
        ),
        closure_criteria=(
            "All sanitized report contract sample tests pass.",
            "Repository guards pass.",
        ),
        recommended_next_phase="CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.SANITIZED_REPORT.RENDERER.READINESS.GATE.V1",
        commit_message="docs: add sanitized report contract sample gate",
        tag_name="cid-dev-stable-sanitized-report-contract-sample-gate-v1",
    )


def test_sanitized_report_contract_doc_exists():
    assert DOC.exists()


def test_source_modules_exist():
    assert GENERATOR.exists()
    assert IMPL.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTRACT.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_GATE_V1_CLOSED" in text


def test_starting_state_is_sanitized_report_readiness_state():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_PASSED_READY_FOR_REPORT_CONTRACT_GATE" in text


def test_acceleration_tooling_state_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_PRODUCT_GATES" in text


def test_target_state_is_renderer_implementation_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_DEFINED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text


def test_source_product_and_generator_phases_are_referenced():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.READINESS.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_READINESS_GATE_V1_CLOSED" in text
    assert "CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_QA_GATE_V1_CLOSED" in text


def test_contract_record_is_declared():
    text = _doc_text()
    required_fields = [
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SOURCE_READINESS_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SOURCE_IMPLEMENTATION_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SOURCE_IMPLEMENTATION_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SOURCE_GENERATOR_RECORD_ID",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SOURCE_GENERATOR_HANDLE",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_SCHEMA_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_MARKDOWN_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_RENDERER_STATUS",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_VERDICT",
    ]
    for field in required_fields:
        assert field in text


def test_contract_record_values_are_present():
    text = _doc_text()
    required_values = [
        "controlled_stat_implementation_sanitized_report_contract_001",
        "controlled_stat_implementation_sanitized_report_readiness_001",
        "controlled_stat_implementation_001",
        "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        "gate_generator_rich_template_qa_001",
        "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001",
        "defined",
        "not_implemented",
        "no_product_code_changed",
        "sanitized_markdown_report_contract_defined_without_stat_open_or_metadata_read",
    ]
    for value in required_values:
        assert value in text


def test_report_title_contract_is_defined():
    text = _doc_text()
    assert "CID Local Media Agent — Controlled Stat Implementation Sanitized Report" in text


def test_required_markdown_sections_are_defined_in_order():
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
    cursor = -1
    for section in sections:
        index = text.index(section)
        assert index > cursor
        cursor = index


def test_report_record_fields_are_defined():
    text = _doc_text()
    fields = [
        "`report_record_id`",
        "`report_schema_version`",
        "`source_implementation_record_id`",
        "`source_implementation_handle`",
        "`sanitized_selection_token`",
        "`report_scope`",
        "`report_mode`",
        "`report_verdict`",
    ]
    for field in fields:
        assert field in text


def test_source_implementation_fields_are_defined():
    text = _doc_text()
    fields = [
        "`implementation_record_id`",
        "`implementation_handle`",
        "`implementation_verdict`",
        "`implementation_boundary_status`",
        "`source_request_record_id`",
        "`source_sanitized_selection_token`",
    ]
    for field in fields:
        assert field in text


def test_controlled_stat_status_map_fields_are_defined():
    text = _doc_text()
    fields = [
        "`filesystem_stat_status`",
        "`file_access_status`",
        "`file_open_status`",
        "`file_bytes_status`",
        "`filesystem_metadata_status`",
        "`file_size_status`",
        "`timestamp_status`",
        "`hash_status`",
        "`ffmpeg_status`",
        "`ffprobe_status`",
        "`scanner_status`",
        "`saas_status`",
    ]
    for field in fields:
        assert field in text


def test_non_execution_boundary_fields_are_defined():
    text = _doc_text()
    fields = [
        "`filesystem_stat`",
        "`file_access`",
        "`file_open`",
        "`file_bytes`",
        "`filesystem_metadata`",
        "`file_size`",
        "`timestamps`",
        "`hashes`",
        "`ffmpeg`",
        "`ffprobe`",
        "`scanner`",
        "`saas`",
    ]
    for field in fields:
        assert field in text


def test_disclosure_boundary_fields_are_defined():
    text = _doc_text()
    fields = [
        "`absolute_local_path`",
        "`relative_local_path`",
        "`windows_path`",
        "`mount_path`",
        "`unc_path`",
        "`sensitive_filename`",
        "`parent_folder`",
        "`real_file_size`",
        "`real_timestamp`",
        "`real_hash`",
        "`operator_home_directory`",
        "`customer_private_name`",
        "`project_private_name`",
    ]
    for field in fields:
        assert field in text


def test_media_tooling_and_saas_boundary_fields_are_defined():
    text = _doc_text()
    fields = [
        "`media_decode_status`",
        "`media_probe_status`",
        "`media_scan_status`",
        "`transcription_status`",
        "`thumbnail_status`",
        "`waveform_status`",
        "`ffmpeg_execution_status`",
        "`ffprobe_execution_status`",
        "`scanner_execution_status`",
        "`saas_backend_status`",
        "`saas_frontend_status`",
        "`database_status`",
        "`docker_status`",
        "`alembic_status`",
        "`stripe_status`",
        "`ai_jobs_status`",
        "`credits_ledger_status`",
    ]
    for field in fields:
        assert field in text


def test_allowed_values_are_defined():
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


def test_forbidden_values_are_defined_without_real_examples():
    text = _doc_text()
    forbidden_values = [
        "A real absolute local path.",
        "A real relative local path.",
        "A Windows drive prefix.",
        "A WSL mount prefix.",
        "A UNC prefix.",
        "A real filename.",
        "A real parent folder.",
        "A real file size.",
        "A real file timestamp.",
        "A real file hash.",
        "Real file bytes.",
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
    for value in forbidden_values:
        assert value in text


def test_fixed_sanitized_token_contract_is_defined():
    text = _doc_text()
    assert "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN" in text
    assert "No operator-provided token may be written to committed fixtures." in text
    assert "No local selection label may be written to committed fixtures." in text
    assert "No real filename may be substituted for the sanitized token." in text


def test_machine_readable_status_map_contract_is_defined():
    text = _doc_text()
    fields = [
        "`report_record_id`",
        "`report_schema_version`",
        "`source_implementation_record_id`",
        "`source_implementation_handle`",
        "`sanitized_selection_token`",
        "`filesystem_stat_status`",
        "`file_access_status`",
        "`file_open_status`",
        "`file_bytes_status`",
        "`filesystem_metadata_status`",
        "`file_size_status`",
        "`timestamp_status`",
        "`hash_status`",
        "`ffmpeg_status`",
        "`ffprobe_status`",
        "`scanner_status`",
        "`saas_status`",
        "`path_disclosure_status`",
        "`filename_disclosure_status`",
        "`parent_folder_disclosure_status`",
        "`report_verdict`",
    ]
    for field in fields:
        assert field in text


def test_human_readable_verdict_contract_is_defined():
    text = _doc_text()
    assert "Sanitized report generated from a non-executing controlled stat implementation result." in text
    assert "No filesystem stat, file access, file open, byte read, metadata read, media probing, scanner execution, or SaaS integration was performed." in text


def test_future_renderer_acceptance_criteria_are_safe():
    text = _doc_text()
    criteria = [
        "Accept only a controlled stat implementation result object.",
        "Return Markdown text only.",
        "Avoid writing files.",
        "Avoid modifying existing files.",
        "Avoid filesystem stat execution.",
        "Avoid file access.",
        "Avoid file opening.",
        "Avoid byte reads.",
        "Avoid filesystem metadata reads.",
        "Avoid media decode.",
        "Avoid media probe.",
        "Avoid media scan.",
        "Avoid transcription.",
        "Avoid thumbnail generation.",
        "Avoid waveform generation.",
        "Avoid FFmpeg execution.",
        "Avoid ffprobe execution.",
        "Avoid scanner execution.",
        "Avoid SaaS integration.",
        "Preserve the fixed sanitized token.",
        "Redact any operator token before rendering.",
        "Emit only allowed fields.",
        "Reject or omit forbidden fields.",
        "Produce deterministic output.",
        "Preserve current controlled stat implementation behavior.",
    ]
    for criterion in criteria:
        assert criterion in text


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


def test_rich_generator_can_build_contract_plan_without_writing():
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
        "The sanitized report readiness state is preserved as product source.",
        "The rich generator QA state remains available as acceleration tooling.",
        "The sanitized report contract record is defined.",
        "The report title contract is defined.",
        "The Markdown section order is defined.",
        "The report record fields are defined.",
        "The source implementation fields are defined.",
        "The controlled stat status map fields are defined.",
        "The non-execution boundary fields are defined.",
        "The disclosure boundary fields are defined.",
        "The media tooling boundary fields are defined.",
        "The SaaS boundary fields are defined.",
        "The allowed values are defined.",
        "The forbidden values are defined.",
        "The fixed sanitized token contract is defined.",
        "The machine-readable status map contract is defined.",
        "The human-readable verdict contract is defined.",
        "The renderer acceptance criteria are defined.",
        "The future renderer remains non-writing.",
        "The future renderer remains non-executing.",
        "The future renderer remains no-media-access.",
        "The future renderer remains no-SaaS-integration.",
    ]
    for assertion in assertions:
        assert assertion in text


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


def test_next_phase_boundary_is_renderer_readiness_gate():
    text = _doc_text()
    assert "The next conservative phase may be a sanitized report renderer implementation readiness gate." in text
    assert "That future readiness gate should prepare implementation of a pure renderer." in text
    assert "That future readiness gate must remain doc and test-only unless explicitly scoped otherwise." in text
    assert "That future readiness gate must preserve this contract." in text
    assert "That future readiness gate must not execute filesystem stat operations." in text
    assert "That future readiness gate must not access a real file." in text
    assert "That future readiness gate must not open media." in text
    assert "That future readiness gate must not read file bytes." in text
    assert "That future readiness gate must not read real metadata." in text
    assert "That future readiness gate must not execute media tooling." in text


def test_required_checks_reference_product_and_generator_chain():
    text = _doc_text()
    required_checks = [
        "This sanitized report contract gate test.",
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


def test_closing_state_is_renderer_implementation_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTRACT_DEFINED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text
