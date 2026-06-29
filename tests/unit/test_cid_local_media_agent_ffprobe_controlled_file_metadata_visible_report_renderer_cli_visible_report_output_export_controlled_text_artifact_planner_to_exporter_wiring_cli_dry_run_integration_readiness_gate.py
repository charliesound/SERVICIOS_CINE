from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate.py"
)

CLOSURE_REVIEW_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review_v1.md"
)

CLOSURE_REVIEW_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review.py"
)

IMPLEMENTATION_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

IMPLEMENTATION_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_READINESS_GATE_PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "14eabb64e0e5f760fd05497e3537c616dfb597b5"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-controlled-dry-run-implementation-qa-gate-closure-review-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-cli-dry-run-integration-readiness-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.READINESS.GATE.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [CLOSURE_REVIEW_DOC_PATH, CLOSURE_REVIEW_TEST_PATH, IMPLEMENTATION_MODULE_PATH, IMPLEMENTATION_TEST_PATH],
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
        "This is a doc/test-only readiness gate.",
        "This readiness gate evaluates a future CLI dry-run integration boundary.",
        "This readiness gate does not add CLI integration code.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_cli_dry_run_integration_readiness_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target closure review test passed with 109 checks.",
        "previous controlled dry-run implementation QA gate test passed with 140 checks.",
        "previous controlled dry-run implementation test passed with 40 checks.",
        "previous implementation readiness QA gate test passed with 144 checks.",
        "previous contract test passed with 155 checks.",
        "planner implementation test passed with 27 checks.",
        "py_compile passed.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "target tag absent locally before tagging.",
        "target tag absent remotely before tagging.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_readiness_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The project is ready for a future doc/test-only CLI dry-run integration readiness QA gate.",
        "The project is not yet ready for CLI dry-run integration code.",
        "The project is not yet ready for CLI argument parsing changes.",
        "The project is not yet ready for CLI command routing changes.",
        "The project is not yet ready for write-enabled export behavior.",
        "The project is not yet ready for directory creation.",
        "The project is not yet ready for artifact creation on disk.",
        "The project is not yet ready for real media execution.",
        "The project is not yet ready for public, client-facing, or production use.",
    ],
)
def test_readiness_assessment_is_conservative(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future CLI dry-run integration may only be considered after a separate CLI dry-run integration readiness QA gate closes successfully.",
        "A future CLI dry-run integration must remain dry-run only.",
        "A future CLI dry-run integration must call or route to the controlled dry-run bridge without changing its safety contract.",
        "A future CLI dry-run integration must preserve `write_performed=False`.",
        "A future CLI dry-run integration must preserve `artifact_created_on_disk=False`.",
        "A future CLI dry-run integration must display planned artifact path as human-visible information only.",
        "A future CLI dry-run integration must not state that a file was written.",
        "A future CLI dry-run integration must not state that an artifact exists on disk.",
        "A future CLI dry-run integration must not accept write-enabled export flags.",
        "A future CLI dry-run integration must not create output directories.",
        "A future CLI dry-run integration must not create artifacts on disk.",
        "A future CLI dry-run integration must not execute ffprobe.",
        "A future CLI dry-run integration must not execute FFmpeg.",
        "A future CLI dry-run integration must not execute child processes.",
        "A future CLI dry-run integration must not scan arbitrary folders.",
        "A future CLI dry-run integration must not use real media.",
        "A future CLI dry-run integration must not access the network.",
        "A future CLI dry-run integration must not touch SaaS, database, backend, frontend, installer, public demo, client demo, or production code.",
    ],
)
def test_future_cli_integration_boundary_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "CLI-visible output includes the planned artifact path.",
        "CLI-visible output includes `dry_run=True`.",
        "CLI-visible output includes `write_performed=False`.",
        "CLI-visible output includes `artifact_created_on_disk=False`.",
        "CLI-visible output includes `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED` for accepted dry-run.",
        "CLI-visible output does not claim file creation.",
        "CLI-visible output does not claim directory creation.",
        "CLI-visible output does not claim artifact creation on disk.",
        "CLI-visible output redacts or avoids sensitive paths when required by existing privacy policy.",
        "CLI-visible failure output fails closed.",
        "CLI-visible failure output does not continue into write behavior.",
        "bridge validation errors surface as controlled CLI errors.",
        "existing bridge tests remain passing.",
        "existing QA gate tests remain passing.",
        "WSL guard remains passing.",
        "database regression guard remains passing.",
    ],
)
def test_future_cli_acceptance_criteria_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
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
def test_future_cli_non_goals_are_declared(required_text: str) -> None:
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


def test_readiness_decision_allows_only_next_doc_test_qa_gate() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled dry-run bridge is ready to be evaluated for future CLI dry-run integration." in doc
    assert "The project is ready for a future doc/test-only CLI dry-run integration readiness QA gate." in doc
    assert "The project is not ready for CLI dry-run integration code." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_existing_bridge_still_exposes_expected_dry_run_markers() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

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
    source = _read(IMPLEMENTATION_MODULE_PATH)

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
