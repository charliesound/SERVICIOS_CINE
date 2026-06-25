from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_closure_review_v1.md"
)

PREVIOUS_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_v1.md"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate.py"
)

IMPLEMENTATION_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_v1.md"
)

IMPLEMENTATION_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation.py"
)

IMPLEMENTATION_SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.V1"
PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_QA_GATE_PASS_CLOSED"
RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_TEXT_ARTIFACT_EXPORT_PATH_CONTRACT"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.PATH.CONTRACT.V1"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_controlled_export_implementation_qa_gate_closure_review_files_exist():
    assert DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert IMPLEMENTATION_DOC_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()


def test_controlled_export_implementation_qa_gate_closure_review_declares_phase_result_and_next_phase():
    text = _read(DOC_PATH)

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_qa_gate_closure_review_references_previous_closed_gate():
    text = _read(DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert str(PREVIOUS_QA_GATE_DOC_PATH) in text
    assert str(PREVIOUS_QA_GATE_TEST_PATH) in text
    assert str(IMPLEMENTATION_DOC_PATH) in text
    assert str(IMPLEMENTATION_TEST_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text


def test_controlled_export_implementation_qa_gate_closure_review_is_doc_and_test_only():
    text = _read(DOC_PATH)

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add runtime behavior.",
        "It does not modify the controlled export implementation.",
        "It does not write files.",
        "It does not create artifacts on disk.",
        "It does not authorize any real media workflow.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_qa_gate_closure_review_summarizes_gate_findings():
    text = _read(DOC_PATH)

    required_phrases = [
        "Provides a pure local-only in-memory descriptor builder.",
        "Preserves already-safe controlled visible report text.",
        "Produces deterministic metadata.",
        "Computes deterministic content hash.",
        "Computes deterministic line and byte counts.",
        "Generates sanitized suggested filenames.",
        "Declares `write_performed` as false.",
        "Declares `artifact_created_on_disk` as false.",
        "Declares complete negative safety flags.",
        "Uses defensive copies for safety flags.",
        "Rejects invalid input.",
        "Has no CLI entrypoint.",
        "Has no arbitrary path arguments.",
        "Imports no filesystem, network, process, media, SaaS, or database tooling.",
        "Performs no file writes.",
        "Performs no process execution.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_qa_gate_closure_review_decision_is_limited():
    text = _read(DOC_PATH)

    assert "The controlled export implementation QA gate is closed." in text
    assert "ready only for a future controlled export path contract" in text
    assert "does not itself authorize writing files or creating artifacts on disk" in text


def test_controlled_export_implementation_qa_gate_closure_review_non_authorization_is_complete():
    text = _read(DOC_PATH)

    required_phrases = [
        "does not authorize file writing",
        "does not authorize artifact generation on disk",
        "does not authorize real media",
        "does not authorize arbitrary folders",
        "does not authorize scanner execution",
        "does not authorize ffprobe or FFmpeg execution",
        "does not authorize subprocess or process execution",
        "does not authorize audio extraction",
        "does not authorize sync",
        "does not authorize transcription",
        "does not authorize subtitles",
        "does not authorize timeline export",
        "does not authorize network access",
        "does not authorize SaaS or database integration",
        "does not authorize installer work",
        "does not authorize public demo, client demo, sales demo, or production use",
    ]

    lowered = text.lower()
    for phrase in required_phrases:
        assert phrase.lower() in lowered


def test_controlled_export_implementation_qa_gate_closure_review_previous_gate_contains_expected_result():
    text = _read(PREVIOUS_QA_GATE_DOC_PATH)

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text
    assert "This phase is documentation and test-only." in text
    assert "It does not add new runtime behavior." in text
    assert "It does not modify the implementation." in text


def test_controlled_export_implementation_qa_gate_closure_review_previous_gate_test_exists_and_is_safe():
    source = _read(PREVIOUS_QA_GATE_TEST_PATH)
    tree = ast.parse(source)

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
    assert "build_controlled_text_artifact_descriptor" in source


def test_controlled_export_implementation_qa_gate_closure_review_implementation_script_remains_pathless_and_in_memory():
    source = _read(IMPLEMENTATION_SCRIPT_PATH).lower()

    required_phrases = [
        "build_controlled_text_artifact_descriptor",
        "write_performed",
        "artifact_created_on_disk",
        "already_safe_controlled_visible_report_text",
        "no_ffprobe_execution",
        "no_ffmpeg_execution",
    ]

    forbidden_phrases = [
        "argparse",
        "click",
        "typer",
        "sys.argv",
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


def test_controlled_export_implementation_qa_gate_closure_review_implementation_script_has_no_forbidden_imports():
    tree = ast.parse(_read(IMPLEMENTATION_SCRIPT_PATH))

    forbidden_import_roots = {
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "pathlib",
        "os",
        "shutil",
        "tempfile",
        "psycopg",
        "sqlalchemy",
    }

    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(forbidden_import_roots)


def test_controlled_export_implementation_qa_gate_closure_review_test_source_has_no_external_execution_or_network_imports():
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


def test_controlled_export_implementation_qa_gate_closure_review_does_not_claim_runtime_readiness():
    combined = f"{_read(DOC_PATH)}\n{_read(PREVIOUS_QA_GATE_DOC_PATH)}\n{_read(IMPLEMENTATION_DOC_PATH)}".lower()

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
