from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_v1.md"
)
RUNTIME_SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py")

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.V1"
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.CONTRACT.QA.GATE.V1"
)
ACCEPTANCE = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_CONTRACT_"
    "PASS_READY_FOR_QA_GATE"
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
    "real rodaje material",
    "real media files",
    "scanner execution",
    "ffmpeg processing",
    "audio extraction",
    "sync generation",
    "transcription generation",
    "subtitle generation",
    "timeline export",
    "SaaS upload",
    "database write",
    "installer creation",
    "client-facing use",
    "public demo",
    "sales demo",
    "production use",
]


def safe_flags() -> dict[str, bool]:
    return {flag: False for flag in SAFE_FLAGS}


def successful_payload() -> dict[str, object]:
    return {
        "phase": "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1",
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
        "phase": "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1",
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": "failed_fixture.mov",
        "ffprobe_command_kind": "metadata_json",
        "result": "FFPROBE_METADATA_PREFLIGHT_FAIL",
        "failure_reason": "controlled metadata command failed",
        "metadata": {"format": None, "streams": []},
        **safe_flags(),
    }


def render_visible_report(payload: dict[str, object]) -> str:
    metadata = payload.get("metadata")
    assert isinstance(metadata, dict)
    metadata_format = metadata.get("format")
    streams = metadata.get("streams")

    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["ffprobe_command_kind"] == "metadata_json"
    assert isinstance(streams, list)
    for flag in SAFE_FLAGS:
        assert payload[flag] is False

    if isinstance(metadata_format, dict):
        format_summary = (
            f"format={metadata_format.get('format_name', 'unknown')}; "
            f"duration={metadata_format.get('duration', 'unknown')}; "
            f"size={metadata_format.get('size', 'unknown')}"
        )
    else:
        format_summary = "format unavailable; duration unavailable; size unavailable"

    video_streams = [stream for stream in streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]

    video_summary = "; ".join(
        f"index={stream.get('index')}, codec={stream.get('codec_name')}, "
        f"size={stream.get('width')}x{stream.get('height')}, "
        f"duration={stream.get('duration')}"
        for stream in video_streams
    ) or "no video streams reported"
    audio_summary = "; ".join(
        f"index={stream.get('index')}, codec={stream.get('codec_name')}, "
        f"sample_rate={stream.get('sample_rate')}, channels={stream.get('channels')}, "
        f"duration={stream.get('duration')}"
        for stream in audio_streams
    ) or "no audio streams reported"

    blocked = ", ".join(BLOCKED_OPERATIONS)
    failure_reason = payload.get("failure_reason", "not applicable")

    return "\n".join([
        "# Report title: CID controlled metadata visible report",
        f"## Phase: {PHASE}",
        f"## Input policy: {payload['input_policy']}",
        f"## Redacted input filename: {payload['input_path_redacted']}",
        f"## Preflight result: {payload['result']}",
        f"## Format summary: {format_summary}",
        f"## Stream summary: total={len(streams)}, video={len(video_streams)}, audio={len(audio_streams)}",
        f"## Video stream summary: {video_summary}",
        f"## Audio stream summary: {audio_summary}",
        "## Safety boundary summary: local-only, controlled-fixture-only, documentation/test-only; no runtime rendering is implemented.",
        f"## Blocked operations summary: {blocked}",
        f"## Failure note: {failure_reason}",
        "## Human review required note: human review is required before any implementation phase.",
        f"## Next safe phase: {NEXT_PHASE}",
    ])


def assert_required_sections(report: str) -> None:
    for section in [
        "Report title",
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
    ]:
        assert section in report


def assert_no_forbidden_visible_content(report: str) -> None:
    for forbidden in [
        "/tmp/cid_local_media_agent_controlled_ffprobe",
        "/home/",
        "tests/fixtures/local_media_agent/controlled_media",
        "raw private file location",
        "scanner output:",
        "audio extraction output:",
        "sync output:",
        "transcription output:",
        "subtitle output:",
        "timeline output:",
        "saas_job_id",
        "db_id",
    ]:
        assert forbidden not in report


def test_documentation_declares_visible_report_contract_scope() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        PHASE,
        "only a visible report contract",
        "does not implement runtime rendering yet",
        "does not authorize real media",
        "scanner execution",
        "ffmpeg processing",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "SaaS/DB",
        "installer",
        "client-facing",
        "public demo",
        "sales demo",
        "production use",
        ACCEPTANCE,
        NEXT_PHASE,
    ]:
        assert required in text


def test_documentation_declares_required_report_sections() -> None:
    text = DOC.read_text(encoding="utf-8")
    for section in [
        "Report title",
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
    ]:
        assert section in text


def test_success_payload_renders_format_and_stream_summaries_safely() -> None:
    report = render_visible_report(successful_payload())
    assert_required_sections(report)
    assert "second_fixture_controlled.mov" in report
    assert "FFPROBE_METADATA_PREFLIGHT_PASS" in report
    assert "format=mov,mp4,m4a,3gp,3g2,mj2" in report
    assert "duration=12.500000" in report
    assert "total=2, video=1, audio=1" in report
    assert "codec=h264" in report
    assert "size=1920x1080" in report
    assert "codec=pcm_s16le" in report
    assert "sample_rate=48000" in report
    assert_no_forbidden_visible_content(report)


def test_failure_payload_renders_safe_useful_report() -> None:
    report = render_visible_report(failure_payload())
    assert_required_sections(report)
    assert "failed_fixture.mov" in report
    assert "FFPROBE_METADATA_PREFLIGHT_FAIL" in report
    assert "controlled metadata command failed" in report
    assert "format unavailable" in report
    assert "total=0, video=0, audio=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_forbidden_visible_content(report)


def test_report_includes_blocked_operations_and_human_review_note() -> None:
    report = render_visible_report(successful_payload())
    for blocked in BLOCKED_OPERATIONS:
        assert blocked in report
    assert "human review is required before any implementation phase" in report


def test_contract_requires_expected_input_policy_and_safety_shape() -> None:
    payload = successful_payload()
    assert payload["input_path_redacted"] == "second_fixture_controlled.mov"
    assert "/" not in str(payload["input_path_redacted"])
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["ffprobe_command_kind"] == "metadata_json"
    metadata = payload["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["format"] is None or isinstance(metadata["format"], dict)
    assert isinstance(metadata["streams"], list)
    for flag in SAFE_FLAGS:
        assert payload[flag] is False


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
        "subprocess." + ".*" + media_processor,
        media_processor + " -i",
        media_processor + " -y",
        media_processor + " -nostdin",
        f'"{media_processor}"',
        f"'{media_processor}'",
    ]:
        assert token not in source


def test_runtime_script_is_outside_visible_report_contract_scope() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert RUNTIME_SCRIPT.exists()
    assert "does not modify runtime scripts" in text
    assert "runtime rendering" in text
