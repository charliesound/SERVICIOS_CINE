from pathlib import Path
import ast


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_readiness_contract_v1.md"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.V1"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT_PASS_READY_FOR_QA_GATE"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.READINESS.CONTRACT.QA.GATE.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_IMPLEMENTATION_READINESS_CONTRACT"


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_readiness_contract_document_exists():
    assert DOC_PATH.exists()


def test_controlled_export_implementation_readiness_contract_declares_exact_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert "Implementation Readiness Contract v1" in text


def test_controlled_export_implementation_readiness_contract_links_previous_closed_phase():
    text = _read_doc()

    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_readiness_contract_is_documentation_and_test_only():
    text = _read_doc()

    required_phrases = [
        "This phase is documentation and test-only.",
        "This phase does not implement export.",
        "This phase does not write output files.",
        "This phase does not create artifacts.",
        "This phase does not add runtime code.",
        "This phase does not modify existing renderer behavior.",
        "This phase does not modify existing CLI behavior.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_preserves_local_only_boundary():
    text = _read_doc()

    required_phrases = [
        "local-only",
        "controlled",
        "deterministic",
        "already-safe controlled metadata/report inputs",
        "preserves the local-only product boundary",
        "preserves the controlled fixture boundary",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_rejects_real_media_and_arbitrary_folders():
    text = _read_doc()

    required_phrases = [
        "does not enable real media usage",
        "does not enable arbitrary folder usage",
        "does not authorize real media",
        "does not authorize arbitrary folders",
        "no dependency on real media",
        "no dependency on arbitrary user folders",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_rejects_media_processing_capabilities():
    text = _read_doc()

    required_phrases = [
        "does not enable scanner execution",
        "does not enable ffprobe or FFmpeg execution",
        "does not enable audio extraction",
        "does not enable sync",
        "does not enable transcription",
        "does not enable subtitle generation",
        "does not enable timeline export",
        "does not authorize audio extraction, sync, transcription, subtitles, timeline export",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_rejects_external_execution_and_network():
    text = _read_doc()

    required_phrases = [
        "does not add process spawning or external command execution",
        "does not enable network access",
        "does not spawn external commands",
        "does not perform audio, video, transcription, subtitle, sync, timeline, or network operations",
        "does not authorize process execution",
        "does not authorize ffprobe or FFmpeg execution",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_rejects_wider_product_authorization():
    text = _read_doc()

    required_phrases = [
        "does not enable SaaS integration",
        "does not enable installer work",
        "does not enable public, client, sales, or production use",
        "does not authorize installer work, public demo, client demo, sales demo, or production use",
        "non-client-facing until a later explicit authorization phase",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_defines_future_readiness_requirements():
    text = _read_doc()

    required_phrases = [
        "The implementation phase is explicit and separately named.",
        "The implementation operates only on controlled synthetic or already-safe controlled visible report content.",
        "The implementation has deterministic output.",
        "The implementation is covered by unit tests before closure.",
        "The implementation has a QA gate before any wider use.",
        "The implementation reports safety flags clearly.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_readiness_contract_declares_expected_result_and_next_phase():
    text = _read_doc()

    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required QA Gate" in text


def test_controlled_export_implementation_readiness_contract_does_not_claim_implementation_is_ready_for_use():
    text = _read_doc()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "export implemented",
        "artifact generated",
        "files written",
    ]

    lowered = text.lower()
    for claim in forbidden_claims:
        assert claim not in lowered


def test_controlled_export_implementation_readiness_test_has_no_external_execution_or_network_imports():
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


def test_controlled_export_implementation_readiness_contract_has_no_runtime_entrypoint_language():
    text = _read_doc()

    forbidden_phrases = [
        "command line usage",
        "run this exporter",
        "write the report to",
        "open media folder",
        "scan folder",
        "how to execute ffprobe",
        "how to execute ffmpeg",
        "ffprobe command example",
        "ffmpeg command example",
        "upload",
        "download",
    ]

    lowered = text.lower()
    for phrase in forbidden_phrases:
        assert phrase not in lowered
