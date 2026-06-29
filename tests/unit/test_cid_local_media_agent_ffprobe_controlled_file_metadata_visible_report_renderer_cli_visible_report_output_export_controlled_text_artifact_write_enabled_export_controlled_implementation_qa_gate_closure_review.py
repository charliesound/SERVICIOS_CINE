from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as dry_run_cli,
)
from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export import (
    DEFAULT_FILENAME,
    WRITE_AUTHORIZATION,
    export_controlled_visible_report_text_artifact,
)


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate.py"
)

IMPLEMENTATION_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
)

IMPLEMENTATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_implementation_readiness_gate_v1.md"
)

DRY_RUN_CLI_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

DRY_RUN_BRIDGE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTROLLED."
    "IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CONTROLLED_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_CLOSED"
)

PREVIOUS_COMMIT = "7123ae84e93d656d863578f9ff3ed0e8625ce1bd"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-controlled-impl-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-controlled-impl-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.READINESS.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        QA_GATE_DOC_PATH,
        QA_GATE_TEST_PATH,
        IMPLEMENTATION_MODULE_PATH,
        IMPLEMENTATION_TEST_PATH,
        READINESS_DOC_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_closure_review_exist(path: Path) -> None:
    assert path.is_file()


@pytest.mark.parametrize(
    "required_text",
    [
        PHASE_ID,
        RESULT_ID,
        PREVIOUS_COMMIT,
        PREVIOUS_TAG,
        TARGET_TAG,
        NEXT_PHASE_ID,
        "This is a doc/test-only closure review.",
        "This closure review closes the controlled write-enabled export implementation QA gate.",
        "This closure review does not add runtime implementation.",
        "This closure review does not modify the controlled write-enabled export implementation.",
        "This closure review does not modify the current dry-run CLI.",
        "This closure review does not modify the current dry-run bridge.",
        "This closure review does not authorize CLI integration.",
        "This closure review does not authorize client-facing usage.",
        "This closure review does not authorize production usage.",
    ],
)
def test_closure_review_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "accidental root untracked files were safely removed before staging.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target QA gate test passed with 183 checks.",
        "controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target QA gate tag absent locally before tagging.",
        "target QA gate tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final readiness gate test passed with 322 checks.",
        "final contract QA closure review test passed with 266 checks.",
        "final contract QA gate test passed with 244 checks.",
        "final contract test passed with 251 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the QA gate is doc/test-only.",
        "the QA gate does not add runtime implementation.",
        "the QA gate does not modify the controlled implementation.",
        "the QA gate does not modify the dry-run CLI.",
        "the QA gate does not modify the dry-run bridge.",
        "the QA gate accepts `export_controlled_visible_report_text_artifact`.",
        "the QA gate accepts explicit authorization `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.",
        "the QA gate accepts only `controlled_visible_report.controlled.txt`.",
        "the QA gate accepts controlled visible report text from memory only.",
        "the QA gate accepts fixture-owned output roots only.",
        "the QA gate accepts no-overwrite behavior.",
        "the QA gate accepts no directory creation.",
        "the QA gate accepts no arbitrary cleanup.",
        "the QA gate accepts UTF-8 byte verification.",
        "the QA gate accepts SHA256 verification.",
        "the QA gate accepts deterministic result shape.",
        "the QA gate accepts explicit conservative safety flags.",
        "the QA gate confirms no scanner execution.",
        "the QA gate confirms no ffprobe execution.",
        "the QA gate confirms no FFmpeg execution.",
        "the QA gate confirms no external process execution.",
        "the QA gate confirms no network access.",
        "the QA gate confirms no SaaS or database access.",
        "the QA gate confirms no client-facing behavior.",
        "the QA gate confirms no production behavior.",
    ],
)
def test_closure_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`export_controlled_visible_report_text_artifact`",
        "`CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`",
        "`controlled_visible_report.controlled.txt`",
        "`utf-8 text`",
        "`fixture-owned output root only`",
        "`NO_OVERWRITE`",
        "`bytes and SHA256 before and after write`",
        "`FIXTURE_OWNED_OUTPUT_CLEANUP_BY_TEST_OWNER`",
    ],
)
def test_controlled_primitive_accepted_state_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize CLI integration.",
        "This closure review does not authorize command-line write flags.",
        "This closure review does not authorize writing outside fixture-owned roots.",
        "This closure review does not authorize directory creation.",
        "This closure review does not authorize overwrite.",
        "This closure review does not authorize multiple artifacts.",
        "This closure review does not authorize arbitrary cleanup.",
        "This closure review does not authorize real media access.",
        "This closure review does not authorize scanner execution.",
        "This closure review does not authorize ffprobe execution.",
        "This closure review does not authorize FFmpeg execution.",
        "This closure review does not authorize external process execution.",
        "This closure review does not authorize network access.",
        "This closure review does not authorize SaaS integration.",
        "This closure review does not authorize database integration.",
        "This closure review does not authorize backend changes.",
        "This closure review does not authorize frontend changes.",
        "This closure review does not authorize installer work.",
        "This closure review does not authorize client-facing demo work.",
        "This closure review does not authorize public demo work.",
        "This closure review does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_closure_review_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export implementation QA gate is accepted and closed." in doc
    assert "The current project has a QA-accepted controlled fixture-owned write-enabled export primitive." in doc
    assert "The current project remains not ready for CLI write-enabled export." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not add CLI write flags." in doc
    assert "That next step must not connect the primitive to user-facing command execution." in doc
    assert "That next step may only define the future CLI integration boundary." in doc


def test_qa_gate_document_supports_closure_review() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "The controlled write-enabled export implementation is accepted by QA gate." in source
    assert "The current project now has a controlled fixture-owned write-enabled export primitive." in source
    assert "The current project remains not ready for CLI write-enabled export." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source


def test_controlled_implementation_still_writes_only_fixture_owned_artifact(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Closure review controlled report\n",
        controlled_output_root=tmp_path,
        write_authorization=WRITE_AUTHORIZATION,
    )

    artifact_path = tmp_path / DEFAULT_FILENAME

    assert artifact_path.is_file()
    assert result["write_performed"] is True
    assert result["artifact_created_on_disk"] is True
    assert result["filename"] == DEFAULT_FILENAME
    assert result["write_authorization"] == WRITE_AUTHORIZATION
    assert result["verification_status"] == "VERIFIED"
    assert result["errors"] == []


def test_controlled_implementation_still_rejects_uncontrolled_root() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_implementation_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Report",
        controlled_output_root=tmp_path,
        write_authorization="CONTROLLED_DRY_RUN_ACCEPTED",
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "write authorization is dry-run-only" in result["errors"]


def test_current_dry_run_cli_still_has_no_write_options() -> None:
    parser = dry_run_cli.build_parser()
    option_strings = {
        option
        for action in parser._actions
        for option in action.option_strings
    }

    assert "--dry-run" in option_strings
    assert "--visible-report-text" in option_strings
    assert "--planner-result-json" in option_strings
    assert "--caller-context-json" in option_strings

    for forbidden_option in {
        "--write",
        "--write-enabled",
        "--output",
        "--output-path",
        "--create-dir",
        "--mkdir",
        "--overwrite",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
        "--production",
    }:
        assert forbidden_option not in option_strings


def test_current_dry_run_bridge_remains_dry_run_only() -> None:
    source = _read(DRY_RUN_BRIDGE_PATH)

    assert "CONTROLLED_DRY_RUN_ACCEPTED" in source
    assert '"write_requested": False' in source
    assert '"write_performed": False' in source
    assert '"artifact_created_on_disk": False' in source
    assert "Only dry-run mode is supported" in source
    assert "write_requested must remain false" in source


def test_implementation_source_still_has_no_prohibited_runtime_integrations() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    for marker in [
        ".mkdir(",
        ".rmdir(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "shutil",
        "Popen",
        "os.system",
        "import subprocess",
        "subprocess.",
        "socket.",
        "requests.",
        "urllib.",
        "http.client",
        "scanner_execution_performed = True",
        "ffprobe_execution_performed = True",
        "ffmpeg_execution_performed = True",
        "external_process_execution_performed = True",
        "network_access_performed = True",
        "saas_or_database_access_performed = True",
        "directory_creation_performed = True",
        "overwrite_performed = True",
    ]:
        assert marker not in source
