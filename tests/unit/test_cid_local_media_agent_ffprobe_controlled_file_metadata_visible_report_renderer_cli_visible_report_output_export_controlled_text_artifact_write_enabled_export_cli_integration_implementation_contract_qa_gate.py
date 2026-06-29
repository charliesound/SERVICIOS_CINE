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
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
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

IMPLEMENTATION_READINESS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate.py"
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
    "CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_CONTRACT_QA_GATE_PASS"
)

PREVIOUS_COMMIT = "051c9d73220c6f1b7317ff5b16d8bf388bdb8178"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-contract-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)

FUTURE_ISOLATED_CLI_MODULE = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

FUTURE_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        IMPLEMENTATION_CONTRACT_DOC_PATH,
        IMPLEMENTATION_CONTRACT_TEST_PATH,
        IMPLEMENTATION_READINESS_DOC_PATH,
        IMPLEMENTATION_READINESS_TEST_PATH,
        CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_qa_review_exist(path: Path) -> None:
    assert path.is_file()


def test_future_isolated_cli_module_is_not_created_in_this_qa_gate_phase() -> None:
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
        "This is a doc/test-only QA gate.",
        "This QA gate audits the controlled implementation contract for a future isolated write-enabled CLI.",
        "This QA gate does not implement CLI code.",
        "This QA gate does not create the future isolated CLI module.",
        "This QA gate does not add command-line write flags.",
        "This QA gate does not add output path flags.",
        "This QA gate does not add overwrite flags.",
        "This QA gate does not connect `export_controlled_visible_report_text_artifact` to current command execution.",
        "This QA gate does not modify the current dry-run CLI.",
        "This QA gate does not modify the current dry-run bridge.",
        "This QA gate does not write artifacts from the command line.",
        "This QA gate does not authorize client-facing usage.",
        "This QA gate does not authorize production usage.",
    ],
)
def test_qa_gate_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration implementation contract test passed with 235 checks.",
        "previous CLI integration implementation readiness gate test passed with 179 checks.",
        "previous CLI integration contract QA closure review test passed with 132 checks.",
        "previous CLI integration contract test passed with 189 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target implementation contract tag was absent locally before tagging.",
        "target implementation contract tag was absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration implementation contract test passed with 235 checks.",
        "final CLI integration implementation readiness gate test passed with 179 checks.",
        "final CLI integration contract QA closure review test passed with 132 checks.",
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
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the controlled implementation contract document exists.",
        "the controlled implementation contract test exists.",
        "the controlled implementation readiness gate is closed.",
        "the controlled implementation contract is doc/test-only.",
        "the controlled implementation contract does not implement CLI code.",
        "the controlled implementation contract does not create the future isolated CLI module.",
        "the controlled implementation contract does not modify the current dry-run CLI.",
        "the controlled implementation contract does not modify the current dry-run bridge.",
        "the controlled implementation contract does not add write-enabled behavior to the current dry-run command.",
        "the controlled implementation contract selects a separate future isolated CLI module.",
        "the future isolated CLI module name is explicitly reserved.",
        "the future command identity is explicitly defined.",
        "the future allowed arguments are explicitly defined.",
        "the future forbidden arguments are explicitly defined.",
        "the future dry-run behavior is explicitly defined.",
        "the future controlled write behavior is explicitly defined.",
        "the future result JSON schema is explicitly defined.",
        "the future exit code policy is explicitly defined.",
        "the future mandatory rejection cases are explicitly defined.",
        "the future mandatory compatibility checks are explicitly defined.",
        "the future implementation remains limited to fixture-owned controlled output roots.",
        "the future implementation preserves explicit write authorization.",
        "the future implementation preserves no-overwrite behavior.",
        "the future implementation preserves no-directory-creation behavior.",
        "the future implementation preserves single-artifact behavior.",
        "the future implementation preserves byte count verification.",
        "the future implementation preserves SHA256 verification.",
        "the future implementation preserves conservative safety flags.",
        "the future implementation preserves fail-closed behavior.",
        "the current CLI remains dry-run-only.",
        "the current bridge remains dry-run-only.",
        "the accepted write-enabled primitive remains isolated from current command execution.",
    ],
)
def test_qa_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        FUTURE_ISOLATED_CLI_MODULE,
        "This QA gate verifies that the reserved future module is not created in this QA gate.",
        "This QA gate verifies that no write-enabled CLI implementation exists yet.",
        "This QA gate verifies that the current dry-run CLI remains unchanged in behavior.",
        "This QA gate verifies that the current dry-run bridge remains unchanged in behavior.",
    ],
)
def test_future_isolated_cli_module_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        FUTURE_COMMAND_NAME,
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
def test_future_command_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "must not create an artifact.",
        "must report `dry_run_requested` as true.",
        "must report `write_requested` as false.",
        "must report `write_performed` as false.",
        "must report `artifact_created_on_disk` as false.",
        "must report `verification_status` as `DRY_RUN_ONLY`.",
    ],
)
def test_future_dry_run_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "must require visible report text.",
        "must require controlled output root.",
        "must require exact write authorization.",
        "must use `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.",
        "must call `export_controlled_visible_report_text_artifact`.",
        "must preserve fixture-owned root validation.",
        "must preserve filename `controlled_visible_report.controlled.txt`.",
        "must preserve no-overwrite behavior.",
        "must preserve no-directory-creation behavior.",
        "must preserve UTF-8 byte count verification.",
        "must preserve SHA256 verification.",
        "must preserve deterministic result dictionary.",
        "must preserve conservative safety flags.",
        "must preserve fail-closed behavior.",
    ],
)
def test_future_write_enabled_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "phase.",
        "cli_contract_version.",
        "command_name.",
        "module_name.",
        "mode.",
        "dry_run_requested.",
        "write_requested.",
        "write_performed.",
        "artifact_created_on_disk.",
        "controlled_output_root.",
        "artifact_path.",
        "filename.",
        "extension.",
        "write_authorization.",
        "bytes_intended.",
        "bytes_written.",
        "content_sha256_before_write.",
        "content_sha256_after_write.",
        "overwrite_policy.",
        "verification_status.",
        "safety_flags.",
        "warnings.",
        "errors.",
        "exit_code.",
    ],
)
def test_future_result_json_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The contract requires exit code `0` only when:",
        "dry-run completed without write; or",
        "controlled fixture-owned write completed and verification status is `VERIFIED`.",
        "The contract requires non-zero exit code when input, authorization, output root, overwrite, path traversal, external process, network, SaaS, database, client-facing, or production conditions are rejected.",
    ],
)
def test_future_exit_code_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "missing write authorization.",
        "dry-run authorization.",
        "unknown write authorization.",
        "missing visible report text.",
        "empty visible report text.",
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
        "external process execution request.",
        "network request.",
        "SaaS integration request.",
        "database integration request.",
    ],
)
def test_mandatory_rejection_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the current dry-run CLI parser has no write-enabled options.",
        "the current dry-run CLI source does not import the write-enabled primitive.",
        "the current dry-run bridge source does not import the write-enabled primitive.",
        "the current dry-run bridge remains dry-run-only.",
        "the future isolated write-enabled CLI has its own parser.",
        "the future isolated write-enabled CLI rejects unknown arguments.",
        "the future isolated write-enabled CLI rejects unsafe output aliases.",
        "the future isolated write-enabled CLI supports dry-run without writing.",
        "the future isolated write-enabled CLI supports controlled fixture-owned write only with explicit authorization.",
        "the future isolated write-enabled CLI returns deterministic result data.",
        "the future isolated write-enabled CLI returns non-zero exit on rejected inputs.",
        "the accepted primitive still rejects dry-run authorization.",
        "the accepted primitive still rejects repository root output.",
        "the accepted primitive still rejects existing artifacts.",
        "the accepted primitive still performs no directory creation.",
        "the accepted primitive still performs no overwrite.",
        "the accepted primitive still performs no external process execution.",
        "the accepted primitive still performs no network access.",
        "the accepted primitive still performs no SaaS or database access.",
    ],
)
def test_mandatory_compatibility_contract_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize CLI implementation.",
        "This QA gate does not authorize creation of the future isolated CLI module.",
        "This QA gate does not authorize command-line write flags in the current dry-run CLI.",
        "This QA gate does not authorize output path flags in the current dry-run CLI.",
        "This QA gate does not authorize overwrite flags.",
        "This QA gate does not authorize writing from current user-facing command execution.",
        "This QA gate does not authorize writing outside fixture-owned roots.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize overwrite.",
        "This QA gate does not authorize multiple artifacts.",
        "This QA gate does not authorize arbitrary cleanup.",
        "This QA gate does not authorize real media access.",
        "This QA gate does not authorize scanner execution.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize external process execution.",
        "This QA gate does not authorize network access.",
        "This QA gate does not authorize SaaS integration.",
        "This QA gate does not authorize database integration.",
        "This QA gate does not authorize backend changes.",
        "This QA gate does not authorize frontend changes.",
        "This QA gate does not authorize installer work.",
        "This QA gate does not authorize client-facing demo work.",
        "This QA gate does not authorize public demo work.",
        "This QA gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled implementation contract QA gate passes." in doc
    assert "The controlled implementation contract is accepted for closure review." in doc
    assert "A later controlled implementation contract QA gate closure review may be prepared." in doc
    assert "The current project remains dry-run-only from the current command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not implement CLI code." in doc
    assert "That next step must not create the future isolated CLI module." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only close this controlled implementation contract QA gate." in doc


def test_implementation_contract_document_supports_qa_gate() -> None:
    source = _read(IMPLEMENTATION_CONTRACT_DOC_PATH)

    assert "The controlled implementation contract for isolated write-enabled CLI integration is defined." in source
    assert "A later controlled implementation QA gate may be prepared." in source
    assert "The current project remains dry-run-only from the current command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not implement CLI code." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only audit this controlled implementation contract." in source


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
        visible_report_text="CLI integration implementation contract QA gate controlled report\n",
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
        visible_report_text="CLI integration implementation contract QA gate report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation contract QA gate report",
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
