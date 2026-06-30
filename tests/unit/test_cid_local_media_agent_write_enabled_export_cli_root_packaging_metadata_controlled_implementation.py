from __future__ import annotations

import ast
import importlib
import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
NESTED_PYPROJECT = REPO_ROOT / "ai-dubbing-legal-studio/pyproject.toml"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
PROJECT_NAME = "cid-local-media-agent"
TARGET = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main"
TARGET_MODULE = "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli"
TARGET_CALLABLE = "main"

EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_CONTROLLED_IMPLEMENTATION_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_pyproject() -> dict:
    return tomllib.loads(_read(PYPROJECT_PATH))


def test_root_pyproject_exists_and_is_parseable() -> None:
    assert PYPROJECT_PATH.exists()
    data = _load_pyproject()

    assert data["project"]["name"] == PROJECT_NAME
    assert data["project"]["requires-python"] == ">=3.12"
    assert data["build-system"]["build-backend"] == "setuptools.build_meta"


def test_root_pyproject_defines_exact_single_script_entry() -> None:
    data = _load_pyproject()
    scripts = data["project"]["scripts"]

    assert scripts == {COMMAND_NAME: TARGET}


def test_root_pyproject_uses_namespace_package_discovery_for_scripts_tree() -> None:
    data = _load_pyproject()
    find_config = data["tool"]["setuptools"]["packages"]["find"]

    assert find_config["include"] == ["scripts*"]
    assert find_config["namespaces"] is True


def test_root_pyproject_does_not_modify_nested_project() -> None:
    assert NESTED_PYPROJECT.exists()

    nested = _read(NESTED_PYPROJECT)
    assert "[tool.pytest.ini_options]" in nested
    assert COMMAND_NAME not in nested
    assert "[project.scripts]" not in nested


def test_root_pyproject_entrypoint_target_imports_and_exposes_callable() -> None:
    module = importlib.import_module(TARGET_MODULE)
    assert callable(getattr(module, TARGET_CALLABLE, None))


def test_root_pyproject_has_no_extra_root_packaging_files() -> None:
    assert not (REPO_ROOT / "setup.cfg").exists()
    assert not (REPO_ROOT / "setup.py").exists()


def test_root_pyproject_controlled_implementation_preserves_cli_command_constant() -> None:
    module = importlib.import_module(TARGET_MODULE)
    assert getattr(module, "COMMAND_NAME") == COMMAND_NAME


def test_root_pyproject_controlled_implementation_test_has_no_forbidden_imports() -> None:
    forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp"}
    forbidden.add("sub" + "process")

    tree = ast.parse(_read(Path(__file__)))
    imported: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert imported.isdisjoint(forbidden)


def test_root_pyproject_contains_expected_closure_result_marker() -> None:
    assert EXPECTED_RESULT.endswith("_CLOSED")
