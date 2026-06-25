from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_v1.md"
)

PREVIOUS_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_v1.md"
)

PREVIOUS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT_PASS_READY_FOR_QA_GATE"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_PASS_CLOSED"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_previous_doc() -> str:
    return PREVIOUS_DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_readiness_contract_qa_gate_document_exists():
    assert DOC_PATH.exists()


def test_controlled_export_implementation_readiness_contract_qa_gate_previous_contract_exists():
    assert PREVIOUS_DOC_PATH.exists()
    assert PREVIOUS_TEST_PATH.exists()


def test_controlled_export_implementation_readiness_contract_qa_gate_declares_exact_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert "Implementation Readiness Contract QA Gate v1" in text


def test_controlled_export_implementation_readiness_contract_qa_gate_links_previous_contract():
    text = _read_doc()

    assert str(PREVIOUS_DOC_PATH) in text
    assert str(PREVIOUS_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_readiness_contract_qa_gate_declares_result_and_next_phase():
    text = _read_doc()

    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_readiness_contract_qa_gate_is_documentation_and_test_only():
    text = _read_doc()

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not implement export.",
        "It does not write output files.",
        "It does not create artifacts.",
        "It does not modify runtime code.",
        "It does not modify renderer behavior.",
        "It does not modify CLI behavior.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_qa_gate_validates_previous_contract_core_content():
    previous_text = _read_previous_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "This phase is documentation and test-only.",
        "This phase does not implement export.",
        "This phase does not write output files.",
        "This phase does not create artifacts.",
        "This phase does not add runtime code.",
        "preserves the local-only product boundary",
        "preserves the controlled fixture boundary",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_readiness_contract_qa_gate_validates_previous_contract_non_authorization():
    previous_text = _read_previous_doc()

    required_phrases = [
        "It does not authorize implementation.",
        "It does not authorize export.",
        "It does not authorize file writing.",
        "It does not authorize artifact generation.",
        "It does not authorize real media.",
        "It does not authorize arbitrary folders.",
        "It does not authorize scanner execution.",
        "It does not authorize ffprobe or FFmpeg execution.",
        "It does not authorize process execution.",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_readiness_contract_qa_gate_validates_previous_contract_rejects_media_processing():
    previous_text = _read_previous_doc()

    required_phrases = [
        "does not enable audio extraction",
        "does not enable sync",
        "does not enable transcription",
        "does not enable subtitle generation",
        "does not enable timeline export",
        "does not enable network access",
        "does not enable SaaS integration",
        "does not enable installer work",
        "does not enable public, client, sales, or production use",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_readiness_contract_qa_gate_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for this QA gate test.",
        "This QA gate unit test.",
        "Previous readiness contract unit test.",
        "Previous controlled export contract regression tests.",
        "WSL repository guard.",
        "Database backend regression guard.",
        "Staged diff check.",
        "Protected files check.",
        "Target tag absence check locally and remotely.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_qa_gate_rejects_wider_authorization():
    text = _read_doc()

    required_phrases = [
        "It does not authorize implementation.",
        "It does not authorize export.",
        "It does not authorize file writing.",
        "It does not authorize artifact generation.",
        "It does not authorize real media.",
        "It does not authorize arbitrary folders.",
        "It does not authorize scanner execution.",
        "It does not authorize ffprobe or FFmpeg execution.",
        "It does not authorize subprocess or process execution.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export, network access, SaaS/DB integration, installer work, public demo, client demo, sales demo, or production use.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_qa_gate_does_not_claim_runtime_or_client_readiness():
    text = _read_doc()
    previous_text = _read_previous_doc()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "export implemented",
        "artifact generated",
        "files written",
        "runtime exporter is available",
        "users can export",
    ]

    combined = f"{text}\n{previous_text}".lower()
    for claim in forbidden_claims:
        assert claim not in combined


def test_controlled_export_implementation_readiness_contract_qa_gate_has_no_runtime_entrypoint_language():
    text = _read_doc()

    forbidden_phrases = [
        "command line usage",
        "cli invocation",
        "run the exporter",
        "export command",
        "output path argument",
        "media folder argument",
        "ffprobe command example",
        "ffmpeg command example",
        "upload endpoint",
        "download endpoint",
    ]

    lowered = text.lower()
    for phrase in forbidden_phrases:
        assert phrase not in lowered


def test_controlled_export_implementation_readiness_contract_qa_gate_source_has_no_external_execution_or_network_imports():
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))

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


def test_controlled_export_implementation_readiness_contract_qa_gate_source_only_reads_expected_docs():
    source = TEST_PATH.read_text(encoding="utf-8")

    allowed_path_fragments = [
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_v1.md",
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_v1.md",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py",
    ]

    tree = ast.parse(source)

    forbidden_attribute_names = {
        "write" + "_text",
        "unlink",
        "mkdir",
    }

    observed_forbidden_attributes = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in forbidden_attribute_names
    }

    assert observed_forbidden_attributes == set()

    for fragment in allowed_path_fragments:
        assert fragment in source


def test_controlled_export_implementation_readiness_contract_qa_gate_preserves_closure_review_as_next_step():
    text = _read_doc()

    assert "closure review phase" in text
    assert NEXT_PHASE in text
    assert "Closing this QA gate only validates the readiness contract" in text
