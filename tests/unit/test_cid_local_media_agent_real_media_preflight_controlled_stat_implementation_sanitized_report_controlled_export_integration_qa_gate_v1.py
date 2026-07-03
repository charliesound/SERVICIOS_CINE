from __future__ import annotations

from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationRequest,
    build_controlled_stat_implementation_result,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_exporter import (
    EXPORTER_HANDLE,
    EXPORTER_RECORD_ID,
    FIXED_SANITIZED_SELECTION_TOKEN,
    PHASE_ID as EXPORTER_PHASE,
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
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_qa_gate_v1.md"
IMPLEMENTATION_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_implementation_gate_v1.md"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_implementation_gate_v1.py"
EXPORTER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_readiness_gate_v1.md"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.md"
RENDERER_IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.QA.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_"
    "CONTROLLED_EXPORT_INTEGRATION_QA_GATE_V1_CLOSED"
)
STARTING_HEAD = "03ef0156c9c96daa36c1d59fff53ae4f974204be"
STARTING_STATE = "CONTROLLED_EXPORT_INTEGRATION_IMPLEMENTATION_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.IMPLEMENTATION.GATE.V1"
)
EXCLUDED_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def _markdown() -> str:
    request = ControlledStatImplementationRequest(
        input_record_id="qa_gate_input_001",
        sanitized_selection_token="LOCAL_OPERATOR_TOKEN_MUST_NOT_EXPORT",
        manual_confirmation_handle="QA_MANUAL_HANDLE_001",
        isolated_boundary_handle="QA_BOUNDARY_HANDLE_001",
        skeleton_handle="QA_SKELETON_HANDLE_001",
    )
    return build_controlled_stat_sanitized_markdown_report(
        build_controlled_stat_implementation_result(request)
    )


def test_qa_gate_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
    ])


def test_qa_gate_declares_documental_scope_and_no_runtime_changes() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is documentation-only and test-only.",
        "This phase does not implement new runtime.",
        "This phase does not modify the exporter.",
        "This phase does not modify the renderer.",
        "This phase does not connect the exporter to a real CLI.",
        "This phase audits the already implemented isolated controlled exporter.",
    ])


def test_qa_gate_declares_exporter_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The audited exporter accepts only sanitized Markdown already rendered by the validated renderer.",
        "The audited exporter requires `export_opt_in=True`.",
        f"The audited exporter requires the fixed redacted token `{FIXED_SANITIZED_SELECTION_TOKEN}`.",
        "The audited exporter rejects non-sanitized content.",
        "The audited exporter rejects unsafe paths.",
        "The audited exporter does not create directories.",
        "The audited exporter does not overwrite existing files.",
        "The audited exporter writes only UTF-8 Markdown in a controlled path.",
        "Any test write must be limited to `tmp_path`.",
        "The audited exporter does not use real media.",
        "The audited exporter does not execute FFmpeg, ffprobe, or external process execution.",
        "The audited exporter does not touch scanner runtime, real CLI integration, backend SaaS, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [
        IMPLEMENTATION_DOC,
        IMPLEMENTATION_TEST,
        EXPORTER,
        RENDERER,
        READINESS_DOC,
        RENDERER_QA_DOC,
        RENDERER_IMPL_DOC,
    ]:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_exporter_exports_only_to_tmp_path_with_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "qa_sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=True)

    assert result.verification_status == "VERIFIED"
    assert result.export_performed is True
    assert result.artifact_created_on_disk is True
    assert result.output_path == str(output.resolve())
    assert output.read_text(encoding="utf-8") == _markdown()


def test_exporter_rejects_without_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "qa_sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=False)

    assert result.export_performed is False
    assert "explicit export opt-in is required" in result.errors
    assert not output.exists()


def test_exporter_requires_fixed_redacted_token(tmp_path: Path) -> None:
    markdown = _markdown().replace(FIXED_SANITIZED_SELECTION_TOKEN, "REDACTED_OTHER_TOKEN")
    result = export_controlled_sanitized_markdown_report(markdown, tmp_path / "qa_sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "fixed sanitized selection token is missing" in result.errors


def test_exporter_rejects_non_sanitized_markdown(tmp_path: Path) -> None:
    result = export_controlled_sanitized_markdown_report("# Not sanitized\n", tmp_path / "qa_sanitized_report.md", export_opt_in=True)

    assert result.export_performed is False
    assert "markdown text is not the validated sanitized report" in result.errors


def test_exporter_rejects_unsafe_paths_without_writing() -> None:
    unsafe_paths = [
        "",
        "../qa_sanitized_report.md",
        "C" + ":" + "/qa_sanitized_report.md",
        "/" + "mnt" + "/c/qa_sanitized_report.md",
        "\\" + "\\" + "server/share/qa_sanitized_report.md",
        "~/qa_sanitized_report.md",
        "$EXPORT_ROOT/qa_sanitized_report.md",
    ]
    for path in unsafe_paths:
        result = export_controlled_sanitized_markdown_report(_markdown(), path, export_opt_in=True)
        assert result.export_performed is False


def test_exporter_does_not_create_directories(tmp_path: Path) -> None:
    output = tmp_path / "missing" / "qa_sanitized_report.md"
    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=True)

    assert result.export_performed is False
    assert "output parent directory does not exist" in result.errors
    assert not output.parent.exists()


def test_exporter_does_not_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "qa_sanitized_report.md"
    output.write_text("existing", encoding="utf-8")

    result = export_controlled_sanitized_markdown_report(_markdown(), output, export_opt_in=True)

    assert result.export_performed is False
    assert "output file already exists" in result.errors
    assert output.read_text(encoding="utf-8") == "existing"


def test_boundary_description_declares_restrictions() -> None:
    boundary = describe_controlled_sanitized_report_export_boundary()
    expected = {
        "record_id": EXPORTER_RECORD_ID,
        "handle": EXPORTER_HANDLE,
        "phase": EXPORTER_PHASE,
        "input_mode": "validated_sanitized_markdown_text_only",
        "output_mode": "controlled_markdown_utf8_file_only",
        "export_opt_in": "required",
        "directory_creation": "not_performed",
        "overwrite": "not_performed",
        "renderer_modification": "not_performed",
        "cli_integration": "not_performed",
        "real_media_access": "not_performed",
        "scanner_execution": "not_performed",
        "ffprobe_execution": "not_performed",
        "ffmpeg_execution": "not_performed",
        "external_process_execution": "not_performed",
        "network_access": "not_performed",
        "saas_access": "not_performed",
        "database_access": "not_performed",
        "docker_access": "not_performed",
        "alembic_access": "not_performed",
        "stripe_access": "not_performed",
        "ai_jobs_access": "not_performed",
        "credits_ledger_access": "not_performed",
    }
    assert boundary == expected


def test_static_exporter_inspection_finds_no_forbidden_runtime_patterns() -> None:
    source = _text(EXPORTER)
    forbidden = [
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
    for pattern in forbidden:
        assert pattern not in source


def test_static_renderer_inspection_confirms_existing_api() -> None:
    assert SANITIZED_REPORT_RENDERER_RECORD_ID == "controlled_stat_sanitized_report_renderer_001"
    assert SANITIZED_REPORT_RENDERER_HANDLE == "CONTROLLED_STAT_SANITIZED_REPORT_RENDERER_HANDLE_001"
    assert SANITIZED_REPORT_SCHEMA_VERSION == "controlled_stat_sanitized_report_v1"
    assert SANITIZED_REPORT_TITLE == "CID Local Media Agent — Controlled Stat Implementation Sanitized Report"
    renderer_source = _text(RENDERER)
    assert "build_controlled_stat_sanitized_markdown_report" in renderer_source
    assert FIXED_SANITIZED_SELECTION_TOKEN in renderer_source


def test_excluded_historical_test_is_documented_but_not_in_battery() -> None:
    text = _text(DOC)
    assert EXCLUDED_TEST in text
    assert "The historical renderer implementation readiness test must not be executed in this QA gate:" in text
    assert "The controlled export integration implementation gate test." in text
    assert "The renderer implementation gate test." in text


def test_new_qa_doc_and_test_contain_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(Path(__file__))
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined
