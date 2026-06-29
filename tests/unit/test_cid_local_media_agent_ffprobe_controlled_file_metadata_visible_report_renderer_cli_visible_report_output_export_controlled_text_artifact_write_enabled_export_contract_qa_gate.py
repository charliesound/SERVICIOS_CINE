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
    "controlled_text_artifact_write_enabled_export_contract_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_qa_gate.py"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract_v1.md"
)

CONTRACT_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_write_enabled_export_contract.py"
)

PLANNING_DOC_PATH = ROOT / (
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
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_WRITE_ENABLED_EXPORT_CONTRACT_QA_GATE_PASS_READY_FOR_CLOSURE_REVIEW"
)

PREVIOUS_COMMIT = "bea2a6d842c4e21645588503222a4e8a2d8f4425"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-contract-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-write-enabled-export-contract-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_write_enabled_export_contract_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_write_enabled_export_contract_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [
        CONTRACT_DOC_PATH,
        CONTRACT_TEST_PATH,
        PLANNING_DOC_PATH,
        CLI_MODULE_PATH,
        BRIDGE_MODULE_PATH,
    ],
)
def test_artifacts_under_qa_exist(path: Path) -> None:
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
        "This is a doc/test-only QA gate.",
        "This QA gate validates the controlled write-enabled export contract.",
        "This QA gate does not add implementation code.",
        "This QA gate does not modify CLI argument parsing.",
        "This QA gate does not modify command routing.",
        "This QA gate does not modify the controlled dry-run bridge.",
        "This QA gate does not perform write-enabled export.",
        "This QA gate does not create directories.",
        "This QA gate does not create artifacts on disk.",
    ],
)
def test_qa_gate_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_contract_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_write_enabled_export_contract_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target write-enabled export contract test passed with 251 checks.",
        "next scope planning test passed with 142 checks.",
        "smoke execution QA closure review test passed with 113 checks.",
        "smoke execution test passed with 128 checks.",
        "implementation test passed with 41 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "current CLI forbidden marker check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target write-enabled export contract short tag absent locally before tagging.",
        "target write-enabled export contract short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target write-enabled export contract test passed with 251 checks.",
        "final next scope planning test passed with 142 checks.",
        "final smoke execution QA closure review test passed with 113 checks.",
        "final smoke execution test passed with 128 checks.",
        "final implementation test passed with 41 checks.",
        "final current CLI forbidden marker check passed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the contract is doc/test-only.",
        "the contract defines a future controlled write-enabled export boundary.",
        "the contract does not add implementation code.",
        "the contract does not modify CLI argument parsing.",
        "the contract does not modify command routing.",
        "the contract does not modify the controlled dry-run bridge.",
        "the contract does not perform write-enabled export.",
        "the contract does not create directories.",
        "the contract does not create artifacts on disk.",
        "the contract preserves the previous Path B decision.",
        "the contract keeps the current project dry-run-only.",
        "the contract requires a future contract QA gate.",
        "the contract requires future implementation readiness before implementation.",
        "the contract requires fixture-owned or test-owned output.",
        "the contract requires one controlled visible report text artifact.",
        "the contract requires local-only behavior.",
        "the contract requires isolation from real user media.",
        "the contract requires isolation from client-facing behavior.",
        "the contract requires isolation from public demo and production behavior.",
    ],
)
def test_qa_acceptance_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "controlled output root requirements.",
        "deterministic filename requirements.",
        "extension allowlist requirements.",
        "path boundary checks.",
        "parent traversal rejection.",
        "unsafe absolute path rejection.",
        "home-relative path rejection.",
        "environment-derived path rejection.",
        "symlink boundary ambiguity rejection unless a future explicit symlink policy is defined.",
        "no-overwrite default behavior.",
        "no truncation behavior.",
        "no append behavior.",
        "no replacement behavior.",
        "no overwrite flag support in the first implementation.",
        "empty content rejection.",
        "binary content rejection.",
        "UTF-8 encoding.",
        "pre-write content hash.",
        "pre-write byte count.",
        "exact intended byte write requirement.",
        "post-write content hash verification.",
        "post-write byte count verification.",
        "fail-closed verification behavior.",
    ],
)
def test_boundary_findings_are_recorded(required_text: str) -> None:
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
def test_result_contract_findings_are_recorded(required_text: str) -> None:
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
        "The contract allows `file_write_performed=True` only for the single future controlled artifact write.",
        "The contract allows `artifact_created_on_disk=True` only for the single future controlled artifact write.",
        "The contract requires every other operational safety flag to remain false in the accepted future result.",
    ],
)
def test_safety_flag_findings_are_recorded(required_text: str) -> None:
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
def test_failure_contract_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "fixture-owned output only.",
        "cleanup under test ownership.",
        "no deletion of arbitrary user files.",
        "no cleanup outside the controlled output root.",
        "no parent directory removal.",
        "cleanup expectations to be reported instead of broad cleanup.",
        "partial artifact behavior to be decided in a future implementation readiness gate.",
        "no cleanup implementation in the current contract.",
    ],
)
def test_cleanup_and_rollback_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the existing controlled dry-run CLI as dry-run-only.",
        "the existing controlled dry-run bridge as dry-run-only.",
        "the future write-enabled CLI must not reuse `--dry-run` semantics to perform writing.",
        "the future write-enabled CLI must use a distinct explicit write authorization mechanism.",
        "the future write-enabled CLI must require controlled output root.",
        "the future write-enabled CLI must not accept arbitrary output paths.",
        "the future write-enabled CLI must not accept real media paths.",
        "the future write-enabled CLI must not accept scanner execution flags.",
        "the future write-enabled CLI must not accept ffprobe execution flags.",
        "the future write-enabled CLI must not accept FFmpeg execution flags.",
        "the future write-enabled CLI must not accept network flags.",
        "the future write-enabled CLI must not accept production flags.",
    ],
)
def test_cli_boundary_findings_are_recorded(required_text: str) -> None:
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
def test_implementation_readiness_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "accepts implementation code.",
        "accepts CLI argument parsing changes.",
        "accepts command routing changes.",
        "accepts controlled dry-run bridge changes.",
        "accepts immediate write-enabled implementation.",
        "accepts directory creation now.",
        "accepts artifact creation on disk now.",
        "accepts real file writing now.",
        "accepts media scanning.",
        "accepts real media decoding.",
        "accepts scanner execution.",
        "accepts ffprobe execution.",
        "accepts FFmpeg execution.",
        "accepts external process execution.",
        "accepts network access.",
        "accepts SaaS integration.",
        "accepts database changes.",
        "accepts backend changes.",
        "accepts frontend changes.",
        "accepts installer work.",
        "accepts client-facing demo.",
        "accepts public demo.",
        "accepts production use.",
        "accepts arbitrary output paths.",
        "accepts overwrite behavior in the first future implementation.",
        "accepts missing content hash verification.",
        "accepts missing byte count verification.",
        "accepts missing failure behavior.",
        "accepts missing fixture-owned output policy.",
        "accepts skipping implementation readiness.",
    ],
)
def test_qa_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize write-enabled export implementation.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize artifact creation on disk now.",
        "This QA gate does not authorize real file writing now.",
        "This QA gate does not authorize media scanning.",
        "This QA gate does not authorize real media decoding.",
        "This QA gate does not authorize scanner execution.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize external process execution.",
        "This QA gate does not authorize audio extraction.",
        "This QA gate does not authorize sync.",
        "This QA gate does not authorize transcription.",
        "This QA gate does not authorize subtitle generation.",
        "This QA gate does not authorize timeline export.",
        "This QA gate does not authorize network access.",
        "This QA gate does not authorize SaaS integration.",
        "This QA gate does not authorize database changes.",
        "This QA gate does not authorize backend changes.",
        "This QA gate does not authorize frontend changes.",
        "This QA gate does not authorize installer work.",
        "This QA gate does not authorize public demo work.",
        "This QA gate does not authorize client-facing demo work.",
        "This QA gate does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_decision_allows_only_closure_review_next() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled write-enabled export contract is accepted by QA gate." in doc
    assert "The current project remains dry-run-only." in doc
    assert "The current project remains not ready for write-enabled implementation." in doc
    assert "The current project remains not ready for directory creation." in doc
    assert "The current project remains not ready for artifact creation on disk." in doc
    assert "The current project remains not ready for real media execution." in doc
    assert "The current project remains not ready for public, client-facing, or production use." in doc
    assert "The next phase must be a QA gate closure review." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc


def test_contract_doc_remains_conservative() -> None:
    source = _read(CONTRACT_DOC_PATH)

    assert "This contract does not add implementation code." in source
    assert "This contract does not perform write-enabled export." in source
    assert "This contract does not create directories." in source
    assert "This contract does not create artifacts on disk." in source
    assert "The current project remains dry-run-only." in source
    assert "The current project remains not ready for write-enabled implementation." in source


def test_previous_planning_doc_remains_contract_first() -> None:
    source = _read(PLANNING_DOC_PATH)

    assert "PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST" in source
    assert "The next product direction is controlled write-enabled export contract-first." in source
    assert "The next phase must define boundaries before implementation." in source
    assert "The current project remains dry-run-only." in source
    assert "The current project remains not ready for write-enabled behavior." in source


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
