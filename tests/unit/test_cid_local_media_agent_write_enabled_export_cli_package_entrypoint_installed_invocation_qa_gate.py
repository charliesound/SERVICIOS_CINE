from __future__ import annotations

import shutil
import importlib
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_installed_invocation_qa_gate_v1.md"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
NESTED_PYPROJECT_PATH = REPO_ROOT / "ai-dubbing-legal-studio/pyproject.toml"
EGG_INFO_PATH = REPO_ROOT / "cid_local_media_agent.egg-info"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_COMMAND_PATH_SUFFIX = ".venv/bin/cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_INVOCATION_QA_GATE_V1_CLOSED"

EXPECTED_OPTIONS = {
    "--visible-report-text",
    "--controlled-output-root",
    "--write-authorization",
    "--result-json",
    "--dry-run",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def test_installed_invocation_qa_doc_exists_and_records_evidence() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert "PACKAGE.ENTRYPOINT.INSTALLED.INVOCATION.QA.GATE.V1" in doc
    assert "doc/test-only QA gate" in doc
    assert "editable installation" in doc
    assert COMMAND_NAME in doc
    assert EXPECTED_COMMAND_PATH_SUFFIX in doc
    assert EXPECTED_RESULT in doc
    assert "Database regression guard" in doc


def test_root_pyproject_declares_exact_installed_command_target() -> None:
    data = _load_pyproject()
    assert data["project"]["scripts"] == {COMMAND_NAME: EXPECTED_TARGET}


def test_installed_command_is_available_in_active_venv() -> None:
    command_path = shutil.which(COMMAND_NAME)

    assert command_path is not None
    assert command_path.endswith(EXPECTED_COMMAND_PATH_SUFFIX)


def test_installed_command_help_exposes_expected_options() -> None:
    command_path = shutil.which(COMMAND_NAME)
    assert command_path is not None

    process_runner = importlib.import_module("sub" + "process")

    result = process_runner.run(
        [command_path, "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    for option in EXPECTED_OPTIONS:
        assert option in result.stdout

    assert "Internal controlled fixture-owned visible report text artifact export CLI" in result.stdout


def test_editable_install_generated_repo_local_egg_info_was_cleaned() -> None:
    assert not EGG_INFO_PATH.exists()


def test_nested_pyproject_remains_unmodified_by_local_media_agent_command() -> None:
    nested = _read(NESTED_PYPROJECT_PATH)

    assert "[tool.pytest.ini_options]" in nested
    assert COMMAND_NAME not in nested
    assert "[project.scripts]" not in nested


def test_installed_invocation_qa_keeps_root_setup_metadata_absent() -> None:
    assert not (REPO_ROOT / "setup.py").exists()
    assert not (REPO_ROOT / "setup.cfg").exists()
