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
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning.py"
)

PREVIOUS_CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_controlled_smoke_execution_qa_gate_closure_review_v1.md"
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
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.NEXT_SCOPE.PLANNING.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_NEXT_SCOPE_PLANNING_"
    "PASS_READY_FOR_WRITE_ENABLED_EXPORT_CONTRACT"
)

PREVIOUS_COMMIT = "90b7374cc5285b4eba9b9f6adcdff86e931ca9fb"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-smoke-execution-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-next-scope-planning-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTRACT.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_next_scope_planning_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_next_scope_planning_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize("path", [PREVIOUS_CLOSURE_DOC_PATH, CLI_MODULE_PATH, BRIDGE_MODULE_PATH])
def test_artifacts_under_planning_review_exist(path: Path) -> None:
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
        "This is a doc/test-only next-scope planning phase.",
        "This planning phase selects the next product path after the controlled CLI dry-run smoke execution closure.",
        "This planning phase does not add implementation code.",
        "This planning phase does not modify CLI argument parsing.",
        "This planning phase does not modify command routing.",
        "This planning phase does not modify the controlled dry-run bridge.",
        "This planning phase does not authorize write-enabled behavior.",
    ],
)
def test_planning_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_planning_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_next_scope_planning.py"
    ) in doc

    assert "No other files are in scope." in doc


def test_path_b_is_selected_and_path_a_deferred() -> None:
    doc = _read(DOC_PATH)

    assert "PATH_B_WRITE_ENABLED_EXPORT_CONTRACT_FIRST" in doc
    assert "PATH_A_QA_UX_DRY_RUN_USAGE_DOCS_DEFERRED" in doc
    assert "Path B is selected." in doc
    assert "Path B is not an implementation authorization." in doc
    assert "Path B only authorizes a future contract/readiness sequence for controlled write-enabled export." in doc
    assert "Path B must not skip directly into write-enabled code." in doc
    assert "Path B must not skip directly into disk artifact creation." in doc
    assert "Path B must not skip directly into real media." in doc
    assert "Path B must not skip directly into client-facing use." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "controlled implementation.",
        "controlled implementation QA gate.",
        "controlled implementation QA gate closure review.",
        "controlled smoke execution.",
        "controlled smoke execution QA gate.",
        "controlled smoke execution QA gate closure review.",
    ],
)
def test_planning_records_closed_chain_before_path_b(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The future contract must specify exactly one minimal controlled output artifact.",
        "The future contract must specify exactly one controlled temporary or fixture-owned output root.",
        "The future contract must specify a strict filename allowlist.",
        "The future contract must specify extension allowlist behavior.",
        "The future contract must specify parent directory boundary checks.",
        "The future contract must specify no overwrite behavior.",
        "The future contract must specify deterministic text content behavior.",
        "The future contract must specify post-write verification requirements.",
        "The future contract must specify cleanup or fixture isolation requirements.",
        "The future contract must specify audit metadata.",
        "The future contract must specify failure behavior.",
        "The future contract must specify rollback expectations if a write attempt fails.",
        "The future contract must specify that real media remains out of scope.",
        "The future contract must specify that scanner execution remains out of scope.",
        "The future contract must specify that ffprobe execution remains out of scope.",
        "The future contract must specify that FFmpeg execution remains out of scope.",
        "The future contract must specify that external process execution remains out of scope.",
        "The future contract must specify that network access remains out of scope.",
        "The future contract must specify that SaaS, database, backend, frontend, installer, client demo, public demo, and production behavior remain out of scope.",
    ],
)
def test_next_scope_objective_is_contract_first(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "1. controlled write-enabled export contract.",
        "2. controlled write-enabled export contract QA gate.",
        "3. controlled write-enabled export contract QA gate closure review.",
        "4. controlled write-enabled export implementation readiness gate.",
        "5. controlled write-enabled export implementation readiness QA gate.",
        "6. controlled write-enabled export implementation readiness QA gate closure review.",
        "7. minimal controlled implementation.",
        "8. implementation QA gate.",
        "9. implementation QA gate closure review.",
        "10. controlled execution using fixture-owned output only.",
        "11. controlled execution QA gate.",
        "12. controlled execution QA gate closure review.",
    ],
)
def test_required_future_gate_sequence_is_complete(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the output root is controlled.",
        "the output root is test-owned or fixture-owned.",
        "the output path remains inside the controlled output root.",
        "the filename is deterministic.",
        "the extension is approved.",
        "parent traversal is rejected.",
        "absolute unsafe paths are rejected.",
        "home-relative paths are rejected.",
        "environment-derived paths are rejected.",
        "overwrite is rejected by default.",
        "content is deterministic.",
        "content hash is computed before write.",
        "content hash is verified after write.",
        "the result reports bytes intended.",
        "the result reports bytes written.",
        "the result reports content hash before and after.",
        "the result reports artifact path.",
        "the result reports write state.",
        "the result reports cleanup expectations.",
    ],
)
def test_future_contract_boundaries_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "no real media access.",
        "no scanner execution.",
        "no ffprobe execution.",
        "no FFmpeg execution.",
        "no external process execution.",
        "no network access.",
        "no SaaS integration.",
        "no database changes.",
        "no backend changes.",
        "no frontend changes.",
        "no installer work.",
        "no client-facing demo.",
        "no public demo.",
        "no production use.",
    ],
)
def test_current_prohibitions_remain_for_future_contract(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
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
        "omits a contract-first sequence.",
        "omits contract QA gate.",
        "omits readiness gate.",
        "omits implementation QA gate.",
        "omits controlled execution QA gate.",
        "skips directly to production behavior.",
    ],
)
def test_planning_rejection_conditions_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This planning phase does not authorize write-enabled export.",
        "This planning phase does not authorize directory creation.",
        "This planning phase does not authorize artifact creation on disk.",
        "This planning phase does not authorize real file writing.",
        "This planning phase does not authorize media scanning.",
        "This planning phase does not authorize real media decoding.",
        "This planning phase does not authorize ffprobe execution.",
        "This planning phase does not authorize FFmpeg execution.",
        "This planning phase does not authorize external process execution.",
        "This planning phase does not authorize audio extraction.",
        "This planning phase does not authorize sync.",
        "This planning phase does not authorize transcription.",
        "This planning phase does not authorize subtitle generation.",
        "This planning phase does not authorize timeline export.",
        "This planning phase does not authorize network access.",
        "This planning phase does not authorize SaaS integration.",
        "This planning phase does not authorize database changes.",
        "This planning phase does not authorize backend changes.",
        "This planning phase does not authorize frontend changes.",
        "This planning phase does not authorize installer work.",
        "This planning phase does not authorize public demo work.",
        "This planning phase does not authorize client-facing demo work.",
        "This planning phase does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_planning_decision_allows_only_write_enabled_contract_next() -> None:
    doc = _read(DOC_PATH)

    assert "Path B is selected." in doc
    assert "The next product direction is controlled write-enabled export contract-first." in doc
    assert "The next phase must be doc/test-only." in doc
    assert "The next phase must define boundaries before implementation." in doc
    assert "The current project remains dry-run-only." in doc
    assert "The current project remains not ready for write-enabled behavior." in doc
    assert "The current project remains not ready for directory creation." in doc
    assert "The current project remains not ready for artifact creation on disk." in doc
    assert "The current project remains not ready for real media execution." in doc
    assert "The current project remains not ready for public, client-facing, or production use." in doc
    assert NEXT_PHASE_ID in doc
    assert "That next step must remain doc/test-only." in doc


def test_previous_closure_review_remains_conservative() -> None:
    source = _read(PREVIOUS_CLOSURE_DOC_PATH)

    assert "The controlled CLI dry-run smoke execution QA gate is accepted and closed." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to inline controlled values." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to deterministic stdout JSON output." in source
    assert "The controlled CLI dry-run smoke execution remains restricted to dry-run-only behavior." in source
    assert "The project is not ready for write-enabled export behavior." in source
    assert "The project is not ready for artifact creation on disk." in source


def test_cli_parser_still_exposes_only_safe_options() -> None:
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
        "--output",
        "--output-path",
        "--create-dir",
        "--mkdir",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
        "--production",
    }:
        assert forbidden_option not in option_strings


def test_cli_source_has_no_forbidden_runtime_markers() -> None:
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


def test_bridge_safety_contract_remains_visible() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    required_markers = [
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_performed": False',
        '"artifact_created_on_disk": False',
        "Only dry-run mode is supported",
        "write_requested must remain false",
    ]

    for marker in required_markers:
        assert marker in source
