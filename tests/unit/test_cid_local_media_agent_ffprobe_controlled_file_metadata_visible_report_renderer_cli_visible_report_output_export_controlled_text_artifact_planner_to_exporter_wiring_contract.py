from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_contract.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CONTRACT_PASS_READY_FOR_QA_GATE"
)

PREVIOUS_COMMIT = "ee53dcc8c1fd1aac98a58878d95b4478f89937dc"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-readiness-gate-v1-20260629"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-contract-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.QA.GATE.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_contract_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


@pytest.mark.parametrize(
    "required_text",
    [
        PHASE_ID,
        RESULT_ID,
        PREVIOUS_COMMIT,
        PREVIOUS_TAG,
        TARGET_TAG,
        NEXT_PHASE_ID,
        "This is a doc/test-only contract.",
        "This contract does not implement planner-to-exporter wiring.",
        "This contract does not modify planner runtime code.",
        "This contract does not modify exporter runtime code.",
        "This contract does not authorize write-enabled behavior.",
    ],
)
def test_contract_declares_lineage_scope_and_result(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_contract_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_contract.py"
    ) in doc

    assert "No other files are in scope." in doc


@pytest.mark.parametrize(
    "required_text",
    [
        "The existing controlled export path planner remains a pure planning component.",
        "The planner validates the controlled export root.",
        "The planner validates the suggested controlled visible report filename.",
        "The planner requires the suffix `.controlled_visible_report.txt`.",
        "The planner returns a planned controlled text artifact path descriptor.",
        "The planner returns `write_performed=False`.",
        "The planner returns `artifact_created_on_disk=False`.",
        "The planner does not write files.",
        "The planner does not create directories.",
        "The planner does not create artifacts on disk.",
        "The planner does not execute media tooling.",
        "The planner does not access the network.",
    ],
)
def test_existing_planner_boundary_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "planner validates the root and filename.",
        "planner returns a controlled planner result.",
        "exporter receives the planner result as an input.",
        "exporter validates that the planner result is safe.",
        "exporter uses the planner result as the only source of the planned artifact path.",
        "exporter reports hash and write status deterministically.",
        "The exporter must not silently recompute path policy.",
        "The exporter must not accept arbitrary caller-provided output paths.",
        "The exporter must not bypass planner safety decisions.",
    ],
)
def test_future_wiring_model_is_defined_without_runtime_implementation(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`visible_report_text`: controlled text content intended for a visible report artifact.",
        "`controlled_export_root`: controlled export root already subject to planner policy.",
        "`controlled_descriptor`: descriptor containing a controlled suggested filename.",
        "`planner_result`: controlled planner result returned by the planner.",
        "`dry_run`: boolean mode flag.",
        "`write_requested`: boolean intent flag.",
        "`artifact_format`: controlled artifact format.",
        "`caller_context`: non-sensitive local caller context.",
        "The input must not include arbitrary output paths.",
        "The input must not include raw media file content.",
        "The input must not include secrets.",
        "The input must not include network locations.",
        "The input must not include SaaS tenant data.",
        "The input must not include database identifiers.",
    ],
)
def test_future_input_schema_is_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`controlled_export_root`.",
        "`suggested_filename`.",
        "`planned_artifact_path`.",
        "`artifact_format`.",
        "`content_sha256`.",
        "`write_performed`.",
        "`artifact_created_on_disk`.",
        "`path_boundary`.",
        "`safety_flags`.",
        "The exporter must reject planner results that omit required fields.",
        "The exporter must reject planner results with unsafe path boundaries.",
        "The exporter must reject planner results with unsafe safety flags.",
        "The exporter must reject planner results with a filename that does not end in `.controlled_visible_report.txt`.",
        "The exporter must reject planner results that claim a write was already performed during planning.",
        "The exporter must reject planner results that claim an artifact was already created during planning.",
    ],
)
def test_future_planner_result_schema_is_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "`planned_artifact_path`.",
        "`artifact_format`.",
        "`content_sha256`.",
        "`write_requested`.",
        "`write_performed`.",
        "`artifact_created_on_disk`.",
        "`path_boundary`.",
        "`safety_flags`.",
        "`exporter_decision`.",
        "`human_visible_summary`.",
        "The output must distinguish planning from writing.",
        "The output must distinguish write intent from write execution.",
        "The output must distinguish artifact path planning from artifact creation on disk.",
    ],
)
def test_future_output_schema_is_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "Dry-run mode is the only behavior allowed by this contract.",
        "In dry-run mode, the future exporter must not write files.",
        "In dry-run mode, the future exporter must not create directories.",
        "In dry-run mode, the future exporter must not create artifacts on disk.",
        "In dry-run mode, the future exporter must return `write_performed=False`.",
        "In dry-run mode, the future exporter must return `artifact_created_on_disk=False`.",
        "In dry-run mode, the future exporter must preserve the planned artifact path for human review.",
    ],
)
def test_dry_run_behavior_is_strictly_defined(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "Write-enabled behavior is not authorized by this contract.",
        "A later separate contract must exist before write-enabled behavior can be considered.",
        "A later separate QA gate must exist before write-enabled behavior can be considered.",
        "A later separate implementation gate must exist before write-enabled behavior can be implemented.",
    ],
)
def test_write_behavior_remains_not_authorized(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "missing planner result.",
        "malformed planner result.",
        "unsafe path boundary.",
        "unsafe safety flags.",
        "wrong filename suffix.",
        "empty visible report text.",
        "empty controlled export root.",
        "empty suggested filename.",
        "traversal in filename.",
        "path separators in filename.",
        "hidden filename.",
        "absolute output path provided by caller.",
        "write requested during dry-run.",
        "artifact already marked as created before exporter decision.",
        "Failure results must not write files.",
        "Failure results must not create directories.",
        "Failure results must not create artifacts on disk.",
        "Failure results must preserve a human-readable reason.",
    ],
)
def test_failure_modes_fail_closed(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "controlled export root.",
        "suggested filename.",
        "planned artifact path.",
        "artifact format.",
        "content hash.",
        "dry-run mode.",
        "write requested.",
        "write performed.",
        "artifact created on disk.",
        "safety decision.",
        "A future CLI-visible output must not expose secrets.",
        "A future CLI-visible output must not expose raw media content.",
        "A future CLI-visible output must not imply that an artifact exists when no write occurred.",
    ],
)
def test_cli_visible_contract_is_limited(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "Any future implementation must preserve existing planner tests.",
        "Any future implementation must preserve existing closure review tests.",
        "Any future implementation must preserve this contract test.",
        "Any future implementation must add implementation-specific tests before runtime changes are accepted.",
        "Any future implementation must keep WSL guard passing.",
        "Any future implementation must keep the database regression guard passing.",
    ],
)
def test_regression_expectations_are_declared(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


@pytest.mark.parametrize(
    "required_text",
    [
        "This contract does not authorize connecting the planner to the exporter.",
        "This contract does not authorize changing the planner module.",
        "This contract does not authorize changing exporter runtime code.",
        "This contract does not authorize path resolver expansion.",
        "This contract does not authorize file writing.",
        "This contract does not authorize directory creation.",
        "This contract does not authorize artifact generation on disk.",
        "This contract does not authorize real media usage.",
        "This contract does not authorize arbitrary folder scanning.",
        "This contract does not authorize scanner execution.",
        "This contract does not authorize ffprobe execution.",
        "This contract does not authorize FFmpeg execution.",
        "This contract does not authorize child process execution.",
        "This contract does not authorize audio extraction.",
        "This contract does not authorize sync.",
        "This contract does not authorize transcription.",
        "This contract does not authorize subtitle generation.",
        "This contract does not authorize timeline export.",
        "This contract does not authorize network access.",
        "This contract does not authorize SaaS integration.",
        "This contract does not authorize database changes.",
        "This contract does not authorize backend changes.",
        "This contract does not authorize frontend changes.",
        "This contract does not authorize installer work.",
        "This contract does not authorize public demo work.",
        "This contract does not authorize client-facing demo work.",
        "This contract does not authorize production use.",
    ],
)
def test_explicit_non_authorization_is_preserved(required_text: str) -> None:
    assert required_text in _read(DOC_PATH)


def test_contract_decision_allows_only_next_qa_gate() -> None:
    doc = _read(DOC_PATH)

    assert "The planner-to-exporter wiring design is defined enough for a future QA gate." in doc
    assert "The project is not ready for planner-to-exporter runtime implementation." in doc
    assert "The project is not ready for write-enabled export behavior." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for client-facing or production use." in doc
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


def test_contract_test_does_not_import_runtime_modules() -> None:
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
