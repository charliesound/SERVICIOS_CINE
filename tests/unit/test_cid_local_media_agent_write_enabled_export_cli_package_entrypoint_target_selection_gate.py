from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.TARGET.SELECTION.GATE.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_package_entrypoint_target_selection_gate_v1.md"
AUTHORIZATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_authorization_gate.py"
READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"

ROOT_PACKAGING_FILES = [
    REPO_ROOT / "pyproject.toml",
    REPO_ROOT / "setup.cfg",
    REPO_ROOT / "setup.py",
]

NESTED_PYPROJECT = REPO_ROOT / "ai-dubbing-legal-studio/pyproject.toml"

ACCEPTED_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_TARGET_SELECTION_GATE_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_target_selection_gate_doc_exists_and_declares_blocking_decision() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only gate" in doc
    assert "blocked until the correct packaging target is explicitly selected" in doc
    assert "The nested file is not authorized as the Local Media Agent package entry point target by this gate." in doc
    assert "Database regression guard" in doc


def test_target_selection_gate_records_historical_root_packaging_absence_and_transition() -> None:
    doc = _read(DOC_PATH)

    assert "Root `pyproject.toml`: missing." in doc
    assert "Root `setup.cfg`: missing." in doc
    assert "Root `setup.py`: missing." in doc

    root_pyproject = REPO_ROOT / "pyproject.toml"
    root_setup_cfg = REPO_ROOT / "setup.cfg"
    root_setup_py = REPO_ROOT / "setup.py"

    assert root_pyproject.exists()
    assert not root_setup_cfg.exists()
    assert not root_setup_py.exists()
    assert "cid-local-media-agent-visible-report-write-enabled-export" in _read(root_pyproject)


def test_target_selection_gate_identifies_nested_pyproject_as_not_authorized() -> None:
    assert NESTED_PYPROJECT.exists()

    nested_text = _read(NESTED_PYPROJECT)
    doc = _read(DOC_PATH)

    assert "ai-dubbing-legal-studio/pyproject.toml" in doc
    assert "[tool.pytest.ini_options]" in nested_text
    assert "[project.scripts]" not in nested_text
    assert ACCEPTED_COMMAND_NAME not in nested_text


def test_target_selection_gate_defines_allowed_future_target_choices() -> None:
    doc = _read(DOC_PATH)

    assert "Create a root-level packaging metadata file for the Local Media Agent command." in doc
    assert "Select an existing packaging metadata file only after proving it owns the Local Media Agent packaging boundary." in doc
    assert "Defer package entry point implementation and keep using the direct module invocation path." in doc


def test_target_selection_gate_blocks_wrong_target_and_real_entrypoint_work() -> None:
    doc = _read(DOC_PATH)

    assert "Editing `ai-dubbing-legal-studio/pyproject.toml` for the Local Media Agent command." in doc
    assert "Adding a package entry point to an unrelated nested project." in doc
    assert "Creating root packaging metadata without a dedicated implementation phase." in doc
    assert "Editing runtime implementation." in doc


def test_target_selection_gate_keeps_required_related_artifacts_present() -> None:
    assert AUTHORIZATION_TEST_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert IMPLEMENTATION_PATH.exists()


def test_target_selection_gate_test_has_no_forbidden_imports() -> None:
    forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp"}
    forbidden.add("sub" + "process")

    tree = ast.parse(_read(Path(__file__)))
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_names.add(node.module.split(".")[0])

    assert imported_names.isdisjoint(forbidden)


def test_target_selection_gate_document_contains_no_shell_paste_artifacts() -> None:
    doc = _read(DOC_PATH)

    forbidden_fragments = [
        "git " + "status",
        "TARGET_SELECTION_GATE_DOC_" + "CREATED",
        "pri" + "ntf",
        "controlled_" + "git",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc
