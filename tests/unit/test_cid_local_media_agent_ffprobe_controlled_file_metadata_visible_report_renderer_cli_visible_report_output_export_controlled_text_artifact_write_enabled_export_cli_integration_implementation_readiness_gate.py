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
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate.py"
)

CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review_v1.md"
)

CLOSURE_REVIEW_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_qa_gate_v1.md"
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
    "CLI.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_"
    "CONTROLLED_IMPLEMENTATION_CONTRACT"
)

PREVIOUS_COMMIT = "fb96f0c5d2d9e3890b97158380103680b1addcc9"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-qa-closure-review-v1-20260629"
)

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-readiness-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        CLOSURE_REVIEW_DOC_PATH,
        CLOSURE_REVIEW_TEST_PATH,
        QA_GATE_DOC_PATH,
        CONTRACT_DOC_PATH,
        READINESS_DOC_PATH,
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
        "This is a doc/test-only implementation readiness gate.",
        "This readiness gate decides whether a later controlled implementation contract may be prepared.",
        "This readiness gate does not implement CLI code.",
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
def test_readiness_gate_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration contract QA closure review test passed with 132 checks.",
        "previous CLI integration contract QA gate test passed with 173 checks.",
        "previous CLI integration contract test passed with 189 checks.",
        "previous CLI integration readiness test passed with 113 checks.",
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
        "final target CLI integration contract QA closure review test passed with 132 checks.",
        "final CLI integration contract QA gate test passed with 173 checks.",
        "final CLI integration contract test passed with 189 checks.",
        "final CLI integration readiness test passed with 113 checks.",
        "final controlled implementation QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the closure review is closed.",
        "the CLI integration contract QA gate is closed.",
        "the CLI integration contract is accepted.",
        "the current CLI remains dry-run-only.",
        "the current dry-run bridge remains dry-run-only.",
        "the write-enabled primitive remains not connected to command execution.",
        "no command-line write flags exist in the current dry-run CLI.",
        "no output path flags exist in the current dry-run CLI.",
        "no overwrite flags exist in the current dry-run CLI.",
        "no current user-facing command can write an artifact.",
        "future implementation remains limited to controlled write-enabled integration.",
        "future implementation must preserve explicit write authorization.",
        "future implementation must preserve controlled output root validation.",
        "future implementation must preserve fixture-owned root restrictions unless a later explicit root-policy contract changes that.",
        "future implementation must preserve single-artifact behavior.",
        "future implementation must preserve no-overwrite behavior.",
        "future implementation must preserve byte count verification.",
        "future implementation must preserve SHA256 verification.",
        "future implementation must preserve deterministic result JSON.",
        "future implementation must preserve conservative safety flags.",
        "future implementation must fail closed on invalid input.",
        "future implementation must keep dry-run and write-enabled command paths separated.",
    ],
)
def test_readiness_acceptance_criteria_are_recorded(required_text: str) -> None:
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
def test_accepted_primitive_under_readiness_gate_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "a separate CLI module dedicated to controlled write-enabled export; or",
        "an isolated write-enabled subcommand that cannot change current dry-run behavior.",
        "This readiness gate does not choose the final implementation design.",
        "This readiness gate does not authorize implementation.",
        "This readiness gate only allows a later implementation contract to define the final implementation design.",
    ],
)
def test_future_implementation_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact command name or module name.",
        "exact allowed arguments.",
        "explicit write authorization argument.",
        "explicit controlled output root argument.",
        "visible report text input policy.",
        "planner result JSON input policy, if any.",
        "caller context JSON input policy, if any.",
        "deterministic result JSON schema.",
        "controlled error schema.",
        "safety flag schema.",
        "dry-run/write-enabled separation rule.",
        "no-overwrite behavior.",
        "fixture-owned root restriction.",
        "no directory creation behavior.",
        "no real media access behavior.",
        "no scanner execution behavior.",
        "no ffprobe execution behavior.",
        "no FFmpeg execution behavior.",
        "no network behavior.",
        "no SaaS integration behavior.",
        "no database integration behavior.",
        "no client-facing behavior.",
        "no production behavior.",
    ],
)
def test_mandatory_constraints_for_later_implementation_contract_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "missing write authorization.",
        "dry-run authorization.",
        "unknown write authorization.",
        "missing controlled output root.",
        "uncontrolled output root.",
        "current working directory as output root.",
        "repository root as output root.",
        "existing artifact path.",
        "unsupported filename.",
        "path traversal.",
        "overwrite request.",
        "directory creation request.",
        "production mode request.",
        "client-facing mode request.",
        "public demo mode request.",
        "real media access request.",
        "scanner execution request.",
        "ffprobe execution request.",
        "FFmpeg execution request.",
        "network request.",
        "SaaS integration request.",
        "database integration request.",
    ],
)
def test_mandatory_rejection_cases_for_later_implementation_contract_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the current dry-run CLI parser has no write-enabled options.",
        "the current dry-run CLI does not import the write-enabled primitive.",
        "the current dry-run bridge does not import the write-enabled primitive.",
        "the current dry-run bridge remains dry-run-only.",
        "the write-enabled primitive still requires explicit authorization.",
        "the write-enabled primitive still rejects dry-run authorization.",
        "the write-enabled primitive still rejects repository root output.",
        "the write-enabled primitive still rejects existing artifacts.",
        "the write-enabled primitive still performs no directory creation.",
        "the write-enabled primitive still performs no overwrite.",
        "the write-enabled primitive still performs no external process execution.",
        "the write-enabled primitive still performs no network access.",
        "the write-enabled primitive still performs no SaaS or database access.",
    ],
)
def test_mandatory_compatibility_checks_for_later_implementation_contract_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize CLI implementation.",
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

    assert "The write-enabled export CLI integration implementation readiness gate passes." in doc
    assert "A later controlled implementation contract may be prepared." in doc
    assert "The current project remains dry-run-only from the command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not implement CLI code." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only define a future controlled implementation contract." in doc


def test_closure_review_document_supports_implementation_readiness_gate() -> None:
    source = _read(CLOSURE_REVIEW_DOC_PATH)

    assert "The write-enabled export CLI integration contract QA gate is closed." in source
    assert "The future CLI integration implementation readiness gate may be prepared." in source
    assert "The current project remains dry-run-only from the command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not implement CLI code." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source


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
        visible_report_text="CLI integration implementation readiness gate controlled report\n",
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
        visible_report_text="CLI integration implementation readiness gate report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation readiness gate report",
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
