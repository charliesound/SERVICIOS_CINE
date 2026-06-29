from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate.py"
)

CONTRACT_CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review_v1.md"
)

CONTRACT_QA_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_v1.md"
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
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_IMPLEMENTATION_READINESS_GATE_"
    "PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "db40907b7e5cce8c48a7af4dc17d45d9d8f28ce0"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-contract-qa-closure-review-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-impl-readiness-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [CONTRACT_CLOSURE_DOC_PATH, CONTRACT_QA_DOC_PATH, CONTRACT_DOC_PATH, BRIDGE_MODULE_PATH],
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
        "This readiness gate prepares a future CLI dry-run controlled implementation.",
        "This readiness gate does not add CLI integration code.",
        "This readiness gate does not modify CLI argument parsing.",
        "This readiness gate does not modify CLI command routing.",
        "This readiness gate does not modify the controlled dry-run bridge.",
        "This readiness gate does not modify planner runtime code.",
        "This readiness gate does not modify exporter runtime code.",
        "This readiness gate does not authorize write-enabled behavior.",
    ],
)
def test_readiness_gate_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_readiness_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run integration contract QA gate closure review test passed with 101 checks.",
        "previous CLI dry-run integration contract QA gate test passed with 157 checks.",
        "previous CLI dry-run integration contract test passed with 141 checks.",
        "previous readiness QA closure review test passed with 93 checks.",
        "previous controlled dry-run implementation test passed with 40 checks.",
        "py_compile passed.",
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
        "final target test passed with 101 checks.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future implementation may be considered only after this readiness gate is validated by a QA gate.",
        "A future implementation may add controlled CLI dry-run integration only after a later implementation phase explicitly authorizes code.",
        "This readiness gate does not itself authorize implementation.",
        "The future implementation must be limited to CLI dry-run integration.",
        "The future implementation must not write files.",
        "The future implementation must not create directories.",
        "The future implementation must not create artifacts on disk.",
        "The future implementation must not execute ffprobe.",
        "The future implementation must not execute FFmpeg.",
        "The future implementation must not execute subprocesses.",
        "The future implementation must not scan arbitrary folders.",
        "The future implementation must not use real media.",
        "The future implementation must not access the network.",
        "The future implementation must not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
    ],
)
def test_implementation_readiness_boundary_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The only accepted future implementation target is a controlled CLI dry-run surface that calls or wraps the existing controlled dry-run bridge.",
        "The controlled dry-run bridge must remain the source of truth for dry-run exporter decisions.",
        "The future CLI dry-run integration must preserve the bridge safety contract.",
        "The future CLI dry-run integration must preserve `dry_run=True`.",
        "The future CLI dry-run integration must preserve `write_requested=False`.",
        "The future CLI dry-run integration must preserve `write_performed=False`.",
        "The future CLI dry-run integration must preserve `artifact_created_on_disk=False`.",
        "The future CLI dry-run integration must preserve `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` for accepted dry-run.",
    ],
)
def test_future_implementation_target_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future controlled implementation may only add dry-run-only CLI wiring after explicit implementation authorization.",
        "A future controlled implementation may only expose bridge results as visible CLI output.",
        "A future controlled implementation may only use controlled in-memory values.",
        "A future controlled implementation may only surface planned artifact path as dry-run information.",
        "A future controlled implementation may only report that no file was written.",
        "A future controlled implementation may only report that no artifact was created on disk.",
        "A future controlled implementation may only surface controlled validation errors as fail-closed CLI errors.",
    ],
)
def test_future_implementation_allowed_shape_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future controlled implementation must not add write flags.",
        "A future controlled implementation must not add write-enabled export options.",
        "A future controlled implementation must not add directory creation.",
        "A future controlled implementation must not add artifact creation on disk.",
        "A future controlled implementation must not add real media scanning.",
        "A future controlled implementation must not add ffprobe execution.",
        "A future controlled implementation must not add FFmpeg execution.",
        "A future controlled implementation must not add subprocess execution.",
        "A future controlled implementation must not add network access.",
        "A future controlled implementation must not add SaaS integration.",
        "A future controlled implementation must not add database integration.",
        "A future controlled implementation must not add backend changes.",
        "A future controlled implementation must not add frontend changes.",
        "A future controlled implementation must not add installer behavior.",
        "A future controlled implementation must not add public demo behavior.",
        "A future controlled implementation must not add client-facing demo behavior.",
        "A future controlled implementation must not add production behavior.",
    ],
)
def test_future_implementation_forbidden_shape_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "this readiness gate remains doc/test-only.",
        "this readiness gate does not authorize CLI code.",
        "this readiness gate does not authorize parser changes.",
        "this readiness gate does not authorize command routing changes.",
        "this readiness gate preserves the dry-run-only boundary.",
        "this readiness gate preserves the no-write boundary.",
        "this readiness gate preserves the no-directory boundary.",
        "this readiness gate preserves the no-artifact-on-disk boundary.",
        "this readiness gate preserves the no-media-execution boundary.",
        "this readiness gate preserves the no-network boundary.",
        "this readiness gate preserves the no-SaaS and no-database boundary.",
        "this readiness gate preserves the bridge safety contract.",
        "this readiness gate names the future controlled implementation target.",
        "this readiness gate requires fail-closed error behavior.",
    ],
)
def test_required_qa_before_implementation_authorization_is_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize CLI integration code.",
        "This readiness gate does not authorize CLI argument parsing changes.",
        "This readiness gate does not authorize CLI command routing changes.",
        "This readiness gate does not authorize write-enabled export.",
        "This readiness gate does not authorize directory creation.",
        "This readiness gate does not authorize artifact creation on disk.",
        "This readiness gate does not authorize real file writing.",
        "This readiness gate does not authorize media scanning.",
        "This readiness gate does not authorize real media decoding.",
        "This readiness gate does not authorize ffprobe execution.",
        "This readiness gate does not authorize FFmpeg execution.",
        "This readiness gate does not authorize subprocess execution.",
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


def test_readiness_decision_allows_only_qa_gate_next() -> None:
    doc = _read(DOC_PATH)

    assert "The CLI dry-run integration implementation readiness boundary is defined." in doc
    assert "The controlled dry-run bridge remains the only accepted future implementation target." in doc
    assert "The project is ready for a future doc/test-only CLI dry-run integration implementation readiness QA gate." in doc
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


def test_readiness_gate_test_does_not_import_runtime_modules() -> None:
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
