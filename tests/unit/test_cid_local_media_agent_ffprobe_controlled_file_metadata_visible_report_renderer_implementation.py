import importlib.util
from pathlib import Path


SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_v1.md"
)
SOURCE_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_qa_gate_v1.md"
)
SOURCE_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_qa_gate.py"
)

ACCEPTANCE = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "IMPLEMENTATION_PASS_READY_FOR_QA_GATE"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.QA.GATE.V1"
)

SAFE_FLAGS = [
    "media_processing_performed",
    "scanner_executed",
    "real_media_used",
    "ffmpeg_used",
    "audio_extraction_performed",
    "sync_generated",
    "transcription_generated",
    "subtitles_generated",
    "timeline_export_generated",
    "database_write",
    "saas_upload",
    "network_call",
]

REQUIRED_SECTIONS = [
    "CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
    "Phase",
    "Input Policy",
    "Input",
    "Preflight Result",
    "Format Summary",
    "Stream Summary",
    "Video Streams",
    "Audio Streams",
    "Safety Boundary",
    "Blocked Operations",
    "Human Review Required",
    "Next Safe Phase",
]

FORBIDDEN_CLAIMS = [
    "scanner execution: true",
    "media processing: true",
    "audio extraction: true",
    "sync generation: true",
    "transcription generation: true",
    "subtitle generation: true",
    "timeline export: true",
    "SaaS upload: true",
    "DB write: true",
    "installer creation: true",
    "client-facing readiness: true",
    "public demo readiness: true",
    "sales demo readiness: true",
    "production readiness: true",
]


def load_module():
    spec = importlib.util.spec_from_file_location("metadata_visible_report_renderer", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def safe_flags() -> dict[str, bool]:
    return {flag: False for flag in SAFE_FLAGS}


def successful_payload() -> dict[str, object]:
    return {
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": "second_fixture_controlled.mov",
        "ffprobe_command_kind": "metadata_json",
        "result": "FFPROBE_METADATA_PREFLIGHT_PASS",
        "metadata": {
            "format": {
                "filename": "/tmp/cid_local_media_agent_controlled_ffprobe/second_fixture_controlled.mov",
                "duration": "12.500000",
                "size": "1234567",
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            },
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                    "duration": "12.500000",
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "pcm_s16le",
                    "sample_rate": "48000",
                    "channels": 2,
                    "duration": "12.500000",
                },
            ],
        },
        **safe_flags(),
    }


def failure_payload() -> dict[str, object]:
    return {
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": "failed_fixture.mov",
        "ffprobe_command_kind": "metadata_json",
        "result": "FFPROBE_METADATA_PREFLIGHT_FAILED",
        "failure_reason": "controlled metadata failed safely",
        "metadata": {"format": None, "streams": []},
        **safe_flags(),
    }


def render(payload: dict[str, object]) -> str:
    return load_module().render_controlled_ffprobe_metadata_visible_report(payload)


def assert_required_sections(report: str) -> None:
    for section in REQUIRED_SECTIONS:
        assert section in report


def assert_no_full_paths(report: str) -> None:
    for forbidden in [
        "/tmp/cid_local_media_agent_controlled_ffprobe",
        "/tmp/private",
        "/home/",
        "/mnt/",
        "tests/fixtures/local_media_agent/controlled_media",
        "C:\\",
        "\\\\server",
    ]:
        assert forbidden not in report


def test_deterministic_output() -> None:
    payload = successful_payload()
    assert render(payload) == render(payload)


def test_successful_report_sections() -> None:
    report = render(successful_payload())
    assert_required_sections(report)
    assert "second_fixture_controlled.mov" in report
    assert "FFPROBE_METADATA_PREFLIGHT_PASS" in report
    assert "format=mov,mp4,m4a,3gp,3g2,mj2" in report
    assert "total=2, video=1, audio=1, unknown=0" in report
    assert "codec=h264" in report
    assert "codec=pcm_s16le" in report
    assert_no_full_paths(report)


def test_safe_failure_report_behavior() -> None:
    report = render(failure_payload())
    assert_required_sections(report)
    assert "FFPROBE_METADATA_PREFLIGHT_FAILED" in report
    assert "controlled metadata failed safely" in report
    assert "format unavailable" in report
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_full_paths(report)


def test_invalid_input_policy_is_blocked_safely() -> None:
    payload = successful_payload()
    payload["input_policy"] = "arbitrary_path"
    report = render(payload)
    assert_required_sections(report)
    assert "BLOCKED_UNSAFE_CONTROLLED_METADATA_PAYLOAD" in report
    assert "blocked before metadata rendering" in report
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert_no_full_paths(report)


def test_invalid_command_kind_is_blocked_safely() -> None:
    payload = successful_payload()
    payload["ffprobe_command_kind"] = "raw_probe"
    report = render(payload)
    assert "BLOCKED_UNSAFE_CONTROLLED_METADATA_PAYLOAD" in report
    assert "blocked before metadata rendering" in report
    assert_no_full_paths(report)


def test_null_format_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["format"] = None
    report = render(payload)
    assert "format unavailable" in report
    assert_no_full_paths(report)


def test_empty_streams_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["streams"] = []
    report = render(payload)
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_full_paths(report)


def test_unknown_stream_type_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["streams"] = [
        {"index": 3, "codec_type": "data", "codec_name": "bin_data"}
    ]
    report = render(payload)
    assert "total=1, video=0, audio=0, unknown=1" in report
    assert "index=3, type=unknown, codec=bin_data" in report
    assert_no_full_paths(report)


def test_unsafe_full_path_input_is_redacted() -> None:
    for unsafe_input in [
        "/tmp/private/unsafe.mov",
        "C:\\private\\unsafe.mov",
        "..\\unsafe.mov",
        "//server/share/unsafe.mov",
    ]:
        payload = successful_payload()
        payload["input_path_redacted"] = unsafe_input
        report = render(payload)
        assert "<redacted-input>" in report
        assert "unsafe.mov" not in report
        assert_no_full_paths(report)


def test_input_path_redacted_is_filename_only() -> None:
    payload = successful_payload()
    assert "/" not in str(payload["input_path_redacted"])
    assert "\\" not in str(payload["input_path_redacted"])
    assert "second_fixture_controlled.mov" in render(payload)


def test_blocked_operations_human_review_and_next_phase_are_present() -> None:
    report = render(successful_payload())
    for operation in [
        "scanner execution: false",
        "media processing: false",
        "audio extraction: false",
        "sync generation: false",
        "transcription generation: false",
        "subtitle generation: false",
        "timeline export: false",
        "SaaS upload: false",
        "DB write: false",
        "installer creation: false",
        "client-facing readiness: false",
        "public demo readiness: false",
        "sales demo readiness: false",
        "production readiness: false",
    ]:
        assert operation in report
    assert "Human review is required" in report
    assert NEXT_PHASE in report


def test_forbidden_claims_are_absent() -> None:
    report = render(successful_payload())
    for claim in FORBIDDEN_CLAIMS:
        assert claim not in report


def test_no_forbidden_imports_or_subprocess_usage_are_present() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden_imports = [
        "import " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ] + [
        "from " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ]
    for token in [*forbidden_imports, "subprocess"]:
        assert token not in source


def test_no_media_tool_execution_reference_pattern_is_present() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    media_processor = "ff" + "mpeg"
    media_probe = "ff" + "probe"
    for token in [
        media_processor + " -i",
        media_processor + " -y",
        media_processor + " -nostdin",
        f'"{media_processor}"',
        f"'{media_processor}'",
        media_probe + " -v",
        f'"{media_probe}"',
        f"'{media_probe}'",
    ]:
        assert token not in source


def test_source_contract_qa_gate_is_referenced_and_results_declared() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert SOURCE_QA_DOC.exists()
    assert SOURCE_QA_TEST.exists()
    assert str(SOURCE_QA_DOC) in text
    assert str(SOURCE_QA_TEST) in text
    assert ACCEPTANCE in text
    assert NEXT_PHASE in text
