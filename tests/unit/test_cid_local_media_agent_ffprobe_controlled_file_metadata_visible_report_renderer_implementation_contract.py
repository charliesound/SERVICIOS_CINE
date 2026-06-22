from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_contract_v1.md"
)
SOURCE_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate_v1.md"
)
SOURCE_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_qa_gate.py"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.V1"
SOURCE_QA_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1"
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
ACCEPTANCE = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"
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

BLOCKED_OPERATIONS = [
    "media processing",
    "scanner execution",
    "audio extraction",
    "sync generation",
    "transcription generation",
    "subtitle generation",
    "timeline export",
    "SaaS upload",
    "DB write",
    "installer creation",
    "client-facing readiness",
    "public demo readiness",
    "sales demo readiness",
    "production readiness",
]

SECTIONS = [
    "Title",
    "Phase",
    "Input policy",
    "Redacted input filename",
    "Preflight result",
    "Format summary",
    "Stream summary",
    "Video stream summary",
    "Audio stream summary",
    "Safety boundary summary",
    "Blocked operations summary",
    "Human review required note",
    "Next safe phase",
]


def false_flags() -> dict[str, bool]:
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
        **false_flags(),
    }


def failure_payload() -> dict[str, object]:
    return {
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": "failed_fixture.mov",
        "ffprobe_command_kind": "metadata_json",
        "result": "FFPROBE_METADATA_PREFLIGHT_FAIL",
        "failure_reason": "controlled metadata failed safely",
        "metadata": {"format": None, "streams": []},
        **false_flags(),
    }


def render_controlled_ffprobe_metadata_visible_report(payload: dict[str, object]) -> str:
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    metadata_format = metadata.get("format")
    streams = metadata.get("streams") if isinstance(metadata.get("streams"), list) else []
    input_policy = str(payload.get("input_policy", "missing"))
    command_kind = str(payload.get("ffprobe_command_kind", "missing"))
    flags_are_false = all(payload.get(flag) is False for flag in SAFE_FLAGS)
    blocked = input_policy != "controlled_fixture_only" or command_kind != "metadata_json" or not flags_are_false

    filename = Path(str(payload.get("input_path_redacted", "redacted-input"))).name or "redacted-input"
    visible_streams = [] if blocked else streams

    if blocked:
        result = "BLOCKED_UNSAFE_CONTROLLED_METADATA_PAYLOAD"
        format_summary = "blocked before metadata rendering"
    else:
        result = str(payload.get("result", "unknown"))
        if isinstance(metadata_format, dict):
            format_summary = (
                f"format={metadata_format.get('format_name', 'unknown')}; "
                f"duration={metadata_format.get('duration', 'unknown')}; "
                f"size={metadata_format.get('size', 'unknown')}"
            )
        else:
            format_summary = "format unavailable"

    video_streams = [stream for stream in visible_streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in visible_streams if stream.get("codec_type") == "audio"]
    unknown_streams = [
        stream for stream in visible_streams if stream.get("codec_type") not in {"video", "audio"}
    ]
    video_summary = "; ".join(
        f"index={stream.get('index')}, codec={stream.get('codec_name')}, "
        f"size={stream.get('width')}x{stream.get('height')}, duration={stream.get('duration')}"
        for stream in video_streams
    ) or "no video streams reported"
    audio_summary = "; ".join(
        f"index={stream.get('index')}, codec={stream.get('codec_name')}, "
        f"sample_rate={stream.get('sample_rate')}, channels={stream.get('channels')}, "
        f"duration={stream.get('duration')}"
        for stream in audio_streams
    ) or "no audio streams reported"
    unknown_summary = "; ".join(
        f"index={stream.get('index')}, type=unknown, codec={stream.get('codec_name', 'unknown')}"
        for stream in unknown_streams
    ) or "no unknown streams reported"
    failure_note = str(payload.get("failure_reason", "not applicable"))

    return "\n".join([
        "# Title: CID controlled metadata visible report implementation contract",
        f"## Phase: {PHASE}",
        f"## Input policy: {input_policy}",
        f"## Redacted input filename: {filename}",
        f"## Preflight result: {result}",
        f"## Format summary: {format_summary}",
        (
            "## Stream summary: "
            f"total={len(visible_streams)}, video={len(video_streams)}, "
            f"audio={len(audio_streams)}, unknown={len(unknown_streams)}"
        ),
        f"## Video stream summary: {video_summary}",
        f"## Audio stream summary: {audio_summary}",
        f"## Unknown stream summary: {unknown_summary}",
        "## Safety boundary summary: local-only, controlled-fixture-only, implementation-contract-only; no runtime renderer is implemented.",
        f"## Blocked operations summary: {', '.join(BLOCKED_OPERATIONS)}",
        f"## Failure note: {failure_note}",
        "## Human review required note: human review is required before runtime implementation.",
        f"## Next safe phase: {NEXT_PHASE}",
    ])


def assert_sections(report: str) -> None:
    for section in SECTIONS:
        assert section in report


def assert_no_path_leakage(report: str) -> None:
    for forbidden in [
        "/tmp/cid_local_media_agent_controlled_ffprobe",
        "/home/",
        "tests/fixtures/local_media_agent/controlled_media",
        "raw private file location",
        "rodaje/private material",
        "saas_job_id",
        "db_id",
        "production ready",
    ]:
        assert forbidden not in report


def test_documentation_declares_required_contract_metadata() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        PHASE,
        "Define how a future runtime renderer implementation should behave",
        "This is only the implementation contract",
        "4993c1a60fcb9b746a69680bdfada43cfe730f8d",
        SOURCE_QA_PHASE,
        "render_controlled_ffprobe_metadata_visible_report(payload) -> str",
        "Input Payload Contract",
        "Output Report Contract",
        "Deterministic Rendering Rules",
        "Safe Failure Behavior",
        "Full Path Redaction Behavior",
        "Invalid Input Policy Behavior",
        "Null Format Behavior",
        "Empty Streams Behavior",
        "Unknown Stream Behavior",
        "Blocked Operation Flags Expectation",
        ACCEPTANCE,
        NEXT_PHASE,
    ]:
        assert required in text


def test_successful_payload_output_sections_are_safe() -> None:
    report = render_controlled_ffprobe_metadata_visible_report(successful_payload())
    assert_sections(report)
    assert "FFPROBE_METADATA_PREFLIGHT_PASS" in report
    assert "second_fixture_controlled.mov" in report
    assert "format=mov,mp4,m4a,3gp,3g2,mj2" in report
    assert "total=2, video=1, audio=1, unknown=0" in report
    assert "codec=h264" in report
    assert "codec=pcm_s16le" in report
    assert_no_path_leakage(report)


def test_safe_failure_report_behavior() -> None:
    report = render_controlled_ffprobe_metadata_visible_report(failure_payload())
    assert_sections(report)
    assert "FFPROBE_METADATA_PREFLIGHT_FAIL" in report
    assert "controlled metadata failed safely" in report
    assert "format unavailable" in report
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_path_leakage(report)


def test_invalid_input_policy_is_blocked_safely() -> None:
    payload = successful_payload()
    payload["input_policy"] = "arbitrary_path"
    payload["input_path_redacted"] = "/tmp/private/unsafe.mov"
    report = render_controlled_ffprobe_metadata_visible_report(payload)
    assert_sections(report)
    assert "arbitrary_path" in report
    assert "unsafe.mov" in report
    assert "BLOCKED_UNSAFE_CONTROLLED_METADATA_PAYLOAD" in report
    assert "blocked before metadata rendering" in report
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert_no_path_leakage(report)


def test_null_format_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["format"] = None
    report = render_controlled_ffprobe_metadata_visible_report(payload)
    assert "format unavailable" in report
    assert_no_path_leakage(report)


def test_empty_streams_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["streams"] = []
    report = render_controlled_ffprobe_metadata_visible_report(payload)
    assert "total=0, video=0, audio=0, unknown=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_path_leakage(report)


def test_unknown_stream_type_behavior() -> None:
    payload = successful_payload()
    payload["metadata"]["streams"] = [
        {"index": 3, "codec_type": "data", "codec_name": "bin_data"}
    ]
    report = render_controlled_ffprobe_metadata_visible_report(payload)
    assert "total=1, video=0, audio=0, unknown=1" in report
    assert "index=3, type=unknown, codec=bin_data" in report
    assert_no_path_leakage(report)


def test_input_path_redacted_is_filename_only() -> None:
    payload = successful_payload()
    assert "/" not in str(payload["input_path_redacted"])
    report = render_controlled_ffprobe_metadata_visible_report(payload)
    assert "second_fixture_controlled.mov" in report
    assert_no_path_leakage(report)


def test_blocked_operations_human_review_and_next_phase_are_present() -> None:
    report = render_controlled_ffprobe_metadata_visible_report(successful_payload())
    for operation in BLOCKED_OPERATIONS:
        assert operation in report
    assert "human review is required before runtime implementation" in report
    assert NEXT_PHASE in report


def test_deterministic_output_for_same_payload() -> None:
    payload = successful_payload()
    assert render_controlled_ffprobe_metadata_visible_report(payload) == render_controlled_ffprobe_metadata_visible_report(payload)


def test_no_forbidden_imports_are_present() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_imports = [
        "import " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ] + [
        "from " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ]
    for token in forbidden_imports:
        assert token not in source


def test_no_media_processor_execution_reference_is_present() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    media_processor = "ff" + "mpeg"
    for token in [
        "subprocess." + "*" + media_processor,
        media_processor + " -i",
        media_processor + " -y",
        media_processor + " -nostdin",
        f'"{media_processor}"',
        f"'{media_processor}'",
    ]:
        assert token not in source


def test_no_runtime_script_is_required_and_source_qa_gate_is_referenced() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "No runtime scripts are modified" in text
    assert "No runtime renderer is implemented" in text
    assert SOURCE_QA_DOC.exists()
    assert SOURCE_QA_TEST.exists()
    assert str(SOURCE_QA_DOC) in text
    assert str(SOURCE_QA_TEST) in text
    assert SOURCE_QA_PHASE in text


def test_acceptance_result_and_next_qa_gate_phase_are_declared() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert ACCEPTANCE in text
    assert NEXT_PHASE in text
