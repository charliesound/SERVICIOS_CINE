from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli as cli,
)


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract.py"
)

PREVIOUS_PLANNING_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning_v1.md"
)

CLI_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli.py"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CONTRACT_PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "90220f5ed763e8fc93a5760d978d545752f8761b"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-next-scope-planning-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-contract-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_write_enabled_export_contract_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_write_enabled_export_contract_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize("path", [PREVIOUS_PLANNING_DOC_PATH, CLI_MODULE_PATH, BRIDGE_MODULE_PATH])
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
        "This contract defines a future controlled write-enabled export boundary.",
        "This contract does not add implementation code.",
        "This contract does not modify CLI argument parsing.",
        "This contract does not modify command routing.",
        "This contract does not modify the controlled dry-run bridge.",
        "This contract does not perform write-enabled export.",
        "This contract does not create directories.",
        "This contract does not create artifacts on disk.",
        "PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST",
    ],
)
def test_contract_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_contract_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_contract.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "The product intent is to prepare the first future controlled write-enabled export path.",
        "The first future controlled write-enabled export path must export one controlled visible report text artifact.",
        "The first future controlled write-enabled export path must remain local-only.",
        "The first future controlled write-enabled export path must remain fixture-owned or test-owned.",
        "The first future controlled write-enabled export path must remain isolated from real user media.",
        "The first future controlled write-enabled export path must remain isolated from client-facing behavior.",
        "The first future controlled write-enabled export path must remain isolated from public demo and production behavior.",
    ],
)
def test_product_intent_is_controlled_and_local_only(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`controlled_visible_report_text`",
        "The future artifact must be plain UTF-8 text.",
        "The future artifact must be deterministic for the same input.",
        "The future artifact must be generated only from controlled visible report text already present in memory.",
        "The future artifact must not require media files.",
        "The future artifact must not require scanner execution.",
        "The future artifact must not require ffprobe execution.",
        "The future artifact must not require FFmpeg execution.",
        "The future artifact must not require external process execution.",
        "The future artifact must not require network access.",
        "The future artifact must not require SaaS or database access.",
    ],
)
def test_future_artifact_type_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future write-enabled export must require an explicit controlled output root.",
        "The controlled output root must be provided by a test fixture or equivalent controlled caller.",
        "The controlled output root must not be inferred from the current working directory.",
        "The controlled output root must not be inferred from user home.",
        "The controlled output root must not be inferred from environment variables.",
        "The controlled output root must not be inferred from input media paths.",
        "The controlled output root must not be inferred from SaaS state.",
        "The controlled output root must be resolved before write.",
        "The controlled output root must exist before write unless a future explicit directory-creation contract authorizes otherwise.",
        "This contract does not authorize directory creation.",
    ],
)
def test_future_controlled_output_root_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future write-enabled export must use deterministic filenames.",
        "`controlled_visible_report.controlled.txt`",
        "`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-`",
        "The filename must not contain path separators.",
        "The filename must not contain parent traversal.",
        "The filename must not begin with a dot.",
        "The filename must not be empty.",
        "The filename must not be generated from unsanitized input.",
        "The filename must not be generated from real media names.",
        "The filename must not be generated from user-provided folder names.",
    ],
)
def test_future_filename_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The first future allowed extension is:",
        "`.controlled.txt`",
        "The future write-enabled export must reject unsupported extensions.",
        "The future write-enabled export must reject extensionless names.",
        "The future write-enabled export must reject compound unsafe names.",
        "The future write-enabled export must reject names that only appear to end with the allowed extension after traversal or separator manipulation.",
    ],
)
def test_future_extension_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future write-enabled export must resolve the controlled output root.",
        "The future write-enabled export must resolve the candidate artifact path.",
        "The future write-enabled export must verify that the candidate artifact path remains inside the controlled output root.",
        "The future write-enabled export must reject parent traversal.",
        "The future write-enabled export must reject absolute unsafe paths.",
        "The future write-enabled export must reject home-relative paths.",
        "The future write-enabled export must reject environment-derived paths.",
        "The future write-enabled export must reject symlink boundary ambiguity unless a future explicit symlink policy is defined.",
        "The future write-enabled export must reject path boundary ambiguity.",
    ],
)
def test_future_path_boundary_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future write-enabled export must reject overwrite by default.",
        "The future write-enabled export must not truncate an existing file.",
        "The future write-enabled export must not append to an existing file.",
        "The future write-enabled export must not replace an existing file.",
        "The future write-enabled export must not support overwrite flags in the first implementation.",
        "The future write-enabled export must report an explicit failure if the target artifact already exists.",
    ],
)
def test_future_overwrite_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future write-enabled export must accept controlled visible report text already present in memory.",
        "The future write-enabled export must reject empty content.",
        "The future write-enabled export must reject binary content.",
        "The future write-enabled export must encode text as UTF-8.",
        "The future write-enabled export must compute content hash before write.",
        "The future write-enabled export must compute byte count before write.",
        "The future write-enabled export must write exactly the intended bytes.",
        "The future write-enabled export must verify content hash after write.",
        "The future write-enabled export must verify byte count after write.",
        "The future write-enabled export must fail closed if verification fails.",
    ],
)
def test_future_content_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "phase.",
        "contract version.",
        "artifact type.",
        "artifact format.",
        "controlled output root.",
        "artifact path.",
        "filename.",
        "extension.",
        "write_requested.",
        "write_performed.",
        "artifact_created_on_disk.",
        "bytes_intended.",
        "bytes_written.",
        "content_sha256_before_write.",
        "content_sha256_after_write.",
        "path_boundary.",
        "overwrite_policy.",
        "verification_status.",
        "cleanup_expectation.",
        "safety_flags.",
        "warnings.",
        "errors.",
    ],
)
def test_future_result_contract_fields_are_recorded(required_text: str) -> None:
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
        "file_write_performed.",
        "artifact_created_on_disk.",
        "overwrite_performed.",
        "path_boundary_violation_detected.",
        "The future accepted result may set `file_write_performed=True` only for the single controlled artifact write.",
        "The future accepted result may set `artifact_created_on_disk=True` only for the single controlled artifact write.",
        "The future accepted result must keep every other operational safety flag false.",
    ],
)
def test_future_safety_flags_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "controlled output root is missing.",
        "controlled output root does not exist.",
        "output root is not controlled.",
        "output root is ambiguous.",
        "filename is missing.",
        "filename is unsupported.",
        "filename contains separators.",
        "filename contains parent traversal.",
        "filename begins with a dot.",
        "extension is unsupported.",
        "candidate path escapes controlled output root.",
        "candidate path is absolute unsafe.",
        "candidate path is home-relative.",
        "candidate path is environment-derived.",
        "target artifact already exists.",
        "content is empty.",
        "content cannot be encoded as UTF-8.",
        "bytes written differ from bytes intended.",
        "content hash after write differs from content hash before write.",
        "post-write verification fails.",
        "unexpected warnings appear.",
        "any prohibited operation is attempted.",
    ],
)
def test_future_failure_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The first future write-enabled export implementation must use fixture-owned output only.",
        "The first future write-enabled export implementation must keep cleanup under test ownership.",
        "The first future write-enabled export implementation must not delete arbitrary user files.",
        "The first future write-enabled export implementation must not clean outside the controlled output root.",
        "The first future write-enabled export implementation must not remove parent directories.",
        "The first future write-enabled export implementation must report cleanup expectations instead of performing broad cleanup.",
        "If a partial artifact is produced during a failed controlled write, future implementation readiness must define whether the artifact is removed or preserved for forensic inspection.",
        "This contract does not authorize cleanup implementation.",
    ],
)
def test_future_rollback_and_cleanup_contract_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The existing controlled dry-run CLI must remain dry-run-only until a future explicit implementation gate is closed.",
        "A future write-enabled CLI must not reuse `--dry-run` semantics to perform writing.",
        "A future write-enabled CLI must use a distinct explicit write authorization mechanism.",
        "A future write-enabled CLI must require controlled output root.",
        "A future write-enabled CLI must require deterministic filename or controlled default filename.",
        "A future write-enabled CLI must not accept arbitrary output paths.",
        "A future write-enabled CLI must not accept real media paths.",
        "A future write-enabled CLI must not accept scanner execution flags.",
        "A future write-enabled CLI must not accept ffprobe execution flags.",
        "A future write-enabled CLI must not accept FFmpeg execution flags.",
        "A future write-enabled CLI must not accept network flags.",
        "A future write-enabled CLI must not accept production flags.",
    ],
)
def test_future_cli_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "exact module boundaries.",
        "exact function name.",
        "exact inputs.",
        "exact outputs.",
        "exact failure modes.",
        "exact allowed filesystem operation.",
        "exact prohibited filesystem operations.",
        "exact fixture-owned output policy.",
        "exact no-overwrite policy.",
        "exact post-write verification policy.",
        "exact test coverage.",
        "exact guard commands.",
        "exact rollback expectations.",
        "exact non-authorization of real media, scanner, ffprobe, FFmpeg, external process, network, SaaS, database, backend, frontend, installer, client demo, public demo, and production behavior.",
    ],
)
def test_future_implementation_readiness_requirements_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The existing controlled dry-run chain remains accepted.",
        "The existing controlled dry-run CLI remains dry-run-only.",
        "The existing controlled dry-run bridge remains dry-run-only.",
        "The existing controlled smoke execution remains accepted.",
        "The existing controlled smoke execution QA gate remains accepted and closed.",
        "The existing next-scope planning remains accepted and closed.",
        "This contract does not weaken any previous dry-run safety boundary.",
    ],
)
def test_current_dry_run_chain_preservation_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "adds implementation code.",
        "modifies CLI argument parsing.",
        "modifies command routing.",
        "modifies the controlled dry-run bridge.",
        "authorizes immediate write-enabled implementation.",
        "authorizes directory creation now.",
        "authorizes artifact creation on disk now.",
        "authorizes real file writing now.",
        "authorizes real media access.",
        "authorizes scanner execution.",
        "authorizes ffprobe execution.",
        "authorizes FFmpeg execution.",
        "authorizes external process execution.",
        "authorizes network access.",
        "authorizes SaaS integration.",
        "authorizes database changes.",
        "authorizes backend changes.",
        "authorizes frontend changes.",
        "authorizes installer work.",
        "authorizes client-facing demo.",
        "authorizes public demo.",
        "authorizes production use.",
        "omits controlled output root boundaries.",
        "omits filename boundaries.",
        "omits extension boundaries.",
        "omits path boundary checks.",
        "omits no-overwrite policy.",
        "omits content hash verification.",
        "omits byte count verification.",
        "omits failure behavior.",
        "omits fixture-owned output policy.",
        "skips implementation readiness.",
    ],
)
def test_contract_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This contract does not authorize write-enabled export implementation.",
        "This contract does not authorize directory creation.",
        "This contract does not authorize artifact creation on disk now.",
        "This contract does not authorize real file writing now.",
        "This contract does not authorize media scanning.",
        "This contract does not authorize real media decoding.",
        "This contract does not authorize ffprobe execution.",
        "This contract does not authorize FFmpeg execution.",
        "This contract does not authorize external process execution.",
        "This contract does not authorize audio extraction.",
        "This contract does not authorize sync.",
        "This contract does not authorize transcription.",
        "This contract does not authorize subtitle generation.",
        "This contract does not authorize timeline export.",
        "This contract does not authorize network access.",
        "This contract does not authorize SaaS integration.",
        "This contract does not authorize database changes.",
        "This contract does not authorize backend changes.",
        "This contract does not authorize frontend changes.",
        "This contract does not authorize installer work.",
        "This contract does not authorize public demo work.",
        "This contract does not authorize client-facing demo work.",
        "This contract does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_decision_allows_only_contract_qa_gate_next() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export contract is accepted as a future boundary." in doc
    assert "The current project remains dry-run-only." in doc
    assert "The current project remains not ready for write-enabled implementation." in doc
    assert "The current project remains not ready for directory creation." in doc
    assert "The current project remains not ready for artifact creation on disk." in doc
    assert "The current project remains not ready for real media execution." in doc
    assert "The current project remains not ready for public, client-facing, or production use." in doc
    assert "The next phase must be a contract QA gate." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc


def test_previous_planning_doc_selected_path_b_but_did_not_authorize_writing() -> None:
    source = _read(PREVIOUS_PLANNING_DOC_PATH)

    assert "PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST" in source
    assert "The next product direction is controlled write-enabled export contract-first." in source
    assert "The current project remains dry-run-only." in source
    assert "The current project remains not ready for write-enabled behavior." in source
    assert "This planning phase does not authorize write-enabled export." in source
    assert "This planning phase does not authorize artifact creation on disk." in source


def test_current_cli_parser_still_exposes_only_dry_run_safe_options() -> None:
    parser = cli.build_parser()
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


def test_current_cli_source_has_no_forbidden_runtime_markers() -> None:
    source = _read(CLI_MODULE_PATH)

    forbidden_markers = [
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
    ]

    for marker in forbidden_markers:
        assert marker not in source

    assert "sub" + "process" not in source


def test_current_bridge_safety_contract_remains_dry_run_only() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    required_markers = [
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_requested": False',
        '"write_performed": False',
        '"artifact_created_on_disk": False',
        "Only dry-run mode is supported",
        "write_requested must remain false",
    ]

    for marker in required_markers:
        assert marker in source
