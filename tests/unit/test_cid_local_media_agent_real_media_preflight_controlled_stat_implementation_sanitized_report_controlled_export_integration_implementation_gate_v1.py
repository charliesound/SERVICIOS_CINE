from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationRequest,
    build_controlled_stat_implementation_result,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_exporter import (
    ARTIFACT_FORMAT,
    ARTIFACT_TYPE,
    EXPORTER_HANDLE,
    EXPORTER_RECORD_ID,
    FIXED_SANITIZED_SELECTION_TOKEN,
    PHASE_ID,
    ControlledSanitizedReportExportResult,
    describe_controlled_sanitized_report_export_boundary,
    export_controlled_sanitized_markdown_report,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_renderer import (
    SANITIZED_REPORT_RENDERER_HANDLE,
    SANITIZED_REPORT_RENDERER_RECORD_ID,
    SANITIZED_REPORT_SCHEMA_VERSION,
    SANITIZED_REPORT_TITLE,
    build_controlled_stat_sanitized_markdown_report,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_implementation_gate_v1.md"
EXPORTER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_readiness_gate_v1.md"

PHASE = PHASE_ID
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_"
    "CONTROLLED_EXPORT_INTEGRATION_IMPLEMENTATION_GATE_V1_CLOSED"
)
STARTING_HEAD = "07bd10a02cd5ed959c2a2a4f985064c1768c3b8f"
STARTING_STATE = "CONTROLLED_EXPORT_INTEGRATION_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
TARGET_STATE = (
    "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_INTEGRATION_"
    "IMPLEMENTED_READY_FOR_QA_GATE"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.READINESS.GATE.V1"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _request() -> ControlledStatImplementationRequest:
    return ControlledStatImplementationRequest(
        input_record_id="controlled_export_input_001",
        sanitized_selection_token="LOCAL_OPERATOR_TOKEN_MUST_NOT_EXPORT",
        manual_confirmation_handle="MANUAL_OPERATOR_CONFIRMATION_HANDLE_001",
        isolated_boundary_handle="ISOLATED_IMPLEMENTATION_BOUNDARY_HANDLE_001",
        skeleton_handle="CODE_SKELETON_HANDLE_001",
    )


def _markdown() -> str:
    return build_controlled_stat_sanitized_markdown_report(
        build_controlled_stat_implementation_result(_request())
    )


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def test_document_exists_and_declares_phase_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        TARGET_STATE,
        PREVIOUS_PHASE,
    ])


def test_document_declares_implementation_scope_and_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase implements only an isolated and controlled exporter for sanitized Markdown reports.",
        "This phase does not integrate the exporter into a real CLI.",
        "This phase does not integrate the exporter into a client flow.",
        "This phase does not modify the existing renderer.",
        "This phase does not modify scanner runtime.",
        "The exporter accepts only sanitized Markdown already rendered by the validated renderer.",
        "The exporter requires explicit opt-in through `export_opt_in=True`.",
        "The exporter rejects unsafe paths.",
        "The exporter does not create directory trees.",
        "The exporter does not overwrite existing files.",
        "The exporter writes only UTF-8 Markdown text.",
        f"The operator token must remain redacted as `{FIXED_SANITIZED_SELECTION_TOKEN}`.",
    ])


def test_document_declares_safety_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The exporter does not read real media.",
        "The exporter does not execute FFmpeg.",
        "The exporter does not execute ffprobe.",
        "The exporter does not execute external processes.",
        "The exporter does not touch scanner runtime.",
        "The exporter does not touch real CLI integration.",
        "The exporter does not touch backend SaaS.",
        "The exporter does not touch frontend.",
        "The exporter does not touch database services.",
        "The exporter does not touch Docker.",
        "The exporter does not touch Alembic.",
        "The exporter does not touch Stripe.",
        "The exporter does not touch AI Jobs.",
        "The exporter does not touch credits.",
        "The exporter does not touch ledger.",
    ])


def test_module_exists_and_public_identity_is_stable() -> None:
    assert EXPORTER.exists()
    assert EXPORTER_RECORD_ID == "controlled_stat_sanitized_report_controlled_exporter_001"
    assert EXPORTER_HANDLE == "CONTROLLED_STAT_SANITIZED_REPORT_CONTROLLED_EXPORTER_HANDLE_001"
    assert ARTIFACT_TYPE == "controlled_sanitized_markdown_report"
    assert ARTIFACT_FORMAT == "markdown_utf8"


def test_successful_controlled_export_with_explicit_opt_in(tmp_path: Path) -> None:
    markdown = _markdown()
    output = tmp_path / "sanitized_report.md"
    payload = markdown.encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()

    result = export_controlled_sanitized_markdown_report(markdown, output, export_opt_in=True)

    assert isinstance(result, ControlledSanitizedReportExportResult)
    assert output.read_text(encoding="utf-8") == markdown
    assert result.phase == PHASE
    assert result.export_opt_in is True
    assert result.export_performed is True
    assert result.artifact_created_on_disk is True
    assert result.bytes_intended == len(payload)
    assert result.bytes_written == len(payload)
    assert result.content_sha256_before_write == digest
    assert result.content_sha256_after_write == digest
    assert result.path_boundary == "INSIDE_EXISTING_PARENT_DIRECTORY"
    assert result.overwrite_policy == "NO_OVERWRITE"
    assert result.verification_status == "VERIFIED"
    assert result.errors == ()
    assert result.safety_flags["file_write_performed"] is True
    assert result.safety_flags["artifact_created_on_disk"] is True


def test_rejects_without_explicit_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=False)

    assert result.export_performed is False
    assert "explicit export opt-in is required" in result.errors
    assert not output.exists()


def test_rejects_non_string_content(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report(b"not text", tmp_path / "sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "markdown text must be a string" in result.errors


def test_rejects_empty_content(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report("", tmp_path / "sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "markdown text must not be empty" in result.errors


def test_rejects_markdown_not_from_validated_renderer(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report("# Other report\n", tmp_path / "sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "markdown text is not the validated sanitized report" in result.errors


def test_rejects_missing_fixed_redacted_token(tmp_path: Path) -> None:
    markdown = _markdown().replace(FIXED_SANITIZED_SELECTION_TOKEN, "REDACTED_DIFFERENT_TOKEN")
    result = export_controlled_sanitized_markdown_report(markdown, tmp_path / "sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "fixed sanitized selection token is missing" in result.errors


def test_rejects_operator_token_marker(tmp_path: Path) -> None:
    markdown = _markdown() + "\nLOCAL_OPERATOR_TOKEN_SHOULD_NOT_EXPORT\n"
    result = export_controlled_sanitized_markdown_report(markdown, tmp_path / "sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "markdown text contains an unsanitized operator token marker" in result.errors


@pytest.mark.parametrize(
    ("path_value", "expected_error"),
    [
        ("", "output path must not be empty"),
        ("../sanitized_report.md", "output path must not contain traversal or dot segments"),
        ("folder/../sanitized_report.md", "output path must not contain traversal or dot segments"),
        ("C" + ":" + "/sanitized_report.md", "output path must not be drive-like"),
        ("/" + "mnt" + "/c/sanitized_report.md", "output path must not be mount-like"),
        ("\\" + "\\" + "server/share/sanitized_report.md", "output path must not be UNC-like"),
        ("~/sanitized_report.md", "output path must not be home-relative"),
        ("$EXPORT_ROOT/sanitized_report.md", "output path must not be environment-like"),
    ],
)
def test_rejects_unsafe_paths(path_value: str, expected_error: str) -> None:
    result = export_controlled_sanitized_markdown_report(_markdown(), path_value, export_opt_in=True)

    assert result.export_performed is False
    assert expected_error in result.errors


def test_rejects_parent_that_does_not_exist(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / "sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), missing, export_opt_in=True)

    assert result.export_performed is False
    assert "output parent directory does not exist" in result.errors
    assert not missing.parent.exists()


def test_rejects_directory_as_target(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report(_markdown(), tmp_path, export_opt_in=True)

    assert result.export_performed is False
    assert "output path must target a Markdown file" in result.errors


def test_rejects_existing_file_and_does_not_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    output.write_text("existing", encoding="utf-8")

    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=True)

    assert result.export_performed is False
    assert "output file already exists" in result.errors
    assert output.read_text(encoding="utf-8") == "existing"


def test_does_not_create_directories(tmp_path: Path) -> None:
    output = tmp_path / "new" / "nested" / "sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=True)

    assert result.export_performed is False
    assert "output parent directory does not exist" in result.errors
    assert not (tmp_path / "new").exists()


def test_result_dict_shape_is_deterministic(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report(_markdown(), tmp_path / "sanitized_report.md", export_opt_in=True)

    assert list(result.to_dict().keys()) == [
        "phase",
        "implementation_version",
        "exporter_record_id",
        "exporter_handle",
        "artifact_type",
        "artifact_format",
        "output_path",
        "output_filename",
        "export_opt_in",
        "export_requested",
        "export_performed",
        "artifact_created_on_disk",
        "bytes_intended",
        "bytes_written",
        "content_sha256_before_write",
        "content_sha256_after_write",
        "path_boundary",
        "overwrite_policy",
        "verification_status",
        "safety_flags",
        "errors",
    ]


def test_boundary_description_declares_restrictions() -> None:
    boundary = describe_controlled_sanitized_report_export_boundary()

    assert boundary["record_id"] == EXPORTER_RECORD_ID
    assert boundary["handle"] == EXPORTER_HANDLE
    assert boundary["phase"] == PHASE
    assert boundary["input_mode"] == "validated_sanitized_markdown_text_only"
    assert boundary["output_mode"] == "controlled_markdown_utf8_file_only"
    assert boundary["export_opt_in"] == "required"
    assert boundary["directory_creation"] == "not_performed"
    assert boundary["overwrite"] == "not_performed"
    assert boundary["renderer_modification"] == "not_performed"
    assert boundary["cli_integration"] == "not_performed"
    assert boundary["real_media_access"] == "not_performed"
    assert boundary["scanner_execution"] == "not_performed"
    assert boundary["ffprobe_execution"] == "not_performed"
    assert boundary["ffmpeg_execution"] == "not_performed"
    assert boundary["external_process_execution"] == "not_performed"
    assert boundary["saas_access"] == "not_performed"
    assert boundary["database_access"] == "not_performed"
    assert boundary["docker_access"] == "not_performed"
    assert boundary["alembic_access"] == "not_performed"
    assert boundary["stripe_access"] == "not_performed"
    assert boundary["ai_jobs_access"] == "not_performed"
    assert boundary["credits_ledger_access"] == "not_performed"


def test_exporter_source_has_no_forbidden_runtime_patterns() -> None:
    source = _text(EXPORTER)
    forbidden_patterns = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process.",
        "ffmpeg -",
        "ffprobe -",
        "scanner_runtime",
        "backend_runtime",
        "frontend_runtime",
        "sqlite3",
        "Dockerfile",
        "alembic upgrade",
        "stripe.",
        "ai_jobs.",
        "credits.",
        "ledger.",
        "mkdir",
        ".mkdir(",
        ".replace(",
        ".rename(",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in source


def test_exporter_source_contains_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(EXPORTER)
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined


def test_renderer_existing_api_remains_intact() -> None:
    assert RENDERER.exists()
    assert SANITIZED_REPORT_RENDERER_RECORD_ID == "controlled_stat_sanitized_report_renderer_001"
    assert SANITIZED_REPORT_RENDERER_HANDLE == "CONTROLLED_STAT_SANITIZED_REPORT_RENDERER_HANDLE_001"
    assert SANITIZED_REPORT_SCHEMA_VERSION == "controlled_stat_sanitized_report_v1"
    assert SANITIZED_REPORT_TITLE == "CID Local Media Agent — Controlled Stat Implementation Sanitized Report"


def test_previous_readiness_gate_feeds_this_implementation_gate() -> None:
    text = _text(READINESS_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.READINESS.GATE.V1",
        "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_INTEGRATION_READINESS_GATE_V1_CLOSED",
        "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_INTEGRATION_READINESS_PASSED_READY_FOR_CONTROLLED_EXPORT_INTEGRATION_GATE",
    ])
