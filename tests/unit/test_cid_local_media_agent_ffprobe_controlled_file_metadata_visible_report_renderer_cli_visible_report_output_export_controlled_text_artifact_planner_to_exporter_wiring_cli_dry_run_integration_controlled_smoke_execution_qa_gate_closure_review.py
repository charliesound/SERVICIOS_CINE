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
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate.py"
)

SMOKE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_v1.md"
)

SMOKE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution.py"
)

CLI_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_SMOKE_EXECUTION_"
    "QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_CLI_DRY_RUN_NEXT_SCOPE"
)

PREVIOUS_COMMIT = "695cf41cd52d9c0b4f5f61b541c2efb8365c587c"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.NEXT_SCOPE.PLANNING.V1"
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
        SMOKE_DOC_PATH,
        SMOKE_TEST_PATH,
        CLI_MODULE_PATH,
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
        "This closure review validates that the controlled CLI dry-run smoke execution QA gate can be closed.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_closure_review_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_closure_review.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target smoke execution QA gate test passed with 147 checks.",
        "smoke execution test passed with 128 checks.",
        "implementation QA closure review test passed with 113 checks.",
        "implementation test passed with 41 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "new CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target smoke execution QA gate short tag absent locally before tagging.",
        "target smoke execution QA gate short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target QA gate test passed with 147 checks.",
        "final smoke execution test passed with 128 checks.",
        "final implementation QA closure review test passed with 113 checks.",
        "final implementation test passed with 41 checks.",
        "final new CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the controlled CLI dry-run smoke execution is accepted.",
        "the controlled CLI dry-run smoke execution remains restricted to inline controlled values.",
        "the controlled CLI dry-run smoke execution remains restricted to stdout JSON output.",
        "the controlled CLI dry-run smoke execution remains restricted to dry-run-only behavior.",
        "the controlled CLI dry-run smoke execution remains accepted only because no file, media, process, network, SaaS, database, backend, frontend, installer, client demo, public demo, or production behavior was used.",
        "the controlled CLI dry-run executed through the Python entrypoint.",
        "the execution used only inline controlled arguments.",
        "the execution used controlled visible report text.",
        "the execution used controlled planner result JSON.",
        "the execution used controlled caller context JSON.",
        "the execution captured stdout.",
        "the execution parsed stdout as JSON.",
        "the execution verified exit code `0`.",
        "the execution verified no stderr on accepted dry-run.",
        "the execution verified `cli_decision=CONTROLLED_CLI_DRY_RUN_ACCEPTED`.",
        "the execution verified `dry_run=True`.",
        "the execution verified `write_requested=False`.",
        "the execution verified `write_performed=False`.",
        "the execution verified `artifact_created_on_disk=False`.",
        "the execution verified bridge `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`.",
        "the execution verified fail-closed behavior for invalid planner JSON.",
        "the execution verified fail-closed behavior for missing `--dry-run`.",
        "the execution verified fail-closed behavior for forbidden operational flags.",
        "the execution verified the CLI parser exposes only safe options.",
        "the execution verified the CLI source has no file write markers.",
        "the execution verified the CLI source has no directory creation markers.",
        "the execution verified the CLI source has no network markers.",
        "the execution verified the CLI source has no external process markers.",
    ],
)
def test_closure_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The controlled smoke execution QA gate is closed only for controlled dry-run smoke behavior.",
        "The controlled smoke execution QA gate is closed only for inline controlled arguments.",
        "The controlled smoke execution QA gate is closed only for deterministic stdout JSON output.",
        "The controlled smoke execution QA gate is closed only for no-stderr accepted dry-run behavior.",
        "The controlled smoke execution QA gate is closed only for fail-closed invalid input behavior.",
        "The controlled smoke execution QA gate is closed only because all write and artifact flags remain false.",
        "The controlled smoke execution QA gate is closed only because no filesystem write is performed.",
        "The controlled smoke execution QA gate is closed only because no directory creation is performed.",
        "The controlled smoke execution QA gate is closed only because no artifact is created on disk.",
        "The controlled smoke execution QA gate is closed only because no media, external process, network, SaaS, database, backend, frontend, installer, client demo, public demo, or production behavior is used.",
    ],
)
def test_accepted_execution_boundary_is_recorded(required_text: str) -> None:
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


def test_closure_decision_allows_only_next_scope_planning() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled CLI dry-run smoke execution QA gate is accepted and closed." in doc
    assert "The controlled CLI dry-run smoke execution remains accepted." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to inline controlled values." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to deterministic stdout JSON output." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to dry-run-only behavior." in doc
    assert "The controlled CLI dry-run smoke execution remains accepted only because no file, media, external process, network, SaaS, database, backend, frontend, installer, client demo, public demo, or production behavior was used." in doc
    assert "The project is ready for a future controlled CLI dry-run next-scope planning phase." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only unless an explicit implementation gate is created and closed first." in doc


def test_qa_gate_doc_remains_conservative() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "This QA gate does not authorize write-enabled export." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to inline controlled values." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to stdout JSON output." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to dry-run-only behavior." in source
    assert "The project is not ready for write-enabled export behavior." in source
    assert "The project is not ready for artifact creation on disk." in source


def test_smoke_execution_test_remains_inline_and_controlled() -> None:
    source = _read(SMOKE_TEST_PATH)

    assert "exit_code = cli.main(_valid_smoke_argv())" in source
    assert "captured = capsys.readouterr()" in source
    assert "payload = json.loads(captured.out)" in source
    assert 'payload["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"' in source
    assert 'payload["write_requested"] is False' in source
    assert 'payload["write_performed"] is False' in source
    assert 'payload["artifact_created_on_disk"] is False' in source


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
