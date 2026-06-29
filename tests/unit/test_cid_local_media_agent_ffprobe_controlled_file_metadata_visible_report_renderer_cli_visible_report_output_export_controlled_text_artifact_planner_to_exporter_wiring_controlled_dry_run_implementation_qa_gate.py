from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
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
    "CONTROLLED.DRY_RUN.IMPLEMENTATION.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CONTROLLED_DRY_RUN_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_CLOSURE_REVIEW"
)

PREVIOUS_COMMIT = "2e029d8e9cd08b2a25129d6a860322ff81fa65a8"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-controlled-dry-run-implementation-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-controlled-dry-run-implementation-qa-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CONTROLLED.DRY_RUN.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_implementation_artifacts_under_qa_exist() -> None:
    assert IMPLEMENTATION_MODULE_PATH.is_file()
    assert IMPLEMENTATION_TEST_PATH.is_file()


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
        "This QA gate validates the controlled dry-run planner-to-exporter bridge implementation.",
        "This QA gate does not add runtime behavior.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "py_compile passed.",
        "target controlled dry-run implementation test passed with 40 checks.",
        "previous implementation readiness QA gate test passed with 144 checks.",
        "previous implementation readiness gate test passed with 127 checks.",
        "previous contract QA gate test passed with 131 checks.",
        "previous contract test passed with 155 checks.",
        "planner implementation test passed with 27 checks.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "module runtime safety check passed.",
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
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "a pure controlled dry-run bridge.",
        "explicit planner result validation.",
        "explicit visible report text validation.",
        "explicit dry-run enforcement.",
        "explicit write request rejection.",
        "explicit controlled suffix validation.",
        "explicit planned artifact path validation.",
        "explicit content hash validation.",
        "explicit prior write claim rejection.",
        "explicit prior artifact creation claim rejection.",
        "explicit path boundary validation.",
        "explicit safety flags validation.",
        "explicit caller context sanitization.",
        "human-visible dry-run summary.",
        "exporter-facing decision metadata.",
        "no disk write behavior.",
        "no directory creation behavior.",
        "no artifact creation behavior.",
        "no media execution behavior.",
        "no network behavior.",
        "no SaaS, database, backend, frontend, installer, public demo, client demo, or production behavior.",
    ],
)
def test_qa_gate_accepts_required_implementation_content(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_records_empty_mapping_defensive_validation() -> None:
    doc = _read(DOC_PATH)

    assert "empty mappings are rejected" in doc
    assert "`path_boundary`." in doc
    assert "`safety_flags`." in doc
    assert "all([]) == True" in doc
    assert "is not accepted" in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "the bridge remains dry-run only.",
        "`dry_run=False` is rejected.",
        "`write_requested=True` is rejected.",
        "missing planner result fields are rejected.",
        "non-mapping planner results are rejected.",
        "empty visible report text is rejected.",
        "wrong filename suffix is rejected.",
        "planned artifact paths that do not include the suggested filename are rejected.",
        "content hash mismatch is rejected.",
        "prior write execution claims are rejected.",
        "prior artifact creation claims are rejected.",
        "unsafe path boundary values are rejected.",
        "empty path boundary mappings are rejected.",
        "unsafe safety flags are rejected.",
        "empty safety flag mappings are rejected.",
        "non-scalar caller context values are rejected.",
        "empty caller context keys are rejected.",
        "successful dry-run returns `write_performed=False`.",
        "successful dry-run returns `artifact_created_on_disk=False`.",
        "successful dry-run returns `exporter_decision=CONTROLLED_DRY_RUN_ACCEPTED`.",
        "successful dry-run preserves the planned artifact path for human review.",
        "successful dry-run states that no file was written.",
        "successful dry-run states that no artifact was created on disk.",
    ],
)
def test_required_implementation_guarantees_are_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "writes files.",
        "creates directories.",
        "creates artifacts on disk.",
        "executes subprocesses.",
        "executes ffprobe.",
        "executes FFmpeg.",
        "scans media folders.",
        "decodes media.",
        "extracts audio.",
        "performs sync.",
        "performs transcription.",
        "generates subtitles.",
        "exports timelines.",
        "accesses the network.",
        "touches SaaS code.",
        "touches database code.",
        "touches backend code.",
        "touches frontend code.",
        "touches installer code.",
        "adds public demo behavior.",
        "adds client-facing demo behavior.",
        "adds production behavior.",
        "imports existing planner runtime modules.",
        "imports existing exporter runtime modules.",
        "accepts empty path boundary mappings.",
        "accepts empty safety flag mappings.",
        "accepts write execution claims.",
        "accepts artifact creation claims.",
        "returns `write_performed=True`.",
        "returns `artifact_created_on_disk=True`.",
    ],
)
def test_qa_rejection_conditions_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize write-enabled export.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize artifact creation on disk.",
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

    assert "The controlled dry-run implementation is accepted." in doc
    assert "The project is ready for a future controlled dry-run implementation closure review." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_implementation_module_contains_expected_dry_run_contract_markers() -> None:
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


def test_implementation_test_preserves_empty_mapping_regression_cases() -> None:
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
