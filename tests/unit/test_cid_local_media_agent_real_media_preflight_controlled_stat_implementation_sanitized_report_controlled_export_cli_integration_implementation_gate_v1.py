from __future__ import annotations

import io
import json
from pathlib import Path

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationRequest,
    build_controlled_stat_implementation_result,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli import (
    EXIT_CONTROLLED_ERROR,
    EXIT_SUCCESS,
    EXIT_USAGE,
    main,
    run_controlled_sanitized_report_export_cli,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_exporter import (
    FIXED_SANITIZED_SELECTION_TOKEN,
)
from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_renderer import (
    SANITIZED_REPORT_RENDERER_RECORD_ID,
    SANITIZED_REPORT_SCHEMA_VERSION,
    build_controlled_stat_sanitized_markdown_report,
)


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_implementation_gate_v1.md"
CLI = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli.py"
EXPORTER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_controlled_exporter.py"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
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
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.IMPLEMENTATION.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_"
    "CONTROLLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_GATE_V1_CLOSED"
)
STARTING_HEAD = "09501313578aa4c271fecddf2ecc167758c6475e"
STARTING_STATE = "CONTROLLED_EXPORT_CLI_INTEGRATION_READINESS_GATE_CLOSED_REMOTE_VERIFIED"
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.READINESS.GATE.V1"
)
EXCLUDED_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)
EXCLUDED_CLI_READINESS_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_controlled_export_cli_integration_readiness_gate_v1.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def _markdown() -> str:
    request = ControlledStatImplementationRequest(
        input_record_id="controlled_export_cli_input_001",
        sanitized_selection_token="LOCAL_OPERATOR_TOKEN_MUST_NOT_EXPORT",
        manual_confirmation_handle="CLI_MANUAL_HANDLE_001",
        isolated_boundary_handle="CLI_BOUNDARY_HANDLE_001",
        skeleton_handle="CLI_SKELETON_HANDLE_001",
    )
    return build_controlled_stat_sanitized_markdown_report(
        build_controlled_stat_implementation_result(request)
    )


def _run(argv: list[str]) -> tuple[int, dict]:
    stdout = io.StringIO()
    exit_code = run_controlled_sanitized_report_export_cli(argv, stdout=stdout)
    payload = json.loads(stdout.getvalue())
    return exit_code, payload


def test_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_HEAD,
        STARTING_STATE,
        PREVIOUS_PHASE,
    ])


def test_document_declares_scope_and_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase implements only a new, isolated, and controlled CLI.",
        "This phase does not modify existing historical CLIs.",
        "This phase does not connect the real client flow.",
        "This phase does not modify the exporter.",
        "This phase does not modify the renderer.",
        "The CLI calls the existing exporter `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`.",
        "The CLI does not duplicate write logic.",
        "The CLI requires explicit opt-in through `--export-opt-in`.",
        "The CLI receives already-rendered sanitized Markdown through the explicit `--markdown-text` argument.",
        "The CLI receives the output path through the explicit `--output-path` argument.",
        "The CLI validates output path and content through the existing exporter.",
        "The CLI returns structured and deterministic JSON output.",
        "The CLI returns exit code `0` on controlled success.",
        "The CLI returns a non-zero exit code on controlled error.",
    ])


def test_document_declares_safety_boundaries() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "Any test write must be limited to `tmp_path`.",
        "The CLI does not use real media.",
        "The CLI does not execute FFmpeg.",
        "The CLI does not execute ffprobe.",
        "The CLI does not use subprocess.",
        "The CLI does not touch scanner runtime.",
        "The CLI does not touch backend SaaS.",
        "The CLI does not touch frontend.",
        "The CLI does not touch DB.",
        "The CLI does not touch Docker.",
        "The CLI does not touch Alembic.",
        "The CLI does not touch Stripe.",
        "The CLI does not touch AI Jobs.",
        "The CLI does not touch credits.",
        "The CLI does not touch ledger.",
    ])


def test_new_cli_exists_and_exposes_testable_api() -> None:
    assert CLI.exists()
    assert run_controlled_sanitized_report_export_cli.__name__ == "run_controlled_sanitized_report_export_cli"
    assert main.__name__ == "main"
    source = _text(CLI)
    _assert_all_present(source, [
        "def run_controlled_sanitized_report_export_cli(",
        "def main(",
        "export_controlled_sanitized_markdown_report(",
        "raise SystemExit(main())",
    ])


def test_cli_calls_exporter_and_does_not_duplicate_write_logic() -> None:
    source = _text(CLI)
    assert "from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_exporter import" in source
    assert "export_controlled_sanitized_markdown_report(" in source
    forbidden = [
        "os.open",
        "os.write",
        "write_text(",
        "write_bytes(",
        "open(",
        ".mkdir(",
        ".rename(",
        ".replace(",
    ]
    for pattern in forbidden:
        assert pattern not in source


def test_cli_success_with_sanitized_markdown_tmp_path_and_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    exit_code, payload = _run([
        "--markdown-text",
        _markdown(),
        "--output-path",
        str(output),
        "--export-opt-in",
    ])

    assert exit_code == EXIT_SUCCESS
    assert payload["verification_status"] == "VERIFIED"
    assert payload["export_performed"] is True
    assert payload["artifact_created_on_disk"] is True
    assert payload["errors"] == []
    assert output.read_text(encoding="utf-8") == _markdown()


def test_cli_returns_error_without_opt_in(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    exit_code, payload = _run([
        "--markdown-text",
        _markdown(),
        "--output-path",
        str(output),
    ])

    assert exit_code == EXIT_CONTROLLED_ERROR
    assert payload["export_performed"] is False
    assert "explicit export opt-in is required" in payload["errors"]
    assert not output.exists()


def test_cli_returns_error_with_non_sanitized_markdown(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    exit_code, payload = _run([
        "--markdown-text",
        "# Not sanitized",
        "--output-path",
        str(output),
        "--export-opt-in",
    ])

    assert exit_code == EXIT_CONTROLLED_ERROR
    assert payload["export_performed"] is False
    assert "markdown text is not the validated sanitized report" in payload["errors"]
    assert not output.exists()


def test_cli_returns_error_with_unsafe_path_via_exporter() -> None:
    exit_code, payload = _run([
        "--markdown-text",
        _markdown(),
        "--output-path",
        "../sanitized_report.md",
        "--export-opt-in",
    ])

    assert exit_code == EXIT_CONTROLLED_ERROR
    assert payload["export_performed"] is False
    assert "output path must not contain traversal or dot segments" in payload["errors"]


def test_cli_does_not_create_directories(tmp_path: Path) -> None:
    output = tmp_path / "missing" / "sanitized_report.md"
    exit_code, payload = _run([
        "--markdown-text",
        _markdown(),
        "--output-path",
        str(output),
        "--export-opt-in",
    ])

    assert exit_code == EXIT_CONTROLLED_ERROR
    assert payload["export_performed"] is False
    assert "output parent directory does not exist" in payload["errors"]
    assert not output.parent.exists()


def test_cli_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    output.write_text("existing", encoding="utf-8")
    exit_code, payload = _run([
        "--markdown-text",
        _markdown(),
        "--output-path",
        str(output),
        "--export-opt-in",
    ])

    assert exit_code == EXIT_CONTROLLED_ERROR
    assert payload["export_performed"] is False
    assert "output file already exists" in payload["errors"]
    assert output.read_text(encoding="utf-8") == "existing"


def test_cli_usage_error_returns_safe_json() -> None:
    exit_code, payload = _run([])

    assert exit_code == EXIT_USAGE
    assert payload == {
        "command": "cid-controlled-sanitized-report-export",
        "error": "invalid CLI usage",
        "export_performed": False,
        "verification_status": "CLI_USAGE_ERROR",
    }


def test_cli_output_json_is_deterministic_and_safe(tmp_path: Path) -> None:
    output = tmp_path / "sanitized_report.md"
    stdout = io.StringIO()
    exit_code = run_controlled_sanitized_report_export_cli([
        "--markdown-text",
        _markdown(),
        "--output-path",
        str(output),
        "--export-opt-in",
    ], stdout=stdout)
    payload_text = stdout.getvalue()
    payload = json.loads(payload_text)

    assert exit_code == EXIT_SUCCESS
    assert payload_text == json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    assert "LOCAL_OPERATOR_TOKEN" not in payload_text
    assert "markdown_text" not in payload_text


def test_cli_static_inspection_finds_no_forbidden_runtime_patterns() -> None:
    source = _text(CLI)
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


def test_exporter_and_renderer_existing_contracts_remain_intact() -> None:
    exporter_source = _text(EXPORTER)
    renderer_source = _text(RENDERER)
    assert "def export_controlled_sanitized_markdown_report(" in exporter_source
    assert "def describe_controlled_sanitized_report_export_boundary()" in exporter_source
    assert "class ControlledSanitizedReportExportResult" in exporter_source
    assert SANITIZED_REPORT_RENDERER_RECORD_ID == "controlled_stat_sanitized_report_renderer_001"
    assert SANITIZED_REPORT_SCHEMA_VERSION == "controlled_stat_sanitized_report_v1"
    assert FIXED_SANITIZED_SELECTION_TOKEN in renderer_source


def test_historical_clis_exist_and_are_not_connected_to_new_exporter() -> None:
    for path in HISTORICAL_CLIS:
        assert path.exists(), path
        assert "export_controlled_sanitized_markdown_report" not in _text(path)


def test_readiness_gate_feeds_this_implementation_gate() -> None:
    readiness = _text(READINESS_DOC)
    _assert_all_present(readiness, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.CONTROLLED_EXPORT.CLI_INTEGRATION.READINESS.GATE.V1",
        "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_CLI_INTEGRATION_READINESS_GATE_V1_CLOSED",
        "CONTROLLED_EXPORT_CLI_INTEGRATION_READINESS_PASSED_READY_FOR_EXPLICIT_CLI_INTEGRATION_GATE",
    ])


def test_cli_readiness_gate_is_historical_after_implementation() -> None:
    text = _text(DOC)
    readiness_test_source = _text(READINESS_TEST)
    _assert_all_present(text, [
        "The CLI integration readiness gate test is historical and not applicable as a post-implementation regression after this phase:",
        EXCLUDED_CLI_READINESS_TEST,
        "That readiness test validated the pre-implementation state and asserted that no CLI specific to the controlled exporter existed yet.",
        "After this implementation gate, the new isolated CLI exists by design and is connected to `export_controlled_sanitized_markdown_report(markdown_text, output_path, export_opt_in)`, so that pre-implementation assertion must not be executed as an applicable post-implementation regression.",
    ])
    assert READINESS_TEST.exists()
    assert "test_no_specific_cli_is_connected_to_new_controlled_exporter_yet" in readiness_test_source
    assert "assert connected == []" in readiness_test_source


def test_excluded_historical_test_is_documented_but_not_in_battery() -> None:
    text = _text(DOC)
    assert EXCLUDED_TEST in text
    assert "The historical renderer implementation readiness test must not be executed in this implementation gate:" in text
    assert "This CLI integration implementation gate test." in text
    assert "The sanitized report renderer implementation gate test." in text


def test_new_doc_test_and_cli_contain_no_windows_or_mount_paths() -> None:
    combined = _text(DOC) + "\n" + _text(CLI) + "\n" + _text(Path(__file__))
    forbidden_fragments = [
        "C" + ":" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/" + "mnt" + "/c",
        "/" + "mnt" + "/C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in combined
