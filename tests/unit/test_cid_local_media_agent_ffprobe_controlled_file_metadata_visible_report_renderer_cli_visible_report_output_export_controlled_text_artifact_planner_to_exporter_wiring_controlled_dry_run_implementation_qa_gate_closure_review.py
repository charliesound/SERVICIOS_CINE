from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review.py"
)

QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_v1.md"
)

QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate.py"
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
    "CONTROLLED.DRY_RUN.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CONTROLLED_DRY_RUN_IMPLEMENTATION_QA_GATE_"
    "CLOSURE_REVIEW_PASS_READY_FOR_NEXT_READINESS_GATE"
)

PREVIOUS_COMMIT = "717302ac29f84d7a17993bb5774ab514e0c05321"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-controlled-dry-run-implementation-qa-gate-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-controlled-dry-run-implementation-qa-gate-closure-review-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.READINESS.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [QA_GATE_DOC_PATH, QA_GATE_TEST_PATH, IMPLEMENTATION_MODULE_PATH, IMPLEMENTATION_TEST_PATH],
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
        "This closure review validates that the controlled dry-run implementation QA gate can be closed.",
        "This closure review does not add runtime behavior.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_closure_review.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target controlled dry-run implementation QA gate test passed with 140 checks.",
        "previous controlled dry-run implementation test passed with 40 checks.",
        "previous implementation readiness QA gate test passed with 144 checks.",
        "previous implementation readiness gate test passed with 127 checks.",
        "previous contract QA gate test passed with 131 checks.",
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
def test_closure_review_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the implementation remains a pure controlled dry-run bridge.",
        "the implementation validates planner result shape.",
        "the implementation validates visible report text.",
        "the implementation enforces dry-run mode.",
        "the implementation rejects write requests.",
        "the implementation validates controlled filename suffix.",
        "the implementation validates planned artifact path.",
        "the implementation validates content hash.",
        "the implementation rejects prior write claims.",
        "the implementation rejects prior artifact creation claims.",
        "the implementation validates path boundary.",
        "the implementation rejects empty path boundary mappings.",
        "the implementation validates safety flags.",
        "the implementation rejects empty safety flag mappings.",
        "the implementation sanitizes caller context.",
        "the implementation returns exporter-facing decision metadata.",
        "the implementation returns human-visible dry-run summary.",
        "the implementation returns `write_performed=False`.",
        "the implementation returns `artifact_created_on_disk=False`.",
        "the implementation has no disk write behavior.",
        "the implementation has no directory creation behavior.",
        "the implementation has no artifact creation behavior.",
        "the implementation has no media execution behavior.",
        "the implementation has no network behavior.",
        "the implementation has no SaaS, database, backend, frontend, installer, public demo, client demo, or production behavior.",
    ],
)
def test_closure_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "target QA gate test passed.",
        "controlled dry-run implementation test passed.",
        "implementation readiness QA gate test passed.",
        "implementation readiness gate test passed.",
        "contract QA gate test passed.",
        "contract test passed.",
        "planner implementation test passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "exact staged file check passed.",
        "staged diff check passed.",
        "target tag was absent before closure.",
        "post-push verification passed.",
        "working tree was clean.",
    ],
)
def test_regression_findings_are_recorded(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_empty_mapping_bug_closure_is_recorded() -> None:
    doc = _read(DOC_PATH)

    assert "empty mapping validation bug is closed" in doc
    assert "no longer accepts an empty `path_boundary` mapping" in doc
    assert "no longer accepts an empty `safety_flags` mapping" in doc
    assert "all([]) == True" in doc
    assert "remains rejected" in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "This closure review does not authorize write-enabled export.",
        "This closure review does not authorize directory creation.",
        "This closure review does not authorize artifact creation on disk.",
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


def test_closure_decision_allows_only_next_readiness_gate() -> None:
    doc = _read(DOC_PATH)

    assert "The controlled dry-run implementation QA gate is accepted and closed." in doc
    assert "The project has a validated pure dry-run bridge from planner result to exporter-facing decision metadata." in doc
    assert "The project is ready for a future doc/test-only readiness gate for the next integration boundary." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only unless a later explicit gate authorizes CLI integration code." in doc


def test_implementation_module_still_contains_dry_run_contract_markers() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    required_markers = [
        "plan_controlled_text_artifact_exporter_dry_run_from_planner_result",
        "ControlledTextArtifactPlannerToExporterDryRunError",
        "CONTROLLED_VISIBLE_REPORT_SUFFIX",
        "Only dry-run mode is supported",
        "write_requested must remain false",
        "planner_result missing required fields",
        "content hash does not match",
        "planner_result must not claim prior write execution",
        "planner_result must not claim prior artifact creation",
        "path_boundary is not accepted as safe",
        "safety_flags must all be false",
        "CONTROLLED_DRY_RUN_ACCEPTED",
        '"write_performed": False',
        '"artifact_created_on_disk": False',
    ]

    for marker in required_markers:
        assert marker in source


def test_implementation_test_still_preserves_empty_mapping_regression_cases() -> None:
    source = _read(IMPLEMENTATION_TEST_PATH)

    assert "test_rejects_unsafe_path_boundary" in source
    assert "test_rejects_unsafe_safety_flags" in source
    assert "{}," in source
    assert 'match="path_boundary is not accepted as safe"' in source
    assert 'match="safety_flags must all be false"' in source


def test_implementation_module_contains_no_disk_network_or_process_runtime_markers() -> None:
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


def test_implementation_module_does_not_import_existing_planner_or_exporter_runtime() -> None:
    source = _read(IMPLEMENTATION_MODULE_PATH)

    forbidden_markers = [
        "from scripts" + ".local_media_agent",
        "import scripts" + ".local_media_agent",
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
