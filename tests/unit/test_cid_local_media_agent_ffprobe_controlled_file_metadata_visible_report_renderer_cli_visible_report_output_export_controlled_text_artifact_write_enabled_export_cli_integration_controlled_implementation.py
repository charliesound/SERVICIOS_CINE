from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as dry_run_cli,
)
from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli as cli,
)


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
)

AUTHORIZATION_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate_v1.md"
)

AUTHORIZATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate.py"
)

READINESS_V2_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.md"
)

CONTROLLED_PRIMITIVE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
)

DRY_RUN_CLI_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

DRY_RUN_BRIDGE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"

MODULE_NAME = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

AUTHORIZED_TEST = (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parser_option_strings() -> set[str]:
    parser = cli.build_parser()
    return {
        option
        for action in parser._actions
        for option in action.option_strings
    }


def test_authorized_runtime_module_exists() -> None:
    assert MODULE_PATH.is_file()


def test_authorized_implementation_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        AUTHORIZATION_DOC_PATH,
        AUTHORIZATION_TEST_PATH,
        READINESS_V2_DOC_PATH,
        CONTROLLED_PRIMITIVE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_required_prior_artifacts_exist(path: Path) -> None:
    assert path.is_file()


def test_module_identity_constants_match_authorization_gate() -> None:
    assert cli.PHASE_ID == PHASE_ID
    assert cli.CLI_CONTRACT_VERSION == "1.0"
    assert cli.COMMAND_NAME == COMMAND_NAME
    assert cli.MODULE_NAME == MODULE_NAME
    assert cli.DEFAULT_FILENAME == "controlled_visible_report.controlled.txt"
    assert cli.WRITE_AUTHORIZATION == "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
    assert cli.DRY_RUN_AUTHORIZATION == "CONTROLLED_DRY_RUN_ACCEPTED"


def test_authorization_gate_supports_this_controlled_implementation() -> None:
    doc = _read(AUTHORIZATION_DOC_PATH)

    assert "A later controlled implementation phase may be prepared." in doc
    assert "That later implementation phase may create exactly one new runtime module:" in doc
    assert MODULE_NAME in doc
    assert "That later implementation phase may create exactly one new implementation test file:" in doc
    assert AUTHORIZED_TEST in doc
    assert "That later implementation phase may import `export_controlled_visible_report_text_artifact` only from the accepted controlled write-enabled primitive." in doc
    assert "That later implementation phase may build an isolated parser only in the new isolated module." in doc
    assert COMMAND_NAME in doc
    assert PHASE_ID in doc
    assert "That next step may implement only the new isolated CLI module and its implementation test." in doc
    assert "That next step must not modify the current dry-run CLI." in doc
    assert "That next step must not modify the current dry-run bridge." in doc
    assert "That next step must not modify the accepted controlled write-enabled primitive." in doc


def test_parser_contains_only_allowed_option_strings() -> None:
    assert _parser_option_strings() == cli.ALLOWED_OPTION_STRINGS


@pytest.mark.parametrize(
    "option",
    [
        "--visible-report-text",
        "--controlled-output-root",
        "--write-authorization",
        "--result-json",
        "--dry-run",
        "-h",
        "--help",
    ],
)
def test_allowed_option_strings_are_present(option: str) -> None:
    assert option in _parser_option_strings()


@pytest.mark.parametrize(
    "forbidden_option",
    sorted(cli.FORBIDDEN_UNSAFE_ALIASES),
)
def test_forbidden_unsafe_aliases_are_rejected_by_parser(forbidden_option: str) -> None:
    with pytest.raises(SystemExit):
        cli.parse_args([forbidden_option])


@pytest.mark.parametrize(
    "unknown_option",
    [
        "--unknown",
        "--write",
        "--write-enabled",
        "--write-artifact",
        "--output-root",
        "--real-media",
        "--scanner",
        "--subprocess",
    ],
)
def test_unknown_arguments_are_rejected_by_parser(unknown_option: str) -> None:
    with pytest.raises(SystemExit):
        cli.parse_args([unknown_option])


@pytest.mark.parametrize(
    "unsafe_option",
    sorted(cli.FORBIDDEN_UNSAFE_ALIASES),
)
def test_execute_rejects_forbidden_unsafe_aliases_without_writing(
    unsafe_option: str,
    tmp_path: Path,
) -> None:
    result = cli.execute(
        [
            "--visible-report-text",
            "Unsafe alias rejection report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
            "--result-json",
            unsafe_option,
        ]
    )

    assert result["exit_code"] == 2
    assert result["verification_status"] == "REJECTED"
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "argument parsing failed" in result["errors"]
    assert not (tmp_path / cli.DEFAULT_FILENAME).exists()


def test_parse_args_uses_no_abbreviation() -> None:
    with pytest.raises(SystemExit):
        cli.parse_args(["--visible-report-te", "partial"])


def test_dry_run_returns_success_without_artifact_creation(tmp_path: Path) -> None:
    result = cli.execute(
        [
            "--dry-run",
            "--visible-report-text",
            "Dry-run report text",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    assert result["phase"] == PHASE_ID
    assert result["cli_contract_version"] == "1.0"
    assert result["command_name"] == COMMAND_NAME
    assert result["module_name"] == MODULE_NAME
    assert result["mode"] == "dry_run"
    assert result["dry_run_requested"] is True
    assert result["write_requested"] is False
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["verification_status"] == "DRY_RUN_ONLY"
    assert result["exit_code"] == 0
    assert result["result_json_requested"] is True
    assert not (tmp_path / cli.DEFAULT_FILENAME).exists()


def test_dry_run_does_not_call_controlled_write_even_with_dry_run_authorization(tmp_path: Path) -> None:
    result = cli.execute(
        [
            "--dry-run",
            "--visible-report-text",
            "Dry-run authorization report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.DRY_RUN_AUTHORIZATION,
        ]
    )

    assert result["dry_run_requested"] is True
    assert result["write_requested"] is False
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["verification_status"] == "DRY_RUN_ONLY"
    assert result["exit_code"] == 0
    assert not (tmp_path / cli.DEFAULT_FILENAME).exists()


def test_controlled_write_creates_exactly_one_fixture_owned_artifact(tmp_path: Path) -> None:
    report_text = "Controlled implementation visible report\n"

    result = cli.execute(
        [
            "--visible-report-text",
            report_text,
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    artifact_path = tmp_path / cli.DEFAULT_FILENAME

    assert result["phase"] == PHASE_ID
    assert result["cli_contract_version"] == "1.0"
    assert result["command_name"] == COMMAND_NAME
    assert result["module_name"] == MODULE_NAME
    assert result["mode"] == "controlled_write"
    assert result["dry_run_requested"] is False
    assert result["write_requested"] is True
    assert result["write_performed"] is True
    assert result["artifact_created_on_disk"] is True
    assert result["verification_status"] == "VERIFIED"
    assert result["exit_code"] == 0
    assert result["filename"] == cli.DEFAULT_FILENAME
    assert result["extension"] == ".txt"
    assert result["write_authorization"] == cli.WRITE_AUTHORIZATION
    assert result["bytes_intended"] == len(report_text.encode("utf-8"))
    assert result["bytes_written"] == len(report_text.encode("utf-8"))
    assert artifact_path.is_file()
    assert artifact_path.read_text(encoding="utf-8") == report_text
    assert sorted(path.name for path in tmp_path.iterdir()) == [cli.DEFAULT_FILENAME]


def test_controlled_write_result_preserves_safety_flags(tmp_path: Path) -> None:
    result = cli.execute(
        [
            "--visible-report-text",
            "Safety flag report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    flags = result["safety_flags"]

    assert flags["fixture_owned_output_root_required"] is True
    assert flags["single_artifact_only"] is True
    assert flags["directory_creation_performed"] is False
    assert flags["overwrite_performed"] is False
    assert flags["scanner_execution_performed"] is False
    assert flags["ffprobe_execution_performed"] is False
    assert flags["ffmpeg_execution_performed"] is False
    assert flags["external_process_execution_performed"] is False
    assert flags["network_access_performed"] is False
    assert flags["saas_or_database_access_performed"] is False
    assert flags["client_facing_or_production_usage_authorized"] is False


@pytest.mark.parametrize(
    ("argv", "expected_error"),
    [
        (
            [
                "--controlled-output-root",
                "tmp",
                "--write-authorization",
                cli.WRITE_AUTHORIZATION,
            ],
            "missing visible report text",
        ),
        (
            [
                "--visible-report-text",
                "",
                "--controlled-output-root",
                "tmp",
                "--write-authorization",
                cli.WRITE_AUTHORIZATION,
            ],
            "empty visible report text",
        ),
        (
            [
                "--visible-report-text",
                "report",
                "--write-authorization",
                cli.WRITE_AUTHORIZATION,
            ],
            "missing controlled output root",
        ),
        (
            [
                "--visible-report-text",
                "report",
                "--controlled-output-root",
                "tmp",
            ],
            "missing write authorization",
        ),
        (
            [
                "--visible-report-text",
                "report",
                "--controlled-output-root",
                "tmp",
                "--write-authorization",
                cli.DRY_RUN_AUTHORIZATION,
            ],
            "dry-run authorization is not valid for controlled write",
        ),
        (
            [
                "--visible-report-text",
                "report",
                "--controlled-output-root",
                "tmp",
                "--write-authorization",
                "UNKNOWN_AUTHORIZATION",
            ],
            "unknown write authorization",
        ),
    ],
)
def test_controlled_write_input_rejections(argv: list[str], expected_error: str) -> None:
    result = cli.execute(argv)

    assert result["mode"] == "controlled_write_rejected"
    assert result["write_requested"] is True
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["verification_status"] == "REJECTED"
    assert result["exit_code"] == 1
    assert expected_error in result["errors"]


def test_controlled_write_rejects_repository_root() -> None:
    result = cli.execute(
        [
            "--visible-report-text",
            "Repository root rejection report",
            "--controlled-output-root",
            str(ROOT),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    assert result["write_requested"] is True
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["verification_status"] != "VERIFIED"
    assert result["exit_code"] == 1
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_write_rejects_current_working_directory() -> None:
    result = cli.execute(
        [
            "--visible-report-text",
            "Current working directory rejection report",
            "--controlled-output-root",
            ".",
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["exit_code"] == 1
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_write_rejects_existing_artifact_without_overwrite(tmp_path: Path) -> None:
    first = cli.execute(
        [
            "--visible-report-text",
            "First report\n",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    second = cli.execute(
        [
            "--visible-report-text",
            "Second report\n",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    artifact_path = tmp_path / cli.DEFAULT_FILENAME

    assert first["exit_code"] == 0
    assert first["verification_status"] == "VERIFIED"
    assert second["exit_code"] == 1
    assert second["write_performed"] is False
    assert second["artifact_created_on_disk"] is False
    assert artifact_path.read_text(encoding="utf-8") == "First report\n"


def test_result_to_json_is_deterministic_and_parseable(tmp_path: Path) -> None:
    result = cli.execute(
        [
            "--dry-run",
            "--visible-report-text",
            "JSON report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    payload_a = cli.result_to_json(result)
    payload_b = cli.result_to_json(result)
    decoded = json.loads(payload_a)

    assert payload_a == payload_b
    assert decoded["phase"] == PHASE_ID
    assert decoded["command_name"] == COMMAND_NAME
    assert decoded["verification_status"] == "DRY_RUN_ONLY"
    assert decoded["exit_code"] == 0


def test_main_prints_json_only_when_result_json_requested(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            "Main JSON report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )

    captured = capsys.readouterr()
    decoded = json.loads(captured.out)

    assert exit_code == 0
    assert decoded["result_json_requested"] is True
    assert decoded["verification_status"] == "DRY_RUN_ONLY"
    assert captured.err == ""


def test_main_does_not_print_json_when_not_requested(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    exit_code = cli.main(
        [
            "--dry-run",
            "--visible-report-text",
            "Main silent report",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            cli.WRITE_AUTHORIZATION,
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""


def test_current_dry_run_cli_has_no_write_enabled_options() -> None:
    parser = dry_run_cli.build_parser()
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
        "--write-enabled",
        "--write-artifact",
        "--output",
        "--output-path",
        "--output-root",
        "--artifact-path",
        "--create-dir",
        "--mkdir",
        "--overwrite",
        "--force",
        "--production",
        "--client",
        "--public-demo",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
    }:
        assert forbidden_option not in option_strings


def test_current_dry_run_cli_does_not_import_isolated_write_enabled_cli() -> None:
    source = _read(DRY_RUN_CLI_PATH)

    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli" not in source
    assert "export_controlled_visible_report_text_artifact" not in source
    assert "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY" not in source


def test_current_dry_run_bridge_does_not_import_isolated_write_enabled_cli() -> None:
    source = _read(DRY_RUN_BRIDGE_PATH)

    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli" not in source
    assert "export_controlled_visible_report_text_artifact" not in source


def test_isolated_cli_source_does_not_perform_forbidden_runtime_actions_directly() -> None:
    source = _read(MODULE_PATH)

    for marker in [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "shutil",
        "Popen",
        "os.system",
        "import subprocess",
        "subprocess.",
        "socket.",
        "requests.",
        "urllib.",
        "http.client",
        "scanner_execution_performed = True",
        "ffprobe_execution_performed = True",
        "ffmpeg_execution_performed = True",
        "external_process_execution_performed = True",
        "network_access_performed = True",
        "saas_or_database_access_performed = True",
        "directory_creation_performed = True",
        "overwrite_performed = True",
    ]:
        assert marker not in source


def test_accepted_write_enabled_primitive_source_still_has_no_prohibited_runtime_integrations() -> None:
    source = _read(CONTROLLED_PRIMITIVE_PATH)

    for marker in [
        ".mkdir(",
        ".rmdir(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "shutil",
        "Popen",
        "os.system",
        "import subprocess",
        "subprocess.",
        "socket.",
        "requests.",
        "urllib.",
        "http.client",
        "scanner_execution_performed = True",
        "ffprobe_execution_performed = True",
        "ffmpeg_execution_performed = True",
        "external_process_execution_performed = True",
        "network_access_performed = True",
        "saas_or_database_access_performed = True",
        "directory_creation_performed = True",
        "overwrite_performed = True",
    ]:
        assert marker not in source
