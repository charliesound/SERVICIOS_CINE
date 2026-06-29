from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_v1.md"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate.py"
)

READINESS_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_v1.md"
)

READINESS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract.py"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_qa_gate_closure_review.py"
)

PATH_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_v1.md"
)

PATH_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract.py"
)

IMPLEMENTATION_SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_PASS_CLOSED"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_CONTRACT"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.CONTRACT.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_path_readiness_qa_gate_closure_review_files_exist():
    assert DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert READINESS_DOC_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PATH_CONTRACT_DOC_PATH.exists()
    assert PATH_CONTRACT_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_path_readiness_qa_gate_closure_review_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_path_readiness_qa_gate_closure_review_references_previous_closed_gate():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(PREVIOUS_QA_GATE_DOC_PATH) in text
    assert str(PREVIOUS_QA_GATE_TEST_PATH) in text
    assert str(READINESS_DOC_PATH) in text
    assert str(READINESS_TEST_PATH) in text
    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert str(PATH_CONTRACT_DOC_PATH) in text
    assert str(PATH_CONTRACT_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_path_readiness_qa_gate_closure_review_is_doc_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add runtime behavior.",
        "It does not implement a path resolver.",
        "It does not modify the controlled export implementation.",
        "It does not write files.",
        "It does not create artifacts on disk.",
        "It does not authorize filesystem export implementation.",
        "It does not authorize any real media workflow.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_summarizes_gate_findings():
    text = _read(DOC_PATH)

    required_phrases = [
        "Defines readiness requirements before any future controlled export path resolver implementation.",
        "Requires any future implementation to be a pure controlled path planner.",
        "Forbids file writing.",
        "Forbids directory creation.",
        "Forbids artifact generation on disk.",
        "Forbids folder scanning.",
        "Forbids ffprobe and FFmpeg execution.",
        "Forbids subprocess and external process execution.",
        "Forbids network access.",
        "Forbids SaaS, database, installer, and client-facing code changes.",
        "Defines allowed future planner inputs.",
        "Defines forbidden future planner inputs.",
        "Defines validation rules for controlled export root and suggested filename.",
        "Defines required planned path descriptor fields.",
        "Requires `write_performed` as false.",
        "Requires `artifact_created_on_disk` as false.",
        "Keeps the current implementation pathless and in-memory.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_decision_is_limited():
    text = _read(DOC_PATH)

    assert "The controlled export path implementation readiness contract QA gate is closed." in text
    assert "ready only for a future controlled export path planner implementation contract" in text
    assert "does not itself authorize implementation, path resolver code, file writing, or artifact generation on disk" in text


def test_controlled_export_path_readiness_qa_gate_closure_review_non_authorization_is_complete():
    text = _read(DOC_PATH)
    lowered = text.lower()

    required_phrases = [
        "does not authorize path resolver implementation",
        "does not authorize file writing",
        "does not authorize artifact generation on disk",
        "does not authorize real media",
        "does not authorize arbitrary folders",
        "does not authorize scanner execution",
        "does not authorize ffprobe or ffmpeg execution",
        "does not authorize subprocess or process execution",
        "does not authorize audio extraction",
        "does not authorize sync",
        "does not authorize transcription",
        "does not authorize subtitles",
        "does not authorize timeline export",
        "does not authorize network access",
        "does not authorize saas or database integration",
        "does not authorize installer work",
        "does not authorize public demo, client demo, sales demo, or production use",
    ]

    for phrase in required_phrases:
        assert phrase in lowered


def test_controlled_export_path_readiness_qa_gate_closure_review_previous_gate_contains_expected_result():
    text = _read(PREVIOUS_QA_GATE_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "This QA gate validates the controlled export path implementation readiness contract." in text
    assert "This phase is documentation and test-only." in text
    assert "This QA gate does not authorize implementation." in text
    assert "PATH_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_PASS_CLOSED" in text


def test_controlled_export_path_readiness_qa_gate_closure_review_previous_gate_defines_validation_evidence():
    text = _read(PREVIOUS_QA_GATE_DOC_PATH)

    required_phrases = [
        "Python compile check for this QA gate test.",
        "This QA gate unit test.",
        "Previous readiness contract unit test.",
        "Previous path contract QA gate closure review unit test.",
        "Previous path contract QA gate unit test.",
        "Previous path contract unit test.",
        "WSL repository guard.",
        "Database backend regression guard.",
        "Diff check.",
        "Protected files check.",
        "Target tag absence check locally and remotely.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_readiness_contract_contains_expected_result():
    text = _read(READINESS_DOC_PATH)

    assert "This contract defines readiness requirements before any future controlled export path resolver implementation." in text
    assert "PATH_IMPLEMENTATION_READINESS_CONTRACT_PASS_READY_FOR_QA_GATE" in text
    assert "This readiness contract only defines requirements before a later controlled implementation contract." in text


def test_controlled_export_path_readiness_qa_gate_closure_review_readiness_contract_defines_core_scope():
    text = _read(READINESS_DOC_PATH)

    required_phrases = [
        "That future implementation must be a pure controlled path planner.",
        "It must not write files.",
        "It must not create directories.",
        "It must not create artifacts on disk.",
        "It must not scan folders.",
        "It must not execute ffprobe or FFmpeg.",
        "It must not execute subprocesses or external processes.",
        "It must not access the network.",
        "It must not touch SaaS, database, installer, or client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_readiness_contract_defines_descriptor_and_false_flags():
    text = _read(READINESS_DOC_PATH)

    required_phrases = [
        "`controlled_export_root`",
        "`suggested_filename`",
        "`planned_artifact_path`",
        "`artifact_format`",
        "`content_sha256`",
        "`write_performed`",
        "`artifact_created_on_disk`",
        "`path_boundary`",
        "`safety_flags`",
        "`write_performed` as false.",
        "`artifact_created_on_disk` as false.",
        "Safety flags confirming no real media access.",
        "Safety flags confirming no ffprobe execution.",
        "Safety flags confirming no FFmpeg execution.",
        "Safety flags confirming no subprocess execution.",
        "Safety flags confirming no network access.",
        "Safety flags confirming no SaaS or database integration.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_path_contract_contains_path_boundaries():
    text = _read(PATH_CONTRACT_DOC_PATH)

    required_phrases = [
        "must accept only a controlled export root selected by an explicit future controlled phase",
        "must accept only a descriptor produced by the controlled in-memory descriptor builder",
        "must use only the descriptor `suggested_filename` as the file name candidate",
        "must reject parent traversal segments",
        "must reject path separators in suggested filenames",
        "must reject Windows drive prefixes",
        "must reject UNC paths",
        "must require the `.controlled_visible_report.txt` suffix",
        "must verify the resolved final path remains inside the controlled export root",
        "must return only a planned path descriptor until a later explicit file-writing phase",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_readiness_qa_gate_closure_review_current_implementation_remains_pathless():
    source = _read(IMPLEMENTATION_SCRIPT_PATH).lower()

    required_phrases = [
        "build_controlled_text_artifact_descriptor",
        "suggested_filename",
        "write_performed",
        "artifact_created_on_disk",
    ]

    forbidden_phrases = [
        "resolve_export_path",
        "planned_artifact_path",
        "controlled_export_root",
        "output_path",
        "input_path",
        "media_folder",
        "folder_path",
        "ffprobe command",
        "ffmpeg command",
        "upload",
        "download",
    ]

    for phrase in required_phrases:
        assert phrase in source

    for phrase in forbidden_phrases:
        assert phrase not in source


def test_controlled_export_path_readiness_qa_gate_closure_review_test_sources_have_no_external_execution_or_network_imports():
    for path in [TEST_PATH, PREVIOUS_QA_GATE_TEST_PATH, READINESS_TEST_PATH, PREVIOUS_CLOSURE_TEST_PATH, PATH_CONTRACT_TEST_PATH]:
        tree = ast.parse(_read(path))

        forbidden_import_roots = {
            "subprocess",
            "socket",
            "requests",
            "httpx",
            "urllib",
            "ftplib",
            "smtplib",
        }

        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_roots.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".")[0])

        assert imported_roots.isdisjoint(forbidden_import_roots)


def test_controlled_export_path_readiness_qa_gate_closure_review_does_not_claim_runtime_or_client_readiness():
    combined = "\n".join(
        [
            _read(DOC_PATH),
            _read(PREVIOUS_QA_GATE_DOC_PATH),
            _read(READINESS_DOC_PATH),
            _read(PATH_CONTRACT_DOC_PATH),
        ]
    ).lower()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "disk export ready",
        "export file created",
        "runtime exporter writes files",
        "users can export",
        "installer ready",
    ]

    for claim in forbidden_claims:
        assert claim not in combined
