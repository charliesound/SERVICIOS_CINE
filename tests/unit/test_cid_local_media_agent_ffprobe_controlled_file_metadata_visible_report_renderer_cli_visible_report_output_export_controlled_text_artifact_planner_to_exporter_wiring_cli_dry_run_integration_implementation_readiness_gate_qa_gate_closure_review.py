from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_v1.md"
)

BRIDGE_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.IMPLEMENTATION.READINESS.GATE.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_IMPLEMENTATION_READINESS_GATE_"
    "QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_IMPLEMENTATION"
)

PREVIOUS_COMMIT = "870af879c223d9126581b50772090666d2b17e75"

PREVIOUS_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-impl-readiness-qa-gate-v1-20260629"

TARGET_TAG = "cid-dev-stable-local-media-agent-cli-dry-run-impl-readiness-qa-closure-review-v1-20260629"

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [QA_GATE_DOC_PATH, QA_GATE_TEST_PATH, READINESS_DOC_PATH, BRIDGE_MODULE_PATH],
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
        "This closure review validates that the CLI dry-run integration implementation readiness QA gate can be closed.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_closure_review_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_implementation_readiness_gate_qa_gate_closure_review.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target CLI dry-run implementation readiness QA gate test passed with 160 checks.",
        "previous implementation readiness gate test passed with 132 checks.",
        "previous contract QA closure review test passed with 101 checks.",
        "previous contract QA gate test passed with 157 checks.",
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
        "final target test passed with 160 checks.",
        "working tree was clean after post-push verification.",
    ],
)
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the CLI dry-run integration implementation readiness gate is accepted.",
        "the CLI dry-run integration implementation readiness boundary is accepted.",
        "the controlled dry-run bridge remains the only accepted future implementation target.",
        "the readiness QA gate remains doc/test-only.",
        "the readiness QA gate does not authorize CLI code.",
        "the readiness QA gate does not authorize parser changes.",
        "the readiness QA gate does not authorize command routing changes.",
        "the readiness QA gate preserves the dry-run-only boundary.",
        "the readiness QA gate preserves the no-write boundary.",
        "the readiness QA gate preserves the no-directory boundary.",
        "the readiness QA gate preserves the no-artifact-on-disk boundary.",
        "the readiness QA gate preserves the no-media-execution boundary.",
        "the readiness QA gate preserves the no-network boundary.",
        "the readiness QA gate preserves the no-SaaS and no-database boundary.",
        "the readiness QA gate preserves the bridge safety contract.",
        "the readiness QA gate names the future controlled implementation target.",
        "the readiness QA gate requires fail-closed error behavior.",
    ],
)
def test_closure_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future controlled implementation may be considered after this closure review is closed.",
        "The next controlled implementation must be limited to CLI dry-run integration.",
        "The next controlled implementation must call or wrap the existing controlled dry-run bridge.",
        "The next controlled implementation must preserve the bridge safety contract.",
        "The next controlled implementation must preserve `dry_run=True`.",
        "The next controlled implementation must preserve `write_requested=False`.",
        "The next controlled implementation must preserve `write_performed=False`.",
        "The next controlled implementation must preserve `artifact_created_on_disk=False`.",
        "The next controlled implementation must preserve `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` for accepted dry-run.",
        "The next controlled implementation must surface validation failures as fail-closed CLI errors.",
        "The next controlled implementation must not write files.",
        "The next controlled implementation must not create directories.",
        "The next controlled implementation must not create artifacts on disk.",
        "The next controlled implementation must not execute ffprobe.",
        "The next controlled implementation must not execute FFmpeg.",
        "The next controlled implementation must not execute subprocesses.",
        "The next controlled implementation must not scan arbitrary folders.",
        "The next controlled implementation must not use real media.",
        "The next controlled implementation must not access the network.",
        "The next controlled implementation must not touch SaaS, database, backend, frontend, installer, client demo, public demo, or production code.",
    ],
)
def test_controlled_implementation_authorization_boundary_is_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
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


def test_closure_decision_allows_only_controlled_implementation_next() -> None:
    doc = _read(DOC_PATH)

    assert "The CLI dry-run integration implementation readiness QA gate is accepted and closed." in doc
    assert "The CLI dry-run integration implementation readiness boundary remains accepted." in doc
    assert "The controlled dry-run bridge remains the only accepted future implementation target." in doc
    assert "The project is ready for a future controlled CLI dry-run integration implementation phase." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step may add controlled CLI dry-run integration code only within the explicit dry-run-only boundary." in doc


def test_qa_gate_doc_remains_conservative() -> None:
    source = _read(QA_GATE_DOC_PATH)

    assert "This QA gate does not authorize CLI integration code." in source
    assert "This QA gate does not authorize CLI argument parsing changes." in source
    assert "This QA gate does not authorize CLI command routing changes." in source
    assert "This QA gate does not authorize write-enabled behavior." in source
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
