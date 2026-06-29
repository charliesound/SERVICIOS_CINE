from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as cli,
)


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution.py"
)

CLI_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

IMPLEMENTATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation.py"
)

QA_CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review_v1.md"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_SMOKE_EXECUTION_"
    "PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "6881ac27f00daf0b31c555955b322aa11b68370a"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _visible_report_text() -> str:
    return "# Controlled CLI Smoke Execution\n\nNo file was written.\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_planner_result() -> dict[str, object]:
    text = _visible_report_text()
    return {
        "controlled_export_root": "controlled_export_root",
        "suggested_filename": "controlled_cli_smoke.controlled_visible_report.txt",
        "planned_artifact_path": "controlled_export_root/controlled_cli_smoke.controlled_visible_report.txt",
        "artifact_format": "controlled_visible_report_text",
        "content_sha256": _sha256_text(text),
        "write_performed": False,
        "artifact_created_on_disk": False,
        "path_boundary": "safe",
        "safety_flags": {
            "real_media_access_performed": False,
            "scanner_execution_performed": False,
            "ffprobe_execution_performed": False,
            "ffmpeg_execution_performed": False,
            "subprocess_execution_performed": False,
            "network_access_performed": False,
            "saas_or_database_access_performed": False,
            "file_write_performed": False,
            "directory_creation_performed": False,
            "artifact_created_on_disk": False,
        },
    }


def _valid_smoke_argv() -> list[str]:
    return [
        "--dry-run",
        "--visible-report-text",
        _visible_report_text(),
        "--planner-result-json",
        json.dumps(_valid_planner_result(), sort_keys=True),
        "--caller-context-json",
        json.dumps({"smoke_execution": "controlled_inline"}, sort_keys=True),
    ]


def test_smoke_execution_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_smoke_execution_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [CLI_MODULE_PATH, IMPLEMENTATION_TEST_PATH, QA_CLOSURE_DOC_PATH, BRIDGE_MODULE_PATH],
)
def test_artifacts_under_smoke_execution_exist(path: Path) -> None:
    assert path.is_file()


@pytest.mark.parametrize(
    "required_text",
    [
        PHASE_ID,
        RESULT_ID,
        PREVIOUS_COMMIT,
        PREVIOUS_TAG,
        TARGET_TAG,
        NEXT_PHASE_ID,
        "This is a controlled smoke execution.",
        "This smoke execution validates the controlled CLI dry-run integration through the Python entrypoint with inline controlled arguments.",
        "This smoke execution does not write files.",
        "This smoke execution does not create directories.",
        "This smoke execution does not create artifacts on disk.",
        "This smoke execution does not use real media.",
        "This smoke execution does not scan folders.",
        "This smoke execution does not execute ffprobe.",
        "This smoke execution does not execute FFmpeg.",
        "This smoke execution does not execute external processes.",
        "This smoke execution does not access networks.",
    ],
)
def test_smoke_doc_declares_lineage_scope_result_and_boundaries(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_smoke_doc_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run controlled implementation QA gate closure review test passed with 113 checks.",
        "controlled implementation QA gate test passed with 145 checks.",
        "controlled implementation test passed with 41 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "new CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target controlled implementation QA closure review short tag absent locally before tagging.",
        "target controlled implementation QA closure review short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target closure review test passed with 113 checks.",
        "final controlled implementation QA gate test passed with 145 checks.",
        "final controlled implementation test passed with 41 checks.",
        "final new CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_smoke_doc_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This smoke execution uses controlled inline visible report text.",
        "This smoke execution uses controlled inline planner result JSON.",
        "This smoke execution uses controlled inline caller context JSON.",
        "This smoke execution invokes `main(...)` directly with controlled arguments.",
        "This smoke execution captures stdout.",
        "This smoke execution parses stdout as deterministic JSON.",
        "This smoke execution verifies exit code `0`.",
        "This smoke execution verifies `cli_decision=CONTROLLED_CLI_DRY_RUN_ACCEPTED`.",
        "This smoke execution verifies `dry_run=True`.",
        "This smoke execution verifies `write_requested=False`.",
        "This smoke execution verifies `write_performed=False`.",
        "This smoke execution verifies `artifact_created_on_disk=False`.",
        "This smoke execution verifies bridge `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`.",
        "This smoke execution verifies no stderr output on accepted dry-run.",
        "This smoke execution verifies fail-closed behavior for invalid planner JSON.",
        "This smoke execution verifies fail-closed behavior for missing `--dry-run`.",
        "This smoke execution verifies fail-closed behavior for forbidden operational flags.",
    ],
)
def test_controlled_smoke_execution_scope_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The controlled smoke execution is accepted only because it does not write files.",
        "The controlled smoke execution is accepted only because it does not create directories.",
        "The controlled smoke execution is accepted only because it does not create artifacts on disk.",
        "The controlled smoke execution is accepted only because it does not read files.",
        "The controlled smoke execution is accepted only because it does not read real media.",
        "The controlled smoke execution is accepted only because it does not scan folders.",
        "The controlled smoke execution is accepted only because it does not execute ffprobe.",
        "The controlled smoke execution is accepted only because it does not execute FFmpeg.",
        "The controlled smoke execution is accepted only because it does not execute external processes.",
        "The controlled smoke execution is accepted only because it does not access networks.",
        "The controlled smoke execution is accepted only because it uses inline controlled arguments.",
        "The controlled smoke execution is accepted only because it emits JSON to stdout.",
    ],
)
def test_controlled_smoke_boundaries_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "accepted dry-run exits with a non-zero code.",
        "accepted dry-run writes to stderr.",
        "accepted dry-run emits non-JSON stdout.",
        "accepted dry-run omits the phase.",
        "accepted dry-run omits the functional result.",
        "accepted dry-run omits the next safe phase.",
        "accepted dry-run omits the CLI decision.",
        "accepted dry-run omits bridge result.",
        "accepted dry-run claims write_requested true.",
        "accepted dry-run claims write_performed true.",
        "accepted dry-run claims artifact_created_on_disk true.",
        "accepted dry-run claims a bridge decision other than CONTROLLED_DRY_RUN_ACCEPTED.",
        "invalid planner JSON fails open.",
        "missing `--dry-run` fails open.",
        "forbidden operational flags fail open.",
        "the CLI source exposes write options.",
        "the CLI source exposes output file options.",
        "the CLI source contains file write markers.",
        "the CLI source contains directory creation markers.",
        "the CLI source contains network markers.",
        "the CLI source contains external process markers.",
    ],
)
def test_smoke_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This smoke execution does not authorize write-enabled export.",
        "This smoke execution does not authorize directory creation.",
        "This smoke execution does not authorize artifact creation on disk.",
        "This smoke execution does not authorize real file writing.",
        "This smoke execution does not authorize media scanning.",
        "This smoke execution does not authorize real media decoding.",
        "This smoke execution does not authorize ffprobe execution.",
        "This smoke execution does not authorize FFmpeg execution.",
        "This smoke execution does not authorize external process execution.",
        "This smoke execution does not authorize audio extraction.",
        "This smoke execution does not authorize sync.",
        "This smoke execution does not authorize transcription.",
        "This smoke execution does not authorize subtitle generation.",
        "This smoke execution does not authorize timeline export.",
        "This smoke execution does not authorize network access.",
        "This smoke execution does not authorize SaaS integration.",
        "This smoke execution does not authorize database changes.",
        "This smoke execution does not authorize backend changes.",
        "This smoke execution does not authorize frontend changes.",
        "This smoke execution does not authorize installer work.",
        "This smoke execution does not authorize public demo work.",
        "This smoke execution does not authorize client-facing demo work.",
        "This smoke execution does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_controlled_smoke_execution_accepts_valid_inline_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(_valid_smoke_argv())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["phase"] == cli.PHASE
    assert payload["functional_result"] == cli.FUNCTIONAL_RESULT
    assert payload["next_safe_phase"] == cli.NEXT_SAFE_PHASE
    assert payload["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"
    assert payload["dry_run"] is True
    assert payload["write_requested"] is False
    assert payload["write_performed"] is False
    assert payload["artifact_created_on_disk"] is False
    assert payload["bridge_result"]["exporter_decision"] == "CONTROLLED_DRY_RUN_ACCEPTED"
    assert payload["bridge_result"]["dry_run"] is True
    assert payload["bridge_result"]["write_requested"] is False
    assert payload["bridge_result"]["write_performed"] is False
    assert payload["bridge_result"]["artifact_created_on_disk"] is False
    assert "No file was written" in payload["human_visible_summary"]


@pytest.mark.parametrize(
    "argv",
    [
        [
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "{}",
        ],
        [
            "--dry-run",
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "not-json",
        ],
        [
            "--write",
            "--dry-run",
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "{}",
        ],
    ],
)
def test_controlled_smoke_execution_fails_closed_for_invalid_inputs(
    argv: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(argv)

    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err


def test_controlled_smoke_execution_decision_is_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled CLI dry-run smoke execution is accepted." in doc
    assert "The controlled CLI dry-run can execute with inline controlled values." in doc
    assert "The controlled CLI dry-run emits deterministic JSON stdout." in doc
    assert "The controlled CLI dry-run fails closed for invalid inputs." in doc
    assert "The controlled CLI dry-run remains restricted to dry-run-only behavior." in doc
    assert "The project is ready for a future controlled smoke execution QA gate." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc


def test_next_allowed_step_is_qa_gate_only() -> None:
    doc = _read(DOC_PATH)

    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc


def test_cli_source_has_no_forbidden_runtime_markers() -> None:
    source = _read(CLI_MODULE_PATH)

    forbidden_markers = [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        "open(",
        "Popen",
        "socket",
        "requests",
        "urllib",
        "http.client",
    ]

    for marker in forbidden_markers:
        assert marker not in source

    assert "sub" + "process" not in source


def test_cli_parser_still_exposes_only_safe_options() -> None:
    parser = cli.build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert "--dry-run" in option_strings
    assert "--visible-report-text" in option_strings
    assert "--planner-result-json" in option_strings
    assert "--caller-context-json" in option_strings

    for forbidden_option in {
        "--write",
        "--output",
        "--output-path",
        "--create-dir",
        "--mkdir",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
        "--production",
    }:
        assert forbidden_option not in option_strings


def test_bridge_safety_contract_remains_visible() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    required_markers = [
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_performed": False',
        '"artifact_created_on_disk": False',
        "Only dry-run mode is supported",
        "write_requested must remain false",
    ]

    for marker in required_markers:
        assert marker in source
