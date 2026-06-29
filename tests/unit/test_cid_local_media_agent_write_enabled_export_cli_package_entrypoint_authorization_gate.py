from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.AUTHORIZATION.GATE.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_authorization_gate_v1.md"
READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"

ACCEPTED_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
ACCEPTED_MODULE = "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_AUTHORIZATION_GATE_V1_CLOSED"

ALLOWED_OPTIONS = {
    "--visible-report-text",
    "--controlled-output-root",
    "--write-authorization",
    "--result-json",
    "--dry-run",
}


class _OptionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.options: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("--"):
                self.options.add(arg.value)
        self.generic_visit(node)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _collect_options(source: str) -> set[str]:
    tree = ast.parse(source)
    collector = _OptionCollector()
    collector.visit(tree)
    return collector.options


def test_authorization_gate_doc_exists_and_declares_decision() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only authorization gate" in doc
    assert "does not add the entry point" in doc
    assert "does not modify packaging metadata" in doc
    assert "does not modify runtime" in doc
    assert "Database regression guard" in doc


def test_authorization_gate_references_accepted_command_module_and_callable() -> None:
    doc = _read(DOC_PATH)

    assert ACCEPTED_COMMAND_NAME in doc
    assert ACCEPTED_MODULE in doc
    assert "Accepted callable: `main`" in doc


def test_authorization_gate_defines_future_scope_but_blocks_current_entrypoint_change() -> None:
    doc = _read(DOC_PATH)

    assert "future implementation phase may modify packaging metadata" in doc
    assert "single purpose of exposing the accepted command name" in doc
    assert "Editing packaging metadata." in doc
    assert "Adding a real package entry point." in doc


def test_authorization_gate_keeps_required_related_artifacts_present() -> None:
    assert READINESS_TEST_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert IMPLEMENTATION_PATH.exists()


def test_authorization_gate_preserves_parser_surface_contract() -> None:
    source = _read(IMPLEMENTATION_PATH)
    options = _collect_options(source)

    assert ALLOWED_OPTIONS.issubset(options)
    assert options <= ALLOWED_OPTIONS


def test_authorization_gate_test_has_no_forbidden_imports() -> None:
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


def test_authorization_gate_document_contains_no_shell_paste_artifacts() -> None:
    doc = _read(DOC_PATH)

    forbidden_fragments = [
        "git status",
        "AUTHORIZATION_GATE_DOC_REWRITTEN_CLEAN",
        "controlled_git",
        "printf",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc
