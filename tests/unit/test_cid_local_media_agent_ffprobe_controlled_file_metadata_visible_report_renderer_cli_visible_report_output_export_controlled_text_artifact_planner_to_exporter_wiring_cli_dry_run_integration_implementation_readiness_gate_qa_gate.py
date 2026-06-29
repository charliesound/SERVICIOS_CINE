from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_v1.md"
)

READINESS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate.py"
)

CONTRACT_CLOSURE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_contract_qa_gate_closure_review_v1.md"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_IMPLEMENTATION_READINESS_GATE_"
    "QA_GATE_PASS_READY_FOR_CLOSURE_REVIEW"
)

PREVIOUS_COMMIT = "2dbc455d34cfd566ed03dd683737e3ebf2ccbe36"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-impl-readiness-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-impl-readiness-qa-gate-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [READINESS_DOC_PATH, READINESS_TEST_PATH, CONTRACT_CLOSURE_DOC_PATH, BRIDGE_MODULE_PATH],
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
        "This QA gate validates the CLI dry-run integration implementation readiness gate.",
        "This QA gate does not add CLI integration code.",
        "This QA gate does not modify CLI argument parsing.",
        "This QA gate does not modify CLI command routing.",
        "This QA gate does not modify the controlled dry-run bridge.",
        "This QA gate does not modify planner runtime code.",
        "This QA gate does not modify exporter runtime code.",
        "This QA gate does not authorize write-enabled behavior.",
    ],
)
def test_qa_gate_declares_lineage_scope_result_and_next_step(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run implementation readiness gate test passed with 132 checks.",
        "previous contract QA closure review test passed with 101 checks.",
        "previous contract QA gate test passed with 157 checks.",
        "previous contract test passed with 141 checks.",
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
        "final target test passed with 132 checks.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the CLI dry-run integration implementation readiness boundary is defined.",
        "the controlled dry-run bridge remains the only accepted future implementation target.",
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
def test_qa_acceptance_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future implementation may be considered only after this readiness gate is validated by this QA gate and closed by a closure review.",
        "A future implementation may add controlled CLI dry-run integration only after a later implementation phase explicitly authorizes code.",
        "The future implementation must be limited to CLI dry-run integration.",
        "The future implementation must call or wrap the existing controlled dry-run bridge.",
        "The future implementation must preserve the bridge safety contract.",
        "The future implementation must preserve `dry_run=True`.",
        "The future implementation must preserve `write_requested=False`.",
        "The future implementation must preserve `write_performed=False`.",
        "The future implementation must preserve `artifact_created_on_disk=False`.",
        "The future implementation must preserve `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` for accepted dry-run.",
        "The future implementation must surface validation failures as fail-closed CLI errors.",
    ],
)
def test_future_implementation_boundary_is_accepted_for_later_authorization(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future implementation is still forbidden before explicit implementation authorization.",
        "CLI integration code is still forbidden before explicit implementation authorization.",
        "CLI argument parsing changes are still forbidden before explicit implementation authorization.",
        "CLI command routing changes are still forbidden before explicit implementation authorization.",
        "Write-enabled export is still forbidden.",
        "Directory creation is still forbidden.",
        "Artifact creation on disk is still forbidden.",
        "Real file writing is still forbidden.",
        "Media scanning is still forbidden.",
        "Real media decoding is still forbidden.",
        "ffprobe execution is still forbidden.",
        "FFmpeg execution is still forbidden.",
        "Subprocess execution is still forbidden.",
        "Audio extraction is still forbidden.",
        "Sync is still forbidden.",
        "Transcription is still forbidden.",
        "Subtitle generation is still forbidden.",
        "Timeline export is still forbidden.",
        "Network access is still forbidden.",
        "SaaS integration is still forbidden.",
        "Database changes are still forbidden.",
        "Backend changes are still forbidden.",
        "Frontend changes are still forbidden.",
        "Installer work is still forbidden.",
        "Public demo work is still forbidden.",
        "Client-facing demo work is still forbidden.",
        "Production use is still forbidden.",
    ],
)
def test_future_implementation_remains_forbidden_before_authorization(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "authorizes CLI integration code.",
        "authorizes CLI argument parsing changes.",
        "authorizes CLI command routing changes.",
        "authorizes write-enabled export.",
        "authorizes directory creation.",
        "authorizes artifact creation on disk.",
        "authorizes real file writing.",
        "authorizes media scanning.",
        "authorizes real media decoding.",
        "authorizes ffprobe execution.",
        "authorizes FFmpeg execution.",
        "authorizes subprocess execution.",
        "authorizes audio extraction.",
        "authorizes sync.",
        "authorizes transcription.",
        "authorizes subtitle generation.",
        "authorizes timeline export.",
        "authorizes network access.",
        "authorizes SaaS integration.",
        "authorizes database changes.",
        "authorizes backend changes.",
        "authorizes frontend changes.",
        "authorizes installer work.",
        "authorizes public demo behavior.",
        "authorizes client-facing demo behavior.",
        "authorizes production behavior.",
        "omits doc/test-only status.",
        "omits future implementation target.",
        "omits bridge safety contract preservation.",
        "omits dry-run-only boundary.",
        "omits fail-closed behavior.",
        "omits no-write boundary.",
        "omits no-artifact-created-on-disk boundary.",
    ],
)
def test_qa_rejection_conditions_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize CLI integration code.",
        "This QA gate does not authorize CLI argument parsing changes.",
        "This QA gate does not authorize CLI command routing changes.",
        "This QA gate does not authorize write-enabled export.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize artifact creation on disk.",
        "This QA gate does not authorize real file writing.",
        "This QA gate does not authorize media scanning.",
        "This QA gate does not authorize real media decoding.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize subprocess execution.",
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

    assert "The CLI dry-run integration implementation readiness gate is accepted." in doc
    assert "The CLI dry-run integration implementation readiness boundary is accepted." in doc
    assert "The controlled dry-run bridge remains the only accepted future implementation target." in doc
    assert "The project is ready for a future doc/test-only CLI dry-run integration implementation readiness QA gate closure review." in doc
    assert "The project is not ready for CLI dry-run integration code." in doc
    assert "The project is not ready for CLI argument parsing changes." in doc
    assert "The project is not ready for CLI command routing changes." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_readiness_doc_remains_conservative() -> None:
    source = _read(READINESS_DOC_PATH)

    assert "This readiness gate does not authorize CLI integration code." in source
    assert "This readiness gate does not authorize CLI argument parsing changes." in source
    assert "This readiness gate does not authorize CLI command routing changes." in source
    assert "This readiness gate does not authorize write-enabled behavior." in source
    assert "The controlled dry-run bridge remains the only accepted future implementation target." in source
    assert "The project is not ready for CLI dry-run integration code." in source


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


def test_qa_gate_test_does_not_import_runtime_modules() -> None:
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
