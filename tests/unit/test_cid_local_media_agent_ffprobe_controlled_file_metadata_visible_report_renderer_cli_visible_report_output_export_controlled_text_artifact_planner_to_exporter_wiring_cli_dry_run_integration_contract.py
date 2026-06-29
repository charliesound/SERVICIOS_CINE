from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract.py"
)

PREVIOUS_CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate_qa_gate_closure_review_v1.md"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

BRIDGE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTRACT.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTRACT_PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "7ec53d5ee662eb4f8d8dc9f082483ec9d48394c2"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-readiness-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-contract-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTRACT.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_contract_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize("path", [PREVIOUS_CLOSURE_DOC_PATH, BRIDGE_MODULE_PATH, BRIDGE_TEST_PATH])
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
        "This contract defines the future CLI dry-run integration boundary.",
        "This contract does not add CLI integration code.",
        "This contract does not modify CLI argument parsing.",
        "This contract does not modify CLI command routing.",
        "This contract does not modify the controlled dry-run bridge.",
        "This contract does not modify planner runtime code.",
        "This contract does not modify exporter runtime code.",
        "This contract does not authorize write-enabled behavior.",
    ],
)
def test_contract_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target closure review test passed with 93 checks.",
        "previous CLI dry-run integration readiness QA gate test passed with 157 checks.",
        "previous CLI dry-run integration readiness gate test passed with 136 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "push main completed.",
        "short tag moved to validated HEAD.",
        "push short tag completed.",
        "old long remote tag was absent.",
        "post-push verification completed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_contract_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI dry-run integration may expose controlled dry-run exporter metadata through an existing or future CLI surface only after a later implementation readiness gate authorizes code.",
        "The future CLI command must remain dry-run only.",
        "The future CLI command must route to the controlled dry-run bridge without changing the bridge safety contract.",
        "The future CLI command must not bypass planner validation.",
        "The future CLI command must not bypass visible report text validation.",
        "The future CLI command must not bypass filename suffix validation.",
        "The future CLI command must not bypass planned artifact path validation.",
        "The future CLI command must not bypass content hash validation.",
        "The future CLI command must not bypass path boundary validation.",
        "The future CLI command must not bypass safety flag validation.",
        "The future CLI command must not bypass caller context sanitization.",
    ],
)
def test_future_cli_command_boundary_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI dry-run integration must receive or build a planner result that already satisfies the controlled dry-run bridge contract.",
        "A future CLI dry-run integration must receive visible report text as controlled text input.",
        "A future CLI dry-run integration must preserve `dry_run=True`.",
        "A future CLI dry-run integration must preserve `write_requested=False`.",
        "A future CLI dry-run integration must reject or fail closed for `write_requested=True`.",
        "A future CLI dry-run integration must reject or fail closed for `dry_run=False`.",
        "A future CLI dry-run integration must reject missing planner result fields.",
        "A future CLI dry-run integration must reject unsafe path boundary data.",
        "A future CLI dry-run integration must reject unsafe safety flag data.",
        "A future CLI dry-run integration must reject content hash mismatch.",
        "A future CLI dry-run integration must reject planner results that claim prior write execution.",
        "A future CLI dry-run integration must reject planner results that claim prior artifact creation.",
    ],
)
def test_future_cli_input_contract_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI dry-run integration must display `dry_run=True`.",
        "A future CLI dry-run integration must display `write_performed=False`.",
        "A future CLI dry-run integration must display `artifact_created_on_disk=False`.",
        "A future CLI dry-run integration must display `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` when accepted.",
        "A future CLI dry-run integration must display the planned artifact path as human-visible dry-run information only.",
        "A future CLI dry-run integration must state that no file was written.",
        "A future CLI dry-run integration must state that no artifact was created on disk.",
        "A future CLI dry-run integration must not claim that an export was produced.",
        "A future CLI dry-run integration must not claim that a directory was created.",
        "A future CLI dry-run integration must not claim that an artifact exists on disk.",
        "A future CLI dry-run integration must redact or avoid sensitive paths when required by existing privacy policy.",
    ],
)
def test_future_cli_output_contract_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI dry-run integration must fail closed.",
        "A future CLI dry-run integration must surface bridge validation errors as controlled CLI errors.",
        "A future CLI dry-run integration must not continue into write behavior after failure.",
        "A future CLI dry-run integration must not create fallback artifacts after failure.",
        "A future CLI dry-run integration must not create fallback directories after failure.",
        "A future CLI dry-run integration must not execute media tools after failure.",
        "A future CLI dry-run integration must not access the network after failure.",
    ],
)
def test_future_cli_failure_contract_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`dry_run=True`",
        "`write_requested=False`",
        "`write_performed=False`",
        "`artifact_created_on_disk=False`",
        "`exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`",
        "planned artifact path for review",
        "no file written",
        "no artifact created on disk",
    ],
)
def test_future_cli_success_markers_are_controlled(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This contract does not authorize CLI integration code.",
        "This contract does not authorize CLI argument parsing changes.",
        "This contract does not authorize CLI command routing changes.",
        "This contract does not authorize write-enabled export.",
        "This contract does not authorize directory creation.",
        "This contract does not authorize artifact creation on disk.",
        "This contract does not authorize real file writing.",
        "This contract does not authorize media scanning.",
        "This contract does not authorize real media decoding.",
        "This contract does not authorize ffprobe execution.",
        "This contract does not authorize FFmpeg execution.",
        "This contract does not authorize subprocess execution.",
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


@pytest.mark.parametrize(
    "required_text",
    [
        "CLI integration code.",
        "CLI argument parsing changes.",
        "CLI command routing changes.",
        "write-enabled export.",
        "directory creation.",
        "artifact creation on disk.",
        "real file writing.",
        "media scanning.",
        "real media decoding.",
        "ffprobe execution.",
        "FFmpeg execution.",
        "subprocess execution.",
        "audio extraction.",
        "sync.",
        "transcription.",
        "subtitle generation.",
        "timeline export.",
        "network access.",
        "SaaS integration.",
        "database changes.",
        "backend changes.",
        "frontend changes.",
        "installer work.",
        "public demo behavior.",
        "client-facing demo behavior.",
        "production behavior.",
    ],
)
def test_contract_rejection_conditions_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_decision_allows_only_qa_gate_next() -> None:
    doc = _read(DOC_PATH)

    assert "The future CLI dry-run integration boundary is defined." in doc
    assert "The controlled dry-run bridge remains the only accepted future integration target." in doc
    assert "The project is ready for a future doc/test-only CLI dry-run integration contract QA gate." in doc
    assert "The project is not ready for CLI dry-run integration code." in doc
    assert "The project is not ready for CLI argument parsing changes." in doc
    assert "The project is not ready for CLI command routing changes." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_existing_bridge_still_exposes_dry_run_safety_markers() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    required_markers = [
        "plan_controlled_text_artifact_exporter_dry_run_from_planner_result",
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_performed": False',
        '"artifact_created_on_disk": False',
        "Only dry-run mode is supported",
        "write_requested must remain false",
    ]

    for marker in required_markers:
        assert marker in source


def test_existing_bridge_contains_no_disk_network_or_process_runtime_markers() -> None:
    source = _read(BRIDGE_MODULE_PATH)

    forbidden_markers = [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        "open(",
        "sub" + "process",
        "Popen",
        "socket",
        "requests",
        "urllib",
        "http.client",
    ]

    for marker in forbidden_markers:
        assert marker not in source


def test_contract_test_does_not_import_runtime_modules() -> None:
    source = _read(THIS_TEST_PATH)

    blocked_runtime_imports = [
        "from scripts" + ".local_media_agent",
        "import scripts" + ".local_media_agent",
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "socket",
        "import " + "http",
    ]

    for blocked in blocked_runtime_imports:
        assert blocked not in source
