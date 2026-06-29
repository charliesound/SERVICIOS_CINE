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
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review.py"
)

IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_v1.md"
)

IMPLEMENTATION_CONTRACT_QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate.py"
)

IMPLEMENTATION_CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_v1.md"
)

IMPLEMENTATION_CONTRACT_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract.py"
)

IMPLEMENTATION_READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v1.md"
)

CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review_v1.md"
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

FUTURE_ISOLATED_CLI_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_CONTRACT_QA_GATE_"
    "CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_IMPLEMENTATION_READINESS_GATE"
)

PREVIOUS_COMMIT = "ddaf786dc5057a587197581d84b229b8e40da072"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-qa-gate-v1-20260629"

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-qa-closure-review-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V2"
)

FUTURE_ISOLATED_CLI_MODULE = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

FUTURE_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH,
        IMPLEMENTATION_CONTRACT_QA_GATE_TEST_PATH,
        IMPLEMENTATION_CONTRACT_DOC_PATH,
        IMPLEMENTATION_CONTRACT_TEST_PATH,
        IMPLEMENTATION_READINESS_DOC_PATH,
        CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_closure_review_exist(path: Path) -> None:
    assert path.is_file()


def test_future_isolated_cli_module_is_not_created_in_this_closure_review_phase() -> None:
    assert not FUTURE_ISOLATED_CLI_MODULE_PATH.exists()


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
        "This closure review closes the controlled implementation contract QA gate.",
        "This closure review decides whether a later controlled implementation readiness gate may be prepared.",
        "This closure review does not implement CLI code.",
        "This closure review does not create the future isolated CLI module.",
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
        "target CLI integration implementation contract QA gate test passed with 243 checks.",
        "previous CLI integration implementation contract test passed with 235 checks.",
        "previous CLI integration implementation readiness gate test passed with 179 checks.",
        "previous CLI integration contract QA closure review test passed with 132 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target QA gate tag was absent locally before tagging.",
        "target QA gate tag was absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration implementation contract QA gate test passed with 243 checks.",
        "final CLI integration implementation contract test passed with 235 checks.",
        "final CLI integration implementation readiness gate test passed with 179 checks.",
        "final CLI integration contract QA closure review test passed with 132 checks.",
        "final CLI integration contract QA gate test passed with 173 checks.",
        "final CLI integration contract test passed with 189 checks.",
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
        "the controlled implementation contract QA gate is closed.",
        "the controlled implementation contract is accepted.",
        "the implementation readiness gate is closed.",
        "the controlled implementation contract remains doc/test-only.",
        "the controlled implementation contract QA gate remains doc/test-only.",
        "this closure review remains doc/test-only.",
        "the future isolated CLI module has not been created.",
        "no CLI implementation has been added.",
        "no command-line write flags have been added to the current dry-run CLI.",
        "no output path flags have been added to the current dry-run CLI.",
        "no overwrite flags have been added.",
        "the current dry-run CLI remains dry-run-only.",
        "the current dry-run bridge remains dry-run-only.",
        "the accepted write-enabled primitive remains isolated from current command execution.",
        "the future isolated CLI module name remains explicitly reserved.",
        "the future command identity remains explicitly defined.",
        "the future allowed argument set remains explicitly defined.",
        "the future forbidden argument set remains explicitly defined.",
        "the future dry-run behavior remains explicitly defined.",
        "the future controlled write behavior remains explicitly defined.",
        "the future result JSON schema remains explicitly defined.",
        "the future exit code policy remains explicitly defined.",
        "the future mandatory rejection cases remain explicitly defined.",
        "the future mandatory compatibility checks remain explicitly defined.",
        "future implementation remains limited to fixture-owned controlled output roots.",
        "future implementation preserves explicit write authorization.",
        "future implementation preserves no-overwrite behavior.",
        "future implementation preserves no-directory-creation behavior.",
        "future implementation preserves single-artifact behavior.",
        "future implementation preserves byte count verification.",
        "future implementation preserves SHA256 verification.",
        "future implementation preserves conservative safety flags.",
        "future implementation preserves fail-closed behavior.",
    ],
)
def test_closure_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "After this closure review, a later controlled implementation readiness gate may be prepared.",
        "That later readiness gate may evaluate whether the reserved isolated module can be implemented safely.",
        FUTURE_ISOLATED_CLI_MODULE,
        FUTURE_COMMAND_NAME,
        "The current dry-run CLI must remain separate.",
        "The current dry-run bridge must remain separate.",
        "The accepted primitive must remain isolated until a later explicit implementation phase authorizes integration.",
    ],
)
def test_future_isolated_cli_boundary_after_closure_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`--visible-report-text`",
        "`--controlled-output-root`",
        "`--write-authorization`",
        "`--result-json`",
        "`--dry-run`",
        "`--output`",
        "`--output-path`",
        "`--artifact-path`",
        "`--overwrite`",
        "`--force`",
        "`--create-dir`",
        "`--mkdir`",
        "`--production`",
        "`--client`",
        "`--public-demo`",
        "`--ffprobe`",
        "`--ffmpeg`",
        "`--network`",
        "`--database`",
    ],
)
def test_accepted_future_argument_policy_after_closure_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "no artifact creation.",
        "`dry_run_requested` true.",
        "`write_requested` false.",
        "`write_performed` false.",
        "`artifact_created_on_disk` false.",
        "`verification_status` equal to `DRY_RUN_ONLY`.",
        "requires visible report text.",
        "requires controlled output root.",
        "requires exact write authorization.",
        "uses `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.",
        "calls `export_controlled_visible_report_text_artifact`.",
        "preserves fixture-owned root validation.",
        "preserves filename `controlled_visible_report.controlled.txt`.",
        "preserves no-overwrite behavior.",
        "preserves no-directory-creation behavior.",
        "preserves UTF-8 byte count verification.",
        "preserves SHA256 verification.",
        "preserves deterministic result dictionary.",
        "preserves conservative safety flags.",
        "preserves fail-closed behavior.",
    ],
)
def test_accepted_future_behavior_after_closure_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize CLI implementation.",
        "This closure review does not authorize creation of the future isolated CLI module.",
        "This closure review does not authorize command-line write flags in the current dry-run CLI.",
        "This closure review does not authorize output path flags in the current dry-run CLI.",
        "This closure review does not authorize overwrite flags.",
        "This closure review does not authorize writing from current user-facing command execution.",
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

    assert "The controlled implementation contract QA gate is closed." in doc
    assert "The controlled implementation contract remains accepted." in doc
    assert "The future CLI integration implementation readiness gate may be prepared." in doc
    assert "The current project remains dry-run-only from the current command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only unless explicitly replaced by a stricter implementation authorization gate." in doc
    assert "That next step must not implement CLI code." in doc
    assert "That next step must not create the future isolated CLI module." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only decide whether a controlled implementation phase can be authorized later." in doc


def test_implementation_contract_qa_gate_document_supports_closure_review() -> None:
    source = _read(IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH)

    assert "The controlled implementation contract QA gate passes." in source
    assert "The controlled implementation contract is accepted for closure review." in source
    assert "A later controlled implementation contract QA gate closure review may be prepared." in source
    assert "The current project remains dry-run-only from the current command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not implement CLI code." in source
    assert "That next step must not create the future isolated CLI module." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only close this controlled implementation contract QA gate." in source


def test_reserved_future_isolated_cli_module_does_not_exist() -> None:
    assert not FUTURE_ISOLATED_CLI_MODULE_PATH.exists()


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
        visible_report_text="CLI integration implementation contract QA closure review controlled report\n",
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
        visible_report_text="CLI integration implementation contract QA closure review report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation contract QA closure review report",
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
