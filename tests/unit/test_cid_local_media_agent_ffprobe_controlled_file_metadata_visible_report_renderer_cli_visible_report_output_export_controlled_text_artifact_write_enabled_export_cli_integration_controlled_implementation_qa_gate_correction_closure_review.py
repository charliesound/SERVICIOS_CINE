from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.CORRECTION.CLOSURE.REVIEW.V1"

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate_correction_closure_review_v1.md"
QA_GATE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation_qa_gate.py"
IMPLEMENTATION_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
IMPLEMENTATION_PATH = REPO_ROOT / "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"

ACCEPTED_CORRECTION_COMMIT = "60511856609bb300c445ce6047d6b4e1e73a0824"
ACCEPTED_CORRECTION_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-controlled-impl-qa-gate-v1-correction-v1-20260629"
SUPERSEDED_HISTORICAL_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-controlled-impl-qa-gate-v1-20260629"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTROLLED_IMPLEMENTATION_QA_GATE_CORRECTION_CLOSURE_REVIEW_V1_CLOSED"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_doc_exists_and_declares_phase_result_and_stable_correction() -> None:
    assert DOC_PATH.exists()
    doc = _read(DOC_PATH)

    assert PHASE in doc
    assert ACCEPTED_CORRECTION_COMMIT in doc
    assert ACCEPTED_CORRECTION_TAG in doc
    assert SUPERSEDED_HISTORICAL_TAG in doc
    assert EXPECTED_RESULT in doc
    assert "not the accepted stable state" in doc
    assert "database regression guard" in doc


def test_closure_review_targets_existing_corrected_artifacts_only() -> None:
    assert QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert IMPLEMENTATION_PATH.exists()


def test_corrected_qa_gate_no_longer_depends_on_nonexistent_filename_constant() -> None:
    qa_source = _read(QA_GATE_TEST_PATH)

    assert 'getattr(module, "FILENAME")' not in qa_source
    assert 'payload.get("filename")' in qa_source
    assert "EXPECTED_ARTIFACT_NAME" in qa_source


def test_corrected_qa_gate_keeps_database_regression_wording_case_safe() -> None:
    qa_source = _read(QA_GATE_TEST_PATH)

    assert '"database regression guard" in doc.lower()' in qa_source


def test_corrected_qa_gate_keeps_result_json_as_flag_not_path_argument() -> None:
    qa_source = _read(QA_GATE_TEST_PATH)

    assert '"--result-json"' in qa_source
    assert '"--result-json",' in qa_source
    assert 'argv.extend(["--result-json", str(result_json)])' not in qa_source


def test_closure_review_and_qa_gate_tests_have_no_forbidden_imports() -> None:
    forbidden = {"socket", "requests", "urllib", "httpx", "aiohttp"}
    forbidden.add("sub" + "process")

    for path in (Path(__file__), QA_GATE_TEST_PATH):
        tree = ast.parse(_read(path))
        imported_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_names.add(node.module.split(".")[0])

        assert imported_names.isdisjoint(forbidden), path


def test_closure_review_does_not_authorize_runtime_or_integration_expansion() -> None:
    doc = _read(DOC_PATH)

    forbidden_authorizations = (
        "runtime feature changes",
        "package entry points",
        "installer work",
        "client demo",
        "public demo",
        "production execution",
        "backend work",
        "frontend work",
        "saas persistence work",
        "real media material",
        "real scanner execution",
        "real media probing tools",
        "external process execution",
        "network behavior",
        "overwrite behavior",
        "multiple artifact export",
    )

    for phrase in forbidden_authorizations:
        assert phrase in doc.lower()
