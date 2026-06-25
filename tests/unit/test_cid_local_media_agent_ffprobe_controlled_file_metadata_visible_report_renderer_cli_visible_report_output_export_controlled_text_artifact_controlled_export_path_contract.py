from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_path_contract_v1.md"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_closure_review.py"
)

IMPLEMENTATION_SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.CONTRACT.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_TEXT_ARTIFACT_EXPORT_PATH_CONTRACT"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_PATH_CONTRACT_PASS_READY_FOR_QA_GATE"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.CONTRACT.QA.GATE.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_path_contract_files_exist():
    assert DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_path_contract_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_path_contract_references_previous_closed_phase():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_path_contract_is_documentation_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add runtime behavior.",
        "It does not modify the controlled export implementation.",
        "It does not write files.",
        "It does not create artifacts on disk.",
        "It does not authorize filesystem export implementation.",
        "It does not authorize any real media workflow.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_contract_scope_is_limited_to_planned_path_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "already-safe controlled visible report text",
        "already-built controlled text artifact descriptor",
        "must not read media",
        "must not scan folders",
        "must not execute ffprobe",
        "must not execute FFmpeg",
        "must not spawn subprocesses or processes",
        "must not access network resources",
        "must not touch SaaS systems or database systems",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_contract_lists_required_path_rules():
    text = _read(DOC_PATH)

    required_phrases = [
        "must accept only a controlled export root selected by an explicit future controlled phase",
        "must accept only a descriptor produced by the controlled in-memory descriptor builder",
        "must use only the descriptor `suggested_filename` as the file name candidate",
        "must reject empty export roots",
        "must reject empty suggested filenames",
        "must reject absolute suggested filenames",
        "must reject parent traversal segments",
        "must reject path separators in suggested filenames",
        "must reject Windows drive prefixes",
        "must reject UNC paths",
        "must reject hidden dotfile names",
        "must require the `.controlled_visible_report.txt` suffix",
        "must resolve the final path under the controlled export root",
        "must verify the resolved final path remains inside the controlled export root",
        "must return only a planned path descriptor until a later explicit file-writing phase",
        "must declare `write_performed` as false",
        "must declare `artifact_created_on_disk` as false",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_contract_lists_forbidden_path_inputs():
    text = _read(DOC_PATH)

    required_fragments = [
        "`..`",
        "`/`",
        "`\\`",
        "drive prefixes such as `C:`",
        "UNC prefixes",
        "empty strings",
        "whitespace-only strings",
        "hidden dotfile names",
        "filenames without `.controlled_visible_report.txt`",
    ]

    for fragment in required_fragments:
        assert fragment in text


def test_controlled_export_path_contract_defines_planned_descriptor_fields():
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

    for field in required_fields:
        assert field in text


def test_controlled_export_path_contract_planned_descriptor_must_not_claim_written_file():
    text = _read(DOC_PATH)

    required_phrases = [
        "must not contain real media paths",
        "must not contain arbitrary source folders",
        "must not imply that a file was written",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_path_contract_non_authorization_is_complete():
    text = _read(DOC_PATH)
    lowered = text.lower()

    required_phrases = [
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


def test_controlled_export_path_contract_previous_closure_review_remains_closed():
    text = _read(PREVIOUS_CLOSURE_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "The controlled export implementation QA gate is closed." in text
    assert "ready only for a future controlled export path contract" in text


def test_controlled_export_path_contract_implementation_script_remains_in_memory_and_pathless():
    source = _read(IMPLEMENTATION_SCRIPT_PATH).lower()

    required_phrases = [
        "build_controlled_text_artifact_descriptor",
        "suggested_filename",
        "write_performed",
        "artifact_created_on_disk",
        "no_ffprobe_execution",
        "no_ffmpeg_execution",
    ]

    forbidden_phrases = [
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


def test_controlled_export_path_contract_test_source_has_no_external_execution_or_network_imports():
    tree = ast.parse(_read(TEST_PATH))

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


def test_controlled_export_path_contract_does_not_claim_runtime_or_client_readiness():
    combined = f"{_read(DOC_PATH)}\n{_read(PREVIOUS_CLOSURE_DOC_PATH)}".lower()

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
