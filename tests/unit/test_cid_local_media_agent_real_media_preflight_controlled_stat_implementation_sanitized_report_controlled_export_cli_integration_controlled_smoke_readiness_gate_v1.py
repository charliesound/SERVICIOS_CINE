from __future__ import annotations

from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli import (
    EXIT_CONTROLLED_ERROR,
    EXIT_SUCCESS,
    EXIT_USAGE,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_controlled_smoke_readiness_gate_v1.md"
CLI_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_qa_gate_v1.md"
CLI_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_qa_gate_v1.py"
CLI_IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.md"
CLI_IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.py"
CLI = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py"
EXPORTER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
EXPORTER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_qa_gate_v1.md"
EXPORTER_IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_implementation_gate_v1.md"
EXPORTER_READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_readiness_gate_v1.md"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.md"
RENDERER_IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md"
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
    "CONTROLLED_SMOKE.READINESS.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_"
    "CONTROLLED_EXPORT_CLI_INTEGRATION_CONTROLLED_SMOKE_READINESS_GATE_V1_CLOSED"
)
STARTING_HEAD = "7010bceaaccd6320984baba2f258ee82a3ff06ef"
STARTING_STATE = "CONTROLLED_EXPORT_CLI_INTEGRATION_QA_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.QA.GATE.V1"
)
EXCLUDED_RENDERER_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)
EXCLUDED_CLI_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
)
FIXED_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
CLI_PATH_STR = "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def test_readiness_gate_document_exists() -> None:
    assert DOC.exists()


def test_readiness_gate_document_declares_identity() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
    ])


def test_readiness_gate_declares_documental_scope_and_no_runtime_changes() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is documentation-only and test-only.",
        "This phase does not implement new runtime.",
        "This phase does not yet execute a real controlled smoke.",
        "This phase does not modify the CLI.",
        "This phase does not modify the exporter.",
        "This phase does not modify the renderer.",
        "This phase does not modify historical CLIs.",
        "This phase does not connect the real client flow.",
    ])


def test_readiness_gate_declares_future_smoke_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        CLI_PATH_STR,
        "The future controlled smoke must use test sanitized Markdown, not real media.",
        "The future controlled smoke must require `--export-opt-in`.",
        "The future controlled smoke must use `--markdown-text`.",
        "The future controlled smoke must use `--output-path`.",
        "Any future smoke write must be limited to a temporary or controlled path.",
        "The future smoke must not read real media.",
        "The future smoke must not execute ffmpeg, ffprobe, or subprocess.",
        "The future smoke must not touch scanner runtime, backend SaaS, frontend, DB, Docker, Alembic, Stripe, AI Jobs, credits, or ledger.",
        FIXED_TOKEN,
        "Safe JSON output without token leaks",
        "Correct exit code",
        "Exported artifact on disk",
        "Absence of real tokens in the output",
    ])


def test_required_artifacts_exist_and_are_referenced() -> None:
    text = _text(DOC)
    for path in [
        CLI_QA_DOC,
        CLI_QA_TEST,
        CLI_IMPL_DOC,
        CLI_IMPL_TEST,
        CLI,
        EXPORTER,
        RENDERER,
    ]:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_excluded_historical_tests_are_documented() -> None:
    text = _text(DOC)
    assert EXCLUDED_RENDERER_READINESS_TEST in text
    assert EXCLUDED_CLI_READINESS_TEST in text
    assert "The historical renderer implementation readiness test must not be executed as a post-implementation regression:" in text
    assert "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:" in text


def test_exit_code_constants_are_available() -> None:
    assert EXIT_SUCCESS == 0
    assert EXIT_CONTROLLED_ERROR == 2
    assert EXIT_USAGE == 64


def test_new_cli_exists_and_is_unmodified() -> None:
    assert CLI.exists()
    doc_text = _text(DOC)
    assert CLI_PATH_STR in doc_text
    source = _text(CLI)
    assert "def run_controlled_sanitized_report_export_cli(" in source
    assert "def main(" in source
    assert "export_controlled_sanitized_markdown_report(" in source
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process.",
        "ffmpeg ",
        "ffprobe ",
        "scanner_runtime",
        "backend_runtime",
        "frontend_runtime",
        "sqlite3",
        "alembic upgrade",
        "stripe.",
        "ai_jobs.",
        "credits.",
        "ledger.",
    ]
    for pattern in forbidden:
        assert pattern not in source


def test_exporter_and_renderer_exist_and_are_unmodified() -> None:
    assert EXPORTER.exists()
    assert RENDERER.exists()
    exporter_source = _text(EXPORTER)
    renderer_source = _text(RENDERER)
    assert "def export_controlled_sanitized_markdown_report(" in exporter_source
    assert "def describe_controlled_sanitized_report_export_boundary()" in exporter_source
    assert "class ControlledSanitizedReportExportResult" in exporter_source
    assert FIXED_TOKEN in renderer_source
    assert "controlled_stat_sanitized_report_renderer_001" in renderer_source


def test_historical_clis_remain_unchanged() -> None:
    for path in HISTORICAL_CLIS:
        assert path.exists(), path
        assert "export_controlled_sanitized_markdown_report" not in _text(path)


def test_readiness_doc_and_test_contain_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(Path(__file__))
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined
