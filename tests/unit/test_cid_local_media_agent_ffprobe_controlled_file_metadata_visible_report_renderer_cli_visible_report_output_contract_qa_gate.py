from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_v1.md"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_CONTRACT_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-contract-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.V1"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        NEXT_PHASE,
    ])


def test_qa_gate_declares_documentation_only_no_runtime() -> None:
    assert_all_present(read(QA_DOC), [
        "QA gate documentation",
        "no runtime implementation",
        "no CLI changes",
        "no renderer changes",
        "does not execute the CLI",
        "does not execute the renderer",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not execute subprocess/process execution",
        "does not use real media",
        "does not use network",
        "does not use SaaS/DB",
    ])


def test_qa_gate_validates_allowed_forbidden_redaction_format_and_blocked() -> None:
    assert_all_present(read(QA_DOC), [
        "defines allowed visible output",
        "defines forbidden visible output",
        "defines redaction/privacy",
        "defines format contract",
        "defines blocked boundaries",
    ])


def test_qa_gate_validates_authorized_chain() -> None:
    assert_all_present(read(QA_DOC), [
        "controlled synthetic JSON fixture",
        "-> existing local-only CLI",
        "-> existing pure renderer",
        "-> safe visible report text",
    ])


def test_qa_gate_validates_previous_contract_does_not_authorize_blocked() -> None:
    assert_all_present(read(QA_DOC), [
        "real media",
        "scanner execution",
        "real ffprobe execution",
        "ffmpeg",
        "subprocess/process execution",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "network",
        "SaaS/DB",
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_previous_contract_exists_and_declares_phase_and_result() -> None:
    assert CONTRACT_DOC.exists()
    content = read(CONTRACT_DOC)
    assert_all_present(content, [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
        "VISIBLE_REPORT_OUTPUT_CONTRACT_PASS_READY_FOR_QA_GATE",
    ])


def test_previous_contract_declares_required_sections() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "## Allowed Visible Output",
        "## Forbidden Visible Output",
        "## Redaction/Privacy",
        "## Format Contract",
        "## Blocked Boundaries",
    ])


def test_previous_contract_declares_blocked_boundaries() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "real media",
        "scanner execution",
        "real ffprobe execution",
        "ffmpeg",
        "subprocess/process execution",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "network",
        "SaaS/DB",
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_previous_contract_does_not_authorize_blocked_capabilities() -> None:
    text = read(CONTRACT_DOC).lower()
    forbidden_authorizations = [
        "authorizes real media",
        "authorizes scanner",
        "authorizes ffprobe",
        "authorizes ffmpeg",
        "authorizes audio extraction",
        "authorizes sync",
        "authorizes transcription",
        "authorizes subtitles",
        "authorizes timeline export",
        "authorizes network",
        "authorizes saas",
        "authorizes db",
    ]
    for phrase in forbidden_authorizations:
        assert phrase not in text


def test_test_file_does_not_import_or_execute_runtime() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "scripts",
        "from " + "scripts",
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process.",
        "request" + "s",
        "sock" + "et",
        "htt" + "px",
        "url" + "lib",
        "ff" + "probe -",
        "ff" + "mpeg -",
    ]
    for token in forbidden:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    assert forbidden_prefix not in read(QA_DOC)
    assert forbidden_prefix not in read(CONTRACT_DOC)
