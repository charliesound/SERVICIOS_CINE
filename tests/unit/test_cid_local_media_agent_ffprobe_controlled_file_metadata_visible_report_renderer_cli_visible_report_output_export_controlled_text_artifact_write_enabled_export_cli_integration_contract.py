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
    "controlled_text_artifact_write_enabled_export_cli_integration_contract_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_contract.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate_v1.md"
)

READINESS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_readiness_gate.py"
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
    "CLI.INTEGRATION.CONTRACT.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_CONTRACT_DEFINED"
)

PREVIOUS_COMMIT = "38dc82dc7f8c85303d3e8e57fa1b1e603cf0deb0"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-readiness-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-contract-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTRACT.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_contract_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        READINESS_DOC_PATH,
        READINESS_TEST_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_contract_review_exist(path: Path) -> None:
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
        "This is a doc/test-only contract.",
        "This contract defines a future write-enabled CLI integration boundary.",
        "This contract does not implement the CLI integration.",
        "This contract does not add command-line write flags.",
        "This contract does not add output path flags.",
        "This contract does not add overwrite flags.",
        "This contract does not connect `export_controlled_visible_report_text_artifact` to current command execution.",
        "This contract does not modify the current dry-run CLI.",
        "This contract does not modify the current dry-run bridge.",
        "This contract does not write artifacts from the command line.",
        "This contract does not authorize client-facing usage.",
        "This contract does not authorize production usage.",
    ],
)
def test_contract_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "precheck was clean.",
        "previous CLI integration readiness input tag was present.",
        "target CLI integration readiness tag was absent locally before tagging.",
        "target CLI integration readiness tag was absent remotely before tagging.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration readiness gate test passed with 113 checks.",
        "previous controlled implementation QA closure review test passed with 110 checks.",
        "previous controlled implementation QA gate test passed with 183 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration readiness gate test passed with 113 checks.",
        "final controlled implementation QA closure review test passed with 110 checks.",
        "final controlled implementation QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final implementation readiness gate test passed with 322 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_contract_records_previous_validation_evidence(required_text: str) -> None:
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
def test_accepted_primitive_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future write-enabled CLI integration must use a separate explicit command path from the current dry-run command.",
        "The current dry-run CLI must remain dry-run-only.",
        "The current dry-run bridge must remain dry-run-only.",
        "A future write-enabled CLI integration must not silently reuse dry-run authorization.",
        "A future write-enabled CLI integration must require explicit write authorization.",
        "A future write-enabled CLI integration must require an explicit controlled output root.",
        "A future write-enabled CLI integration must preserve fixture-owned root validation until a later explicit contract authorizes another root policy.",
        "A future write-enabled CLI integration must preserve single-artifact behavior.",
        "A future write-enabled CLI integration must preserve no-overwrite behavior.",
        "A future write-enabled CLI integration must preserve byte count verification.",
        "A future write-enabled CLI integration must preserve SHA256 verification.",
        "A future write-enabled CLI integration must preserve deterministic result JSON.",
        "A future write-enabled CLI integration must preserve conservative safety flags.",
        "A future write-enabled CLI integration must fail closed on invalid input.",
        "A future write-enabled CLI integration must keep dry-run and write-enabled results clearly separated.",
    ],
)
def test_required_future_cli_integration_shape_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "a separate CLI module dedicated to controlled write-enabled export; or",
        "a separate subcommand isolated from the current dry-run command.",
        "The future command boundary must not be added in this contract phase.",
        "The future command boundary must be introduced only after a future implementation readiness gate.",
        "The future command boundary must include tests proving that the current dry-run command remains unchanged.",
    ],
)
def test_future_command_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "visible report text input source.",
        "controlled output root input.",
        "explicit write authorization input.",
        "artifact filename policy.",
        "dry-run/write-enabled mode separation.",
        "result JSON output policy.",
        "failure output policy.",
        "safety flags output policy.",
        "No future write-enabled CLI integration may infer authorization from environment variables.",
        "No future write-enabled CLI integration may infer output root from the current working directory.",
        "No future write-enabled CLI integration may write to the repository root.",
        "No future write-enabled CLI integration may write to user media folders unless a later explicit client-folder contract authorizes it.",
    ],
)
def test_future_required_cli_inputs_are_recorded(required_text: str) -> None:
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
        "scanner execution request.",
        "ffprobe execution request.",
        "FFmpeg execution request.",
        "network request.",
        "SaaS integration request.",
        "database integration request.",
    ],
)
def test_future_required_rejection_cases_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "phase.",
        "cli_contract_version.",
        "command_name.",
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
    ],
)
def test_future_required_result_json_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "real_media_access_performed.",
        "scanner_execution_performed.",
        "ffprobe_execution_performed.",
        "ffmpeg_execution_performed.",
        "external_process_execution_performed.",
        "network_access_performed.",
        "saas_or_database_access_performed.",
        "directory_creation_performed.",
        "overwrite_performed.",
        "production_execution_performed.",
        "client_facing_execution_performed.",
        "public_demo_execution_performed.",
        "write_requested.",
        "write_performed.",
        "artifact_created_on_disk.",
        "file_write_performed.",
    ],
)
def test_future_safety_flag_expectations_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "current dry-run CLI behavior.",
        "current dry-run bridge behavior.",
        "current controlled write-enabled primitive result shape.",
        "current no-overwrite behavior.",
        "current fixture-owned root restriction.",
        "current safety flag model.",
        "current fail-closed behavior.",
    ],
)
def test_required_compatibility_guarantees_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This contract does not authorize CLI implementation.",
        "This contract does not authorize command-line write flags.",
        "This contract does not authorize output path flags.",
        "This contract does not authorize overwrite flags.",
        "This contract does not authorize writing from user-facing command execution.",
        "This contract does not authorize writing outside fixture-owned roots.",
        "This contract does not authorize directory creation.",
        "This contract does not authorize overwrite.",
        "This contract does not authorize multiple artifacts.",
        "This contract does not authorize arbitrary cleanup.",
        "This contract does not authorize real media access.",
        "This contract does not authorize scanner execution.",
        "This contract does not authorize ffprobe execution.",
        "This contract does not authorize FFmpeg execution.",
        "This contract does not authorize external process execution.",
        "This contract does not authorize network access.",
        "This contract does not authorize SaaS integration.",
        "This contract does not authorize database integration.",
        "This contract does not authorize backend changes.",
        "This contract does not authorize frontend changes.",
        "This contract does not authorize installer work.",
        "This contract does not authorize client-facing demo work.",
        "This contract does not authorize public demo work.",
        "This contract does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The future write-enabled CLI integration contract is defined." in doc
    assert "The current project remains dry-run-only from the command line." in doc
    assert "The current project remains not ready for write-enabled CLI execution." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc
    assert "That next step must not add CLI flags." in doc
    assert "That next step must not connect the primitive to command execution." in doc
    assert "That next step may only audit this contract." in doc


def test_readiness_gate_supports_contract() -> None:
    source = _read(READINESS_DOC_PATH)

    assert "The controlled write-enabled export primitive is ready for a future CLI integration contract." in source
    assert "The current project remains dry-run-only from the command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only define the CLI integration contract." in source


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


def test_controlled_primitive_still_requires_explicit_write_authorization_and_fixture_root(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration contract controlled report\n",
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
        visible_report_text="CLI integration contract report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration contract report",
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
