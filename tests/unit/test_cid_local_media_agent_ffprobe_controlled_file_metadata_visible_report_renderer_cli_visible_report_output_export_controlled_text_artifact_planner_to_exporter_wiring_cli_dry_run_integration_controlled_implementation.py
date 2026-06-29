from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as cli,
)


ROOT = Path(__file__).resolve().parents[2]

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
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_IMPLEMENTATION_"
    "PASS_READY_FOR_QA_GATE"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _visible_report_text() -> str:
    return "# Controlled Visible Report\n\nNo file was written.\n"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _valid_planner_result() -> dict[str, object]:
    text = _visible_report_text()
    return {
        "controlled_export_root": "controlled_export_root",
        "suggested_filename": "controlled_visible_report.controlled_visible_report.txt",
        "planned_artifact_path": (
            "controlled_export_root/controlled_visible_report.controlled_visible_report.txt"
        ),
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


def _valid_argv() -> list[str]:
    return [
        "--dry-run",
        "--visible-report-text",
        _visible_report_text(),
        "--planner-result-json",
        json.dumps(_valid_planner_result(), sort_keys=True),
        "--caller-context-json",
        json.dumps({"operator": "controlled_test"}, sort_keys=True),
    ]


def test_cli_module_exists() -> None:
    assert CLI_MODULE_PATH.is_file()


def test_bridge_module_exists() -> None:
    assert BRIDGE_MODULE_PATH.is_file()


def test_cli_declares_phase_result_and_next_phase() -> None:
    assert cli.PHASE == PHASE_ID
    assert cli.FUNCTIONAL_RESULT == RESULT_ID
    assert cli.NEXT_SAFE_PHASE == NEXT_PHASE_ID


def test_run_controlled_cli_dry_run_returns_structured_result() -> None:
    result = cli.run_controlled_cli_dry_run(
        visible_report_text=_visible_report_text(),
        planner_result=_valid_planner_result(),
        caller_context={"operator": "controlled_test"},
    )

    assert result["phase"] == PHASE_ID
    assert result["functional_result"] == RESULT_ID
    assert result["next_safe_phase"] == NEXT_PHASE_ID
    assert result["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"
    assert result["dry_run"] is True
    assert result["write_requested"] is False
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["bridge_result"]["dry_run"] is True
    assert result["bridge_result"]["write_requested"] is False
    assert result["bridge_result"]["write_performed"] is False
    assert result["bridge_result"]["artifact_created_on_disk"] is False
    assert result["bridge_result"]["exporter_decision"] == "CONTROLLED_DRY_RUN_ACCEPTED"
    assert "No file was written" in result["human_visible_summary"]


def test_main_accepts_controlled_dry_run_and_prints_json(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = cli.main(_valid_argv())

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert captured.err == ""
    assert payload["phase"] == PHASE_ID
    assert payload["functional_result"] == RESULT_ID
    assert payload["cli_decision"] == "CONTROLLED_CLI_DRY_RUN_ACCEPTED"
    assert payload["dry_run"] is True
    assert payload["write_requested"] is False
    assert payload["write_performed"] is False
    assert payload["artifact_created_on_disk"] is False
    assert payload["bridge_result"]["exporter_decision"] == "CONTROLLED_DRY_RUN_ACCEPTED"
    assert "No file was written" in payload["human_visible_summary"]


def test_main_requires_dry_run_flag(capsys: pytest.CaptureFixture[str]) -> None:
    argv = _valid_argv()
    argv.remove("--dry-run")

    exit_code = cli.main(argv)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err
    assert "--dry-run is required" in captured.err


@pytest.mark.parametrize(
    "forbidden_flag",
    [
        "--write",
        "--write-output",
        "--output",
        "--output-path",
        "--create-dir",
        "--mkdir",
        "--scan",
        "--scanner",
        "--media",
        "--ffprobe",
        "--ffmpeg",
        "--" + "sub" + "process",
        "--network",
        "--upload",
        "--database",
        "--backend",
        "--frontend",
        "--installer",
        "--client-demo",
        "--public-demo",
        "--production",
    ],
)
def test_main_rejects_forbidden_flags(
    forbidden_flag: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = cli.main([forbidden_flag, *_valid_argv()])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err
    assert "unsupported flag" in captured.err


@pytest.mark.parametrize(
    "bad_json",
    ["", "not-json", "[]", "null", '"text"'],
)
def test_main_rejects_invalid_planner_result_json(
    bad_json: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    argv = [
        "--dry-run",
        "--visible-report-text",
        _visible_report_text(),
        "--planner-result-json",
        bad_json,
    ]

    exit_code = cli.main(argv)

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err


def test_main_rejects_mismatched_content_hash(capsys: pytest.CaptureFixture[str]) -> None:
    planner_result = _valid_planner_result()
    planner_result["content_sha256"] = "0" * 64

    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            _visible_report_text(),
            "--planner-result-json",
            json.dumps(planner_result, sort_keys=True),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err
    assert "content hash" in captured.err


@pytest.mark.parametrize(
    "mutated_field, mutated_value",
    [
        ("write_performed", True),
        ("artifact_created_on_disk", True),
        ("path_boundary", "unsafe"),
        ("safety_flags", {"file_write_performed": True}),
    ],
)
def test_main_rejects_unsafe_planner_result_fields(
    mutated_field: str,
    mutated_value: object,
    capsys: pytest.CaptureFixture[str],
) -> None:
    planner_result = _valid_planner_result()
    planner_result[mutated_field] = mutated_value

    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            _visible_report_text(),
            "--planner-result-json",
            json.dumps(planner_result, sort_keys=True),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.out == ""
    assert "failed closed" in captured.err


def test_cli_source_contains_no_disk_network_or_process_runtime_markers() -> None:
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


def test_cli_source_does_not_import_media_or_network_modules() -> None:
    source = _read(CLI_MODULE_PATH)

    blocked_imports = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import socket",
        "import requests",
        "import urllib",
        "import http.client",
    ]

    for blocked in blocked_imports:
        assert blocked not in source


def test_cli_does_not_expose_write_or_output_options() -> None:
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
    assert "--write" not in option_strings
    assert "--output" not in option_strings
    assert "--output-path" not in option_strings
    assert "--create-dir" not in option_strings
    assert "--mkdir" not in option_strings


def test_existing_bridge_safety_contract_remains_visible() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    required_markers = [
        "plan_controlled_text_artifact_exporter_dry_run_from_planner_result",
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_performed": False',
        '"artifact_created_on_disk": False',
        "Only dry-run mode is supported",
        "write_requested must remain false",
    ]

    for marker in required_markers:
        assert marker in source
