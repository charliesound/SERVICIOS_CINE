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
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate.py"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_v1.md"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate_v1.md"
)

CONTROLLED_IMPL_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
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
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_"
    "CLI_INTEGRATION_IMPLEMENTATION_READINESS_GATE"
)

PREVIOUS_COMMIT = "463ab4212e30d9a7290f6a4bc1604ba53e90efeb"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V1"
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
        CONTRACT_DOC_PATH,
        READINESS_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
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
        "This closure review closes the write-enabled export CLI integration contract QA gate.",
        "This closure review does not implement CLI integration.",
        "This closure review does not add command-line write flags.",
        "This closure review does not add output path flags.",
        "This closure review does not add overwrite flags.",
        "This closure review does not connect `export_controlled_visible_report_text_artifact` to current command execution.",
        "This closure review does not modify the current dry-run CLI.",
        "This closure review does not modify the current dry-run bridge.",
        "This closure review does not write artifacts from the command line.",
        "This closure review does not authorize client-facing usage.",
        "This closure review does not authorize production usage.",
    ],
)
def test_closure_review_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration contract QA gate test passed with 173 checks.",
        "previous CLI integration contract test passed with 189 checks.",
        "previous CLI integration readiness test passed with 113 checks.",
        "previous controlled implementation QA closure review test passed with 110 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target CLI integration contract QA gate tag was absent locally before tagging.",
        "target CLI integration contract QA gate tag was absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration contract QA gate test passed with 173 checks.",
        "final CLI integration contract test passed with 189 checks.",
        "final CLI integration readiness test passed with 113 checks.",
        "final controlled implementation QA closure review test passed with 110 checks.",
        "final controlled implementation QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
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
        "the QA gate accepts the CLI integration contract.",
        "the QA gate does not implement CLI integration.",
        "the QA gate does not add command-line write flags.",
        "the QA gate does not add output path flags.",
        "the QA gate does not add overwrite flags.",
        "the QA gate does not connect the write-enabled primitive to current command execution.",
        "the QA gate does not modify the current dry-run CLI.",
        "the QA gate does not modify the current dry-run bridge.",
        "the QA gate preserves current dry-run-only command behavior.",
        "the QA gate preserves current dry-run-only bridge behavior.",
        "the QA gate confirms future CLI integration must use a separate explicit command path.",
        "the QA gate confirms future CLI integration must require explicit write authorization.",
        "the QA gate confirms future CLI integration must require explicit controlled output root.",
        "the QA gate confirms future CLI integration must preserve fixture-owned root validation.",
        "the QA gate confirms future CLI integration must preserve single-artifact behavior.",
        "the QA gate confirms future CLI integration must preserve no-overwrite behavior.",
        "the QA gate confirms future CLI integration must preserve byte count verification.",
        "the QA gate confirms future CLI integration must preserve SHA256 verification.",
        "the QA gate confirms future CLI integration must preserve deterministic result JSON.",
        "the QA gate confirms future CLI integration must preserve conservative safety flags.",
        "the QA gate confirms future CLI integration must fail closed on invalid input.",
        "the QA gate confirms future CLI integration must keep dry-run and write-enabled results clearly separated.",
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
        "`single fixture-owned controlled text artifact`",
        "`NO_OVERWRITE`",
        "`UTF-8 bytes and SHA256 before and after write`",
    ],
)
def test_accepted_primitive_under_closure_review_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The current CLI remains dry-run-only.",
        "The current dry-run bridge remains dry-run-only.",
        "The write-enabled primitive remains not connected to command execution.",
        "No command-line write flags are authorized.",
        "No output path flags are authorized.",
        "No overwrite flags are authorized.",
        "No user-facing write execution is authorized.",
    ],
)
def test_cli_state_after_closure_review_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI integration implementation readiness gate must be created before any CLI implementation.",
        "That future readiness gate must remain doc/test-only.",
        "That future readiness gate must decide whether a later implementation phase may add a separate write-enabled CLI module or an isolated subcommand.",
        "That future readiness gate must not implement CLI code.",
        "That future readiness gate must not add write flags.",
        "That future readiness gate must not connect the primitive to command execution.",
        "That future readiness gate must prove the current dry-run CLI and dry-run bridge remain unchanged.",
        "That future readiness gate must preserve all explicit rejection cases from the accepted contract.",
        "That future readiness gate must preserve all safety flag expectations from the accepted contract.",
    ],
)
def test_required_future_implementation_readiness_gate_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize CLI implementation.",
        "This closure review does not authorize command-line write flags.",
        "This closure review does not authorize output path flags.",
        "This closure review does not authorize overwrite flags.",
        "This closure review does not authorize writing from user-facing command execution.",
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

    assert "The write-enabled export CLI integration contract QA gate is closed." in doc
    assert "The future CLI integration implementation readiness gate may be prepared." in doc
    assert "The current project remains dry-run-only from the command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not implement CLI code." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only decide whether a future implementation phase may add isolated write-enabled CLI integration." in doc


def test_qa_gate_document_supports_closure_review() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "The write-enabled export CLI integration contract is accepted by QA gate." in source
    assert "The current project remains dry-run-only from the command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only close this QA gate." in source


def test_current_dry_run_cli_has_no_write_enabled_options() -> None:
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
        "--write-artifact",
        "--output",
        "--output-path",
        "--output-root",
        "--artifact-path",
        "--create-dir",
        "--mkdir",
        "--overwrite",
        "--force",
        "--production",
        "--client",
        "--public-demo",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
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
    assert "export_controlled_visible_report_text_artifact" not in source


def test_current_dry_run_cli_does_not_import_write_enabled_primitive() -> None:
    source = _read(DRY_RUN_CLI_PATH)

    assert "export_controlled_visible_report_text_artifact" not in source
    assert "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY" not in source
    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export" not in source


def test_controlled_primitive_still_requires_explicit_authorization_and_fixture_root(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration contract QA closure review controlled report\n",
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


def test_controlled_primitive_still_rejects_repo_root() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration contract QA closure review report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration contract QA closure review report",
        controlled_output_root=tmp_path,
        write_authorization="CONTROLLED_DRY_RUN_ACCEPTED",
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "write authorization is dry-run-only" in result["errors"]


def test_current_dry_run_cli_source_has_no_forbidden_runtime_markers() -> None:
    source = _read(DRY_RUN_CLI_PATH)

    for marker in [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        "open(",
        "Popen",
        "socket",
        "requests",
        "urllib",
        "http.client",
    ]:
        assert marker not in source

    assert "sub" + "process" not in source


def test_write_enabled_implementation_source_has_no_prohibited_runtime_integrations() -> None:
    source = _read(CONTROLLED_IMPL_MODULE_PATH)

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
