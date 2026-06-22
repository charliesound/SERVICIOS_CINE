from pathlib import Path

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate_v1.md")
SOURCE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_v1.md")
SOURCE_TEST = Path("tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract.py")

QA_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1"
SOURCE_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_phase_and_result_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        QA_PHASE,
        "PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_VALIDATED",
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "06c1dd031b8985e56214624a60423bea10f0fd91",
        "docs: add CID Local Media Agent ffprobe visible report contract",
        "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-contract-v1-20260622",
        SOURCE_PHASE,
    ])


def test_required_source_files_exist() -> None:
    assert QA_DOC.exists()
    assert SOURCE_DOC.exists()
    assert SOURCE_TEST.exists()


def test_required_sections_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "report title",
        "phase",
        "input policy",
        "redacted input filename",
        "preflight result",
        "format summary",
        "stream summary",
        "video stream summary",
        "audio stream summary",
        "safety boundary summary",
        "blocked operations summary",
        "human review required note",
        "next safe phase",
    ])


def test_required_report_boundaries_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "full local paths",
        "real rodaje material references",
        "raw private file locations",
        "scanner output",
        "media processing output",
        "audio extraction output",
        "sync output",
        "transcription output",
        "subtitle output",
        "timeline output",
        "SaaS identifiers",
        "database identifiers",
        "installer claims",
        "client-facing claims",
        "public demo claims",
        "sales demo claims",
        "production use claims",
    ])


def test_required_safe_inputs_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "`input_path_redacted` as filename only",
        "`input_policy` equal to `controlled_fixture_only`",
        "`ffprobe_command_kind` equal to `metadata_json`",
        "`metadata.format` as null or object",
        "`metadata.streams` as a list",
        "all blocked execution flags remaining false",
        "safe report behavior even when preflight result is failure",
        "no full path leakage",
    ])


def test_source_contract_declares_expected_result_and_next_phase() -> None:
    assert_all_present(read(SOURCE_DOC), [
        SOURCE_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_PASS_READY_FOR_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1",
    ])


def test_source_test_mentions_visible_report_requirements() -> None:
    assert_all_present(read(SOURCE_TEST), [
        "Report title",
        "Input policy",
        "Format summary",
        "Stream summary",
        "Human review required",
        "Blocked operations",
        "input_path_redacted",
        "controlled_fixture_only",
        "metadata_json",
    ])


def test_validation_evidence_and_next_safe_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "visible report contract QA gate test passing",
        "visible report contract test passing",
        "second fixture scenario QA gate test passing",
        "no runtime script staged",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.V1",
    ])
