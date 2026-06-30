from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.ROOT.PACKAGING.METADATA.READINESS.GATE.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_readiness_gate_v1.md"
CONTRACT_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_contract.py"
TARGET_SELECTION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_target_selection_gate.py"
AUTHORIZATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_authorization_gate.py"
READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"

ROOT_PYPROJECT = REPO_ROOT / "pyproject.toml"
ROOT_SETUP_CFG = REPO_ROOT / "setup.cfg"
ROOT_SETUP_PY = REPO_ROOT / "setup.py"

ACCEPTED_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_READINESS_GATE_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_root_packaging_metadata_readiness_doc_exists_and_declares_scope() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only readiness gate" in doc
    assert "does not create `pyproject.toml`" in doc
    assert "does not add a package entry point" in doc
    assert "does not modify runtime" in doc
    assert "Database regression guard" in doc


def test_root_packaging_metadata_readiness_records_historical_absence_and_allows_controlled_transition() -> None:
    assert ROOT_PYPROJECT.exists()
    assert not ROOT_SETUP_CFG.exists()
    assert not ROOT_SETUP_PY.exists()

    content = _read(ROOT_PYPROJECT)
    assert "cid-local-media-agent" in content
    assert "cid-local-media-agent-visible-report-write-enabled-export" in content


def test_root_packaging_metadata_readiness_defines_future_creation_constraints() -> None:
    doc = _read(DOC_PATH)

    assert "Create exactly one root-level `pyproject.toml`." in doc
    assert "Avoid editing `ai-dubbing-legal-studio/pyproject.toml`." in doc
    assert "Define one package entry point for the accepted command name." in doc
    assert "Point the command to the accepted module and accepted callable" in doc
    assert ACCEPTED_COMMAND in doc


def test_root_packaging_metadata_readiness_blocks_current_packaging_work() -> None:
    doc = _read(DOC_PATH)

    assert "Creating root `pyproject.toml`." in doc
    assert "Editing root packaging metadata." in doc
    assert "Editing `ai-dubbing-legal-studio/pyproject.toml`." in doc
    assert "Adding a real package entry point." in doc
    assert "Editing runtime implementation." in doc


def test_root_packaging_metadata_readiness_preserves_export_cli_behavior() -> None:
    doc = _read(DOC_PATH)

    for item in [
        "Preserve existing parser options.",
        "Preserve dry-run behavior.",
        "Preserve controlled write authorization.",
        "Preserve fixture-owned output root restriction.",
        "Preserve no-overwrite behavior.",
        "Preserve single-artifact behavior.",
        "Preserve deterministic JSON output.",
    ]:
        assert item in doc


def test_root_packaging_metadata_readiness_related_gates_are_present() -> None:
    assert CONTRACT_TEST_PATH.exists()
    assert TARGET_SELECTION_TEST_PATH.exists()
    assert AUTHORIZATION_TEST_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()


def test_root_packaging_metadata_readiness_test_has_no_forbidden_imports() -> None:
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


def test_root_packaging_metadata_readiness_contains_no_shell_paste_artifacts() -> None:
    doc = _read(DOC_PATH)

    forbidden_fragments = [
        "git " + "status",
        "ROOT_PACKAGING_METADATA_READINESS_GATE_DOC_" + "CREATED",
        "pri" + "ntf",
        "controlled_" + "git",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc
