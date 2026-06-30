from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.READINESS.GATE.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate_v1.md"
IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"

ACCEPTED_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_READINESS_GATE_V1_CLOSED"

ALLOWED_OPTIONS = {
    "--visible-report-text",
    "--controlled-output-root",
    "--write-authorization",
    "--result-json",
    "--dry-run",
}

FORBIDDEN_ENTRYPOINT_TERMS = {
    "[project.scripts]",
    "console_scripts",
    "entry_points",
    "cid-local-media-agent-visible-report-write-enabled-export =",
}


class _OptionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.options: set[str] = set()

    def visit_Call(self, node: ast.Call) -> Any:
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("--"):
                self.options.add(arg.value)
        self.generic_visit(node)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_module() -> Any:
    spec = importlib.util.spec_from_file_location("cid_lma_entrypoint_readiness_target", IMPLEMENTATION_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _collect_options(source: str) -> set[str]:
    tree = ast.parse(source)
    collector = _OptionCollector()
    collector.visit(tree)
    return collector.options


def test_readiness_gate_doc_exists_and_declares_scope() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only" in doc
    assert "does not add, enable, modify, or publish a package entry point" in doc
    assert "database regression guard" in doc.lower()


def test_isolated_cli_module_and_corrected_qa_gate_exist() -> None:
    assert IMPLEMENTATION_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()


def test_accepted_internal_command_name_and_main_callable_exist() -> None:
    module = _load_module()
    source = _read(IMPLEMENTATION_PATH)

    assert ACCEPTED_COMMAND_NAME in source
    assert callable(getattr(module, "main", None))


def test_parser_surface_remains_exactly_the_accepted_surface() -> None:
    source = _read(IMPLEMENTATION_PATH)
    options = _collect_options(source)

    assert ALLOWED_OPTIONS.issubset(options)
    assert options <= ALLOWED_OPTIONS


def test_phase_records_historical_packaging_absence_and_allows_controlled_transition() -> None:
    root_pyproject = REPO_ROOT / "pyproject.toml"
    root_setup_py = REPO_ROOT / "setup.py"
    root_setup_cfg = REPO_ROOT / "setup.cfg"

    assert root_pyproject.exists()
    assert not root_setup_py.exists()
    assert not root_setup_cfg.exists()

    text = _read(root_pyproject)
    assert "[project.scripts]" in text
    assert ACCEPTED_COMMAND_NAME in text
    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main" in text


def test_readiness_gate_test_does_not_authorize_entrypoint_creation() -> None:
    doc = _read(DOC_PATH).lower()

    assert "does not add, enable, modify, or publish a package entry point" in doc
    assert "adding an actual package entry point" in doc
    assert "editing packaging metadata" in doc


def test_readiness_gate_static_imports_do_not_introduce_forbidden_surfaces() -> None:
    forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp"}
    forbidden.add("sub" + "process")

    for path in (Path(__file__), IMPLEMENTATION_PATH):
        tree = ast.parse(_read(path))
        imported_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module.split(".")[0])

        assert imported_names.isdisjoint(forbidden), path
