from pathlib import Path

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_qa_gate_v1.md"
)
SOURCE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_v1.md"
)
SOURCE_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract.py"
)
PREVIOUS_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate_v1.md"
)
PREVIOUS_QA_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate.py"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
SOURCE_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.V1"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.V1"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_phase_and_result_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        QA_PHASE,
        "PASS_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_CONTRACT_VALIDATED",
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_CONTRACT_QA_GATE_PASS_CLOSED",
    ])


def test_source_stable_state_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "957687f3759fad9933e6d9453963e10a08a23e83",
        "docs: add CID Local Media Agent ffprobe visible report renderer implementation contract",
        "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-renderer-implementation-contract-v1-20260622",
        SOURCE_PHASE,
    ])


def test_required_source_files_exist() -> None:
    for path in [
        QA_DOC,
        SOURCE_DOC,
        SOURCE_TEST,
        PREVIOUS_QA_DOC,
        PREVIOUS_QA_TEST,
    ]:
        assert path.exists(), path


def test_required_implementation_contract_behavior_is_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "accepts only already-safe controlled metadata payloads",
        "`input_policy` equal to `controlled_fixture_only`",
        "`input_path_redacted` to be filename-only",
        "blocks or redacts full local paths",
        "`ffprobe_command_kind` equal to `metadata_json`",
        "`metadata.format` as null or object",
        "`metadata.streams` as a list",
        "produces deterministic report output",
        "plain text or Markdown-safe text",
        "renders format summary",
        "renders stream summary",
        "renders video stream summary",
        "renders audio stream summary",
        "renders safety boundary summary",
        "renders blocked operations summary",
        "renders human review required note",
        "renders next safe phase",
        "renders safe failure reports without leaking private data",
        "handles invalid input policy safely",
        "handles null format safely",
        "handles empty streams safely",
        "handles unknown stream types safely",
        "keeps blocked operation flags false",
    ])


def test_required_boundaries_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "runtime renderer implementation",
        "real rodaje material",
        "real media files",
        "arbitrary folders",
        "scanner execution",
        "ffprobe execution on real media",
        "ffmpeg media processing",
        "audio extraction",
        "sync generation",
        "transcription generation",
        "subtitle generation",
        "timeline export",
        "SaaS upload",
        "database writes",
        "installer creation",
        "client-facing use",
        "public demo",
        "sales demo",
        "production use",
    ])


def test_source_implementation_contract_declares_expected_result_and_next_phase() -> None:
    assert_all_present(read(SOURCE_DOC), [
        SOURCE_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.QA.GATE.V1",
    ])


def test_source_test_mentions_implementation_contract_requirements() -> None:
    assert_all_present(read(SOURCE_TEST), [
        "input_path_redacted",
        "controlled_fixture_only",
        "metadata_json",
        "deterministic",
        "Human review",
        "Blocked operations",
    ])


def test_validation_evidence_and_next_safe_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        "visible report renderer implementation contract QA gate test passing",
        "visible report renderer implementation contract test passing",
        "visible report renderer contract QA gate test passing",
        "no wrong phase prefix",
        "no runtime script staged",
        NEXT_PHASE,
    ])


def test_no_wrong_phase_prefix_is_present() -> None:
    for path in [QA_DOC, SOURCE_DOC, SOURCE_TEST]:
        assert "CID.LOCAL_AGENT" not in read(path)


def test_no_forbidden_tooling_import_patterns_are_in_qa_gate_test() -> None:
    content = read(Path(__file__))
    denied_imports = [
        "import " + name for name in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ] + [
        "from " + name for name in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ]
    for item in denied_imports:
        assert item not in content


def test_no_runtime_renderer_implementation_is_claimed() -> None:
    assert_all_present(read(QA_DOC), [
        "does not authorize:",
        "runtime renderer implementation",
        "without implementing runtime rendering in this phase",
    ])
