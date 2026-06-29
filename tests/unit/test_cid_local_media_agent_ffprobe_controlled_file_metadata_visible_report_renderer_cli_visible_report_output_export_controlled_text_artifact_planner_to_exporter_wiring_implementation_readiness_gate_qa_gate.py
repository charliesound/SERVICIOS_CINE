from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_qa_gate.py"
)

READINESS_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_v1.md"
)

READINESS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_IMPLEMENTATION_READINESS_GATE_QA_GATE_PASS_READY_FOR_CONTROLLED_DRY_RUN_IMPLEMENTATION"
)

PREVIOUS_COMMIT = "f38045a82bb3ba9d640f60bd62752bdfba8363de"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-implementation-readiness-gate-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-implementation-readiness-gate-qa-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CONTROLLED.DRY_RUN.IMPLEMENTATION.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_readiness_artifacts_under_qa_exist() -> None:
    assert READINESS_DOC_PATH.is_file()
    assert READINESS_TEST_PATH.is_file()


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
        "This QA gate validates the planner-to-exporter wiring implementation readiness gate.",
        "This QA gate does not implement planner-to-exporter wiring.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target implementation readiness gate test passed with 127 checks.",
        "previous contract QA gate test passed with 131 checks.",
        "previous contract test passed with 155 checks.",
        "previous readiness gate test passed with 13 checks.",
        "previous closure review test passed with 106 checks.",
        "previous QA gate test passed with 35 checks.",
        "planner implementation test passed with 27 checks.",
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
def test_qa_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "doc/test-only readiness status.",
        "previous stable lineage.",
        "target tag.",
        "files in scope.",
        "contract and QA artifacts under review.",
        "previous QA evidence.",
        "conservative readiness assessment.",
        "future implementation boundaries.",
        "future implementation acceptance criteria.",
        "future implementation non-goals.",
        "explicit non-authorization.",
        "readiness decision.",
        "next allowed step.",
    ],
)
def test_qa_gate_accepts_required_readiness_sections(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the project is ready only for a future doc/test-only implementation readiness QA gate.",
        "the project is not ready for planner-to-exporter runtime implementation.",
        "the project is not ready for write-enabled export behavior.",
        "the project is not ready for artifact creation on disk.",
        "the project is not ready for real media execution.",
        "the project is not ready for public, client-facing, or production use.",
        "a future implementation may only be considered after a separate implementation readiness QA gate closes successfully.",
        "a future implementation must remain limited to controlled planner-to-exporter wiring.",
        "a future implementation must preserve dry-run behavior unless a later write-enabled gate authorizes otherwise.",
        "a future implementation must not write files unless a later explicit gate authorizes write-enabled behavior.",
        "a future implementation must not create directories unless a later explicit gate authorizes controlled directory creation.",
        "a future implementation must not create artifacts on disk unless a later explicit gate authorizes artifact creation.",
        "a future implementation must not scan arbitrary folders.",
        "a future implementation must not use real media.",
        "a future implementation must not execute ffprobe.",
        "a future implementation must not execute FFmpeg.",
        "a future implementation must not execute child processes.",
        "a future implementation must not access the network.",
        "a future implementation must not touch SaaS, database, backend, frontend, installer, public demo, client demo, or production code.",
    ],
)
def test_required_readiness_guarantees_are_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "planner result is passed explicitly to exporter-facing logic.",
        "exporter-facing logic rejects missing planner result.",
        "exporter-facing logic rejects malformed planner result.",
        "exporter-facing logic rejects unsafe path boundary.",
        "exporter-facing logic rejects unsafe safety flags.",
        "exporter-facing logic rejects wrong suffix.",
        "exporter-facing logic rejects planner results claiming prior write execution.",
        "exporter-facing logic rejects planner results claiming prior artifact creation.",
        "dry-run behavior returns `write_performed=False`.",
        "dry-run behavior returns `artifact_created_on_disk=False`.",
        "planned artifact path remains human-visible.",
        "write intent remains distinct from write execution.",
        "artifact path planning remains distinct from artifact creation.",
        "existing planner tests remain passing.",
        "existing contract tests remain passing.",
        "existing contract QA gate tests remain passing.",
        "WSL guard remains passing.",
        "database regression guard remains passing.",
    ],
)
def test_future_implementation_acceptance_criteria_are_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "authorizes runtime implementation.",
        "authorizes connecting the planner to the exporter.",
        "authorizes changing the planner module.",
        "authorizes changing exporter runtime code.",
        "authorizes path resolver expansion.",
        "authorizes file writing.",
        "authorizes directory creation.",
        "authorizes artifact generation on disk.",
        "authorizes real media usage.",
        "authorizes arbitrary folder scanning.",
        "authorizes scanner execution.",
        "authorizes ffprobe execution.",
        "authorizes FFmpeg execution.",
        "authorizes child process execution.",
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
        "authorizes public demo work.",
        "authorizes client-facing demo work.",
        "authorizes production use.",
    ],
)
def test_qa_rejection_conditions_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This QA gate does not authorize connecting the planner to the exporter.",
        "This QA gate does not authorize changing the planner module.",
        "This QA gate does not authorize changing exporter runtime code.",
        "This QA gate does not authorize path resolver expansion.",
        "This QA gate does not authorize file writing.",
        "This QA gate does not authorize directory creation.",
        "This QA gate does not authorize artifact generation on disk.",
        "This QA gate does not authorize real media usage.",
        "This QA gate does not authorize arbitrary folder scanning.",
        "This QA gate does not authorize scanner execution.",
        "This QA gate does not authorize ffprobe execution.",
        "This QA gate does not authorize FFmpeg execution.",
        "This QA gate does not authorize child process execution.",
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


def test_qa_gate_decision_allows_only_controlled_dry_run_implementation_next() -> None:
    doc = _read(DOC_PATH)

    assert "The implementation readiness gate is accepted." in doc
    assert "The project is ready for a future controlled dry-run implementation phase." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for directory creation." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "does not write files" in doc
    assert "does not create directories" in doc
    assert "does not create artifacts on disk" in doc


def test_document_contains_no_scope_authorization_markers() -> None:
    doc = _read(DOC_PATH)

    forbidden_markers = [
        "SCOPE_AUTHORIZATION: write-enabled export",
        "SCOPE_AUTHORIZATION: directory creation",
        "SCOPE_AUTHORIZATION: artifact generation",
        "SCOPE_AUTHORIZATION: real media",
        "SCOPE_AUTHORIZATION: scanner execution",
        "SCOPE_AUTHORIZATION: media execution",
        "SCOPE_AUTHORIZATION: child process execution",
        "SCOPE_AUTHORIZATION: network access",
        "SCOPE_AUTHORIZATION: SaaS integration",
        "SCOPE_AUTHORIZATION: database changes",
        "SCOPE_AUTHORIZATION: client-facing demo",
        "SCOPE_AUTHORIZATION: production use",
    ]

    for marker in forbidden_markers:
        assert marker not in doc


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
