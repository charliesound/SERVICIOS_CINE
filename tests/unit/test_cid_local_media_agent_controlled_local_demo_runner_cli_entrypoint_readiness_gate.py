from __future__ import annotations

import importlib
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_cli_entrypoint_readiness_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
RUNNER_PATH = REPO_ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

CURRENT_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
FUTURE_RUNNER_COMMAND = "cid-local-media-agent-controlled-local-demo-runner"

CURRENT_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
FUTURE_RUNNER_TARGET = "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main"

EXPECTED_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.CLI.ENTRYPOINT.READINESS.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_CLI_ENTRYPOINT_READINESS_GATE_V1_CLOSED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_RUNNER_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def _resolve_target(target: str):
    module_name, callable_name = target.split(":")
    module = importlib.import_module(module_name)
    return module, getattr(module, callable_name, None)


def test_runner_cli_entrypoint_readiness_doc_exists_and_records_boundary() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert EXPECTED_PHASE in doc
    assert "doc/test-only readiness gate" in doc
    assert "does not modify `pyproject.toml`" in doc
    assert "does not install the future runner command" in doc
    assert "current installed command remains the only project script" in doc
    assert CURRENT_COMMAND in doc
    assert FUTURE_RUNNER_COMMAND in doc
    assert CURRENT_TARGET in doc
    assert FUTURE_RUNNER_TARGET in doc
    assert str(RUNNER_PATH.relative_to(REPO_ROOT)) in doc
    assert EXPECTED_BOUNDARY in doc
    assert "future runner command must not yet be present in `pyproject.toml`" in doc
    assert "future runner command must not yet be available in the active `.venv`" in doc
    assert "future runner target must already be importable and callable" in doc
    assert "may add exactly one additional script entry" in doc
    assert "must preserve the existing write-enabled export command" in doc
    assert "deterministic `--result-json` output" in doc
    assert "optional `--keep-output`" in doc
    assert "default temporary output cleanup" in doc
    assert "fixture-owned temporary output roots only" in doc
    assert "no repository worktree writes" in doc
    assert EXPECTED_RUNNER_STATUS in doc
    assert "Editing `pyproject.toml`." in doc
    assert "Adding the future runner command to `[project.scripts]`." in doc
    assert "Installing the future runner command." in doc
    assert "Client demo." in doc
    assert "Public demo." in doc
    assert "Production execution." in doc
    assert "Installer packaging." in doc
    assert "Real media material." in doc
    assert "Real scanner execution." in doc
    assert "Real ffprobe execution." in doc
    assert "Real FFmpeg execution." in doc
    assert "Network behavior." in doc
    assert "SaaS persistence." in doc
    assert "Database persistence." in doc
    assert "Database regression guard" in doc
    assert EXPECTED_RESULT in doc


def test_runner_cli_entrypoint_readiness_pyproject_is_readiness_or_controlled_transition_state() -> None:
    data = _load_pyproject()
    scripts = data["project"]["scripts"]

    readiness_scripts = {
        CURRENT_COMMAND: CURRENT_TARGET,
    }
    transition_scripts = {
        CURRENT_COMMAND: CURRENT_TARGET,
        FUTURE_RUNNER_COMMAND: FUTURE_RUNNER_TARGET,
    }

    assert scripts in [readiness_scripts, transition_scripts]


def test_runner_cli_entrypoint_readiness_future_command_absent_or_exact_controlled_target() -> None:
    data = _load_pyproject()
    scripts = data["project"]["scripts"]

    if FUTURE_RUNNER_COMMAND not in scripts:
        return

    assert scripts[FUTURE_RUNNER_COMMAND] == FUTURE_RUNNER_TARGET


def test_runner_cli_entrypoint_readiness_current_command_is_installed() -> None:
    current_path = shutil.which(CURRENT_COMMAND)

    assert current_path is not None
    assert current_path.endswith(".venv/bin/cid-local-media-agent-visible-report-write-enabled-export")


def test_runner_cli_entrypoint_readiness_future_command_absent_or_installed_as_controlled_runner() -> None:
    command_path = shutil.which(FUTURE_RUNNER_COMMAND)

    if command_path is None:
        return

    assert command_path.endswith(".venv/bin/cid-local-media-agent-controlled-local-demo-runner")

    runner_module, _ = _resolve_target(FUTURE_RUNNER_TARGET)
    summary = runner_module.run_controlled_local_demo(keep_output=False)

    assert summary["status"] == EXPECTED_RUNNER_STATUS
    assert summary["operational_boundary"] == EXPECTED_BOUNDARY
    assert summary["output_root_removed"] is True
    assert summary["artifact_available_after_runner"] is False


def test_runner_cli_entrypoint_readiness_current_and_future_targets_are_callable() -> None:
    current_module, current_callable = _resolve_target(CURRENT_TARGET)
    runner_module, runner_callable = _resolve_target(FUTURE_RUNNER_TARGET)

    assert callable(current_callable)
    assert callable(runner_callable)

    assert current_module.COMMAND_NAME == CURRENT_COMMAND
    assert runner_module.RUNNER_NAME == "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner"
    assert runner_module.COMMAND_NAME == CURRENT_COMMAND
    assert runner_module.OPERATIONAL_BOUNDARY == EXPECTED_BOUNDARY


def test_runner_cli_entrypoint_readiness_future_runner_target_executes_controlled_demo_by_import() -> None:
    runner_module, _ = _resolve_target(FUTURE_RUNNER_TARGET)

    summary = runner_module.run_controlled_local_demo(keep_output=False)

    assert summary["status"] == EXPECTED_RUNNER_STATUS
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


def test_runner_cli_entrypoint_readiness_does_not_create_generated_metadata_or_legacy_setup() -> None:
    assert not EGG_INFO_PATH.exists()
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()


def test_runner_cli_entrypoint_readiness_source_has_no_external_process_or_forbidden_runtime_tokens() -> None:
    source = _read(RUNNER_PATH).lower()
    external_process_token = "sub" + "process"

    assert external_process_token not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "socket." not in source
    assert "sqlalchemy" not in source
    assert "psycopg" not in source


def test_runner_cli_entrypoint_readiness_expected_result_marker() -> None:
    assert EXPECTED_RESULT.endswith("_CLOSED")
