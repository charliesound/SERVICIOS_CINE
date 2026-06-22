import importlib.util
import json
from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_smoke_controlled_fixture_v1.md"
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
QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_contract_qa_gate_v1.md"
)
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "VISIBLE_REPORT_OUTPUT_SMOKE_CONTROLLED_FIXTURE_PASS_READY_FOR_QA_GATE"
)
TARGET_TAG = (
    "cid-dev-stable-local-media-agent-ffprobe-controlled-file-metadata-visible-report-"
    "renderer-cli-visible-report-output-smoke-controlled-fixture-v1-20260622"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.SMOKE.CONTROLLED.FIXTURE.QA.GATE.V1"
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


def load_renderer():
    spec = importlib.util.spec_from_file_location("renderer", RENDERER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fixture_payload() -> dict[str, object]:
    parsed = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def assert_no_private_or_path_leakage(text: str) -> None:
    forbidden = [
        "/tmp/",
        "/home/",
        "/mnt/",
        "C:\\",
        "\\\\",
        "\\wsl.localhost",
        "client_name",
        "client name",
        "real client",
        "project_name",
        "project name",
        "real project",
        "production name",
        "harliesound",
        "SERVICIOS_CINE",
        "private material",
        "rodaje",
    ]
    lowered = text.lower()
    for marker in forbidden:
        assert marker.lower() not in lowered


def test_doc_exists_and_declares_phase() -> None:
    assert DOC.exists()
    text = DOC.read_text(encoding="utf-8")
    assert PHASE in text


def test_doc_declares_previous_phase_functional_result_target_tag_and_next() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [PREVIOUS_PHASE, FUNCTIONAL_RESULT, TARGET_TAG, NEXT_PHASE]:
        assert required in text


def test_doc_declares_authorized_chain() -> None:
    text = DOC.read_text(encoding="utf-8")
    for item in [
        "controlled synthetic JSON fixture",
        "-> existing local-only CLI",
        "-> existing pure renderer",
        "-> safe visible report text",
    ]:
        assert item in text


def test_doc_declares_smoke_test_behavior_and_no_runtime() -> None:
    text = DOC.read_text(encoding="utf-8")
    for item in [
        "controlled smoke test",
        "does not execute the CLI",
        "does not execute real ffprobe",
        "does not execute ffmpeg",
        "does not use subprocess/process execution",
        "does not use real media",
        "does not use network",
        "does not use SaaS/DB",
    ]:
        assert item in text


def test_doc_declares_non_authorization_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    for item in [
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
    ]:
        assert item in text


def test_required_files_exist() -> None:
    for path in [DOC, FIXTURE_JSON, EXPECTED_TXT, CONTRACT_DOC, QA_GATE_DOC, RENDERER]:
        assert path.exists(), path


def test_fixture_is_json_dict_controlled() -> None:
    payload = fixture_payload()
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["ffprobe_command_kind"] == "metadata_json"
    assert payload["input_path_redacted"] == "synthetic_controlled_fixture.mov"
    assert isinstance(payload["metadata"], dict)
    assert isinstance(payload["metadata"]["streams"], list)


def test_fixture_safe_flags_are_false() -> None:
    payload = fixture_payload()
    for flag in SAFE_FALSE_FLAGS:
        assert payload[flag] is False


def test_fixture_does_not_contain_forbidden_markers() -> None:
    assert_no_private_or_path_leakage(FIXTURE_JSON.read_text(encoding="utf-8"))


def test_expected_txt_exists_and_is_not_empty() -> None:
    assert EXPECTED_TXT.exists()
    content = EXPECTED_TXT.read_text(encoding="utf-8")
    assert len(content) > 100


def test_expected_txt_contains_required_sections() -> None:
    content = EXPECTED_TXT.read_text(encoding="utf-8")
    for section in [
        "# CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
        "## Phase",
        "## Input Policy",
        "## Input",
        "## Preflight Result",
        "## Format Summary",
        "## Stream Summary",
        "## Video Streams",
        "## Audio Streams",
        "## Unknown Streams",
        "## Safety Boundary",
        "## Blocked Operations",
        "## Human Review Required",
        "## Next Safe Phase",
    ]:
        assert section in content


def test_expected_txt_contains_safe_values() -> None:
    content = EXPECTED_TXT.read_text(encoding="utf-8")
    for value in [
        "controlled_fixture_only",
        "synthetic_controlled_fixture.mov",
        "FFPROBE_METADATA_PREFLIGHT_PASS",
        "scanner execution: false",
        "media processing: false",
        "audio extraction: false",
        "SaaS upload: false",
        "DB write: false",
    ]:
        assert value in content


def test_expected_txt_has_no_private_or_path_leakage() -> None:
    assert_no_private_or_path_leakage(EXPECTED_TXT.read_text(encoding="utf-8"))


def test_renderer_output_matches_expected_fixture() -> None:
    renderer = load_renderer()
    payload = fixture_payload()
    actual = renderer.render_controlled_ffprobe_metadata_visible_report(payload)
    expected = EXPECTED_TXT.read_text(encoding="utf-8")
    assert actual == expected


def test_renderer_output_has_no_private_or_path_leakage() -> None:
    renderer = load_renderer()
    payload = fixture_payload()
    actual = renderer.render_controlled_ffprobe_metadata_visible_report(payload)
    assert_no_private_or_path_leakage(actual)


def test_renderer_output_contains_required_sections() -> None:
    renderer = load_renderer()
    payload = fixture_payload()
    actual = renderer.render_controlled_ffprobe_metadata_visible_report(payload)
    for section in [
        "# CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
        "## Phase",
        "## Input Policy",
        "## Preflight Result",
        "## Format Summary",
        "## Stream Summary",
        "## Safety Boundary",
        "## Blocked Operations",
        "## Human Review Required",
        "## Next Safe Phase",
    ]:
        assert section in actual


def test_renderer_output_does_not_authorize_blocked() -> None:
    renderer = load_renderer()
    payload = fixture_payload()
    actual = renderer.render_controlled_ffprobe_metadata_visible_report(payload).lower()
    for term in [
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
    ]:
        assert term not in actual


def test_renderer_source_has_no_forbidden_imports() -> None:
    source = RENDERER.read_text(encoding="utf-8")
    for token in [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "request" + "s",
        "from " + "request" + "s",
        "import " + "sock" + "et",
        "from " + "sock" + "et",
    ]:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, FIXTURE_JSON, EXPECTED_TXT, CONTRACT_DOC, QA_GATE_DOC, RENDERER]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
