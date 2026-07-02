from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationRequest,
    build_controlled_stat_implementation_result,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_renderer import (
    FIXED_SANITIZED_SELECTION_TOKEN,
    SANITIZED_REPORT_RENDERER_HANDLE,
    SANITIZED_REPORT_RENDERER_RECORD_ID,
    SANITIZED_REPORT_SCHEMA_VERSION,
    SANITIZED_REPORT_TITLE,
    SanitizedControlledStatReport,
    build_controlled_stat_sanitized_markdown_report,
    build_controlled_stat_sanitized_report,
    build_sanitized_disclosure_boundary,
    build_sanitized_media_tooling_boundary,
    build_sanitized_saas_boundary,
    build_sanitized_status_map,
    describe_sanitized_report_renderer_boundary,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _renderer_text() -> str:
    return RENDERER.read_text(encoding="utf-8")


def _impl_text() -> str:
    return IMPL.read_text(encoding="utf-8")


def _result():
    request = ControlledStatImplementationRequest(
        input_record_id="operator_input_001",
        sanitized_selection_token="LOCAL_OPERATOR_TOKEN_SHOULD_NOT_RENDER",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        skeleton_handle="CODE_SKELETON_HANDLE_001",
    )
    return build_controlled_stat_implementation_result(request)


def test_renderer_implementation_doc_exists():
    assert DOC.exists()


def test_renderer_module_exists():
    assert RENDERER.exists()


def test_phase_identifier_is_present():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.RENDERER_IMPLEMENTATION.GATE.V1" in text


def test_expected_closure_result_is_present():
    text = _doc_text()
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_GATE_V1_CLOSED" in text


def test_starting_and_target_states_are_present():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTATION_READINESS_PASSED_READY_FOR_RENDERER_IMPLEMENTATION_GATE" in text
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTED_READY_FOR_QA_GATE" in text


def test_public_constants_are_available():
    assert SANITIZED_REPORT_RENDERER_RECORD_ID == "controlled_stat_sanitized_report_renderer_001"
    assert SANITIZED_REPORT_RENDERER_HANDLE == "CONTROLLED_STAT_SANITIZED_REPORT_RENDERER_HANDLE_001"
    assert SANITIZED_REPORT_SCHEMA_VERSION == "controlled_stat_sanitized_report_v1"
    assert SANITIZED_REPORT_TITLE == "CID Local Media Agent — Controlled Stat Implementation Sanitized Report"
    assert FIXED_SANITIZED_SELECTION_TOKEN == "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"


def test_status_map_preserves_non_execution_result_values():
    result = _result()
    status_map = build_sanitized_status_map(result)

    assert status_map == {
        "filesystem_stat_status": "not_executed",
        "file_access_status": "not_accessed",
        "file_open_status": "not_opened",
        "file_bytes_status": "not_read",
        "filesystem_metadata_status": "not_read",
        "file_size_status": "not_recorded",
        "timestamp_status": "not_recorded",
        "hash_status": "not_recorded",
        "ffmpeg_status": "not_executed",
        "ffprobe_status": "not_executed",
        "scanner_status": "not_executed",
        "saas_status": "no_saas_integration",
    }


def test_disclosure_boundary_is_fully_sanitized():
    boundary = build_sanitized_disclosure_boundary()

    assert boundary["absolute_local_path"] == "not_allowed"
    assert boundary["relative_local_path"] == "not_allowed"
    assert boundary["windows_path"] == "not_allowed"
    assert boundary["mount_path"] == "not_allowed"
    assert boundary["unc_path"] == "not_allowed"
    assert boundary["sensitive_filename"] == "not_allowed"
    assert boundary["parent_folder"] == "not_allowed"
    assert boundary["real_file_size"] == "not_recorded"
    assert boundary["real_timestamp"] == "not_recorded"
    assert boundary["real_hash"] == "not_recorded"
    assert boundary["operator_home_directory"] == "not_allowed"
    assert boundary["customer_private_name"] == "not_allowed"
    assert boundary["project_private_name"] == "not_allowed"


def test_media_tooling_boundary_is_non_executing():
    boundary = build_sanitized_media_tooling_boundary()

    assert boundary["media_decode_status"] == "not_executed"
    assert boundary["media_probe_status"] == "not_executed"
    assert boundary["media_scan_status"] == "not_executed"
    assert boundary["transcription_status"] == "not_executed"
    assert boundary["thumbnail_status"] == "not_generated"
    assert boundary["waveform_status"] == "not_generated"
    assert boundary["ffmpeg_execution_status"] == "not_executed"
    assert boundary["ffprobe_execution_status"] == "not_executed"
    assert boundary["scanner_execution_status"] == "not_executed"


def test_saas_boundary_is_not_touched():
    boundary = build_sanitized_saas_boundary()

    assert boundary == {
        "saas_backend_status": "not_touched",
        "saas_frontend_status": "not_touched",
        "database_status": "not_touched",
        "docker_status": "not_touched",
        "alembic_status": "not_touched",
        "stripe_status": "not_touched",
        "ai_jobs_status": "not_touched",
        "credits_ledger_status": "not_touched",
    }


def test_structured_report_is_sanitized_and_deterministic():
    result = _result()

    first = build_controlled_stat_sanitized_report(result)
    second = build_controlled_stat_sanitized_report(result)

    assert first == second
    assert isinstance(first, SanitizedControlledStatReport)
    assert first.report_record_id == SANITIZED_REPORT_RENDERER_RECORD_ID
    assert first.report_schema_version == SANITIZED_REPORT_SCHEMA_VERSION
    assert first.source_implementation_record_id == "controlled_stat_implementation_001"
    assert first.source_implementation_handle == "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001"
    assert first.sanitized_selection_token == FIXED_SANITIZED_SELECTION_TOKEN
    assert first.report_scope == "controlled"
    assert first.report_mode == "markdown_report"
    assert first.status_map["filesystem_stat_status"] == "not_executed"
    assert first.disclosure_boundary["sensitive_filename"] == "not_allowed"
    assert first.media_tooling_boundary["ffprobe_execution_status"] == "not_executed"
    assert first.saas_boundary["database_status"] == "not_touched"


def test_markdown_report_is_deterministic():
    result = _result()

    first = build_controlled_stat_sanitized_markdown_report(result)
    second = build_controlled_stat_sanitized_markdown_report(result)

    assert first == second


def test_markdown_report_contains_required_sections():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())

    sections = [
        "# CID Local Media Agent — Controlled Stat Implementation Sanitized Report",
        "## Report record",
        "## Source implementation",
        "## Sanitized selection",
        "## Controlled stat status map",
        "## Non-execution boundary",
        "## Disclosure boundary",
        "## Media tooling boundary",
        "## SaaS boundary",
        "## Human-readable verdict",
        "## Machine-readable status map",
        "## Renderer closure criteria",
    ]
    for section in sections:
        assert section in markdown


def test_markdown_report_contains_status_values():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())

    required_fragments = [
        "`filesystem_stat_status`: `not_executed`",
        "`file_access_status`: `not_accessed`",
        "`file_open_status`: `not_opened`",
        "`file_bytes_status`: `not_read`",
        "`filesystem_metadata_status`: `not_read`",
        "`file_size_status`: `not_recorded`",
        "`timestamp_status`: `not_recorded`",
        "`hash_status`: `not_recorded`",
        "`ffmpeg_status`: `not_executed`",
        "`ffprobe_status`: `not_executed`",
        "`scanner_status`: `not_executed`",
        "`saas_status`: `no_saas_integration`",
    ]
    for fragment in required_fragments:
        assert fragment in markdown


def test_markdown_report_redacts_operator_token():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())

    assert "LOCAL_OPERATOR_TOKEN_SHOULD_NOT_RENDER" not in markdown
    assert FIXED_SANITIZED_SELECTION_TOKEN in markdown


def test_markdown_report_contains_human_verdict():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())

    assert "Sanitized report generated from a non-executing controlled stat implementation result." in markdown
    assert "No filesystem stat, file access, file open, byte read, metadata read, media probing, scanner execution, or SaaS integration was performed." in markdown


def test_machine_readable_status_map_is_present():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())

    required_lines = [
        "```text",
        "report_record_id=controlled_stat_sanitized_report_renderer_001",
        "report_schema_version=controlled_stat_sanitized_report_v1",
        "source_implementation_record_id=controlled_stat_implementation_001",
        "source_implementation_handle=CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        f"sanitized_selection_token={FIXED_SANITIZED_SELECTION_TOKEN}",
        "filesystem_stat_status=not_executed",
        "file_access_status=not_accessed",
        "file_open_status=not_opened",
        "file_bytes_status=not_read",
        "filesystem_metadata_status=not_read",
        "file_size_status=not_recorded",
        "timestamp_status=not_recorded",
        "hash_status=not_recorded",
        "ffmpeg_status=not_executed",
        "ffprobe_status=not_executed",
        "scanner_status=not_executed",
        "saas_status=no_saas_integration",
        "path_disclosure_status=not_allowed",
        "filename_disclosure_status=not_allowed",
        "parent_folder_disclosure_status=not_allowed",
    ]
    for line in required_lines:
        assert line in markdown


def test_renderer_boundary_is_safe_and_static():
    boundary = describe_sanitized_report_renderer_boundary()

    assert boundary["record_id"] == SANITIZED_REPORT_RENDERER_RECORD_ID
    assert boundary["handle"] == SANITIZED_REPORT_RENDERER_HANDLE
    assert boundary["schema_version"] == SANITIZED_REPORT_SCHEMA_VERSION
    assert boundary["output_mode"] == "markdown_text_only"
    assert boundary["input_mode"] == "controlled_stat_implementation_result_only"
    assert boundary["filesystem_write"] == "not_performed"
    assert boundary["existing_file_modification"] == "not_performed"
    assert boundary["filesystem_stat"] == "not_executed"
    assert boundary["file_access"] == "not_accessed"
    assert boundary["file_open"] == "not_opened"
    assert boundary["file_bytes"] == "not_read"
    assert boundary["filesystem_metadata"] == "not_read"
    assert boundary["file_size"] == "not_recorded"
    assert boundary["timestamps"] == "not_recorded"
    assert boundary["hashes"] == "not_recorded"
    assert boundary["path_disclosure"] == "not_allowed"
    assert boundary["filename_disclosure"] == "not_allowed"
    assert boundary["parent_folder_disclosure"] == "not_allowed"
    assert boundary["media_decode"] == "not_executed"
    assert boundary["media_probe"] == "not_executed"
    assert boundary["media_scan"] == "not_executed"
    assert boundary["ffmpeg"] == "not_executed"
    assert boundary["ffprobe"] == "not_executed"
    assert boundary["scanner"] == "not_executed"
    assert boundary["saas"] == "no_saas_integration"
    assert boundary["database"] == "not_touched"


def test_doc_declares_implemented_api():
    text = _doc_text()
    required_items = [
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
        "`build_controlled_stat_sanitized_report`",
        "`build_controlled_stat_sanitized_markdown_report`",
        "`describe_sanitized_report_renderer_boundary`",
    ]
    for item in required_items:
        assert item in text


def test_doc_declares_positive_assertions():
    text = _doc_text()
    assertions = [
        "The renderer module is created.",
        "The renderer module compiles.",
        "The renderer public API is available.",
        "The renderer accepts a controlled stat implementation result object.",
        "The renderer returns Markdown text.",
        "The renderer output is deterministic.",
        "The renderer never emits operator-provided selection tokens.",
        "The renderer uses the fixed sanitized selection token.",
        "The renderer does not write files.",
        "The renderer does not execute filesystem stat operations.",
        "The renderer does not access files.",
        "The renderer does not open files.",
        "The renderer does not read bytes.",
        "The renderer does not read metadata.",
        "The renderer does not execute media tooling.",
        "The renderer does not touch SaaS.",
        "The renderer does not touch databases.",
    ]
    for assertion in assertions:
        assert assertion in text


def test_document_renderer_and_implementation_do_not_contain_windows_or_mount_paths():
    combined = _doc_text() + "\n" + _renderer_text() + "\n" + _impl_text()
    forbidden_path_fragments = [
        "C:\\",
        "\\\\wsl.localhost",
        "/mnt/c",
        "/mnt/C",
    ]
    for fragment in forbidden_path_fragments:
        assert fragment not in combined


def test_renderer_does_not_contain_runtime_or_write_patterns():
    text = _renderer_text()
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
        assert pattern not in text


def test_closing_state_is_renderer_qa_readiness():
    text = _doc_text()
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTED_READY_FOR_QA_GATE" in text
