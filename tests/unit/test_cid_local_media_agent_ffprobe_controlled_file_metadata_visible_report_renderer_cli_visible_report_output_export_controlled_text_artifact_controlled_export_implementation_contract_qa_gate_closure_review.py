from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_QA_GATE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_v1.md"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate.py"
)

PREVIOUS_CONTRACT_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md"
)

PREVIOUS_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract.py"
)

PREVIOUS_READINESS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py"
)

PREVIOUS_READINESS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate.py"
)

PREVIOUS_READINESS_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_IMPLEMENTATION"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.V1"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_previous_qa_gate_doc() -> str:
    return PREVIOUS_QA_GATE_DOC_PATH.read_text(encoding="utf-8")


def _read_previous_contract_doc() -> str:
    return PREVIOUS_CONTRACT_DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_contract_qa_gate_closure_review_document_exists():
    assert DOC_PATH.exists()


def test_controlled_export_implementation_contract_qa_gate_closure_review_dependencies_exist():
    assert PREVIOUS_QA_GATE_DOC_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert PREVIOUS_CONTRACT_DOC_PATH.exists()
    assert PREVIOUS_CONTRACT_TEST_PATH.exists()
    assert PREVIOUS_READINESS_CLOSURE_TEST_PATH.exists()
    assert PREVIOUS_READINESS_QA_GATE_TEST_PATH.exists()
    assert PREVIOUS_READINESS_TEST_PATH.exists()


def test_controlled_export_implementation_contract_qa_gate_closure_review_declares_exact_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert "Controlled Export Implementation Contract QA Gate Closure Review v1" in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_links_previous_qa_gate():
    text = _read_doc()

    assert str(PREVIOUS_QA_GATE_DOC_PATH) in text
    assert str(PREVIOUS_QA_GATE_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_declares_result_and_next_phase():
    text = _read_doc()

    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_is_documentation_and_test_only():
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


def test_controlled_export_implementation_contract_qa_gate_closure_review_confirms_previous_gate_closure():
    text = _read_doc()

    required_phrases = [
        "The controlled export implementation contract QA gate is considered closed",
        "The implementation contract exists.",
        "The implementation contract test exists.",
        "The QA gate validates the exact implementation contract phase.",
        "The QA gate validates the expected functional result.",
        "The QA gate validates the required next phase.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_rejects_write_and_artifact_scope():
    text = _read_doc()

    required_phrases = [
        "The QA gate rejects file writes.",
        "The QA gate rejects filesystem artifact creation.",
        "The QA gate rejects arbitrary output paths.",
        "It does not authorize file writing.",
        "It does not authorize artifact generation.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_rejects_real_media_and_scanner_scope():
    text = _read_doc()

    required_phrases = [
        "The QA gate rejects arbitrary input folders.",
        "The QA gate rejects real media.",
        "The QA gate rejects scanner execution.",
        "It does not authorize real media.",
        "It does not authorize arbitrary folders.",
        "It does not authorize scanner execution.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_rejects_execution_media_processing_and_external_access():
    text = _read_doc()

    required_phrases = [
        "The QA gate rejects ffprobe and FFmpeg execution.",
        "The QA gate rejects subprocess and process execution.",
        "The QA gate rejects audio extraction, sync, transcription, subtitles, and timeline export.",
        "The QA gate rejects network access.",
        "The QA gate rejects SaaS/DB integration.",
        "It does not authorize ffprobe or FFmpeg execution.",
        "It does not authorize subprocess or process execution.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export, network access, SaaS/DB integration",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_rejects_client_and_production_scope():
    text = _read_doc()

    required_phrases = [
        "The QA gate rejects installer, public demo, client demo, sales demo, and production behavior.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export, network access, SaaS/DB integration, installer work, public demo, client demo, sales demo, or production use.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_declares_future_implementation_boundary():
    text = _read_doc()

    required_phrases = [
        "the chain may proceed only to a future explicitly named controlled export implementation phase.",
        "pure local-only in-memory descriptor for already-safe controlled visible report text.",
        "That future phase must not write output files.",
        "That future phase must not create filesystem artifacts.",
        "That future phase must not accept arbitrary output paths.",
        "That future phase must not accept arbitrary input folders.",
        "That future phase must not read real media.",
        "That future phase must not scan folders.",
        "That future phase must not execute ffprobe or FFmpeg.",
        "That future phase must not spawn processes.",
        "That future phase must not perform audio extraction, sync, transcription, subtitle generation, or timeline export.",
        "That future phase must not access network resources.",
        "That future phase must not touch SaaS systems or database systems.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_qa_gate_closure_review_validates_previous_qa_gate_content():
    previous_text = _read_previous_qa_gate_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "This QA gate validates the controlled export implementation contract.",
        "This phase is documentation and test-only.",
        "It does not implement export.",
        "Rejects file writes.",
        "Rejects filesystem artifact creation.",
        "Rejects arbitrary output paths.",
        "Rejects real media.",
        "Rejects ffprobe and FFmpeg execution.",
        "Rejects subprocess and process execution.",
        "Rejects network access.",
        "Rejects SaaS/DB integration.",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_contract_qa_gate_closure_review_validates_previous_contract_content():
    previous_text = _read_previous_contract_doc()

    required_phrases = [
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


def test_controlled_export_implementation_contract_qa_gate_closure_review_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for this closure review test.",
        "This closure review unit test.",
        "Previous implementation contract QA gate unit test.",
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


def test_controlled_export_implementation_contract_qa_gate_closure_review_does_not_claim_runtime_or_client_readiness():
    text = _read_doc()
    previous_qa_text = _read_previous_qa_gate_doc()
    previous_contract_text = _read_previous_contract_doc()

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

    combined = f"{text}\n{previous_qa_text}\n{previous_contract_text}".lower()
    for claim in forbidden_claims:
        assert claim not in combined


def test_controlled_export_implementation_contract_qa_gate_closure_review_source_has_no_external_execution_or_network_imports():
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


def test_controlled_export_implementation_contract_qa_gate_closure_review_source_only_reads_expected_docs():
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
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_closure_review_v1.md",
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_v1.md",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate.py",
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate.py",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract.py",
    ]

    for fragment in allowed_path_fragments:
        assert fragment in source
