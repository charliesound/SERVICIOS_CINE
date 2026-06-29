from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as cli,
)


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
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
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_IMPLEMENTATION_"
    "QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_SMOKE_EXECUTION"
)

PREVIOUS_COMMIT = "2f9a76d9a83db405a6992af68c50de2deb1f5196"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-controlled-impl-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        QA_GATE_DOC_PATH,
        QA_GATE_TEST_PATH,
        IMPLEMENTATION_MODULE_PATH,
        IMPLEMENTATION_TEST_PATH,
        BRIDGE_MODULE_PATH,
    ],
)
def test_artifacts_under_closure_review_exist(path: Path) -> None:
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
        "This is a doc/test-only closure review.",
        "This closure review validates that the controlled CLI dry-run integration implementation QA gate can be closed.",
        "This closure review does not add implementation code.",
        "This closure review does not modify CLI argument parsing.",
        "This closure review does not modify command routing.",
        "This closure review does not modify the controlled dry-run bridge.",
        "This closure review does not authorize write-enabled behavior.",
    ],
)
def test_closure_review_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_closure_review_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_implementation_qa_gate_closure_review.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run controlled implementation QA gate test passed with 145 checks.",
        "controlled implementation test passed with 41 checks.",
        "readiness QA closure review test passed with 107 checks.",
        "bridge implementation test passed with 40 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "new CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target controlled implementation QA gate short tag absent locally before tagging.",
        "target controlled implementation QA gate short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target QA gate test passed with 145 checks.",
        "final controlled implementation test passed with 41 checks.",
        "final new CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the controlled CLI dry-run integration implementation is accepted.",
        "the implementation remains restricted to dry-run-only behavior.",
        "the implementation remains restricted to deterministic stdout JSON output.",
        "the implementation remains restricted to the existing controlled dry-run bridge.",
        "the implementation is isolated in a new CLI module.",
        "the implementation does not modify the existing renderer CLI with output writing behavior.",
        "the implementation requires `--dry-run`.",
        "the implementation preserves `dry_run=True`.",
        "the implementation preserves `write_requested=False`.",
        "the implementation preserves `write_performed=False`.",
        "the implementation preserves `artifact_created_on_disk=False`.",
        "the implementation preserves `CONTROLLED_DRY_RUN_ACCEPTED`.",
        "the implementation fails closed for controlled errors.",
        "the implementation rejects forbidden operational flags.",
        "the implementation does not expose write or output file options.",
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
def test_closure_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future controlled smoke execution may be considered after this closure review is closed.",
        "The next controlled smoke execution must be limited to the CLI dry-run integration.",
        "The next controlled smoke execution must use controlled inline argument values.",
        "The next controlled smoke execution must use controlled planner result JSON.",
        "The next controlled smoke execution must print deterministic JSON to stdout.",
        "The next controlled smoke execution must not write files.",
        "The next controlled smoke execution must not create directories.",
        "The next controlled smoke execution must not create artifacts on disk.",
        "The next controlled smoke execution must not read real media.",
        "The next controlled smoke execution must not scan folders.",
        "The next controlled smoke execution must not execute ffprobe.",
        "The next controlled smoke execution must not execute FFmpeg.",
        "The next controlled smoke execution must not execute external processes.",
        "The next controlled smoke execution must not access networks.",
        "The next controlled smoke execution must not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
    ],
)
def test_controlled_smoke_execution_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize write-enabled export.",
        "This closure review does not authorize directory creation.",
        "This closure review does not authorize artifact creation on disk.",
        "This closure review does not authorize real file writing.",
        "This closure review does not authorize media scanning.",
        "This closure review does not authorize real media decoding.",
        "This closure review does not authorize ffprobe execution.",
        "This closure review does not authorize FFmpeg execution.",
        "This closure review does not authorize external process execution.",
        "This closure review does not authorize audio extraction.",
        "This closure review does not authorize sync.",
        "This closure review does not authorize transcription.",
        "This closure review does not authorize subtitle generation.",
        "This closure review does not authorize timeline export.",
        "This closure review does not authorize network access.",
        "This closure review does not authorize SaaS integration.",
        "This closure review does not authorize database changes.",
        "This closure review does not authorize backend changes.",
        "This closure review does not authorize frontend changes.",
        "This closure review does not authorize installer work.",
        "This closure review does not authorize public demo work.",
        "This closure review does not authorize client-facing demo work.",
        "This closure review does not authorize production use.",
    ],
)
def test_remaining_prohibitions_are_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_closure_decision_allows_only_controlled_smoke_execution_next() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled CLI dry-run integration implementation QA gate is accepted and closed." in doc
    assert "The controlled CLI dry-run implementation remains accepted." in doc
    assert "The implementation remains restricted to dry-run-only behavior." in doc
    assert "The implementation remains restricted to deterministic stdout JSON output." in doc
    assert "The implementation remains restricted to the existing controlled dry-run bridge." in doc
    assert "The project is ready for a future controlled CLI dry-run smoke execution phase." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step may execute the controlled CLI dry-run only with inline controlled values and stdout output." in doc


def test_qa_gate_doc_remains_conservative() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "This QA gate does not authorize write-enabled export." in source
    assert "The implementation remains restricted to dry-run-only behavior." in source
    assert "The implementation remains restricted to deterministic stdout JSON output." in source
    assert "The implementation remains restricted to the existing controlled dry-run bridge." in source
    assert "The project is not ready for write-enabled export behavior." in source
    assert "The project is not ready for artifact creation on disk." in source


def test_controlled_implementation_module_still_has_safe_cli_shape() -> None:
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


def test_controlled_implementation_still_fails_closed_without_dry_run(
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
