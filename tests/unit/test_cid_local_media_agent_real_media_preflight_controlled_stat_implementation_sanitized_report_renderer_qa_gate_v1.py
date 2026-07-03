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
    describe_sanitized_report_renderer_boundary,
)

ROOT = Path(__file__).resolve().parents[2]
QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.md"
IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _result():
    request = ControlledStatImplementationRequest(
        input_record_id="qa_input_001",
        sanitized_selection_token="LOCAL_OPERATOR_TOKEN_MUST_NOT_RENDER_IN_QA",
        manual_confirmation_handle="QA_MANUAL_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="QA_ISOLATED_BOUNDARY_HANDLE_001",
        skeleton_handle="QA_CODE_SKELETON_HANDLE_001",
    )
    return build_controlled_stat_implementation_result(request)


def test_qa_doc_declares_phase_result_and_post_implementation_scope():
    assert QA_DOC.exists()
    text = _text(QA_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.RENDERER_QA.GATE.V1" in text
    assert "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_QA_GATE_V1_CLOSED" in text
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_IMPLEMENTED_READY_FOR_QA_GATE" in text
    assert "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_QA_PASSED_READY_FOR_CONTROLLED_EXPORT_INTEGRATION_READINESS_GATE" in text
    assert "does not assert that the future renderer is absent" in text


def test_post_implementation_artifacts_exist():
    assert IMPL_DOC.exists()
    assert RENDERER.exists()
    assert IMPL.exists()


def test_renderer_public_identity_is_stable():
    assert SANITIZED_REPORT_RENDERER_RECORD_ID == "controlled_stat_sanitized_report_renderer_001"
    assert SANITIZED_REPORT_RENDERER_HANDLE == "CONTROLLED_STAT_SANITIZED_REPORT_RENDERER_HANDLE_001"
    assert SANITIZED_REPORT_SCHEMA_VERSION == "controlled_stat_sanitized_report_v1"
    assert SANITIZED_REPORT_TITLE == "CID Local Media Agent — Controlled Stat Implementation Sanitized Report"


def test_structured_report_is_deterministic_sanitized_and_safe():
    first = build_controlled_stat_sanitized_report(_result())
    second = build_controlled_stat_sanitized_report(_result())
    assert first == second
    assert isinstance(first, SanitizedControlledStatReport)
    assert first.sanitized_selection_token == FIXED_SANITIZED_SELECTION_TOKEN
    assert "LOCAL_OPERATOR_TOKEN_MUST_NOT_RENDER_IN_QA" not in repr(first)
    assert first.report_scope == "controlled"
    assert first.report_mode == "markdown_report"


def test_status_and_boundaries_preserve_safe_values():
    report = build_controlled_stat_sanitized_report(_result())
    expected_status = {
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
    assert report.status_map == expected_status
    assert report.disclosure_boundary["sensitive_filename"] == "not_allowed"
    assert report.disclosure_boundary["parent_folder"] == "not_allowed"
    assert report.media_tooling_boundary["transcription_status"] == "not_executed"
    assert report.media_tooling_boundary["thumbnail_status"] == "not_generated"
    assert report.media_tooling_boundary["waveform_status"] == "not_generated"
    assert report.saas_boundary["database_status"] == "not_touched"
    assert report.saas_boundary["credits_ledger_status"] == "not_touched"


def test_markdown_is_deterministic_redacted_and_contract_ordered():
    first = build_controlled_stat_sanitized_markdown_report(_result())
    second = build_controlled_stat_sanitized_markdown_report(_result())
    assert first == second
    assert FIXED_SANITIZED_SELECTION_TOKEN in first
    assert "LOCAL_OPERATOR_TOKEN_MUST_NOT_RENDER_IN_QA" not in first

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
    positions = [first.index(section) for section in sections]
    assert positions == sorted(positions)


def test_machine_readable_status_map_is_present():
    markdown = build_controlled_stat_sanitized_markdown_report(_result())
    for line in [
        "report_record_id=controlled_stat_sanitized_report_renderer_001",
        "report_schema_version=controlled_stat_sanitized_report_v1",
        f"sanitized_selection_token={FIXED_SANITIZED_SELECTION_TOKEN}",
        "filesystem_stat_status=not_executed",
        "file_access_status=not_accessed",
        "file_open_status=not_opened",
        "file_bytes_status=not_read",
        "ffprobe_status=not_executed",
        "scanner_status=not_executed",
        "saas_status=no_saas_integration",
        "path_disclosure_status=not_allowed",
        "filename_disclosure_status=not_allowed",
        "parent_folder_disclosure_status=not_allowed",
    ]:
        assert line in markdown


def test_renderer_boundary_is_static_and_non_executing():
    boundary = describe_sanitized_report_renderer_boundary()
    for key, value in {
        "filesystem_write": "not_performed",
        "filesystem_stat": "not_executed",
        "file_access": "not_accessed",
        "file_open": "not_opened",
        "file_bytes": "not_read",
        "filesystem_metadata": "not_read",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
        "database": "not_touched",
        "docker": "not_touched",
        "alembic": "not_touched",
        "stripe": "not_touched",
        "ai_jobs": "not_touched",
        "credits_ledger": "not_touched",
    }.items():
        assert boundary[key] == value


def test_renderer_source_has_no_runtime_write_or_media_command_patterns():
    text = _text(RENDERER)
    for pattern in [
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
    ]:
        assert pattern not in text


def test_qa_doc_and_renderer_do_not_contain_windows_or_mount_paths():
    combined = _text(QA_DOC) + "\n" + _text(RENDERER)
    for fragment in ["C:\\", "\\\\wsl.localhost", "/mnt/c", "/mnt/C"]:
        assert fragment not in combined
