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
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
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
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_SMOKE_EXECUTION_"
    "QA_GATE_PASS_READY_FOR_CLOSURE_REVIEW"
)

PREVIOUS_COMMIT = "3a4645c61da065062fa66e22296d655a85d84060"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.SMOKE.EXECUTION.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize("path", [SMOKE_DOC_PATH, SMOKE_TEST_PATH, CLI_MODULE_PATH, BRIDGE_MODULE_PATH])
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
        "This QA gate validates the controlled CLI dry-run smoke execution.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target controlled smoke execution test passed with 128 checks.",
        "controlled implementation QA closure review test passed with 113 checks.",
        "controlled implementation QA gate test passed with 145 checks.",
        "controlled implementation test passed with 41 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "new CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target controlled smoke execution short tag absent locally before tagging.",
        "target controlled smoke execution short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target smoke execution test passed with 128 checks.",
        "final implementation QA closure review test passed with 113 checks.",
        "final implementation QA gate test passed with 145 checks.",
        "final implementation test passed with 41 checks.",
        "final new CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
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
        "the execution did not write files.",
        "the execution did not create directories.",
        "the execution did not create artifacts on disk.",
        "the execution did not read files.",
        "the execution did not read real media.",
        "the execution did not scan folders.",
        "the execution did not execute ffprobe.",
        "the execution did not execute FFmpeg.",
        "the execution did not execute external processes.",
        "the execution did not access networks.",
        "the execution did not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
    ],
)
def test_qa_acceptance_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The controlled smoke execution is accepted only as a controlled dry-run smoke.",
        "The controlled smoke execution is accepted only with inline controlled arguments.",
        "The controlled smoke execution is accepted only with deterministic stdout JSON output.",
        "The controlled smoke execution is accepted only with no stderr on accepted dry-run.",
        "The controlled smoke execution is accepted only with fail-closed behavior for invalid inputs.",
        "The controlled smoke execution is accepted only because all write and artifact flags remain false.",
        "The controlled smoke execution is accepted only because no filesystem write is performed.",
        "The controlled smoke execution is accepted only because no directory creation is performed.",
        "The controlled smoke execution is accepted only because no artifact is created on disk.",
        "The controlled smoke execution is accepted only because no media, process, network, SaaS, database, backend, frontend, installer, client demo, public demo, or production behavior is used.",
    ],
)
def test_qa_acceptance_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exits non-zero on accepted dry-run.",
        "writes to stderr on accepted dry-run.",
        "emits non-JSON stdout on accepted dry-run.",
        "omits the phase.",
        "omits the functional result.",
        "omits the next safe phase.",
        "omits the CLI decision.",
        "omits bridge result.",
        "claims `write_requested=True`.",
        "claims `write_performed=True`.",
        "claims `artifact_created_on_disk=True`.",
        "claims a bridge decision other than `CONTROLLED_DRY_RUN_ACCEPTED`.",
        "fails open on invalid planner JSON.",
        "fails open without `--dry-run`.",
        "fails open on forbidden operational flags.",
        "exposes write options.",
        "exposes output file options.",
        "contains file write markers.",
        "contains directory creation markers.",
        "contains network markers.",
        "contains external process markers.",
        "reads files.",
        "reads real media.",
        "scans folders.",
        "executes ffprobe.",
        "executes FFmpeg.",
        "executes external processes.",
        "accesses networks.",
        "touches SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
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

    assert "The controlled CLI dry-run smoke execution is accepted." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to inline controlled values." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to stdout JSON output." in doc
    assert "The controlled CLI dry-run smoke execution remains restricted to dry-run-only behavior." in doc
    assert "The controlled CLI dry-run smoke execution remains accepted only because no file, media, process, network, SaaS, database, backend, frontend, installer, client demo, public demo, or production behavior was used." in doc
    assert "The project is ready for a future controlled smoke execution QA gate closure review." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_smoke_execution_doc_remains_conservative() -> None:
    smoke_doc = _read(SMOKE_DOC_PATH)

    assert "This smoke execution does not write files." in smoke_doc
    assert "This smoke execution does not create directories." in smoke_doc
    assert "This smoke execution does not create artifacts on disk." in smoke_doc
    assert "This smoke execution does not use real media." in smoke_doc
    assert "This smoke execution does not execute ffprobe." in smoke_doc
    assert "This smoke execution does not execute FFmpeg." in smoke_doc
    assert "This smoke execution does not execute external processes." in smoke_doc
    assert "This smoke execution does not access networks." in smoke_doc
    assert "The controlled CLI dry-run smoke execution is accepted." in smoke_doc
    assert "The project is not ready for write-enabled export behavior." in smoke_doc
    assert "The project is not ready for artifact creation on disk." in smoke_doc


def test_smoke_execution_test_contains_real_cli_invocation() -> None:
    smoke_test = _read(SMOKE_TEST_PATH)

    assert "exit_code = cli.main(_valid_smoke_argv())" in smoke_test
    assert "captured = capsys.readouterr()" in smoke_test
    assert "payload = json.loads(captured.out)" in smoke_test
    assert 'payload["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"' in smoke_test
    assert 'payload["dry_run"] is True' in smoke_test
    assert 'payload["write_requested"] is False' in smoke_test
    assert 'payload["write_performed"] is False' in smoke_test
    assert 'payload["artifact_created_on_disk"] is False' in smoke_test


def test_cli_module_still_emits_controlled_json_for_valid_inline_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    visible_report_text = "# QA Gate Inline Smoke\n\nNo file was written.\n"
    planner_result = {
        "controlled_export_root": "controlled_export_root",
        "suggested_filename": "qa_gate_inline_smoke.controlled_visible_report.txt",
        "planned_artifact_path": "controlled_export_root/qa_gate_inline_smoke.controlled_visible_report.txt",
        "artifact_format": "controlled_visible_report_text",
        "content_sha256": __import__("hashlib").sha256(visible_report_text.encode("utf-8")).hexdigest(),
        "write_performed": False,
        "artifact_created_on_disk": False,
        "path_boundary": "safe",
        "safety_flags": {
            "real_media_access_performed": False,
            "scanner_execution_performed": False,
            "ffprobe_execution_performed": False,
            "ffmpeg_execution_performed": False,
            "external_process_execution_performed": False,
            "network_access_performed": False,
            "saas_or_database_access_performed": False,
            "file_write_performed": False,
            "directory_creation_performed": False,
            "artifact_created_on_disk": False,
        },
    }

    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            visible_report_text,
            "--planner-result-json",
            json.dumps(planner_result, sort_keys=True),
            "--caller-context-json",
            json.dumps({"qa_gate": "inline_controlled_smoke"}, sort_keys=True),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"
    assert payload["dry_run"] is True
    assert payload["write_requested"] is False
    assert payload["write_performed"] is False
    assert payload["artifact_created_on_disk"] is False
    assert payload["bridge_result"]["exporter_decision"] == "CONTROLLED_DRY_RUN_ACCEPTED"


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
