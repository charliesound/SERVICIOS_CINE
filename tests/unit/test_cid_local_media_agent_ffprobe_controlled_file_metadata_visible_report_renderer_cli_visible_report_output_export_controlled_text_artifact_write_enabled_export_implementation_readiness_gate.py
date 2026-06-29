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
    "controlled_text_artifact_write_enabled_export_implementation_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_implementation_readiness_gate.py"
)

CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_qa_gate_closure_review_v1.md"
)

CLOSURE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_qa_gate_v1.md"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_v1.md"
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
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "IMPLEMENTATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_"
    "CONTROLLED_IMPLEMENTATION"
)

PREVIOUS_COMMIT = "ab6ae4b8ab4640447dad3665923cae8c38f68aaf"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-contract-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-impl-readiness-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CONTROLLED.IMPLEMENTATION.V1"
)

FUTURE_MODULE = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export.py"
)

FUTURE_TEST = (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_controlled_implementation.py"
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
        CLOSURE_DOC_PATH,
        CLOSURE_TEST_PATH,
        QA_GATE_DOC_PATH,
        CONTRACT_DOC_PATH,
        CLI_MODULE_PATH,
        BRIDGE_MODULE_PATH,
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
        "This readiness gate defines exact boundaries for a future controlled write-enabled export implementation.",
        "This readiness gate does not add implementation code.",
        "This readiness gate does not modify CLI argument parsing.",
        "This readiness gate does not modify command routing.",
        "This readiness gate does not modify the controlled dry-run bridge.",
        "This readiness gate does not perform write-enabled export.",
        "This readiness gate does not create directories.",
        "This readiness gate does not create artifacts on disk.",
    ],
)
def test_readiness_gate_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_readiness_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_implementation_readiness_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_implementation_readiness_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target write-enabled export contract QA closure review test passed with 266 checks.",
        "write-enabled export contract QA gate test passed with 244 checks.",
        "write-enabled export contract test passed with 251 checks.",
        "next scope planning test passed with 142 checks.",
        "implementation test passed with 41 checks.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "current CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target closure review short tag absent locally before tagging.",
        "target closure review short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target closure review test passed with 266 checks.",
        "final QA gate test passed with 244 checks.",
        "final contract test passed with 251 checks.",
        "final next scope planning test passed with 142 checks.",
        "final implementation test passed with 41 checks.",
        "final current CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate accepts that the next phase may be a controlled implementation phase.",
        "This readiness gate does not itself authorize implementation.",
        "This readiness gate does not itself authorize writing.",
        "This readiness gate does not itself authorize directory creation.",
        "This readiness gate does not itself authorize artifact creation on disk.",
        "This readiness gate only defines the exact implementation boundaries that the next controlled implementation phase must obey.",
    ],
)
def test_readiness_decision_is_conservative(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        FUTURE_MODULE,
        FUTURE_TEST,
        "The future controlled implementation must not modify the existing dry-run CLI module.",
        "The future controlled implementation must not modify the existing dry-run bridge module.",
        "The future controlled implementation must not modify scanner modules.",
        "The future controlled implementation must not modify media runtime modules.",
        "The future controlled implementation must not modify SaaS modules.",
        "The future controlled implementation must not modify backend modules.",
        "The future controlled implementation must not modify frontend modules.",
        "The future controlled implementation must not modify installer modules.",
    ],
)
def test_future_module_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`export_controlled_visible_report_text_artifact`",
        "The future controlled implementation may expose supporting private helpers only if they are inside the same new module.",
        "The future controlled implementation must not expose CLI entrypoints.",
        "The future controlled implementation must not expose scanner entrypoints.",
        "The future controlled implementation must not expose ffprobe entrypoints.",
        "The future controlled implementation must not expose FFmpeg entrypoints.",
        "The future controlled implementation must not expose network entrypoints.",
        "The future controlled implementation must not expose SaaS entrypoints.",
    ],
)
def test_future_function_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "controlled visible report text already present in memory.",
        "explicit controlled output root.",
        "deterministic filename.",
        "caller context metadata.",
        "write authorization value.",
        "The controlled visible report text input must be a string.",
        "The controlled visible report text input must not be read from disk.",
        "The controlled output root must be path-like.",
        "The controlled output root must be supplied explicitly by a fixture or controlled caller.",
        "The deterministic filename must default to `controlled_visible_report.controlled.txt`.",
        "The caller context metadata must be optional and inert.",
        "The write authorization value must be explicit.",
        "The write authorization value must not be inferred from dry-run mode.",
        "The write authorization value must not be inferred from environment variables.",
        "The write authorization value must not be inferred from production state.",
    ],
)
def test_future_input_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`",
        "The future controlled implementation must require explicit write authorization.",
        "The future controlled implementation must reject missing authorization.",
        "The future controlled implementation must reject unknown authorization.",
        "The future controlled implementation must reject dry-run authorization for writing.",
        "The future controlled implementation must reject production authorization.",
        "The future controlled implementation must reject client-facing authorization.",
        "The future controlled implementation must reject public demo authorization.",
    ],
)
def test_future_write_authorization_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The controlled output root must already exist.",
        "The controlled output root must be a directory.",
        "The controlled output root must be fixture-owned or test-owned.",
        "The controlled output root must be resolved before candidate path creation.",
        "The controlled output root must not be inferred from current working directory.",
        "The controlled output root must not be inferred from user home.",
        "The controlled output root must not be inferred from environment variables.",
        "The controlled output root must not be inferred from input media paths.",
        "The controlled output root must not be inferred from SaaS state.",
        "The future controlled implementation must not create the output root.",
        "The future controlled implementation must not create parent directories.",
    ],
)
def test_future_output_root_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`controlled_visible_report.controlled.txt`",
        "`.controlled.txt`",
        "The future controlled implementation must reject empty filenames.",
        "The future controlled implementation must reject filenames beginning with a dot.",
        "The future controlled implementation must reject filenames containing path separators.",
        "The future controlled implementation must reject filenames containing parent traversal.",
        "The future controlled implementation must reject filenames containing unsafe characters.",
        "The future controlled implementation must reject filenames generated from real media names.",
        "The future controlled implementation must reject filenames generated from user folder names.",
        "The future controlled implementation must reject unsupported extensions.",
    ],
)
def test_future_filename_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future controlled implementation must resolve the controlled output root.",
        "The future controlled implementation must resolve the candidate artifact path.",
        "The future controlled implementation must verify candidate artifact path remains inside controlled output root.",
        "The future controlled implementation must reject boundary ambiguity.",
        "The future controlled implementation must reject parent traversal.",
        "The future controlled implementation must reject unsafe absolute paths.",
        "The future controlled implementation must reject home-relative paths.",
        "The future controlled implementation must reject environment-derived paths.",
        "The future controlled implementation must reject symlink boundary ambiguity unless a future explicit symlink policy is defined.",
    ],
)
def test_future_path_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future controlled implementation may perform exactly one filesystem write operation.",
        "The single allowed filesystem write operation is exclusive creation of one controlled text artifact.",
        "The future controlled implementation must use no-overwrite semantics.",
        "The future controlled implementation must not truncate an existing file.",
        "The future controlled implementation must not append to an existing file.",
        "The future controlled implementation must not replace an existing file.",
        "The future controlled implementation must not create directories.",
        "The future controlled implementation must not delete files.",
        "The future controlled implementation must not rename files.",
        "The future controlled implementation must not move files.",
        "The future controlled implementation must not scan directories.",
        "The future controlled implementation must not read media files.",
        "The future controlled implementation must not execute external processes.",
        "The future controlled implementation must not access network.",
        "The future controlled implementation must not access SaaS or database state.",
    ],
)
def test_future_allowed_filesystem_operation_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future controlled implementation must accept controlled visible report text already present in memory.",
        "The future controlled implementation must reject empty content.",
        "The future controlled implementation must reject binary-like content.",
        "The future controlled implementation must encode content as UTF-8.",
        "The future controlled implementation must compute content hash before write.",
        "The future controlled implementation must compute intended byte count before write.",
        "The future controlled implementation must write exactly the intended bytes.",
        "The future controlled implementation must compute content hash after write.",
        "The future controlled implementation must compute written byte count after write.",
        "The future controlled implementation must compare before-write hash with after-write hash.",
        "The future controlled implementation must compare intended byte count with written byte count.",
        "The future controlled implementation must fail closed if verification fails.",
    ],
)
def test_future_content_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "phase.",
        "implementation version.",
        "artifact type.",
        "artifact format.",
        "controlled output root.",
        "artifact path.",
        "filename.",
        "extension.",
        "write_authorization.",
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
        "The future result must never include raw media paths.",
        "The future result must never include user home paths unless the controlled fixture path itself is explicitly under test ownership.",
        "The future result must never include secrets.",
        "The future result must never include environment values.",
    ],
)
def test_future_result_boundary_is_recorded(required_text: str) -> None:
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
        "The future accepted success result may set `file_write_performed=True`.",
        "The future accepted success result may set `artifact_created_on_disk=True`.",
        "The future accepted success result must set both true only for the single controlled artifact write.",
        "The future accepted success result must keep all other operational safety flags false.",
        "Failure results must accurately report whether a write was requested, whether a write occurred, and whether an artifact was created.",
    ],
)
def test_future_safety_flag_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "write authorization is missing.",
        "write authorization is unknown.",
        "write authorization is dry-run-only.",
        "controlled output root is missing.",
        "controlled output root does not exist.",
        "controlled output root is not a directory.",
        "controlled output root is not controlled.",
        "controlled output root is ambiguous.",
        "filename is missing.",
        "filename is unsupported.",
        "filename contains separators.",
        "filename contains parent traversal.",
        "filename begins with a dot.",
        "filename contains unsafe characters.",
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
def test_future_failure_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "accepted controlled fixture-owned write.",
        "missing authorization rejection.",
        "unknown authorization rejection.",
        "dry-run authorization rejection.",
        "missing output root rejection.",
        "nonexistent output root rejection.",
        "non-directory output root rejection.",
        "uncontrolled output root rejection.",
        "parent traversal rejection.",
        "path separator filename rejection.",
        "leading-dot filename rejection.",
        "unsafe character filename rejection.",
        "unsupported extension rejection.",
        "target already exists rejection.",
        "empty content rejection.",
        "UTF-8 byte count verification.",
        "content hash before and after verification.",
        "no-overwrite behavior.",
        "no directory creation behavior.",
        "no arbitrary cleanup behavior.",
        "safety flags on success.",
        "safety flags on failure.",
        "deterministic result shape.",
        "existing dry-run CLI remains unchanged.",
        "existing dry-run bridge remains unchanged.",
        "no scanner execution.",
        "no ffprobe execution.",
        "no FFmpeg execution.",
        "no external process execution.",
        "no network access.",
        "no SaaS or database access.",
    ],
)
def test_future_tests_required_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The current dry-run CLI must remain dry-run-only.",
        "The current dry-run bridge must remain dry-run-only.",
        "The current smoke execution chain must remain accepted.",
        "The current smoke execution QA closure review must remain accepted.",
        "The write-enabled implementation must be isolated from dry-run CLI behavior.",
        "The write-enabled implementation must not add write flags to the current dry-run CLI.",
        "The write-enabled implementation must not reinterpret `--dry-run`.",
        "The write-enabled implementation must not modify existing dry-run result semantics.",
    ],
)
def test_current_dry_run_preservation_requirement_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "modifies the current dry-run CLI.",
        "modifies the current dry-run bridge.",
        "adds scanner execution.",
        "adds ffprobe execution.",
        "adds FFmpeg execution.",
        "adds external process execution.",
        "adds network access.",
        "adds SaaS integration.",
        "adds database access.",
        "adds backend changes.",
        "adds frontend changes.",
        "adds installer work.",
        "adds client-facing demo behavior.",
        "adds public demo behavior.",
        "adds production behavior.",
        "creates directories.",
        "deletes files.",
        "overwrites existing files.",
        "accepts arbitrary output paths.",
        "writes outside controlled output root.",
        "writes more than one artifact.",
        "writes from disk-sourced report content.",
        "reads real media.",
        "omits post-write verification.",
        "omits content hash comparison.",
        "omits byte count comparison.",
        "omits safety flags.",
        "weakens existing dry-run tests.",
    ],
)
def test_future_implementation_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize write-enabled export implementation now.",
        "This readiness gate does not authorize directory creation.",
        "This readiness gate does not authorize artifact creation on disk now.",
        "This readiness gate does not authorize real file writing now.",
        "This readiness gate does not authorize media scanning.",
        "This readiness gate does not authorize real media decoding.",
        "This readiness gate does not authorize scanner execution.",
        "This readiness gate does not authorize ffprobe execution.",
        "This readiness gate does not authorize FFmpeg execution.",
        "This readiness gate does not authorize external process execution.",
        "This readiness gate does not authorize audio extraction.",
        "This readiness gate does not authorize sync.",
        "This readiness gate does not authorize transcription.",
        "This readiness gate does not authorize subtitle generation.",
        "This readiness gate does not authorize timeline export.",
        "This readiness gate does not authorize network access.",
        "This readiness gate does not authorize SaaS integration.",
        "This readiness gate does not authorize database changes.",
        "This readiness gate does not authorize backend changes.",
        "This readiness gate does not authorize frontend changes.",
        "This readiness gate does not authorize installer work.",
        "This readiness gate does not authorize public demo work.",
        "This readiness gate does not authorize client-facing demo work.",
        "This readiness gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_readiness_gate_decision_allows_only_controlled_implementation_next() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export implementation boundary is ready for a future controlled implementation phase." in doc
    assert "The current project remains dry-run-only." in doc
    assert "The current project remains not ready for public, client-facing, or production use." in doc
    assert "The next phase may be a controlled implementation phase limited to the exact module, function, write authorization, fixture-owned output, and tests defined here." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step may add the controlled implementation module and implementation tests only within the boundaries defined here." in doc


def test_closure_doc_supports_readiness_next_step() -> None:
    source = _read(CLOSURE_DOC_PATH)

    assert "The controlled write-enabled export contract QA gate is accepted and closed." in source
    assert "The next phase must be a controlled implementation readiness gate." in source
    assert PHASE_ID in source
    assert "That next step must remain doc/test-only." in source


def test_qa_gate_doc_remains_conservative() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "The controlled write-enabled export contract is accepted by QA gate." in source
    assert "The current project remains dry-run-only." in source
    assert "The current project remains not ready for write-enabled implementation." in source
    assert "This QA gate does not authorize write-enabled export implementation." in source
    assert "This QA gate does not authorize artifact creation on disk now." in source
    assert "This QA gate does not authorize real file writing now." in source


def test_contract_doc_remains_conservative() -> None:
    source = _read(CONTRACT_DOC_PATH)

    assert "This contract does not add implementation code." in source
    assert "This contract does not perform write-enabled export." in source
    assert "This contract does not create directories." in source
    assert "This contract does not create artifacts on disk." in source
    assert "The current project remains dry-run-only." in source
    assert "The current project remains not ready for write-enabled implementation." in source


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
