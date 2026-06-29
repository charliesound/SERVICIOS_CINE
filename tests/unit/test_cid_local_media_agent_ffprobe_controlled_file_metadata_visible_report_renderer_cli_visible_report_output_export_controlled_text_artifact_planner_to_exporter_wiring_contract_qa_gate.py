from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate.py"
)

CONTRACT_DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_v1.md"
)

CONTRACT_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.QA.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CONTRACT_QA_GATE_PASS_READY_FOR_IMPLEMENTATION_READINESS_GATE"
)

PREVIOUS_COMMIT = "5ca1aa0656b2ba8e823f2c5749498d6d29ad0d5f"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-contract-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-contract-qa-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "IMPLEMENTATION.READINESS.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_qa_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_contract_document_under_qa_exists() -> None:
    assert CONTRACT_DOC_PATH.is_file()


def test_contract_test_under_qa_exists() -> None:
    assert CONTRACT_TEST_PATH.is_file()


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
        "This QA gate validates the planner-to-exporter wiring contract.",
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
        "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_contract_qa_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "precheck clean.",
        "previous readiness gate tag existed.",
        "target contract tag absent locally before tagging.",
        "target contract tag absent remotely before tagging.",
        "py_compile passed.",
        "target contract test passed with 155 checks.",
        "previous readiness gate test passed with 13 checks.",
        "previous closure review test passed with 106 checks.",
        "previous QA gate test passed with 35 checks.",
        "planner implementation test passed with 27 checks.",
        "exact staged files check passed.",
        "staged diff check passed.",
        "restricted database word check passed.",
        "WSL guard passed.",
        "database regression guard passed.",
        "commit completed.",
        "local tag completed.",
        "push main completed.",
        "push tag completed.",
        "post-push verification completed.",
        "working tree was clean after post-push verification.",
    ],
)
def test_qa_gate_records_previous_contract_validation_evidence(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "doc/test-only contract status.",
        "previous stable lineage.",
        "target tag.",
        "files in scope.",
        "existing planner boundary.",
        "contracted future wiring model.",
        "contracted future input schema.",
        "contracted planner result schema.",
        "contracted future output schema.",
        "contracted dry-run behavior.",
        "write behavior non-authorization.",
        "failure modes.",
        "CLI-visible contract.",
        "regression expectations.",
        "explicit non-authorization.",
        "contract decision.",
        "next allowed QA step.",
    ],
)
def test_qa_gate_accepts_required_contract_sections(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "the planner remains a pure planning component.",
        "the exporter must receive a planner result as input in any future implementation.",
        "the exporter must validate the planner result before using it.",
        "the exporter must use the planner result as the only source of the planned artifact path.",
        "the exporter must not silently recompute path policy.",
        "the exporter must not accept arbitrary caller-provided output paths.",
        "the exporter must not bypass planner safety decisions.",
        "dry-run mode is the only behavior allowed by the contract.",
        "write-enabled behavior is not authorized by the contract.",
        "failure modes must fail closed.",
        "failure results must not write files.",
        "failure results must not create directories.",
        "failure results must not create artifacts on disk.",
        "CLI-visible output must not imply that an artifact exists when no write occurred.",
        "any future implementation must preserve existing planner tests.",
        "any future implementation must preserve existing closure review tests.",
        "any future implementation must preserve the contract test.",
        "any future implementation must add implementation-specific tests before runtime changes are accepted.",
    ],
)
def test_qa_gate_preserves_required_contract_guarantees(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "authorizes runtime implementation.",
        "authorizes connecting the planner to the exporter.",
        "authorizes planner module changes.",
        "authorizes exporter runtime changes.",
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
def test_qa_gate_declares_rejection_conditions(required_text: str) -> None:
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
def test_qa_gate_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_qa_gate_decision_allows_only_future_readiness_gate() -> None:
    doc = _read(DOC_PATH)

    assert "The planner-to-exporter wiring contract is accepted." in doc
    assert "The project is ready for a future doc/test-only implementation readiness gate." in doc
    assert "The project is not ready for planner-to-exporter runtime implementation." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for client-facing or production use." in doc
    assert "That next step must remain doc/test-only unless a later explicit implementation gate authorizes runtime changes." in doc


def test_qa_gate_document_contains_no_scope_authorization_markers() -> None:
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
