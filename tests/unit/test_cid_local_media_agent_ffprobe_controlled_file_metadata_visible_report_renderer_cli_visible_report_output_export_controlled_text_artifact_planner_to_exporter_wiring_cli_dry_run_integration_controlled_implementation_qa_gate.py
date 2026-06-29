from __future__ import annotations

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
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate.py"
)

IMPLEMENTATION_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

IMPLEMENTATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation.py"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_IMPLEMENTATION_"
    "QA_GATE_PASS_READY_FOR_CLOSURE_REVIEW"
)

PREVIOUS_COMMIT = "10312dcad05382a1be910bb1dc9b14324c0896ab"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [IMPLEMENTATION_MODULE_PATH, IMPLEMENTATION_TEST_PATH, BRIDGE_MODULE_PATH],
)
def test_artifacts_under_qa_exist(path: Path) -> None:
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
        "This is a doc/test-only QA gate.",
        "This QA gate validates the controlled CLI dry-run integration implementation.",
        "This QA gate does not add implementation code.",
        "This QA gate does not modify CLI argument parsing.",
        "This QA gate does not modify command routing.",
        "This QA gate does not modify the controlled dry-run bridge.",
        "This QA gate does not authorize write-enabled behavior.",
    ],
)
def test_qa_gate_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run controlled implementation test passed with 41 checks.",
        "previous implementation readiness QA closure review test passed with 107 checks.",
        "previous implementation readiness QA gate test passed with 160 checks.",
        "previous controlled dry-run bridge implementation test passed with 40 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "staged new CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target controlled implementation short tag absent locally before tagging.",
        "target controlled implementation short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target test passed with 41 checks.",
        "final new CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the implementation is isolated in a new CLI module.",
        "the implementation does not modify the existing renderer CLI with output writing behavior.",
        "the implementation calls the existing controlled dry-run bridge.",
        "the implementation requires `--dry-run`.",
        "the implementation accepts controlled visible report text as an argument.",
        "the implementation accepts controlled planner result JSON as an argument.",
        "the implementation accepts optional caller context JSON as an argument.",
        "the implementation emits deterministic JSON to stdout.",
        "the implementation fails closed for controlled errors.",
        "the implementation preserves `dry_run=True`.",
        "the implementation preserves `write_requested=False`.",
        "the implementation preserves `write_performed=False`.",
        "the implementation preserves `artifact_created_on_disk=False`.",
        "the implementation preserves `CONTROLLED_DRY_RUN_ACCEPTED`.",
        "the implementation preserves the bridge safety contract.",
        "the implementation does not expose write or output file options.",
        "the implementation rejects forbidden operational flags.",
        "the implementation does not read files.",
        "the implementation does not write files.",
        "the implementation does not create directories.",
        "the implementation does not create artifacts on disk.",
        "the implementation does not execute ffprobe.",
        "the implementation does not execute FFmpeg.",
        "the implementation does not execute external processes.",
        "the implementation does not scan media folders.",
        "the implementation does not use real media.",
        "the implementation does not access networks.",
        "the implementation does not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
    ],
)
def test_qa_acceptance_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The implementation is accepted only as a controlled CLI dry-run integration.",
        "The implementation is accepted only for in-memory argument-driven dry-run evaluation.",
        "The implementation is accepted only for deterministic JSON stdout output.",
        "The implementation is accepted only because no file artifact is created.",
        "The implementation is accepted only because no filesystem write is performed.",
        "The implementation is accepted only because no directory creation is performed.",
        "The implementation is accepted only because no external media/process/network execution is performed.",
        "The implementation is accepted only because all write and artifact flags remain false.",
    ],
)
def test_implementation_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "modifies the existing renderer CLI write path.",
        "exposes `--write`.",
        "exposes `--output`.",
        "exposes `--output-path`.",
        "exposes `--create-dir`.",
        "exposes `--mkdir`.",
        "accepts execution without `--dry-run`.",
        "writes files.",
        "creates directories.",
        "creates artifacts on disk.",
        "reads media files.",
        "scans arbitrary folders.",
        "executes ffprobe.",
        "executes FFmpeg.",
        "executes external processes.",
        "accesses networks.",
        "touches SaaS systems.",
        "touches database systems.",
        "touches backend code.",
        "touches frontend code.",
        "touches installer code.",
        "enables client demo behavior.",
        "enables public demo behavior.",
        "enables production behavior.",
        "fails open on invalid planner JSON.",
        "fails open on mismatched content hash.",
        "fails open on unsafe planner result fields.",
        "omits deterministic JSON stdout behavior.",
        "omits controlled failure behavior.",
    ],
)
def test_qa_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize write-enabled export.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize artifact creation on disk.",
        "This QA gate does not authorize real file writing.",
        "This QA gate does not authorize media scanning.",
        "This QA gate does not authorize real media decoding.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize external process execution.",
        "This QA gate does not authorize audio extraction.",
        "This QA gate does not authorize sync.",
        "This QA gate does not authorize transcription.",
        "This QA gate does not authorize subtitle generation.",
        "This QA gate does not authorize timeline export.",
        "This QA gate does not authorize network access.",
        "This QA gate does not authorize SaaS integration.",
        "This QA gate does not authorize database changes.",
        "This QA gate does not authorize backend changes.",
        "This QA gate does not authorize frontend changes.",
        "This QA gate does not authorize installer work.",
        "This QA gate does not authorize public demo work.",
        "This QA gate does not authorize client-facing demo work.",
        "This QA gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_decision_allows_only_closure_review_next() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled CLI dry-run integration implementation is accepted." in doc
    assert "The implementation remains restricted to dry-run-only behavior." in doc
    assert "The implementation remains restricted to deterministic stdout JSON output." in doc
    assert "The implementation remains restricted to the existing controlled dry-run bridge." in doc
    assert "The project is ready for a future doc/test-only controlled implementation QA gate closure review." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_controlled_implementation_module_declares_expected_markers() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    required_markers = [
        "CONTROLLED_CLI_DRY_RUN_ACCEPTED",
        "PASS_READY_FOR_QA_GATE",
        "plan_controlled_text_artifact_exporter_dry_run_from_planner_result",
        "write_requested=False",
        "dry_run=True",
        "json.dumps(result, sort_keys=True, indent=2)",
        "--dry-run is required",
        "controlled dry-run CLI failed closed",
    ]

    for marker in required_markers:
        assert marker in source


def test_controlled_implementation_module_has_no_forbidden_runtime_markers() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

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


def test_controlled_implementation_parser_exposes_only_safe_options() -> None:
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


def test_controlled_implementation_main_still_fails_closed_without_dry_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(
        [
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "{}",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err
    assert "--dry-run is required" in captured.err


def test_controlled_implementation_rejects_invalid_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "not-json",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err


@pytest.mark.parametrize(
    "forbidden_flag",
    [
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
    ],
)
def test_controlled_implementation_rejects_forbidden_flags(
    forbidden_flag: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main(
        [
            forbidden_flag,
            "--dry-run",
            "--visible-report-text",
            "controlled visible report",
            "--planner-result-json",
            "{}",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err
    assert "unsupported flag" in captured.err


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
