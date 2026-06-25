from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.V1"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_previous_closure_doc() -> str:
    return PREVIOUS_CLOSURE_DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_contract_document_exists():
    assert DOC_PATH.exists()


def test_controlled_export_implementation_contract_dependencies_exist():
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()


def test_controlled_export_implementation_contract_declares_exact_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert "Controlled Export Implementation Contract v1" in text


def test_controlled_export_implementation_contract_links_previous_closure_review():
    text = _read_doc()

    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_contract_declares_result_and_next_phase():
    text = _read_doc()

    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_contract_is_documentation_and_test_only():
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


def test_controlled_export_implementation_contract_defines_future_implementation_shape():
    text = _read_doc()

    required_phrases = [
        "The future implementation must be local-only, deterministic, pure, and controlled.",
        "The future implementation may only operate on already-safe controlled visible report text",
        "The future implementation may produce an in-memory controlled text artifact descriptor.",
        "The future implementation may calculate deterministic metadata",
        "safe suggested filename",
        "source_boundary",
        "write_performed",
        "artifact_created_on_disk",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_descriptor_requirements_are_safe():
    text = _read_doc()

    required_phrases = [
        "`artifact_format`, limited to a controlled text format.",
        "`suggested_filename`, generated deterministically from controlled metadata only.",
        "`content_text`, containing the already-safe visible report text.",
        "`line_count`, derived from the controlled text content.",
        "`byte_count`, derived from the encoded controlled text content.",
        "`content_sha256`, derived from the controlled text content.",
        "`safety_flags`, explicitly declaring no real media",
        "`write_performed`, which must be false.",
        "`artifact_created_on_disk`, which must be false.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_rejects_file_writes_and_filesystem_artifacts():
    text = _read_doc()

    required_phrases = [
        "The future implementation must not write output files.",
        "The future implementation must not create filesystem artifacts.",
        "The future implementation must not accept arbitrary output paths.",
        "It does not authorize file writing.",
        "It does not authorize artifact generation.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_rejects_real_media_and_arbitrary_folders():
    text = _read_doc()

    required_phrases = [
        "The future implementation must not accept arbitrary input folders.",
        "The future implementation must not read real media.",
        "The future implementation must not scan folders.",
        "It does not authorize real media.",
        "It does not authorize arbitrary folders.",
        "It does not authorize scanner execution.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_rejects_media_processing_and_external_execution():
    text = _read_doc()

    required_phrases = [
        "The future implementation must not execute ffprobe or FFmpeg.",
        "The future implementation must not spawn processes.",
        "The future implementation must not perform audio extraction.",
        "The future implementation must not perform sync.",
        "The future implementation must not perform transcription.",
        "The future implementation must not generate subtitles.",
        "The future implementation must not export timelines.",
        "It does not authorize ffprobe or FFmpeg execution.",
        "It does not authorize subprocess or process execution.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_rejects_network_saas_installer_and_client_use():
    text = _read_doc()

    required_phrases = [
        "The future implementation must not access network resources.",
        "The future implementation must not touch SaaS systems or database systems.",
        "The future implementation must not change installer, licensing, public demo, client demo, sales demo, or production behavior.",
        "It does not authorize audio extraction, sync, transcription, subtitles, timeline export, network access, SaaS/DB integration, installer work, public demo, client demo, sales demo, or production use.",
        "It remains non-client-facing until a later explicit authorization phase.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_acceptance_criteria_are_explicit():
    text = _read_doc()

    required_phrases = [
        "It is separately named as an implementation phase.",
        "It imports or receives already-safe controlled visible report content.",
        "It returns a deterministic in-memory descriptor.",
        "It performs no file writes.",
        "It creates no filesystem artifacts.",
        "It performs no real media operations.",
        "It performs no folder scanning.",
        "It performs no ffprobe or FFmpeg execution.",
        "It performs no subprocess or process execution.",
        "It performs no network operation.",
        "It performs no SaaS or database operation.",
        "It preserves the local-only boundary.",
        "It preserves the controlled fixture boundary.",
        "It includes unit tests.",
        "It has a separate QA gate.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_contract_validates_previous_closure_review():
    previous_text = _read_previous_closure_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "This phase is documentation and test-only.",
        "It does not implement export.",
        "It does not write output files.",
        "It does not create artifacts.",
        "future explicit controlled export implementation contract",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_contract_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for this implementation contract test.",
        "This implementation contract unit test.",
        "Previous closure review unit test.",
        "Previous QA gate unit test.",
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


def test_controlled_export_implementation_contract_does_not_claim_runtime_or_client_readiness():
    text = _read_doc()
    previous_text = _read_previous_closure_doc()

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


def test_controlled_export_implementation_contract_has_no_runtime_entrypoint_language():
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


def test_controlled_export_implementation_contract_source_has_no_external_execution_or_network_imports():
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


def test_controlled_export_implementation_contract_source_only_reads_expected_docs():
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
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_v1.md",
        "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review_v1.md",
        "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_qa_gate_closure_review.py",
    ]

    for fragment in allowed_path_fragments:
        assert fragment in source
