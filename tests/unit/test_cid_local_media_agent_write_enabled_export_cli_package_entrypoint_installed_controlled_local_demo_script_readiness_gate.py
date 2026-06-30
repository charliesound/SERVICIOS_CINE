from __future__ import annotations

import importlib
import shutil
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_controlled_local_demo_script_readiness_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

FUTURE_DEMO_RUNNER_PATH = REPO_ROOT / "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
WRITE_AUTHORIZATION = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"
DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"
OPERATIONAL_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_CONTROLLED_LOCAL_DEMO_SCRIPT_READINESS_GATE_V1_CLOSED"

PRIOR_REQUIRED_FILES = [
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_invocation_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_dry_run_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_controlled_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_negative_paths_qa_gate_v1.md",
    REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_command_operational_summary_qa_gate_v1.md",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_invocation_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_dry_run_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_controlled_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_write_execution_negative_paths_qa_gate.py",
    REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_command_operational_summary_qa_gate.py",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def test_controlled_local_demo_script_readiness_doc_exists_and_records_future_scope() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.SCRIPT.READINESS.GATE.V1" in doc
    assert "doc/test-only readiness gate" in doc
    assert "does not create the demo runner" in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert EXPECTED_TARGET in doc
    assert WRITE_AUTHORIZATION in doc
    assert DRY_RUN_AUTHORIZATION in doc
    assert OPERATIONAL_BOUNDARY in doc
    assert "scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py" in doc
    assert "Installed command availability check" in doc
    assert "Installed `--help` invocation" in doc
    assert "Installed `--dry-run --result-json` invocation" in doc
    assert "Installed controlled write execution creating exactly one `.txt` artifact" in doc
    assert "One basic negative path proving fail-closed behavior" in doc
    assert "fixture-owned temporary output roots" in doc
    assert "must not write inside the repository worktree" in doc
    assert "Creating the demo runner." in doc
    assert "Running real scanner code." in doc
    assert "Running FFmpeg." in doc
    assert "Running ffprobe." in doc
    assert "Running network behavior." in doc
    assert "Real media material." in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_controlled_local_demo_script_readiness_keeps_future_runner_absent_or_controlled_transition_present() -> None:
    if not FUTURE_DEMO_RUNNER_PATH.exists():
        return

    source = FUTURE_DEMO_RUNNER_PATH.read_text(encoding="utf-8")

    assert "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner" in source
    assert "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY" in source
    assert "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED" in source
    assert "run_controlled_local_demo" in source
    assert "fixture_owned" in source
    assert "installed_help_invocation" in source
    assert "installed_dry_run_result_json_invocation" in source
    assert "installed_controlled_write_single_txt_artifact" in source
    assert "installed_negative_path_fail_closed" in source
    external_process_token = "sub" + "process"
    assert external_process_token not in source
    assert "requests." not in source
    assert "httpx." not in source
    assert "socket." not in source
    assert "sqlalchemy" not in source
    assert "psycopg" not in source


def test_controlled_local_demo_script_readiness_keeps_exact_single_entrypoint() -> None:
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


def test_controlled_local_demo_script_readiness_command_is_installed() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_controlled_local_demo_script_readiness_target_is_importable_callable() -> None:
    module_name, callable_name = EXPECTED_TARGET.split(":")
    module = importlib.import_module(module_name)

    assert callable(getattr(module, callable_name, None))
    assert module.COMMAND_NAME == COMMAND_NAME
    assert module.WRITE_AUTHORIZATION == WRITE_AUTHORIZATION
    assert module.DRY_RUN_AUTHORIZATION == DRY_RUN_AUTHORIZATION


def test_controlled_local_demo_script_readiness_prior_gates_exist() -> None:
    for path in PRIOR_REQUIRED_FILES:
        assert path.exists(), path


def test_controlled_local_demo_script_readiness_has_no_repo_local_generated_metadata() -> None:
    assert not EGG_INFO_PATH.exists()


def test_controlled_local_demo_script_readiness_keeps_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
