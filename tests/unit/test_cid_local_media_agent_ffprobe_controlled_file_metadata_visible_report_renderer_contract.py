from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_contract_v1.md"
)
SOURCE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_v1.md"
)
SOURCE_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract.py"
)
SOURCE_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate_v1.md"
)
SOURCE_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_contract_qa_gate.py"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CONTRACT.V1"
SOURCE_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1"
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CONTRACT.QA.GATE.V1"
)
ACCEPTANCE = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CONTRACT_"
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

REQUIRED_SECTIONS = [
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
]


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
        "result": "FFPROBE_METADATA_PREFLIGHT_FAIL",
        "failure_reason": "controlled metadata unavailable",
        "metadata": {"format": None, "streams": []},
        **safe_flags(),
    }


def unsafe_policy_payload() -> dict[str, object]:
    payload = successful_payload()
    payload["input_policy"] = "arbitrary_path"
    payload["input_path_redacted"] = "blocked_fixture.mov"
    return payload


def renderer_contract_report(payload: dict[str, object]) -> str:
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {"format": None, "streams": []}

    metadata_format = metadata.get("format")
    streams = metadata.get("streams")
    if not isinstance(streams, list):
        streams = []

    input_policy = str(payload.get("input_policy", "missing"))
    command_kind = str(payload.get("ffprobe_command_kind", "missing"))
    policy_allowed = input_policy == "controlled_fixture_only" and command_kind == "metadata_json"
    flags_safe = all(payload.get(flag) is False for flag in SAFE_FLAGS)
    blocked_report = not policy_allowed or not flags_safe

    if isinstance(metadata_format, dict) and not blocked_report:
        format_summary = (
            f"format={metadata_format.get('format_name', 'unknown')}; "
            f"duration={metadata_format.get('duration', 'unknown')}; "
            f"size={metadata_format.get('size', 'unknown')}"
        )
    elif blocked_report:
        format_summary = "format blocked by input policy"
    else:
        format_summary = "format unavailable"

    visible_streams = [] if blocked_report else streams
    video_streams = [stream for stream in visible_streams if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in visible_streams if stream.get("codec_type") == "audio"]

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

    safe_filename = Path(str(payload.get("input_path_redacted", "unavailable"))).name
    blocked = ", ".join(BLOCKED_OPERATIONS)
    result = "BLOCKED_UNSAFE_INPUT_POLICY" if blocked_report else str(payload.get("result", "unknown"))
    failure_note = str(payload.get("failure_reason", "not applicable"))

    return "\n".join([
        "# Report title: CID controlled metadata visible report renderer contract",
        f"## Phase: {PHASE}",
        f"## Input policy: {input_policy}",
        f"## Redacted input filename: {safe_filename}",
        f"## Preflight result: {result}",
        f"## Format summary: {format_summary}",
        f"## Stream summary: total={len(visible_streams)}, video={len(video_streams)}, audio={len(audio_streams)}",
        f"## Video stream summary: {video_summary}",
        f"## Audio stream summary: {audio_summary}",
        "## Safety boundary summary: local-only, controlled-fixture-only, renderer-contract-only; no runtime renderer is implemented.",
        f"## Blocked operations summary: {blocked}",
        f"## Failure note: {failure_note}",
        "## Human review required note: human review is required before any implementation phase.",
        f"## Next safe phase: {NEXT_PHASE}",
    ])


def assert_required_sections(report: str) -> None:
    for section in REQUIRED_SECTIONS:
        assert section in report


def assert_no_full_paths_or_private_details(report: str) -> None:
    for forbidden in [
        "/tmp/cid_local_media_agent_controlled_ffprobe",
        "/home/",
        "tests/fixtures/local_media_agent/controlled_media",
        "raw private file location",
        "real rodaje/private material details",
        "scanner output:",
        "audio extraction output:",
        "sync output:",
        "transcription output:",
        "subtitle output:",
        "timeline output:",
        "saas_job_id",
        "db_id",
        "production ready",
    ]:
        assert forbidden not in report


def test_documentation_declares_renderer_contract_scope() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        PHASE,
        "renderer contract only",
        "No runtime renderer is implemented",
        "real media",
        "scanner execution",
        "arbitrary folders",
        "ffmpeg media processing",
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
        ACCEPTANCE,
        NEXT_PHASE,
    ]:
        assert required in text


def test_documentation_declares_input_contract_and_output_sections() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [
        "already-safe controlled metadata payloads",
        "`input_policy` equal to `controlled_fixture_only`",
        "`input_path_redacted` as filename only",
        "`ffprobe_command_kind` equal to `metadata_json`",
        "`metadata.format` as null or object",
        "`metadata.streams` as a list",
        "all safety flags remaining false",
        "Payloads with `input_policy` not equal to `controlled_fixture_only`",
        *REQUIRED_SECTIONS,
    ]:
        assert required in text


def test_successful_payload_report_sections_are_rendered_safely() -> None:
    report = renderer_contract_report(successful_payload())
    assert_required_sections(report)
    assert "FFPROBE_METADATA_PREFLIGHT_PASS" in report
    assert "second_fixture_controlled.mov" in report
    assert "format=mov,mp4,m4a,3gp,3g2,mj2" in report
    assert "total=2, video=1, audio=1" in report
    assert "codec=h264" in report
    assert "size=1920x1080" in report
    assert "codec=pcm_s16le" in report
    assert "sample_rate=48000" in report
    assert_no_full_paths_or_private_details(report)


def test_failure_payload_report_sections_are_rendered_safely() -> None:
    report = renderer_contract_report(failure_payload())
    assert_required_sections(report)
    assert "FFPROBE_METADATA_PREFLIGHT_FAIL" in report
    assert "failed_fixture.mov" in report
    assert "controlled metadata unavailable" in report
    assert "format unavailable" in report
    assert "total=0, video=0, audio=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_full_paths_or_private_details(report)


def test_null_format_and_empty_streams_are_handled_safely() -> None:
    payload = successful_payload()
    payload["metadata"] = {"format": None, "streams": []}
    report = renderer_contract_report(payload)
    assert "format unavailable" in report
    assert "total=0, video=0, audio=0" in report
    assert "no video streams reported" in report
    assert "no audio streams reported" in report
    assert_no_full_paths_or_private_details(report)


def test_unsafe_input_policy_is_blocked_without_path_leakage() -> None:
    report = renderer_contract_report(unsafe_policy_payload())
    assert_required_sections(report)
    assert "arbitrary_path" in report
    assert "BLOCKED_UNSAFE_INPUT_POLICY" in report
    assert "blocked_fixture.mov" in report
    assert "format blocked by input policy" in report
    assert "total=0, video=0, audio=0" in report
    assert_no_full_paths_or_private_details(report)


def test_blocked_operations_human_review_and_next_phase_are_rendered() -> None:
    report = renderer_contract_report(successful_payload())
    for blocked in BLOCKED_OPERATIONS:
        assert blocked in report
    assert "human review is required before any implementation phase" in report
    assert NEXT_PHASE in report


def test_source_visible_report_contract_is_referenced() -> None:
    text = DOC.read_text(encoding="utf-8")
    for path in [SOURCE_DOC, SOURCE_TEST, SOURCE_QA_DOC, SOURCE_QA_TEST]:
        assert path.exists(), path
        assert str(path) in text
    assert SOURCE_PHASE in text


def test_acceptance_result_and_next_phase_are_declared() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert ACCEPTANCE in text
    assert NEXT_PHASE in text


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
