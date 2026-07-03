from __future__ import annotations

from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli import (
    EXIT_CONTROLLED_ERROR,
    EXIT_SUCCESS,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli_controlled_smoke import (
    REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN,
    run_controlled_sanitized_report_export_cli_controlled_smoke,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_qa_gate_v1.md"
IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_implementation_gate_v1.md"
IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_implementation_gate_v1.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_readiness_gate_v1.py"
CLI = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py"
EXPORTER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
SMOKE_SCRIPT = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli_controlled_smoke.py"
HISTORICAL_CLIS = [
    ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
    ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py",
    ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py",
    ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py",
    ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_smoke_controlled_fixture.py",
    ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py",
    ROOT / "scripts/local_media_agent/visible_report_runtime_cli.py",
    ROOT / "scripts/cid_local_media_agent_real_preflight_cli.py",
    ROOT / "scripts/cid_local_media_agent_synthetic_visible_report_cli.py",
]

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION."
    "CONTROLLED_SMOKE.QA.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_"
    "CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_QA_GATE_V1_CLOSED"
)
STARTING_HEAD = "402b2ef69dd9059bc94b49a0855fa2fb8e1918ed"
STARTING_STATE = "CONTROLLED_SMOKE_IMPLEMENTATION_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION."
    "CONTROLLED_SMOKE.IMPLEMENTATION.GATE.V1"
)
TARGET_NEXT_STATE = (
    "CONTROLLED_SMOKE_QA_GATE_PASSED_READY_FOR_REAL_MEDIA_SAFE_INTAKE_READINESS_GATE"
)
EXCLUDED_RENDERER_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)
EXCLUDED_CLI_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
)
FIXED_TOKEN_STR = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def test_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
        TARGET_NEXT_STATE,
    ])


def test_document_does_not_use_ready_for_release() -> None:
    text = _text(DOC)
    assert "READY_FOR_RELEASE" not in text


def test_document_declares_scope_and_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is documentation-only and test-only.",
        "This phase audits the already-implemented controlled smoke of the isolated controlled export CLI.",
        "This phase does not implement new runtime.",
        "This phase does not modify the smoke script.",
        "This phase does not modify the CLI.",
        "This phase does not modify the exporter.",
        "This phase does not modify the renderer.",
        "This phase does not modify historical CLIs.",
        "This phase does not connect the real client flow.",
        "This phase uses only test sanitized Markdown, not real media.",
    ])


def test_document_declares_audited_smoke_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        FIXED_TOKEN_STR,
        "run_controlled_sanitized_report_export_cli",
        "real_media_preflight_controlled_stat_sanitized_report_renderer",
        "real_media_preflight_controlled_stat_implementation",
        "The audited smoke does not duplicate write logic.",
        "The audited smoke does not execute ffmpeg, ffprobe, subprocess, or shell.",
        "The audited smoke does not read real media or scan folders.",
        "The audited smoke does not touch scanner runtime, backend SaaS, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        "The audited smoke uses `io.StringIO` to capture CLI stdout and parses emitted JSON.",
        "Use of real client material remains blocked until explicit future phases.",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [
        IMPL_DOC,
        IMPL_TEST,
        SMOKE_SCRIPT,
        CLI,
        EXPORTER,
        RENDERER,
        READINESS_DOC,
        READINESS_TEST,
    ]:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_smoke_script_exists_and_exposes_function() -> None:
    assert SMOKE_SCRIPT.exists()
    assert run_controlled_sanitized_report_export_cli_controlled_smoke.__name__ == (
        "run_controlled_sanitized_report_export_cli_controlled_smoke"
    )
    source = _text(SMOKE_SCRIPT)
    _assert_all_present(source, [
        "def run_controlled_sanitized_report_export_cli_controlled_smoke(",
        "run_controlled_sanitized_report_export_cli(",
        "io.StringIO()",
        FIXED_TOKEN_STR,
    ])


def test_smoke_script_imports_only_cli_not_renderer_not_implementation() -> None:
    source = _text(SMOKE_SCRIPT)
    assert (
        "from scripts.local_media_agent.real_media_preflight_controlled_stat_"
        "sanitized_report_controlled_export_cli import"
    ) in source
    assert "run_controlled_sanitized_report_export_cli" in source
    forbidden_imports = [
        "real_media_preflight_controlled_stat_sanitized_report_renderer",
        "real_media_preflight_controlled_stat_implementation",
        "ControlledStatImplementationRequest",
        "build_controlled_stat_implementation_result",
        "build_controlled_stat_sanitized_markdown_report",
    ]
    for imp in forbidden_imports:
        assert imp not in source


def test_smoke_script_does_not_modify_cli_exporter_renderer_or_historical_clis() -> None:
    existing = [CLI, EXPORTER, RENDERER] + HISTORICAL_CLIS
    for path in existing:
        assert path.exists(), path


def test_smoke_script_has_no_forbidden_runtime_or_system_patterns() -> None:
    source = _text(SMOKE_SCRIPT)
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
        "sys.exit",
    ]
    for pattern in forbidden:
        assert pattern not in source


def test_smoke_script_has_no_windows_or_mount_paths() -> None:
    source = _text(SMOKE_SCRIPT)
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in source


def test_smoke_success_with_opt_in_and_tmp_path(tmp_path: Path) -> None:
    output = tmp_path / "controlled_smoke_report.md"
    result = run_controlled_sanitized_report_export_cli_controlled_smoke(
        str(output), export_opt_in=True
    )
    assert result["status"] == "ok"
    assert result["cli_exit_code"] == EXIT_SUCCESS
    assert result["created"] is True
    assert result["errors"] == []
    assert result["verification_status"] == "VERIFIED"
    assert output.exists()
    assert FIXED_TOKEN_STR in output.read_text(encoding="utf-8")


def test_smoke_fails_safely_without_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "controlled_smoke_report.md"
    result = run_controlled_sanitized_report_export_cli_controlled_smoke(
        str(output), export_opt_in=False
    )
    assert result["status"] == "error"
    assert result["cli_exit_code"] == EXIT_CONTROLLED_ERROR
    assert result["created"] is False
    assert "explicit export opt-in is required" in result["errors"]
    assert not output.exists()


def test_smoke_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    output = tmp_path / "controlled_smoke_report.md"
    output.write_text("existing content", encoding="utf-8")
    result = run_controlled_sanitized_report_export_cli_controlled_smoke(
        str(output), export_opt_in=True
    )
    assert result["status"] == "error"
    assert result["created"] is False
    assert "output file already exists" in result["errors"]
    assert output.read_text(encoding="utf-8") == "existing content"


def test_smoke_returns_deterministic_and_safe_structure(tmp_path: Path) -> None:
    output = tmp_path / "controlled_smoke_report.md"
    result1 = run_controlled_sanitized_report_export_cli_controlled_smoke(
        str(output), export_opt_in=True
    )
    assert isinstance(result1, dict)
    for key in ("status", "cli_exit_code", "output_path", "created", "errors", "verification_status"):
        assert key in result1
    assert result1["output_path"] == str(output)
    result2 = run_controlled_sanitized_report_export_cli_controlled_smoke(
        str(tmp_path / "other.md"), export_opt_in=True
    )
    assert result1["status"] == result2["status"]
    assert result1["cli_exit_code"] == result2["cli_exit_code"]


def test_smoke_uses_redacted_token_no_real_tokens() -> None:
    assert REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN == FIXED_TOKEN_STR
    source = _text(SMOKE_SCRIPT)
    assert FIXED_TOKEN_STR in source
    assert "LOCAL_OPERATOR_TOKEN" not in source


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


def test_implementation_gate_feeds_this_qa_gate() -> None:
    impl = _text(IMPL_DOC)
    _assert_all_present(impl, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.CONTROLLED_SMOKE.IMPLEMENTATION.GATE.V1",
        "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_IMPLEMENTATION_GATE_V1_CLOSED",
        "CONTROLLED_SMOKE_IMPLEMENTED_READY_FOR_SMOKE_EXECUTION",
    ])


def test_implementation_gate_test_exists() -> None:
    assert IMPL_TEST.exists()


def test_doc_and_test_and_smoke_contain_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(SMOKE_SCRIPT) + "\n" + _text(Path(__file__))
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined
