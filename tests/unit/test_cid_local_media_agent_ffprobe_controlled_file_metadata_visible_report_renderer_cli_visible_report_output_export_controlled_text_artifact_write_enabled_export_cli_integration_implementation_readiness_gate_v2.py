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
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.py"
)

IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review_v1.md"
)

IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review.py"
)

IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_v1.md"
)

IMPLEMENTATION_CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_v1.md"
)

IMPLEMENTATION_READINESS_V1_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v1.md"
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
    "CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V2"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_READINESS_GATE_V2_PASS_READY_FOR_"
    "IMPLEMENTATION_AUTHORIZATION_GATE"
)

PREVIOUS_COMMIT = "3d7b4dc2f7d6ab91bc707108b8247d88f9afc778"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-qa-closure-review-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-readiness-gate-v2-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.AUTHORIZATION.GATE.V1"
)

FUTURE_ISOLATED_CLI_MODULE = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_v2_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_v2_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH,
        IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_TEST_PATH,
        IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH,
        IMPLEMENTATION_CONTRACT_DOC_PATH,
        IMPLEMENTATION_READINESS_V1_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_readiness_v2_review_exist(path: Path) -> None:
    assert path.is_file()


def test_future_isolated_cli_module_is_not_created_in_readiness_v2() -> None:
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
        "This is a doc/test-only readiness gate.",
        "This readiness gate evaluates whether a later strict implementation authorization gate may be prepared.",
        "This readiness gate does not implement CLI code.",
        "This readiness gate does not create the future isolated CLI module.",
        "This readiness gate does not add command-line write flags.",
        "This readiness gate does not add output path flags.",
        "This readiness gate does not add overwrite flags.",
        "This readiness gate does not connect `export_controlled_visible_report_text_artifact` to current command execution.",
        "This readiness gate does not modify the current dry-run CLI.",
        "This readiness gate does not modify the current dry-run bridge.",
        "This readiness gate does not write artifacts from the command line.",
        "This readiness gate does not authorize client-facing usage.",
        "This readiness gate does not authorize production usage.",
    ],
)
def test_readiness_v2_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration implementation contract QA gate closure review test passed with 175 checks.",
        "previous CLI integration implementation contract QA gate test passed with 243 checks.",
        "previous CLI integration implementation contract test passed with 235 checks.",
        "previous CLI integration implementation readiness gate test passed with 179 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target closure review tag was absent locally before tagging.",
        "target closure review tag was absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration implementation contract QA gate closure review test passed with 175 checks.",
        "final CLI integration implementation contract QA gate test passed with 243 checks.",
        "final CLI integration implementation contract test passed with 235 checks.",
        "final CLI integration implementation readiness gate test passed with 179 checks.",
        "final CLI integration contract QA closure review test passed with 132 checks.",
        "final controlled implementation QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_v2_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the implementation contract QA gate closure review is closed.",
        "the implementation contract QA gate is closed.",
        "the implementation contract is accepted.",
        "the implementation readiness gate v1 is closed.",
        "this readiness gate remains doc/test-only.",
        "the future isolated CLI module has not been created.",
        "no CLI implementation has been added.",
        "no command-line write flags have been added to the current dry-run CLI.",
        "no output path flags have been added to the current dry-run CLI.",
        "no overwrite flags have been added.",
        "the current dry-run CLI remains dry-run-only.",
        "the current dry-run bridge remains dry-run-only.",
        "the accepted write-enabled primitive remains isolated from current command execution.",
        "the future isolated CLI module name remains reserved.",
        "the future command identity remains reserved.",
        "the future allowed argument set remains constrained.",
        "the future forbidden argument set remains constrained.",
        "future implementation remains limited to fixture-owned controlled output roots unless a later explicit root-policy gate changes that.",
        "future implementation preserves exact write authorization.",
        "future implementation preserves no-overwrite behavior.",
        "future implementation preserves no-directory-creation behavior.",
        "future implementation preserves single-artifact behavior.",
        "future implementation preserves byte count verification.",
        "future implementation preserves SHA256 verification.",
        "future implementation preserves conservative safety flags.",
        "future implementation preserves fail-closed behavior.",
    ],
)
def test_readiness_v2_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A later strict implementation authorization gate may be prepared.",
        "That later authorization gate must decide whether actual implementation can begin.",
        "That later authorization gate must still be separate from implementation.",
        "That later authorization gate must define the exact files allowed for implementation.",
        "That later authorization gate must define the exact parser behavior allowed for implementation.",
        "That later authorization gate must define the exact command return behavior allowed for implementation.",
        "That later authorization gate must define the exact test matrix required before implementation.",
        "That later authorization gate must define whether a new isolated CLI module can be created.",
        "That later authorization gate must not modify runtime code unless the phase explicitly authorizes it.",
    ],
)
def test_implementation_authorization_readiness_decision_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        FUTURE_ISOLATED_CLI_MODULE,
        "The current dry-run CLI must remain out of implementation scope.",
        "The current dry-run bridge must remain out of implementation scope.",
        "The controlled write-enabled primitive may be imported only by the future isolated CLI module if a later implementation phase explicitly authorizes it.",
    ],
)
def test_future_implementation_file_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "isolated CLI parser construction.",
        "allowed argument set.",
        "forbidden unsafe alias rejection.",
        "unknown argument rejection.",
        "dry-run mode without artifact creation.",
        "missing visible report text rejection.",
        "missing controlled output root rejection.",
        "missing write authorization rejection.",
        "dry-run authorization rejection.",
        "unknown authorization rejection.",
        "repository root rejection.",
        "existing artifact rejection.",
        "no directory creation.",
        "no overwrite.",
        "deterministic JSON result fields.",
        "non-zero exit for rejected inputs.",
        "zero exit for valid dry-run.",
        "zero exit for verified fixture-owned controlled write.",
        "current dry-run CLI remains unchanged.",
        "current dry-run bridge remains unchanged.",
        "future isolated CLI does not execute scanner.",
        "future isolated CLI does not execute ffprobe.",
        "future isolated CLI does not execute FFmpeg.",
        "future isolated CLI does not use external process execution.",
        "future isolated CLI does not use network.",
        "future isolated CLI does not use SaaS or database integration.",
    ],
)
def test_future_test_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize CLI implementation.",
        "This readiness gate does not authorize creation of the future isolated CLI module.",
        "This readiness gate does not authorize command-line write flags in the current dry-run CLI.",
        "This readiness gate does not authorize output path flags in the current dry-run CLI.",
        "This readiness gate does not authorize overwrite flags.",
        "This readiness gate does not authorize writing from current user-facing command execution.",
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


def test_readiness_v2_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The write-enabled export CLI integration implementation readiness gate v2 passes." in doc
    assert "A later strict implementation authorization gate may be prepared." in doc
    assert "The current project remains dry-run-only from the current command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only unless it explicitly and narrowly authorizes a subsequent implementation phase." in doc
    assert "That next step must not implement CLI code." in doc
    assert "That next step must not create the future isolated CLI module." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only decide whether a later controlled implementation phase can be authorized." in doc


def test_previous_closure_review_supports_readiness_v2() -> None:
    source = _read(IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH)

    assert "The controlled implementation contract QA gate is closed." in source
    assert "The controlled implementation contract remains accepted." in source
    assert "The future CLI integration implementation readiness gate may be prepared." in source
    assert "The current project remains dry-run-only from the current command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only unless explicitly replaced by a stricter implementation authorization gate." in source
    assert "That next step must not implement CLI code." in source
    assert "That next step must not create the future isolated CLI module." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only decide whether a controlled implementation phase can be authorized later." in source


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
        visible_report_text="CLI integration implementation readiness gate v2 controlled report\n",
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
        visible_report_text="CLI integration implementation readiness gate v2 report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation readiness gate v2 report",
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
