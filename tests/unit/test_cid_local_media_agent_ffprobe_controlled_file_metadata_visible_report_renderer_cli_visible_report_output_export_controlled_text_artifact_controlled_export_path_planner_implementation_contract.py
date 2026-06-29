from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_planner_implementation_contract_v1.md"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_closure_review.py"
)

READINESS_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_implementation_readiness_contract_qa_gate_v1.md"
)

READINESS_QA_GATE_TEST_PATH = Path(
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

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.CONTRACT.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_CONTRACT"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_PLANNER_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.PLANNER.IMPLEMENTATION.CONTRACT.QA.GATE.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_path_planner_implementation_contract_files_exist():
    assert DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert READINESS_QA_GATE_DOC_PATH.exists()
    assert READINESS_QA_GATE_TEST_PATH.exists()
    assert READINESS_DOC_PATH.exists()
    assert READINESS_TEST_PATH.exists()
    assert PATH_CONTRACT_DOC_PATH.exists()
    assert PATH_CONTRACT_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_path_planner_implementation_contract_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_path_planner_implementation_contract_references_previous_chain():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert str(READINESS_QA_GATE_DOC_PATH) in text
    assert str(READINESS_QA_GATE_TEST_PATH) in text
    assert str(READINESS_DOC_PATH) in text
    assert str(READINESS_TEST_PATH) in text
    assert str(PATH_CONTRACT_DOC_PATH) in text
    assert str(PATH_CONTRACT_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_path_planner_implementation_contract_is_doc_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add runtime behavior.",
        "It does not implement a path planner.",
        "It does not implement a path resolver.",
        "It does not modify the controlled export implementation.",
        "It does not write files.",
        "It does not create directories.",
        "It does not create artifacts on disk.",
        "It does not authorize filesystem export implementation.",
        "It does not authorize any real media workflow.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_future_boundary():
    text = _read(DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may add only a pure path planner.",
        "That future planner must be deterministic.",
        "That future planner must be local-only.",
        "That future planner must be side-effect free.",
        "That future planner must only calculate and return a planned path descriptor.",
        "That future planner must not write files.",
        "That future planner must not create directories.",
        "That future planner must not create artifacts on disk.",
        "That future planner must not scan folders.",
        "That future planner must not execute ffprobe or FFmpeg.",
        "That future planner must not execute subprocesses or external processes.",
        "That future planner must not access the network.",
        "That future planner must not touch SaaS, database, installer, or client-facing code.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_module_boundary():
    text = _read(DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may add a dedicated local media agent planner module only under:",
        "`scripts/local_media_agent/`",
        "The future module must be importable by tests without side effects.",
        "The future module must not perform work at import time.",
        "The future module must not parse command-line arguments.",
        "The future module must not read environment variables.",
        "The future module must not read configuration files.",
        "The future module must not access real media.",
        "The future module must not access arbitrary folders.",
        "The future module must not open, read, write, or delete files.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_function_boundary():
    text = _read(DOC_PATH)

    required_phrases = [
        "A later controlled implementation phase may define one pure planner function.",
        "`controlled_export_root`",
        "A controlled descriptor produced by the existing in-memory descriptor builder.",
        "The function may return only a planned path descriptor.",
        "The function must not return opened file handles.",
        "The function must not return executable commands.",
        "The function must not return shell strings.",
        "The function must not return write instructions.",
        "The function must not return a claim that an artifact exists on disk.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_input_validation():
    text = _read(DOC_PATH)

    required_phrases = [
        "Missing controlled export root.",
        "Empty controlled export root.",
        "Whitespace-only controlled export root.",
        "Missing descriptor.",
        "Descriptor without `suggested_filename`.",
        "Empty suggested filename.",
        "Whitespace-only suggested filename.",
        "Absolute suggested filename.",
        "Parent traversal segments.",
        "Path separators in the suggested filename.",
        "Windows drive prefixes.",
        "UNC path forms.",
        "Hidden dotfile names.",
        "Suggested filename without the `.controlled_visible_report.txt` suffix.",
        "Any final resolved path outside the controlled export root.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_planned_descriptor():
    text = _read(DOC_PATH)

    required_fields = [
        "`controlled_export_root`",
        "`suggested_filename`",
        "`planned_artifact_path`",
        "`artifact_format`",
        "`content_sha256`",
        "`write_performed`",
        "`artifact_created_on_disk`",
        "`path_boundary`",
        "`safety_flags`",
    ]

    required_phrases = [
        "`write_performed` as false.",
        "`artifact_created_on_disk` as false.",
        "`path_boundary` as controlled.",
        "`artifact_format` as controlled visible report text.",
        "Safety flags confirming no real media access.",
        "Safety flags confirming no scanner execution.",
        "Safety flags confirming no ffprobe execution.",
        "Safety flags confirming no FFmpeg execution.",
        "Safety flags confirming no subprocess execution.",
        "Safety flags confirming no network access.",
        "Safety flags confirming no SaaS or database integration.",
        "Safety flags confirming no file write.",
    ]

    for field in required_fields:
        assert field in text

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_defines_future_tests():
    text = _read(DOC_PATH)

    required_phrases = [
        "Valid controlled root plus valid descriptor returns a planned descriptor.",
        "The planned descriptor remains inside the controlled export root.",
        "Empty roots are rejected.",
        "Empty suggested filenames are rejected.",
        "Absolute suggested filenames are rejected.",
        "Parent traversal is rejected.",
        "Path separators are rejected.",
        "Windows drive prefixes are rejected.",
        "UNC path forms are rejected.",
        "Hidden dotfile names are rejected.",
        "Wrong suffixes are rejected.",
        "`write_performed` remains false.",
        "`artifact_created_on_disk` remains false.",
        "No file is created on disk by the planner tests.",
        "No directory is created on disk by the planner tests.",
        "The current in-memory descriptor builder remains compatible.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_boundary_is_explicit():
    text = _read(DOC_PATH)

    required_phrases = [
        "This contract is not an implementation.",
        "This contract is not a QA gate.",
        "This contract is not a file-writing contract.",
        "This contract is not an artifact-generation contract.",
        "This contract only defines what a future controlled implementation phase may implement.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_non_authorization_is_complete():
    text = _read(DOC_PATH)
    lowered = text.lower()

    required_phrases = [
        "does not authorize path planner implementation",
        "does not authorize path resolver implementation",
        "does not authorize file writing",
        "does not authorize directory creation",
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


def test_controlled_export_path_planner_implementation_contract_previous_closure_supports_contract():
    text = _read(PREVIOUS_CLOSURE_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "ready only for a future controlled export path planner implementation contract" in text
    assert "does not itself authorize implementation, path resolver code, file writing, or artifact generation on disk" in text


def test_controlled_export_path_planner_implementation_contract_readiness_contract_supports_planner_scope():
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
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_planner_implementation_contract_path_contract_contains_boundary_rules():
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


def test_controlled_export_path_planner_implementation_contract_current_implementation_remains_pathless():
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


def test_controlled_export_path_planner_implementation_contract_test_sources_have_no_external_execution_or_network_imports():
    for path in [TEST_PATH, PREVIOUS_CLOSURE_TEST_PATH, READINESS_QA_GATE_TEST_PATH, READINESS_TEST_PATH, PATH_CONTRACT_TEST_PATH]:
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


def test_controlled_export_path_planner_implementation_contract_does_not_claim_runtime_or_client_readiness():
    combined = "\n".join(
        [
            _read(DOC_PATH),
            _read(PREVIOUS_CLOSURE_DOC_PATH),
            _read(READINESS_QA_GATE_DOC_PATH),
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
