from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_closure_review_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_closure_review.py"
)

PREVIOUS_QA_GATE_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_v1.md"
)

PREVIOUS_QA_GATE_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate.py"
)

PLANNER_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER."
    "IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_READY_TO_CLOSE"
)

PREVIOUS_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER."
    "IMPLEMENTATION.QA.GATE.V1"
)

PREVIOUS_RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_QA_GATE_PASS_CLOSED"
)

PREVIOUS_STABLE_COMMIT = "a59a42ae010d2753665a8c1c3c3d311264a4834a"

PREVIOUS_STABLE_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-controlled-export-path-planner-implementation-qa-gate-v1-20260622"
)

TARGET_CLOSURE_REVIEW_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-controlled-export-path-planner-implementation-qa-gate-closure-review-v1-20260622"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_closure_review_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_closure_review_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_previous_qa_gate_document_exists() -> None:
    assert PREVIOUS_QA_GATE_DOC_PATH.is_file()


def test_previous_qa_gate_test_exists() -> None:
    assert PREVIOUS_QA_GATE_TEST_PATH.is_file()


def test_planner_module_exists_but_is_not_imported_by_this_review() -> None:
    assert PLANNER_MODULE_PATH.is_file()


@pytest.mark.parametrize(
    "required_text",
    [
        PHASE_ID,
        RESULT_ID,
        PREVIOUS_PHASE_ID,
        PREVIOUS_RESULT_ID,
        PREVIOUS_STABLE_COMMIT,
        PREVIOUS_STABLE_TAG,
        TARGET_CLOSURE_REVIEW_TAG,
        "The scope is strictly doc/test-only.",
        "Only these two files are in scope for this microphase:",
        "No other files are in scope for this microphase.",
        "No planner module changes are authorized.",
        "No previous implementation test changes are authorized.",
        "The implementation QA gate is accepted as properly closed.",
        "This closure review does not expand the product behavior.",
    ],
)
def test_closure_review_document_contains_required_lineage_and_scope(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "working tree clean after post-push verification.",
        "`HEAD` and `origin/main` aligned at `a59a42ae010d2753665a8c1c3c3d311264a4834a`.",
        "previous remote tag points to `a59a42ae010d2753665a8c1c3c3d311264a4834a`.",
        "target closure review tag was absent locally before this review.",
        "target closure review tag was absent remotely before this review.",
        "WSL guard passed.",
        "DB regression guard passed.",
        "mixed recovery cleanup passed.",
        "unexpected modifications were restored from HEAD before closure.",
        "unstaged diff was empty before closure.",
        "exact staged files check passed.",
        "protected staged files check passed.",
        "staged restricted database-word check passed.",
        "py_compile passed using a short cfile path.",
        "implementation QA gate test passed with 35 checks.",
        "path planner implementation test passed with 27 checks.",
        "previous readiness gate QA gate closure review test passed with 17 checks.",
        "previous readiness gate QA gate test passed with 17 checks.",
        "previous planner contract test passed with 18 checks.",
        "commit, local tag, push main, push tag, and post-push verification completed.",
    ],
)
def test_closure_review_document_records_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "accepts `controlled_export_root`.",
        "accepts `controlled_descriptor`.",
        "requires `suggested_filename`.",
        "validates controlled roots.",
        "validates suggested filenames.",
        "requires suffix `.controlled_visible_report.txt`.",
        "returns `planned_artifact_path`.",
        "returns `artifact_format`.",
        "returns `content_sha256`.",
        "returns `write_performed=False`.",
        "returns `artifact_created_on_disk=False`.",
        "returns `path_boundary`.",
        "returns `safety_flags`.",
        "keeps all safety flags false.",
        "does not write files.",
        "does not create directories.",
        "does not create artifacts on disk.",
        "does not scan folders.",
        "does not execute media tooling.",
        "does not access the network.",
        "does not touch SaaS, database, backend, frontend, installer, or client-facing code.",
    ],
)
def test_closure_review_document_summarizes_previous_planner_contract(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "No exporter wiring is authorized.",
        "No path resolver expansion is authorized.",
        "No file writing is authorized.",
        "No directory creation is authorized.",
        "No artifact creation on disk is authorized.",
        "No real media usage is authorized.",
        "No arbitrary folder scanning is authorized.",
        "No ffprobe execution is authorized.",
        "No FFmpeg execution is authorized.",
        "No child process execution is authorized.",
        "No audio extraction is authorized.",
        "No sync is authorized.",
        "No transcription is authorized.",
        "No subtitle generation is authorized.",
        "No timeline export is authorized.",
        "No network access is authorized.",
        "No SaaS integration is authorized.",
        "No database changes are authorized.",
        "No installer work is authorized.",
        "No public demo is authorized.",
        "No client-facing demo is authorized.",
        "No production use is authorized.",
    ],
)
def test_closure_review_document_preserves_non_scope(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "forbidden_marker",
    [
        "SCOPE_AUTHORIZATION: exporter wiring",
        "SCOPE_AUTHORIZATION: path resolver expansion",
        "SCOPE_AUTHORIZATION: file writing",
        "SCOPE_AUTHORIZATION: directory creation",
        "SCOPE_AUTHORIZATION: artifact creation on disk",
        "SCOPE_AUTHORIZATION: real media",
        "SCOPE_AUTHORIZATION: arbitrary folder scanning",
        "SCOPE_AUTHORIZATION: media execution",
        "SCOPE_AUTHORIZATION: audio extraction",
        "SCOPE_AUTHORIZATION: sync",
        "SCOPE_AUTHORIZATION: transcription",
        "SCOPE_AUTHORIZATION: subtitle generation",
        "SCOPE_AUTHORIZATION: timeline export",
        "SCOPE_AUTHORIZATION: network access",
        "SCOPE_AUTHORIZATION: SaaS integration",
        "SCOPE_AUTHORIZATION: database changes",
        "SCOPE_AUTHORIZATION: installer work",
        "SCOPE_AUTHORIZATION: public demo",
        "SCOPE_AUTHORIZATION: client-facing demo",
        "SCOPE_AUTHORIZATION: production use",
    ],
)
def test_closure_review_document_contains_no_expansion_authorization_markers(forbidden_marker: str) -> None:
    assert forbidden_marker not in _read(DOC_PATH)


def test_closure_review_document_declares_next_step_as_separate_gate() -> None:
    doc = _read(DOC_PATH)

    assert "Any future wiring between the planner and exporter requires a separate readiness gate before implementation." in doc
    assert "Any future writing to disk requires a separate contract and QA gate before implementation." in doc
    assert "Any future real media scenario requires a separate controlled real-media authorization gate before execution." in doc


def test_previous_qa_gate_document_is_not_replaced_by_closure_review() -> None:
    previous_doc = _read(PREVIOUS_QA_GATE_DOC_PATH)
    current_doc = _read(DOC_PATH)

    assert PREVIOUS_PHASE_ID in previous_doc
    assert PREVIOUS_RESULT_ID in previous_doc
    assert RESULT_ID not in previous_doc
    assert TARGET_CLOSURE_REVIEW_TAG not in previous_doc
    assert previous_doc != current_doc


def test_current_test_is_doc_test_only_and_does_not_import_planner() -> None:
    test_source = _read(THIS_TEST_PATH)

    forbidden_dynamic_loader = "import" + "lib"
    forbidden_package_loader = "from scripts" + ".local_media_agent"
    forbidden_planner_loader = (
        "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_"
        "export_path_planner " + "import"
    )

    assert forbidden_dynamic_loader not in test_source
    assert forbidden_package_loader not in test_source
    assert forbidden_planner_loader not in test_source


def test_closure_review_document_names_exactly_two_new_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_closure_review_v1.md"
    ) in doc
    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_controlled_export_path_planner_implementation_qa_gate_closure_review.py"
    ) in doc
