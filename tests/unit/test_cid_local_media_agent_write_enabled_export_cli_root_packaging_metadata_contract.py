from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.ROOT.PACKAGING.METADATA.CONTRACT.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_contract_v1.md"
TARGET_SELECTION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_target_selection_gate.py"
AUTHORIZATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_authorization_gate.py"
READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"

ROOT_PYPROJECT = REPO_ROOT / "pyproject.toml"
ROOT_SETUP_CFG = REPO_ROOT / "setup.cfg"
ROOT_SETUP_PY = REPO_ROOT / "setup.py"
NESTED_PYPROJECT = REPO_ROOT / "ai-dubbing-legal-studio/pyproject.toml"

ACCEPTED_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_CONTRACT_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_root_packaging_metadata_contract_doc_exists_and_declares_scope() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only contract" in doc
    assert "does not create `pyproject.toml`" in doc
    assert "does not add a package entry point" in doc
    assert "does not modify runtime" in doc
    assert "Database regression guard" in doc


def test_root_packaging_metadata_contract_preserves_current_absence() -> None:
    assert not ROOT_PYPROJECT.exists()
    assert not ROOT_SETUP_CFG.exists()
    assert not ROOT_SETUP_PY.exists()


def test_root_packaging_metadata_contract_blocks_nested_project_target() -> None:
    assert NESTED_PYPROJECT.exists()

    doc = _read(DOC_PATH)
    nested = _read(NESTED_PYPROJECT)

    assert "ai-dubbing-legal-studio/pyproject.toml" in doc
    assert "remains out of scope" in doc
    assert "[tool.pytest.ini_options]" in nested
    assert ACCEPTED_COMMAND not in nested


def test_root_packaging_metadata_contract_defines_future_minimal_metadata() -> None:
    doc = _read(DOC_PATH)

    assert "future root `pyproject.toml` must be minimal and controlled" in doc
    assert "Exactly one script entry for the accepted command name." in doc
    assert "Project identity for the Local Media Agent packaging boundary." in doc
    assert ACCEPTED_COMMAND in doc


def test_root_packaging_metadata_contract_preserves_export_cli_behavior() -> None:
    doc = _read(DOC_PATH)

    required = [
        "Existing parser surface.",
        "Dry-run behavior.",
        "Controlled write authorization.",
        "Fixture-owned output root restriction.",
        "No-overwrite behavior.",
        "Single-artifact behavior.",
        "No directory creation by the export CLI.",
        "Deterministic JSON output.",
    ]

    for item in required:
        assert item in doc


def test_root_packaging_metadata_contract_related_gates_are_present() -> None:
    assert TARGET_SELECTION_TEST_PATH.exists()
    assert AUTHORIZATION_TEST_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()


def test_root_packaging_metadata_contract_test_has_no_forbidden_imports() -> None:
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


def test_root_packaging_metadata_contract_contains_no_shell_paste_artifacts() -> None:
    doc = _read(DOC_PATH)

    forbidden_fragments = [
        "git " + "status",
        "ROOT_PACKAGING_METADATA_CONTRACT_DOC_" + "CREATED",
        "pri" + "ntf",
        "controlled_" + "git",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc
