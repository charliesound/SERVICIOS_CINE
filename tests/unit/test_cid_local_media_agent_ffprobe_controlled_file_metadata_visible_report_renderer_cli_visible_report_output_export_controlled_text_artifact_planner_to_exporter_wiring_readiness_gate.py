from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = ROOT / (
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_readiness_gate_v1.md"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_readiness_gate.py"
)

PLANNER_MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_export_path_planner.py"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.READINESS.GATE.V1"
)

RESULT_ID = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_READINESS_GATE_PASS_READY_FOR_CONTRACT"
)

PREVIOUS_COMMIT = "4dceb044eebf27f3e90b152db14debecfa87185a"

PREVIOUS_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-controlled-export-path-planner-implementation-qa-gate-closure-review-v1-20260622"
)

TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-cli-visible-report-output-"
    "export-controlled-text-artifact-planner-to-exporter-wiring-readiness-gate-v1-20260629"
)

NEXT_PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING.CONTRACT.V1"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists() -> None:
    assert DOC_PATH.is_file()


def test_readiness_gate_test_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_existing_planner_module_exists_but_is_not_modified_by_this_gate() -> None:
    assert PLANNER_MODULE_PATH.is_file()


def test_readiness_gate_declares_phase_result_and_lineage() -> None:
    doc = _read(DOC_PATH)

    assert PHASE_ID in doc
    assert RESULT_ID in doc
    assert PREVIOUS_COMMIT in doc
    assert PREVIOUS_TAG in doc
    assert TARGET_TAG in doc


def test_readiness_gate_is_doc_test_only() -> None:
    doc = _read(DOC_PATH)

    assert "This is a doc/test-only readiness gate." in doc
    assert "This readiness gate does not implement wiring." in doc
    assert "This readiness gate does not modify runtime code." in doc
    assert "This readiness gate does not authorize writing files." in doc


def test_readiness_gate_names_only_allowed_files() -> None:
    doc = _read(DOC_PATH)

    assert (
        "docs/product/local_media_agent/"
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_readiness_gate_v1.md"
    ) in doc

    assert (
        "tests/unit/"
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
        "controlled_text_artifact_planner_to_exporter_wiring_readiness_gate.py"
    ) in doc

    assert "No other files are in scope." in doc


def test_existing_planner_boundary_is_preserved() -> None:
    doc = _read(DOC_PATH)

    required = [
        "The existing controlled export path planner remains pure.",
        "The planner must continue returning `write_performed=False`.",
        "The planner must continue returning `artifact_created_on_disk=False`.",
        "The planner must not write files.",
        "The planner must not create directories.",
        "The planner must not create artifacts on disk.",
        "The planner must not scan folders.",
        "The planner must not execute media tooling.",
        "The planner must not access the network.",
        "The planner must not touch SaaS, database, backend, frontend, installer, or client-facing code.",
    ]

    for item in required:
        assert item in doc


def test_future_exporter_wiring_constraints_are_defined_without_authorizing_wiring() -> None:
    doc = _read(DOC_PATH)

    required = [
        "the exporter receives a planner result rather than recomputing path policy silently.",
        "the exporter rejects planner results that indicate a failed or unsafe plan.",
        "the exporter preserves controlled-root boundary checks.",
        "the exporter preserves the required `.controlled_visible_report.txt` suffix.",
        "the exporter preserves deterministic content hash reporting.",
        "the exporter records whether a write was requested.",
        "the exporter records whether an artifact was actually created on disk.",
        "the exporter must not write during dry-run planning mode.",
        "the exporter must not create directories unless a later contract explicitly authorizes directory creation.",
        "the exporter must not accept arbitrary absolute output paths from callers.",
        "the exporter must not accept traversal output paths from callers.",
        "the exporter must not expand to real media scanning.",
        "the exporter must not execute ffprobe.",
        "the exporter must not execute FFmpeg.",
        "the exporter must not execute child processes.",
        "the exporter must not access the network.",
        "the exporter must not touch SaaS, database, backend, frontend, installer, or client-facing code.",
    ]

    for item in required:
        assert item in doc


def test_future_contract_requirements_are_declared() -> None:
    doc = _read(DOC_PATH)

    required = [
        "exact input schema.",
        "exact output schema.",
        "allowed dry-run behavior.",
        "allowed write behavior, if any.",
        "whether directory creation remains prohibited or becomes explicitly controlled.",
        "failure modes.",
        "path boundary behavior.",
        "content hash behavior.",
        "safety flags.",
        "CLI-visible output changes, if any.",
        "regression expectations.",
        "tests required before implementation.",
        "explicit non-scope.",
    ]

    for item in required:
        assert item in doc


def test_explicit_non_authorization_is_preserved() -> None:
    doc = _read(DOC_PATH)

    required = [
        "This readiness gate does not authorize connecting the planner to the exporter.",
        "This readiness gate does not authorize changing the planner module.",
        "This readiness gate does not authorize changing exporter runtime code.",
        "This readiness gate does not authorize path resolver expansion.",
        "This readiness gate does not authorize file writing.",
        "This readiness gate does not authorize directory creation.",
        "This readiness gate does not authorize artifact generation on disk.",
        "This readiness gate does not authorize real media usage.",
        "This readiness gate does not authorize arbitrary folder scanning.",
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
    ]

    for item in required:
        assert item in doc


def test_readiness_decision_allows_only_future_contract_phase() -> None:
    doc = _read(DOC_PATH)

    assert "The project is ready for a future doc/test-only contract phase for planner-to-exporter wiring." in doc
    assert "The project is not ready for implementation of planner-to-exporter wiring." in doc
    assert "The project is not ready for write-enabled exporter behavior." in doc
    assert "The project is not ready for real media execution." in doc
    assert "The project is not ready for client-facing or production use." in doc
    assert NEXT_PHASE_ID in doc


def test_document_contains_no_scope_authorization_markers() -> None:
    doc = _read(DOC_PATH)

    forbidden_markers = [
        "SCOPE_AUTHORIZATION: planner to exporter wiring",
        "SCOPE_AUTHORIZATION: runtime code changes",
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


def test_readiness_test_does_not_import_planner_or_exporter_runtime() -> None:
    source = _read(THIS_TEST_PATH)

    blocked_import_a = "from scripts" + ".local_media_agent"
    blocked_import_b = "import scripts" + ".local_media_agent"
    blocked_runtime_a = "import " + "sub" + "process"
    blocked_runtime_b = "from " + "sub" + "process"

    assert blocked_import_a not in source
    assert blocked_import_b not in source
    assert blocked_runtime_a not in source
    assert blocked_runtime_b not in source
