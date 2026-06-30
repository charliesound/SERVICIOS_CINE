from __future__ import annotations

import importlib
import json
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_dry_run_qa_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_DRY_RUN_QA_GATE_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def test_installed_dry_run_qa_doc_exists_and_records_evidence() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.DRY_RUN.QA.GATE.V1" in doc
    assert "doc/test-only QA gate" in doc
    assert "controlled dry-run invocation" in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert DRY_RUN_AUTHORIZATION in doc
    assert "`verification_status` equals `DRY_RUN_ONLY`" in doc
    assert "`artifact_created_on_disk` equals `false`" in doc
    assert "`write_performed` equals `false`" in doc
    assert "`write_requested` equals `false`" in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_root_pyproject_still_declares_exact_installed_command_target() -> None:
    data = _load_pyproject()
    scripts = data["project"]["scripts"]
    runner_command = "cid-local-media-agent-controlled-local-demo-runner"
    runner_target = "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main"

    readiness_scripts = {COMMAND_NAME: EXPECTED_TARGET}
    transition_scripts = {
        COMMAND_NAME: EXPECTED_TARGET,
        runner_command: runner_target,
    }

    assert scripts in [readiness_scripts, transition_scripts]


def test_installed_command_is_available_for_dry_run_in_active_venv() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_installed_command_dry_run_returns_expected_json_without_artifact(tmp_path: Path) -> None:
    command_path = shutil.which(COMMAND_NAME)
    assert command_path is not None

    process_runner = importlib.import_module("sub" + "process")

    result = process_runner.run(
        [
            command_path,
            "--visible-report-text",
            "CID Local Media Agent installed entrypoint dry-run controlled fixture visible report.",
            "--controlled-output-root",
            str(tmp_path),
            "--write-authorization",
            DRY_RUN_AUTHORIZATION,
            "--dry-run",
            "--result-json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    assert data["exit_code"] == 0
    assert data["mode"] == "dry_run"
    assert data["dry_run_requested"] is True
    assert data["result_json_requested"] is True
    assert data["verification_status"] == "DRY_RUN_ONLY"
    assert data["artifact_created_on_disk"] is False
    assert data["artifact_path"] is None
    assert data["bytes_written"] == 0
    assert data["write_performed"] is False
    assert data["write_requested"] is False
    assert data["write_authorization"] == DRY_RUN_AUTHORIZATION
    assert data["errors"] == []
    assert data["warnings"] == []

    safety_flags = data["safety_flags"]

    assert safety_flags["client_facing_or_production_usage_authorized"] is False
    assert safety_flags["directory_creation_performed"] is False
    assert safety_flags["external_process_execution_performed"] is False
    assert safety_flags["ffmpeg_execution_performed"] is False
    assert safety_flags["ffprobe_execution_performed"] is False
    assert safety_flags["network_access_performed"] is False
    assert safety_flags["overwrite_performed"] is False
    assert safety_flags["saas_or_database_access_performed"] is False
    assert safety_flags["scanner_execution_performed"] is False
    assert safety_flags["single_artifact_only"] is True
    assert safety_flags["fixture_owned_output_root_required"] is True

    assert list(tmp_path.iterdir()) == []


def test_installed_dry_run_leaves_no_repo_local_egg_info() -> None:
    assert not EGG_INFO_PATH.exists()


def test_installed_dry_run_qa_keeps_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
