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
    "controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate.py"
)

CONTROLLED_IMPL_QA_CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_closure_review_v1.md"
)

CONTROLLED_IMPL_QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation_qa_gate_v1.md"
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
    "CLI.INTEGRATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_READINESS_GATE_PASS_READY_FOR_"
    "CLI_INTEGRATION_CONTRACT"
)

PREVIOUS_COMMIT = "bb9ef418fa278a9a29e6d745bcb478859e10beca"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-controlled-impl-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-readiness-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTRACT.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        CONTROLLED_IMPL_QA_CLOSURE_REVIEW_DOC_PATH,
        CONTROLLED_IMPL_QA_GATE_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_readiness_review_exist(path: Path) -> None:
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
        "This is a doc/test-only readiness gate.",
        "This readiness gate defines the future CLI integration boundary.",
        "This readiness gate does not add CLI write flags.",
        "This readiness gate does not connect the controlled write-enabled primitive to command execution.",
        "This readiness gate does not modify the current dry-run CLI.",
        "This readiness gate does not modify the current dry-run bridge.",
        "This readiness gate does not add runtime implementation.",
        "This readiness gate does not write artifacts from the command line.",
        "This readiness gate does not authorize client-facing usage.",
        "This readiness gate does not authorize production usage.",
    ],
)
def test_readiness_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target closure review test passed with 110 checks.",
        "QA gate test passed with 183 checks.",
        "controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target closure review tag absent locally before tagging.",
        "target closure review tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target closure review test passed with 110 checks.",
        "final QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final readiness gate test passed with 322 checks.",
        "final contract QA closure review test passed with 266 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`export_controlled_visible_report_text_artifact`",
        "`CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`",
        "`controlled_visible_report.controlled.txt`",
        "`single fixture-owned controlled text artifact`",
        "`UTF-8 bytes and SHA256 before and after write`",
    ],
)
def test_current_accepted_primitive_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The CLI integration boundary is ready to be specified in a future contract.",
        "The current dry-run CLI must remain dry-run-only during this readiness gate.",
        "The current dry-run bridge must remain dry-run-only during this readiness gate.",
        "The controlled primitive must not be reachable from current user-facing command execution during this readiness gate.",
        "The current command parser must not receive write flags during this readiness gate.",
        "The current command parser must not receive output path flags during this readiness gate.",
        "The current command parser must not receive overwrite flags during this readiness gate.",
    ],
)
def test_cli_integration_readiness_decision_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI integration contract may define a controlled write-enabled CLI mode.",
        "That future contract must remain separate from the current dry-run-only command.",
        "That future contract must require explicit write authorization.",
        "That future contract must require explicit controlled output root.",
        "That future contract must preserve no-overwrite behavior.",
        "That future contract must preserve no directory creation unless a later explicit contract authorizes it.",
        "That future contract must preserve one artifact only.",
        "That future contract must preserve byte and SHA256 verification.",
        "That future contract must preserve conservative safety flags.",
        "That future contract must preserve clear dry-run/write-enabled separation.",
        "That future contract must reject production, client-facing, and public demo use until explicitly authorized later.",
    ],
)
def test_future_cli_integration_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "whether write-enabled export is a separate command or a separate subcommand.",
        "whether the dry-run command remains immutable.",
        "how explicit authorization is passed.",
        "how controlled output root is passed.",
        "how fixture-owned roots are verified.",
        "how result JSON reports write status.",
        "how failures remain fail-closed.",
        "how no-overwrite is surfaced.",
        "how safety flags are surfaced.",
        "how tests prevent accidental production use.",
    ],
)
def test_required_future_cli_contract_questions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize CLI integration.",
        "This readiness gate does not authorize command-line write flags.",
        "This readiness gate does not authorize output path flags.",
        "This readiness gate does not authorize overwrite flags.",
        "This readiness gate does not authorize writing from user-facing command execution.",
        "This readiness gate does not authorize writing outside fixture-owned roots.",
        "This readiness gate does not authorize directory creation.",
        "This readiness gate does not authorize overwrite.",
        "This readiness gate does not authorize multiple artifacts.",
        "This readiness gate does not authorize arbitrary cleanup.",
        "This readiness gate does not authorize real media access.",
        "This readiness gate does not authorize scanner execution.",
        "This readiness gate does not authorize ffprobe execution.",
        "This readiness gate does not authorize FFmpeg execution.",
        "This readiness gate does not authorize external process execution.",
        "This readiness gate does not authorize network access.",
        "This readiness gate does not authorize SaaS integration.",
        "This readiness gate does not authorize database integration.",
        "This readiness gate does not authorize backend changes.",
        "This readiness gate does not authorize frontend changes.",
        "This readiness gate does not authorize installer work.",
        "This readiness gate does not authorize client-facing demo work.",
        "This readiness gate does not authorize public demo work.",
        "This readiness gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_readiness_gate_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export primitive is ready for a future CLI integration contract." in doc
    assert "The current project remains dry-run-only from the command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only define the CLI integration contract." in doc


def test_previous_closure_review_supports_readiness_gate() -> None:
    source = _read(CONTROLLED_IMPL_QA_CLOSURE_REVIEW_DOC_PATH)

    assert "The controlled write-enabled export implementation QA gate is accepted and closed." in source
    assert "The current project has a QA-accepted controlled fixture-owned write-enabled export primitive." in source
    assert "The current project remains not ready for CLI write-enabled export." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not add CLI write flags." in source
    assert "That next step must not connect the primitive to user-facing command execution." in source


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


def test_controlled_primitive_still_requires_fixture_owned_root(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Readiness gate controlled report\n",
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


def test_controlled_primitive_still_rejects_current_repo_root() -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Readiness gate report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="Readiness gate report",
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
