from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate.py"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_v1.md"
)

CONTRACT_QA_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate_v1.md"
)

CONTRACT_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract.py"
)

CONTRACT_QA_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "IMPLEMENTATION.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_IMPLEMENTATION_READINESS_GATE_PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "f271dae38c9633a0a6a9fe116bebb2c0773eca85"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-contract-qa-gate-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-implementation-readiness-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "IMPLEMENTATION.READINESS.GATE.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "path",
    [CONTRACT_DOC_PATH, CONTRACT_QA_DOC_PATH, CONTRACT_TEST_PATH, CONTRACT_QA_TEST_PATH],
)
def test_artifacts_under_review_exist(path: Path) -> None:
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
        "This readiness gate evaluates whether the project is ready for a future QA gate before implementation.",
        "This readiness gate does not implement planner-to-exporter wiring.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_implementation_readiness_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "target contract QA gate test passed with 131 checks.",
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
def test_readiness_gate_records_previous_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "The project is ready for a future doc/test-only implementation readiness QA gate.",
        "The project is not yet ready for planner-to-exporter runtime implementation.",
        "The project is not yet ready for write-enabled export behavior.",
        "The project is not yet ready for real artifact creation on disk.",
        "The project is not yet ready for real media execution.",
        "The project is not yet ready for public demo, client demo, or production use.",
    ],
)
def test_readiness_assessment_is_conservative(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "A future implementation may only be considered after a separate implementation readiness QA gate closes successfully.",
        "A future implementation must remain limited to controlled planner-to-exporter wiring.",
        "A future implementation must preserve dry-run behavior unless a later write-enabled gate authorizes otherwise.",
        "A future implementation must not write files unless a later explicit gate authorizes write-enabled behavior.",
        "A future implementation must not create directories unless a later explicit gate authorizes controlled directory creation.",
        "A future implementation must not create artifacts on disk unless a later explicit gate authorizes artifact creation.",
        "A future implementation must not scan arbitrary folders.",
        "A future implementation must not use real media.",
        "A future implementation must not execute ffprobe.",
        "A future implementation must not execute FFmpeg.",
        "A future implementation must not execute child processes.",
        "A future implementation must not access the network.",
        "A future implementation must not touch SaaS, database, backend, frontend, installer, public demo, client demo, or production code.",
    ],
)
def test_future_implementation_boundaries_are_preserved(required_text: str) -> None:
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
def test_future_implementation_acceptance_criteria_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "write-enabled export.",
        "directory creation.",
        "artifact creation on disk.",
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
def test_future_implementation_non_goals_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This readiness gate does not authorize connecting the planner to the exporter.",
        "This readiness gate does not authorize changing the planner module.",
        "This readiness gate does not authorize changing exporter runtime code.",
        "This readiness gate does not authorize path resolver expansion.",
        "This readiness gate does not authorize file writing.",
        "This readiness gate does not authorize directory creation.",
        "This readiness gate does not authorize artifact generation on disk.",
        "This readiness gate does not authorize real media usage.",
        "This readiness gate does not authorize arbitrary folder scanning.",
        "This readiness gate does not authorize scanner execution.",
        "This readiness gate does not authorize ffprobe execution.",
        "This readiness gate does not authorize FFmpeg execution.",
        "This readiness gate does not authorize child process execution.",
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

    assert "The project is ready for a future doc/test-only implementation readiness QA gate." in doc
    assert "The project is not ready for planner-to-exporter runtime implementation." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for artifact creation on disk." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for public, client-facing, or production use." in doc
    assert "That next step must remain doc/test-only." in doc


def test_document_contains_no_scope_authorization_markers() -> None:
    doc = _read(DOC_PATH)

    forbidden_markers = [
        "SCOPE_AUTHORIZATION: planner to exporter wiring",
        "SCOPE_AUTHORIZATION: runtime implementation",
        "SCOPE_AUTHORIZATION: planner module changes",
        "SCOPE_AUTHORIZATION: exporter runtime changes",
        "SCOPE_AUTHORIZATION: path resolver expansion",
        "SCOPE_AUTHORIZATION: file writing",
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
