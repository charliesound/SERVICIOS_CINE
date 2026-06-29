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
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_authorization_gate.py"
)

READINESS_V2_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.md"
)

READINESS_V2_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_readiness_gate_v2.py"
)

IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_implementation_contract_qa_gate_closure_review_v1.md"
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

FUTURE_IMPLEMENTATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.IMPLEMENTATION.AUTHORIZATION.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CLI_INTEGRATION_IMPLEMENTATION_AUTHORIZATION_GATE_PASS_READY_FOR_"
    "CONTROLLED_IMPLEMENTATION_PHASE"
)

PREVIOUS_COMMIT = "8bf095db319424f6d3c8cdece1d9f938dbfbb7e0"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-readiness-gate-v2-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-write-enabled-export-cli-integration-impl-authorization-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)

FUTURE_ISOLATED_CLI_MODULE = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

FUTURE_IMPLEMENTATION_TEST = (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_cli_integration_controlled_implementation.py"
)

FUTURE_COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_authorization_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_authorization_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        READINESS_V2_DOC_PATH,
        READINESS_V2_TEST_PATH,
        IMPLEMENTATION_CONTRACT_QA_CLOSURE_REVIEW_DOC_PATH,
        IMPLEMENTATION_CONTRACT_QA_GATE_DOC_PATH,
        IMPLEMENTATION_CONTRACT_DOC_PATH,
        CONTROLLED_IMPL_MODULE_PATH,
        DRY_RUN_CLI_PATH,
        DRY_RUN_BRIDGE_PATH,
    ],
)
def test_artifacts_under_authorization_review_exist(path: Path) -> None:
    assert path.is_file()


def test_future_runtime_module_is_not_created_in_authorization_gate_phase() -> None:
    assert not FUTURE_ISOLATED_CLI_MODULE_PATH.exists()


def test_future_implementation_test_is_not_created_in_authorization_gate_phase() -> None:
    assert not FUTURE_IMPLEMENTATION_TEST_PATH.exists()


@pytest.mark.parametrize(
    "required_text",
    [
        PHASE_ID,
        RESULT_ID,
        PREVIOUS_COMMIT,
        PREVIOUS_TAG,
        TARGET_TAG,
        NEXT_PHASE_ID,
        "This is a doc/test-only authorization gate.",
        "This authorization gate decides whether a later controlled implementation phase may be prepared.",
        "This authorization gate does not implement CLI code.",
        "This authorization gate does not create the future isolated CLI module.",
        "This authorization gate does not add command-line write flags to the current dry-run CLI.",
        "This authorization gate does not add output path flags to the current dry-run CLI.",
        "This authorization gate does not add overwrite flags.",
        "This authorization gate does not connect `export_controlled_visible_report_text_artifact` to current command execution.",
        "This authorization gate does not modify the current dry-run CLI.",
        "This authorization gate does not modify the current dry-run bridge.",
        "This authorization gate does not write artifacts from the command line.",
        "This authorization gate does not authorize client-facing usage.",
        "This authorization gate does not authorize production usage.",
    ],
)
def test_authorization_gate_declares_scope_lineage_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "target CLI integration implementation readiness gate V2 test passed with 158 checks.",
        "previous CLI integration implementation contract QA closure review test passed with 175 checks.",
        "previous CLI integration implementation contract QA gate test passed with 243 checks.",
        "previous CLI integration implementation contract test passed with 235 checks.",
        "previous controlled implementation test passed with 33 checks.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target readiness gate V2 tag was absent locally before tagging.",
        "target readiness gate V2 tag was absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target CLI integration implementation readiness gate V2 test passed with 158 checks.",
        "final CLI integration implementation contract QA closure review test passed with 175 checks.",
        "final CLI integration implementation contract QA gate test passed with 243 checks.",
        "final CLI integration implementation contract test passed with 235 checks.",
        "final CLI integration implementation readiness gate V1 test passed with 179 checks.",
        "final CLI integration contract QA closure review test passed with 132 checks.",
        "final controlled implementation QA gate test passed with 183 checks.",
        "final controlled implementation test passed with 33 checks.",
        "final dry-run CLI forbidden marker check passed.",
        "final write-enabled implementation safety check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_authorization_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the implementation readiness gate v2 is closed.",
        "the implementation contract QA gate closure review is closed.",
        "the implementation contract QA gate is closed.",
        "the implementation contract is accepted.",
        "this authorization gate remains doc/test-only.",
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
        "future implementation remains limited to fixture-owned controlled output roots.",
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
def test_authorization_acceptance_criteria_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A later controlled implementation phase may be prepared.",
        "That later implementation phase may create exactly one new runtime module:",
        FUTURE_ISOLATED_CLI_MODULE,
        "That later implementation phase may create exactly one new implementation test file:",
        FUTURE_IMPLEMENTATION_TEST,
        "That later implementation phase may import `export_controlled_visible_report_text_artifact` only from the accepted controlled write-enabled primitive.",
        "That later implementation phase may build an isolated parser only in the new isolated module.",
        "That later implementation phase may expose an internal command identity only as data or parser metadata:",
        FUTURE_COMMAND_NAME,
        "That later implementation phase may add an internal `main` function only inside the new isolated module.",
        "That later implementation phase may add an internal `run` or `execute` helper only inside the new isolated module.",
        "That later implementation phase may return deterministic result data.",
        "That later implementation phase may return exit code `0` for valid dry-run.",
        "That later implementation phase may return exit code `0` for verified fixture-owned controlled write.",
        "That later implementation phase must return non-zero exit code for rejected input.",
    ],
)
def test_narrow_implementation_authorization_decision_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The later controlled implementation phase may modify only:",
        FUTURE_ISOLATED_CLI_MODULE,
        FUTURE_IMPLEMENTATION_TEST,
        "No other runtime, test, docs, config, packaging, backend, frontend, database, installer, CI, or deployment files are authorized by this gate.",
        "The current dry-run CLI remains out of implementation scope.",
        "The current dry-run bridge remains out of implementation scope.",
        "The accepted controlled write-enabled primitive remains out of modification scope.",
    ],
)
def test_authorized_later_implementation_file_boundary_is_recorded(required_text: str) -> None:
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
        "The later isolated CLI parser must reject unknown arguments.",
        "The later isolated CLI parser must not be registered as a package entry point.",
        "The later isolated CLI parser must not modify the current dry-run CLI.",
    ],
)
def test_authorized_later_parser_behavior_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "parse allowed arguments.",
        "validate that dry-run mode was requested.",
        "return deterministic result data.",
        "report `dry_run_requested` as true.",
        "report `write_requested` as false.",
        "report `write_performed` as false.",
        "report `artifact_created_on_disk` as false.",
        "report `verification_status` as `DRY_RUN_ONLY`.",
        "return exit code `0`.",
        "create artifacts.",
        "create directories.",
        "overwrite files.",
        "call the controlled write-enabled primitive.",
        "access real media.",
        "execute scanner.",
        "execute ffprobe.",
        "execute FFmpeg.",
        "execute external processes.",
        "use network access.",
        "use SaaS or database integration.",
    ],
)
def test_authorized_later_dry_run_behavior_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "require visible report text.",
        "require controlled output root.",
        "require exact write authorization.",
        "require `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`.",
        "call `export_controlled_visible_report_text_artifact`.",
        "write only `controlled_visible_report.controlled.txt`.",
        "write only under fixture-owned controlled output roots.",
        "preserve no-overwrite behavior.",
        "preserve no-directory-creation behavior.",
        "preserve UTF-8 byte count verification.",
        "preserve SHA256 verification.",
        "return deterministic result data.",
        "return exit code `0` only when verification status is `VERIFIED`.",
        "missing visible report text.",
        "empty visible report text.",
        "missing controlled output root.",
        "uncontrolled output root.",
        "current working directory as output root.",
        "repository root as output root.",
        "existing artifact path.",
        "unsupported filename.",
        "path traversal.",
        "missing write authorization.",
        "dry-run authorization.",
        "unknown write authorization.",
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
def test_authorized_later_controlled_write_behavior_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "isolated CLI module exists.",
        "isolated CLI parser construction.",
        "command identity.",
        "allowed argument set.",
        "forbidden unsafe alias rejection.",
        "unknown argument rejection.",
        "dry-run mode without artifact creation.",
        "dry-run mode does not call the controlled write-enabled primitive.",
        "missing visible report text rejection.",
        "empty visible report text rejection.",
        "missing controlled output root rejection.",
        "missing write authorization rejection.",
        "dry-run authorization rejection.",
        "unknown authorization rejection.",
        "repository root rejection.",
        "current working directory rejection.",
        "existing artifact rejection.",
        "no directory creation.",
        "no overwrite.",
        "deterministic JSON result fields.",
        "non-zero exit for rejected inputs.",
        "zero exit for valid dry-run.",
        "zero exit for verified fixture-owned controlled write.",
        "controlled write creates exactly one artifact.",
        "controlled write uses filename `controlled_visible_report.controlled.txt`.",
        "controlled write verifies byte count.",
        "controlled write verifies SHA256.",
        "current dry-run CLI remains unchanged.",
        "current dry-run bridge remains unchanged.",
        "current dry-run CLI does not import the new isolated CLI module.",
        "current dry-run bridge does not import the new isolated CLI module.",
        "isolated CLI does not execute scanner.",
        "isolated CLI does not execute ffprobe.",
        "isolated CLI does not execute FFmpeg.",
        "isolated CLI does not use external process execution.",
        "isolated CLI does not use network.",
        "isolated CLI does not use SaaS or database integration.",
    ],
)
def test_required_later_implementation_test_matrix_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This authorization gate does not authorize implementation in this phase.",
        "This authorization gate does not authorize modifying the current dry-run CLI.",
        "This authorization gate does not authorize modifying the current dry-run bridge.",
        "This authorization gate does not authorize modifying the accepted controlled write-enabled primitive.",
        "This authorization gate does not authorize package entry points.",
        "This authorization gate does not authorize installer work.",
        "This authorization gate does not authorize client-facing demo work.",
        "This authorization gate does not authorize public demo work.",
        "This authorization gate does not authorize production use.",
        "This authorization gate does not authorize writing outside fixture-owned roots.",
        "This authorization gate does not authorize directory creation.",
        "This authorization gate does not authorize overwrite.",
        "This authorization gate does not authorize multiple artifacts.",
        "This authorization gate does not authorize arbitrary cleanup.",
        "This authorization gate does not authorize real media access.",
        "This authorization gate does not authorize scanner execution.",
        "This authorization gate does not authorize ffprobe execution.",
        "This authorization gate does not authorize FFmpeg execution.",
        "This authorization gate does not authorize external process execution.",
        "This authorization gate does not authorize network access.",
        "This authorization gate does not authorize SaaS integration.",
        "This authorization gate does not authorize database integration.",
        "This authorization gate does not authorize backend changes.",
        "This authorization gate does not authorize frontend changes.",
    ],
)
def test_explicit_non_authorization_retained(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_authorization_gate_decision_and_next_step_are_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "The write-enabled export CLI integration implementation authorization gate passes." in doc
    assert "A later controlled implementation phase may be prepared." in doc
    assert "The later controlled implementation phase is authorized only within the file boundary, parser boundary, behavior boundary, and test boundary defined here." in doc
    assert "The current project remains dry-run-only from the current command line." in doc
    assert "The current project remains not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step may implement only the new isolated CLI module and its implementation test." in doc
    assert "That next step must not modify the current dry-run CLI." in doc
    assert "That next step must not modify the current dry-run bridge." in doc
    assert "That next step must not modify the accepted controlled write-enabled primitive." in doc
    assert "That next step must not add package entry points." in doc
    assert "That next step must not add installer work." in doc
    assert "That next step must not add client-facing or production usage." in doc
    assert "That next step must not touch backend, frontend, database, SaaS, deployment, or external process execution." in doc


def test_readiness_v2_document_supports_authorization_gate() -> None:
    source = _read(READINESS_V2_DOC_PATH)

    assert "The write-enabled export CLI integration implementation readiness gate v2 passes." in source
    assert "A later strict implementation authorization gate may be prepared." in source
    assert "The current project remains dry-run-only from the current command line." in source
    assert "The current project remains not ready for write-enabled CLI execution." in source
    assert "The current project remains not ready for client-facing or production use." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only unless it explicitly and narrowly authorizes a subsequent implementation phase." in source
    assert "That next step must not implement CLI code." in source
    assert "That next step must not create the future isolated CLI module." in source
    assert "That next step must not add CLI flags." in source
    assert "That next step must not connect the primitive to command execution." in source
    assert "That next step may only decide whether a later controlled implementation phase can be authorized." in source


def test_reserved_future_files_do_not_exist_in_authorization_gate_phase() -> None:
    assert not FUTURE_ISOLATED_CLI_MODULE_PATH.exists()
    assert not FUTURE_IMPLEMENTATION_TEST_PATH.exists()


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


def test_current_dry_run_cli_does_not_import_write_enabled_primitive_or_future_module() -> None:
    source = _read(DRY_RUN_CLI_PATH)

    assert "export_controlled_visible_report_text_artifact" not in source
    assert "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY" not in source
    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export" not in source
    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli" not in source


def test_current_dry_run_bridge_does_not_import_future_module() -> None:
    source = _read(DRY_RUN_BRIDGE_PATH)

    assert "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli" not in source


def test_controlled_primitive_still_requires_explicit_authorization_and_fixture_root(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation authorization gate controlled report\n",
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
        visible_report_text="CLI integration implementation authorization gate report",
        controlled_output_root=ROOT,
        write_authorization=WRITE_AUTHORIZATION,
    )

    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert "controlled output root is not controlled" in result["errors"]


def test_controlled_primitive_still_rejects_dry_run_authorization(tmp_path: Path) -> None:
    result = export_controlled_visible_report_text_artifact(
        visible_report_text="CLI integration implementation authorization gate report",
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
