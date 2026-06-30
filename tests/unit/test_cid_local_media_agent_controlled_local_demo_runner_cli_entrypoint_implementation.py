from __future__ import annotations

import json
import shutil
import tomllib
from pathlib import Path

from scripts.local_media_agent import (
    cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner as runner,
)


REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
RUNNER_PATH = REPO_ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"
READINESS_DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_cli_entrypoint_readiness_gate_v1.md"
READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_controlled_local_demo_runner_cli_entrypoint_readiness_gate.py"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

CURRENT_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
RUNNER_COMMAND = "cid-local-media-agent-controlled-local-demo-runner"

CURRENT_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
RUNNER_TARGET = "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main"

EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_CLI_ENTRYPOINT_IMPLEMENTATION_V1_CLOSED"
EXPECTED_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def test_runner_cli_entrypoint_implementation_pyproject_has_exactly_two_scripts() -> None:
    data = _load_pyproject()

    assert data["project"]["scripts"] == {
        CURRENT_COMMAND: CURRENT_TARGET,
        RUNNER_COMMAND: RUNNER_TARGET,
    }


def test_runner_cli_entrypoint_implementation_preserves_current_command_installation() -> None:
    command_path = shutil.which(CURRENT_COMMAND)

    assert command_path is not None
    assert command_path.endswith(".venv/bin/cid-local-media-agent-visible-report-write-enabled-export")


def test_runner_cli_entrypoint_implementation_installs_runner_command() -> None:
    command_path = shutil.which(RUNNER_COMMAND)

    assert command_path is not None
    assert command_path.endswith(".venv/bin/cid-local-media-agent-controlled-local-demo-runner")


def test_runner_cli_entrypoint_implementation_runner_target_contract_is_stable() -> None:
    assert RUNNER_PATH.exists()
    assert runner.RUNNER_NAME == "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner"
    assert runner.COMMAND_NAME == CURRENT_COMMAND
    assert runner.OPERATIONAL_BOUNDARY == EXPECTED_BOUNDARY
    assert callable(runner.main)


def test_runner_cli_entrypoint_implementation_runner_import_execution_still_passes() -> None:
    summary = runner.run_controlled_local_demo(keep_output=False)

    assert summary["status"] == EXPECTED_STATUS
    assert summary["operational_boundary"] == EXPECTED_BOUNDARY
    assert summary["output_root_removed"] is True
    assert summary["artifact_available_after_runner"] is False
    assert summary["dry_run"]["verification_status"] == "DRY_RUN_ONLY"
    assert summary["write"]["verification_status"] == "VERIFIED"
    assert summary["negative_path"]["verification_status"] == "REJECTED"
    assert summary["safety"]["real_media_used"] is False
    assert summary["safety"]["scanner_used"] is False
    assert summary["safety"]["ffprobe_used"] is False
    assert summary["safety"]["ffmpeg_used"] is False
    assert summary["safety"]["network_used"] is False
    assert summary["safety"]["saas_used"] is False
    assert summary["safety"]["database_used"] is False
    assert summary["safety"]["installer_used"] is False


def test_runner_cli_entrypoint_implementation_runner_main_json_contract(capsys) -> None:
    exit_code = runner.main(["--result-json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["status"] == EXPECTED_STATUS
    assert payload["operational_boundary"] == EXPECTED_BOUNDARY
    assert payload["output_root_removed"] is True
    assert payload["artifact_available_after_runner"] is False
    assert payload["safety"]["real_media_used"] is False
    assert payload["safety"]["scanner_used"] is False
    assert payload["safety"]["ffprobe_used"] is False
    assert payload["safety"]["ffmpeg_used"] is False
    assert payload["safety"]["network_used"] is False
    assert payload["safety"]["saas_used"] is False
    assert payload["safety"]["database_used"] is False
    assert payload["safety"]["installer_used"] is False


def test_runner_cli_entrypoint_implementation_keeps_readiness_artifacts_present() -> None:
    assert READINESS_DOC_PATH.exists()
    assert READINESS_TEST_PATH.exists()


def test_runner_cli_entrypoint_implementation_no_generated_metadata_or_legacy_setup() -> None:
    assert not EGG_INFO_PATH.exists()
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()


def test_runner_cli_entrypoint_implementation_source_has_no_external_process_or_forbidden_runtime_tokens() -> None:
    source = RUNNER_PATH.read_text(encoding="utf-8").lower()
    external_process_token = "sub" + "process"

    assert external_process_token not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "socket." not in source
    assert "sqlalchemy" not in source
    assert "psycopg" not in source


def test_runner_cli_entrypoint_implementation_expected_result_marker() -> None:
    assert EXPECTED_RESULT.endswith("_CLOSED")
