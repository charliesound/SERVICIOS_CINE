from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_CONTRACT_PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-contract-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.QA.GATE.V1"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_markdown_exists_and_declares_phase_result_tag_previous_and_next() -> None:
    assert DOC.exists()
    assert_all_present(read_doc(), [
        PHASE,
        FUNCTIONAL_RESULT,
        TARGET_TAG,
        PREVIOUS_PHASE,
        NEXT_PHASE,
    ])


def test_authorized_chain_is_declared() -> None:
    assert_all_present(read_doc(), [
        "controlled synthetic JSON fixture",
        "-> existing local-only CLI",
        "-> existing pure renderer",
        "-> safe visible report text",
    ])


def test_required_sections_are_present() -> None:
    assert_all_present(read_doc(), [
        "## Allowed Visible Output",
        "## Forbidden Visible Output",
        "## Redaction/Privacy",
        "## Format Contract",
        "## Blocked Boundaries",
    ])


def test_no_runtime_cli_or_renderer_changes_are_declared() -> None:
    assert_all_present(read_doc(), [
        "There is no runtime implementation.",
        "There are no CLI changes.",
        "There are no renderer changes.",
        "This phase does not execute the CLI.",
        "This phase does not execute the renderer.",
    ])


def test_media_probe_process_network_and_db_are_blocked() -> None:
    assert_all_present(read_doc(), [
        "real media",
        "scanner execution",
        "real ffprobe execution",
        "ffmpeg",
        "subprocess/process execution",
        "network",
        "SaaS/DB",
    ])


def test_delivery_and_production_boundaries_are_blocked() -> None:
    assert_all_present(read_doc(), [
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "installer",
        "public demo",
        "client demo",
        "sales demo",
        "production use",
    ])


def test_forbidden_visible_output_privacy_items_are_declared() -> None:
    assert_all_present(read_doc(), [
        "full paths",
        "arbitrary folders",
        "real project names",
        "real shoot names",
        "real rodaje names",
        "real media material",
        "local users",
        "home paths",
        "absolute paths",
        "environment values",
        "secrets",
        "DB/SaaS data",
        "network data",
        "audiovisual content",
        "private material",
        "client names",
        "production names",
    ])


def test_allowed_output_and_format_contract_are_declared() -> None:
    assert_all_present(read_doc(), [
        "safe controlled technical information",
        "redacted input marker or controlled filename",
        "safety flags when present, especially as `false`",
        "human-readable plain text or Markdown-safe text",
        "controlled `.txt` or `.md` report",
        "deterministic for the same controlled JSON fixture",
    ])


def test_document_does_not_authorize_blocked_runtime_capabilities() -> None:
    text = read_doc().lower()
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
        "import" + "lib",
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
    assert forbidden_prefix not in read_doc()
