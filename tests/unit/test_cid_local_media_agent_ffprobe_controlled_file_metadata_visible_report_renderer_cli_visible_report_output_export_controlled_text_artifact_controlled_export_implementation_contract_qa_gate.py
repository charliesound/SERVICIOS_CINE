from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_v1.md"
)

PREVIOUS_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md"
)

PREVIOUS_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract.py"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate.py"
)

PREVIOUS_READINESS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_previous_contract_doc() -> str:
    return PREVIOUS_CONTRACT_DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_contract_qa_gate_document_exists():
    assert DOC_PATH.exists()


def test_controlled_export_implementation_contract_qa_gate_dependencies_exist():
    assert PREVIOUS_CONTRACT_DOC_PATH.exists()
    assert PREVIOUS_CONTRACT_TEST_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert PREVIOUS_READINESS_TEST_PATH.exists()


def test_controlled_export_implementation_contract_qa_gate_declares_exact_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert "Controlled Export Implementation Contract QA Gate v1" in text


def test_controlled_export_implementation_contract_qa_gate_links_previous_contract():
    text = _read_doc()

    assert str(PREVIOUS_CONTRACT_DOC_PATH) in text
    assert str(PREVIOUS_CONTRACT_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_contract_qa_gate_declares_result_and_next_phase():
    text = _read_doc()

    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_contract_qa_gate_is_documentation_and_test_only():
    text = _read_doc()

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not implement export.",
        "It does not write output files.",
        "It does not create artifacts.",
        "It does not add runtime code.",
        "It does not modify renderer behavior.",
        "It does not modify CLI behavior.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_validates_descriptor_shape():
    text = _read_doc()

    required_phrases = [
        "Defines a future in-memory controlled text artifact descriptor only.",
        "deterministic metadata such as line count, byte count, content hash",
        "safe suggested filename",
        "safety flags",
        "source boundary",
        "no on-disk artifact flags",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_rejects_write_and_artifact_behavior():
    text = _read_doc()

    required_phrases = [
        "Rejects file writes.",
        "Rejects filesystem artifact creation.",
        "Rejects arbitrary output paths.",
        "It does not authorize file writing.",
        "It does not authorize artifact generation.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_rejects_input_media_and_scanner_scope():
    text = _read_doc()

    required_phrases = [
        "Rejects arbitrary input folders.",
        "Rejects real media.",
        "Rejects scanner execution.",
        "It does not authorize real media.",
        "It does not authorize arbitrary folders.",
        "It does not authorize scanner execution.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_rejects_execution_and_media_processing():
    text = _read_doc()

    required_phrases = [
        "Rejects ffprobe and FFmpeg execution.",
        "Rejects subprocess and process execution.",
        "Rejects audio extraction, sync, transcription, subtitles, and timeline export.",
        "It does not authorize ffprobe or FFmpeg execution.",
        "It does not authorize subprocess or process execution.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_rejects_external_and_client_behaviour():
    text = _read_doc()

    required_phrases = [
        "Rejects network access.",
        "Rejects SaaS/DB integration.",
        "Rejects installer, public demo, client demo, sales demo, and production behavior.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export, network access, SaaS/DB integration, installer work, public demo, client demo, sales demo, or production use.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_requires_later_named_phases():
    text = _read_doc()

    required_phrases = [
        "Requires a later separately named implementation phase.",
        "Requires a later separate QA gate before any implementation can be considered closed.",
        "Closing this QA gate only validates the controlled export implementation contract.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_acceptance_criteria_are_explicit():
    text = _read_doc()

    required_phrases = [
        "The implementation contract document exists.",
        "The implementation contract test exists.",
        "The implementation contract test passes.",
        "The previous readiness QA gate closure review test passes.",
        "The previous readiness QA gate test passes.",
        "The previous readiness contract test passes.",
        "The previous controlled export contract regression tests pass.",
        "The QA gate test contains no external execution imports.",
        "The QA gate test performs no writes.",
        "The QA gate remains documentation and test-only.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_validates_previous_contract_content():
    previous_text = _read_previous_contract_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "The future implementation must be local-only, deterministic, pure, and controlled.",
        "The future implementation may produce an in-memory controlled text artifact descriptor.",
        "The future implementation must not write output files.",
        "The future implementation must not create filesystem artifacts.",
        "The future implementation must not read real media.",
        "The future implementation must not execute ffprobe or FFmpeg.",
        "The future implementation must not spawn processes.",
        "The future implementation must not access network resources.",
        "It does not authorize implementation.",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_contract_qa_gate_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for this QA gate test.",
        "This QA gate unit test.",
        "Previous implementation contract unit test.",
        "Previous readiness QA gate closure review unit test.",
        "Previous readiness QA gate unit test.",
        "Previous readiness contract unit test.",
        "Previous controlled export contract regression tests.",
        "WSL repository guard.",
        "Database backend regression guard.",
        "Diff check.",
        "Protected files check.",
        "Target tag absence check locally and remotely.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_does_not_claim_runtime_or_client_readiness():
    text = _read_doc()
    previous_text = _read_previous_contract_doc()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "export implemented",
        "artifact generated",
        "runtime exporter is available",
        "users can export",
        "installer ready",
        "writes files",
    ]

    combined = f"{text}\n{previous_text}".lower()
    for claim in forbidden_claims:
        assert claim not in combined


def test_controlled_export_implementation_contract_qa_gate_source_has_no_external_execution_or_network_imports():
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


def test_controlled_export_implementation_contract_qa_gate_source_only_reads_expected_docs():
    source = TEST_PATH.read_text(encoding="utf-8")
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

    allowed_path_fragments = [
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_v1.md",
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py",
    ]

    for fragment in allowed_path_fragments:
        assert fragment in source
