from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate.py"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_v1.md"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTRACT_QA_GATE_"
    "CLOSURE_REVIEW_PASS_READY_FOR_IMPLEMENTATION_READINESS_GATE"
)

PREVIOUS_COMMIT = "a3d38d3c2a5da19a72aa57a2d62b32002cd0ef49"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-contract-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-contract-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [QA_GATE_DOC_PATH, QA_GATE_TEST_PATH, CONTRACT_DOC_PATH, BRIDGE_MODULE_PATH],
)
def test_artifacts_under_closure_review_exist(path: Path) -> None:
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
        "This is a doc/test-only closure review.",
        "This closure review validates that the CLI dry-run integration contract QA gate can be closed.",
        "This closure review does not add CLI integration code.",
        "This closure review does not modify CLI argument parsing.",
        "This closure review does not modify CLI command routing.",
        "This closure review does not modify the controlled dry-run bridge.",
        "This closure review does not modify planner runtime code.",
        "This closure review does not modify exporter runtime code.",
        "This closure review does not authorize write-enabled behavior.",
    ],
)
def test_closure_review_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_closure_review_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run integration contract QA gate test passed with 157 checks.",
        "previous CLI dry-run integration contract test passed with 141 checks.",
        "previous readiness QA closure review test passed with 93 checks.",
        "previous readiness QA gate test passed with 157 checks.",
        "previous controlled dry-run implementation test passed with 40 checks.",
        "previous contract test passed with 155 checks.",
        "planner implementation test passed with 27 checks.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target short tag absent locally before tagging.",
        "target short tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "final target test passed with 157 checks.",
        "working tree was clean after post-push verification.",
    ],
)
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the CLI dry-run integration contract is accepted.",
        "the future CLI dry-run integration boundary is accepted.",
        "the controlled dry-run bridge remains the only accepted future integration target.",
        "CLI dry-run integration code is not authorized yet.",
        "CLI argument parsing changes are not authorized yet.",
        "CLI command routing changes are not authorized yet.",
        "the future CLI command must remain dry-run only.",
        "the future CLI command must route to the controlled dry-run bridge without changing the bridge safety contract.",
        "the future CLI command must not bypass planner validation.",
        "the future CLI command must not bypass visible report text validation.",
        "the future CLI command must not bypass filename suffix validation.",
        "the future CLI command must not bypass planned artifact path validation.",
        "the future CLI command must not bypass content hash validation.",
        "the future CLI command must not bypass path boundary validation.",
        "the future CLI command must not bypass safety flag validation.",
        "the future CLI command must not bypass caller context sanitization.",
        "the future CLI dry-run integration must preserve `dry_run=True`.",
        "the future CLI dry-run integration must preserve `write_requested=False`.",
        "the future CLI dry-run integration must reject or fail closed for `write_requested=True`.",
        "the future CLI dry-run integration must reject or fail closed for `dry_run=False`.",
        "the future CLI dry-run integration must display `write_performed=False`.",
        "the future CLI dry-run integration must display `artifact_created_on_disk=False`.",
        "the future CLI dry-run integration must display `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` when accepted.",
        "the future CLI dry-run integration must state that no file was written.",
        "the future CLI dry-run integration must state that no artifact was created on disk.",
        "the future CLI dry-run integration must fail closed.",
        "the future CLI dry-run integration must not continue into write behavior after failure.",
    ],
)
def test_closure_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize CLI integration code.",
        "This closure review does not authorize CLI argument parsing changes.",
        "This closure review does not authorize CLI command routing changes.",
        "This closure review does not authorize write-enabled export.",
        "This closure review does not authorize directory creation.",
        "This closure review does not authorize artifact creation on disk.",
        "This closure review does not authorize real file writing.",
        "This closure review does not authorize media scanning.",
        "This closure review does not authorize real media decoding.",
        "This closure review does not authorize ffprobe execution.",
        "This closure review does not authorize FFmpeg execution.",
        "This closure review does not authorize subprocess execution.",
        "This closure review does not authorize audio extraction.",
        "This closure review does not authorize sync.",
        "This closure review does not authorize transcription.",
        "This closure review does not authorize subtitle generation.",
        "This closure review does not authorize timeline export.",
        "This closure review does not authorize network access.",
        "This closure review does not authorize SaaS integration.",
        "This closure review does not authorize database changes.",
        "This closure review does not authorize backend changes.",
        "This closure review does not authorize frontend changes.",
        "This closure review does not authorize installer work.",
        "This closure review does not authorize public demo work.",
        "This closure review does not authorize client-facing demo work.",
        "This closure review does not authorize production use.",
    ],
)
def test_remaining_prohibitions_are_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_closure_decision_allows_only_implementation_readiness_next() -> None:
    doc = _read(DOC_PATH)

    assert "The CLI dry-run integration contract QA gate is accepted and closed." in doc
    assert "The future CLI dry-run integration boundary remains accepted." in doc
    assert "The controlled dry-run bridge remains the only accepted future integration target." in doc
    assert "The project is ready for a future doc/test-only CLI dry-run integration implementation readiness gate." in doc
    assert "The project is not ready for CLI dry-run integration code." in doc
    assert "The project is not ready for CLI argument parsing changes." in doc
    assert "The project is not ready for CLI command routing changes." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_qa_gate_doc_remains_conservative() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "This QA gate does not authorize CLI integration code." in source
    assert "This QA gate does not authorize CLI argument parsing changes." in source
    assert "This QA gate does not authorize CLI command routing changes." in source
    assert "This QA gate does not authorize write-enabled behavior." in source
    assert "The controlled dry-run bridge remains the only accepted future integration target." in source


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


def test_closure_review_test_does_not_import_runtime_modules() -> None:
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
