from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.ROOT.PACKAGING.METADATA.EXISTENCE.TRANSITION.COMPATIBILITY.GATE.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_existence_transition_compatibility_gate_v1.md"
ROOT_READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_readiness_gate.py"
ROOT_CONTRACT_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_root_packaging_metadata_contract.py"
TARGET_SELECTION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_target_selection_gate.py"
AUTHORIZATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_authorization_gate.py"
ENTRYPOINT_READINESS_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_write_enabled_export_cli_package_entrypoint_readiness_gate.py"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"

ROOT_PYPROJECT = REPO_ROOT / "pyproject.toml"
ROOT_SETUP_CFG = REPO_ROOT / "setup.cfg"
ROOT_SETUP_PY = REPO_ROOT / "setup.py"

EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_ROOT_PACKAGING_METADATA_EXISTENCE_TRANSITION_COMPATIBILITY_GATE_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_existence_transition_compatibility_doc_exists_and_declares_scope() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert EXPECTED_RESULT in doc
    assert "doc/test-only compatibility gate" in doc
    assert "historical precondition" in doc
    assert "does not create `pyproject.toml`" in doc
    assert "does not edit previous tests" in doc
    assert "does not add a package entry point" in doc
    assert "does not modify runtime" in doc
    assert "Database regression guard" in doc


def test_existence_transition_compatibility_preserves_current_absence() -> None:
    assert not ROOT_PYPROJECT.exists()
    assert not ROOT_SETUP_CFG.exists()
    assert not ROOT_SETUP_PY.exists()


def test_existence_transition_compatibility_records_prior_blocking_assertions() -> None:
    readiness = _read(ROOT_READINESS_TEST_PATH)
    contract = _read(ROOT_CONTRACT_TEST_PATH)
    target_selection = _read(TARGET_SELECTION_TEST_PATH)

    assert "assert not ROOT_PYPROJECT.exists()" in readiness
    assert "assert not ROOT_PYPROJECT.exists()" in contract
    assert "ROOT_PACKAGING_FILES" in target_selection
    assert "assert not path.exists()" in target_selection


def test_existence_transition_compatibility_authorizes_future_narrow_update() -> None:
    doc = _read(DOC_PATH)

    assert "may update prior doc/test-only gates" in doc
    assert "convert absolute absence assertions into historical-baseline assertions or phase-bounded assertions" in doc
    assert "must not weaken unrelated safety checks" in doc


def test_existence_transition_compatibility_names_known_prior_gates() -> None:
    doc = _read(DOC_PATH)

    assert "Package entrypoint target selection gate." in doc
    assert "Root packaging metadata contract." in doc
    assert "Root packaging metadata readiness gate." in doc


def test_existence_transition_compatibility_related_gates_are_present() -> None:
    assert ROOT_READINESS_TEST_PATH.exists()
    assert ROOT_CONTRACT_TEST_PATH.exists()
    assert TARGET_SELECTION_TEST_PATH.exists()
    assert AUTHORIZATION_TEST_PATH.exists()
    assert ENTRYPOINT_READINESS_TEST_PATH.exists()
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()


def test_existence_transition_compatibility_test_has_no_forbidden_imports() -> None:
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


def test_existence_transition_compatibility_contains_no_shell_paste_artifacts() -> None:
    doc = _read(DOC_PATH)

    forbidden_fragments = [
        "git " + "status",
        "ROOT_PACKAGING_METADATA_EXISTENCE_TRANSITION_COMPATIBILITY_GATE_DOC_" + "CREATED",
        "pri" + "ntf",
        "controlled_" + "git",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in doc
