import importlib.util
import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_second_fixture_scenario_v1.md"
)
PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1"


def load_module():
    spec = importlib.util.spec_from_file_location("ffprobe_controlled_preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def completed(stdout: str, returncode: int = 0):
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def second_fixture_payload():
    return {
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
    }


def test_second_controlled_tmp_fixture_scenario_preserves_metadata():
    module = load_module()
    input_path = "/tmp/cid_local_media_agent_controlled_ffprobe/second_fixture_controlled.mov"
    payload = second_fixture_payload()

    with patch.object(module.subprocess, "run", return_value=completed(json.dumps(payload))) as run:
        result = module.run_preflight(input_path)

    assert result["phase"] == PHASE
    assert result["result"] == "FFPROBE_METADATA_PREFLIGHT_PASS"
    assert result["metadata"]["format"] == payload["format"]
    assert result["metadata"]["streams"] == payload["streams"]
    assert result["ffprobe_command_kind"] == "metadata_json"
    assert result["input_path_redacted"] == "second_fixture_controlled.mov"

    command = run.call_args.args[0]
    assert command == [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(Path(input_path).resolve(strict=False)),
    ]


def test_second_repo_controlled_fixture_path_is_accepted_and_redacted():
    module = load_module()
    input_path = "tests/fixtures/local_media_agent/controlled_media/second_fixture_controlled.mov"
    payload = second_fixture_payload()

    with patch.object(module.subprocess, "run", return_value=completed(json.dumps(payload))):
        result = module.run_preflight(input_path)

    serialized = json.dumps(result)
    assert result["input_path_redacted"] == "second_fixture_controlled.mov"
    assert "tests/fixtures/local_media_agent/controlled_media" not in serialized
    assert str(Path(input_path).resolve(strict=False)) not in serialized


def test_video_and_audio_stream_requirements_are_represented():
    payload = second_fixture_payload()
    streams = payload["streams"]
    video = next(stream for stream in streams if stream["codec_type"] == "video")
    audio = next(stream for stream in streams if stream["codec_type"] == "audio")

    assert video["codec_name"] == "h264"
    assert video["width"] == 1920
    assert video["height"] == 1080
    assert video["duration"] == "12.500000"
    assert audio["codec_name"] in {"pcm_s16le", "aac"}
    assert audio["sample_rate"] == "48000"
    assert audio["channels"] == 2
    assert audio["duration"] == "12.500000"


def test_all_blocked_flags_remain_false_in_second_scenario():
    module = load_module()
    input_path = "/tmp/cid_local_media_agent_controlled_ffprobe/second_fixture_controlled.mov"

    with patch.object(module.subprocess, "run", return_value=completed(json.dumps(second_fixture_payload()))):
        result = module.run_preflight(input_path)

    for key in [
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
    ]:
        assert result[key] is False


def test_uncontrolled_paths_are_still_rejected():
    module = load_module()
    assert not module.is_controlled_fixture_path("/tmp/uncontrolled/second_fixture_controlled.mov")
    try:
        module.build_ffprobe_command("/tmp/uncontrolled/second_fixture_controlled.mov")
    except ValueError as exc:
        assert "controlled fixture" in str(exc)
    else:
        raise AssertionError("uncontrolled path was accepted")


def test_missing_controlled_fixture_flag_is_still_rejected():
    module = load_module()
    parser = module.build_parser()
    try:
        parser.parse_args([
            "--input",
            "/tmp/cid_local_media_agent_controlled_ffprobe/second_fixture_controlled.mov",
            "--json",
        ])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("missing --controlled-fixture was accepted")


def test_no_forbidden_imports_or_ffmpeg_execution_pattern_is_present():
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden_imports = [
        "import " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ] + [
        "from " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ]
    for token in forbidden_imports:
        assert token not in source

    media_processor = "ff" + "mpeg"
    for token in [
        f'"{media_processor}"',
        f"'{media_processor}'",
        media_processor + " -i",
        media_processor + " -y",
        media_processor + " -nostdin",
    ]:
        assert token not in source


def test_second_scenario_documentation_declares_boundaries_and_next_phase():
    text = DOC.read_text(encoding="utf-8")
    for term in [
        "only a second controlled fixture scenario",
        "real media",
        "scanner execution",
        "arbitrary folders",
        "`ffmpeg` media processing",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "SaaS upload",
        "database write",
        "installer behavior",
        "client-facing use",
        "public demo",
        "sales demo",
        "production use",
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_SECOND_FIXTURE_SCENARIO_PASS_READY_FOR_QA_GATE",
        "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.SECOND.FIXTURE.SCENARIO.QA.GATE.V1",
    ]:
        assert term in text
