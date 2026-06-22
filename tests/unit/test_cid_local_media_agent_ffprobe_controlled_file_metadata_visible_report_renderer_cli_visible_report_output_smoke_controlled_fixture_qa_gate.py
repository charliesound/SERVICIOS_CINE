import json
from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_qa_gate_v1.md"
)
PREVIOUS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_v1.md"
)
PREVIOUS_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture.py"
)
FIXTURE_JSON = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"
)
EXPECTED_TXT = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_expected_v1.txt"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_v1.md"
)
CONTRACT_QA_GATE = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_qa_gate_v1.md"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_SMOKE_CONTROLLED_FIXTURE_QA_GATE_PASS_CLOSED"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-smoke-controlled-fixture-qa-gate-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.INTEGRATION.READINESS.CONTRACT.V1"
)

SAFE_FALSE_FLAGS = [
    "media_processing_performed",
    "scanner_executed",
    "real_media_used",
    "ffmpeg_used",
    "audio_extraction_performed",
    "sync_performed",
    "database_write",
    "saas_upload",
    "network_call",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def assert_no_private_or_path_leakage(text: str) -> None:
    forbidden = [
        "/home/",
        "/mnt/",
        "C:\\",
        "\\\\",
        "\\wsl.localhost",
        "full absolute path",
        "secrets",
        "environment values",
        "real client",
        "real project",
        "real production",
        "private material",
    ]
    lowered = text.lower()
    for marker in forbidden:
        assert marker.lower() not in lowered


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_target_tag_and_next_are_declared() -> None:
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
        "does not modify existing scripts",
        "does not modify existing fixtures",
        "does not execute the CLI",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not use subprocess/process execution",
        "does not use real media",
        "does not use scanner",
        "does not use arbitrary folders",
        "does not use network",
        "does not use SaaS/DB",
    ])


def test_qa_gate_validates_authorized_chain() -> None:
    assert_all_present(read(QA_DOC), [
        "controlled synthetic JSON fixture",
        "-> existing local-only CLI",
        "-> existing pure renderer",
        "-> safe visible report text",
    ])


def test_qa_gate_validates_previous_phase_non_authorizations() -> None:
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


def test_qa_gate_does_not_authorize_blocked_capabilities() -> None:
    text = read(QA_DOC).lower()
    for phrase in [
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
        "authorizes production",
    ]:
        assert phrase not in text


def test_required_files_exist() -> None:
    for path in [
        QA_DOC,
        PREVIOUS_DOC,
        PREVIOUS_TEST,
        FIXTURE_JSON,
        EXPECTED_TXT,
        CONTRACT_DOC,
        CONTRACT_QA_GATE,
    ]:
        assert path.exists(), path


def test_previous_doc_exists_and_declares_phase_and_result() -> None:
    assert PREVIOUS_DOC.exists()
    content = read(PREVIOUS_DOC)
    assert_all_present(content, [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
        "VISIBLE_REPORT_OUTPUT_SMOKE_CONTROLLED_FIXTURE_PASS_READY_FOR_QA_GATE",
    ])


def test_previous_doc_declares_authorized_chain_and_no_runtime() -> None:
    assert_all_present(read(PREVIOUS_DOC), [
        "controlled synthetic JSON fixture",
        "existing pure renderer",
        "safe visible report text",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not use subprocess/process execution",
        "does not use real media",
        "does not use network",
        "does not use SaaS/DB",
        "production use",
    ])


def test_expected_txt_exists_and_is_not_empty() -> None:
    assert EXPECTED_TXT.exists()
    content = read(EXPECTED_TXT)
    assert len(content) > 100


def test_expected_txt_contains_required_sections() -> None:
    content = read(EXPECTED_TXT)
    for section in [
        "# CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
        "## Phase",
        "## Input Policy",
        "## Input",
        "## Preflight Result",
        "## Format Summary",
        "## Stream Summary",
        "## Safety Boundary",
        "## Blocked Operations",
        "## Human Review Required",
    ]:
        assert section in content


def test_expected_txt_contains_safety_false_markers() -> None:
    content = read(EXPECTED_TXT)
    for marker in [
        "scanner execution: false",
        "media processing: false",
        "audio extraction: false",
        "SaaS upload: false",
        "DB write: false",
    ]:
        assert marker in content


def test_fixture_json_maintains_safe_flags_false() -> None:
    payload = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    for flag in SAFE_FALSE_FLAGS:
        assert payload[flag] is False


def test_fixture_json_is_controlled() -> None:
    payload = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["input_path_redacted"] == "synthetic_controlled_fixture.mov"


def test_no_private_or_path_leakage_in_qa_gate_doc() -> None:
    assert_no_private_or_path_leakage(read(QA_DOC))


def test_no_private_or_path_leakage_in_previous_doc() -> None:
    assert_no_private_or_path_leakage(read(PREVIOUS_DOC))


def test_no_private_or_path_leakage_in_expected_txt() -> None:
    assert_no_private_or_path_leakage(read(EXPECTED_TXT))


def test_no_private_or_path_leakage_in_fixture_json() -> None:
    assert_no_private_or_path_leakage(read(FIXTURE_JSON))


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [QA_DOC, PREVIOUS_DOC, FIXTURE_JSON, EXPECTED_TXT, CONTRACT_DOC, CONTRACT_QA_GATE]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")


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
