import importlib.util
from pathlib import Path


SCRIPT = Path("scripts/editorial_intelligence/media_probe/media_probe.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_media_probe_core", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_asset_id_passthrough_exact():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "index": 0},
            {"codec_type": "audio", "codec_name": "pcm_s16le", "index": 1, "sample_rate": "48000", "channels": 2},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0042", "/tmp/project/sample.mov", payload, size_bytes=1024)
    assert result["asset_id"] == "asset_0042"


def test_contract_identity_and_container_fields():
    module = load_module()
    payload = {
        "format": {
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "format_long_name": "QuickTime / MOV",
            "duration": "10.500",
            "start_time": "0.000",
        },
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "index": 0},
            {"codec_type": "audio", "codec_name": "aac", "index": 1, "sample_rate": "48000", "channels": 2},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0001", "/tmp/project/sample.mov", payload, size_bytes=2048)
    assert result["phase"] == module.PHASE
    assert result["container"]["format_name"] == "mov,mp4,m4a,3gp,3g2,mj2"
    assert result["container"]["format_long_name"] == "QuickTime / MOV"
    assert result["container"]["duration_seconds"] == 10.5
    assert result["container"]["start_time_seconds"] == 0.0
    assert result["container"]["size_bytes"] == 2048


def test_video_plus_audio_normal():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "codec_long_name": "H.264 / AVC",
                "width": "1920",
                "height": "1080",
                "pix_fmt": "yuv420p",
                "index": 0,
            },
            {"codec_type": "audio", "codec_name": "aac", "sample_rate": "48000", "channels": 2, "index": 1},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0002", "/tmp/project/sample.mov", payload)
    assert result["media_probe_state"] == module.STATE_PROBE_COMPLETED
    assert result["media_kind"] == module.MEDIA_KIND_VIDEO_WITH_AUDIO
    assert result["video"]["has_video"] is True
    assert result["video"]["video_stream_count"] == 1
    assert result["audio"]["has_audio"] is True
    assert result["audio"]["audio_stream_count"] == 1
    video = result["video"]["streams"][0]
    assert video["width"] == 1920
    assert video["height"] == 1080
    assert video["pix_fmt"] == "yuv420p"


def test_audio_only():
    module = load_module()
    payload = {
        "format": {"format_name": "wav"},
        "streams": [
            {"codec_type": "audio", "codec_name": "pcm_s16le", "sample_rate": "48000", "channels": 2, "index": 0},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0003", "/tmp/project/take.wav", payload)
    assert result["media_probe_state"] == module.STATE_NO_VIDEO
    assert result["media_kind"] == module.MEDIA_KIND_STANDALONE_AUDIO
    assert result["audio"]["has_audio"] is True
    assert result["video"]["has_video"] is False


def test_video_without_audio():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [
            {"codec_type": "video", "codec_name": "prores", "index": 0},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0004", "/tmp/project/sample.mov", payload)
    assert result["media_probe_state"] == module.STATE_NO_AUDIO
    assert result["media_kind"] == module.MEDIA_KIND_VIDEO_WITHOUT_AUDIO
    assert result["video"]["has_video"] is True
    assert result["audio"]["has_audio"] is False


def test_missing_timecode_is_absent():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [{"codec_type": "video", "index": 0}],
    }
    result = module.parse_ffprobe_payload("asset_0005", "/tmp/project/sample.mov", payload)
    assert result["timecode"]["TIMECODE_PRESENT"] is False
    assert result["timecode"]["embedded_timecode"] is None
    assert result["timecode"]["embedded_timecode_status"] == module.EMBEDDED_TIMECODE_ABSENT
    assert result["timecode"]["embedded_timecode_candidates"] == []


def test_present_timecode_from_format_and_stream_tags():
    module = load_module()
    payload = {
        "format": {
            "format_name": "mov",
            "tags": {"timecode": "01:00:00:00"},
        },
        "streams": [
            {"codec_type": "video", "index": 0, "tags": {"timecode": "01:00:02:00"}},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0006", "/tmp/project/sample.mov", payload)
    assert result["timecode"]["TIMECODE_PRESENT"] is True
    assert result["timecode"]["embedded_timecode"] == "01:00:02:00"
    assert result["timecode"]["embedded_timecode_source"] == "stream_tag"
    assert result["timecode"]["embedded_timecode_status"] == module.EMBEDDED_TIMECODE_PRESENT
    assert len(result["timecode"]["embedded_timecode_candidates"]) == 2


def test_format_timecode_used_when_no_stream_tag():
    module = load_module()
    payload = {
        "format": {"format_name": "mov", "tags": {"timecode": "10:00:00:00"}},
        "streams": [{"codec_type": "video", "index": 0}],
    }
    result = module.parse_ffprobe_payload("asset_0007", "/tmp/project/sample.mov", payload)
    assert result["timecode"]["TIMECODE_PRESENT"] is True
    assert result["timecode"]["embedded_timecode"] == "10:00:00:00"
    assert result["timecode"]["embedded_timecode_source"] == "format_tag"


def test_missing_creation_time_is_absent():
    module = load_module()
    payload = {"format": {"format_name": "mov"}, "streams": [{"codec_type": "video", "index": 0}]}
    result = module.parse_ffprobe_payload("asset_0008", "/tmp/project/sample.mov", payload)
    assert result["creation_time"]["creation_time_present"] is False
    assert result["creation_time"]["creation_time_raw"] is None
    assert result["creation_time"]["creation_time_source"] is None


def test_present_creation_time_kept_raw_and_normalized():
    module = load_module()
    payload = {
        "format": {
            "format_name": "mov",
            "tags": {"creation_time": "2026-07-15T10:30:00.000000Z"},
        },
        "streams": [{"codec_type": "video", "index": 0}],
    }
    result = module.parse_ffprobe_payload("asset_0009", "/tmp/project/sample.mov", payload)
    assert result["creation_time"]["creation_time_present"] is True
    assert result["creation_time"]["creation_time_raw"] == "2026-07-15T10:30:00.000000Z"
    assert result["creation_time"]["creation_time_source"] == "format_tag"
    assert result["creation_time"]["creation_time_normalized"].endswith("+00:00")


def test_multiple_audio_streams_preferred_selection():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [
            {"codec_type": "video", "index": 0},
            {"codec_type": "audio", "index": 1, "sample_rate": "44100", "channels": 2, "codec_name": "aac"},
            {"codec_type": "audio", "index": 2, "sample_rate": "48000", "channels": 2, "codec_name": "aac"},
        ],
    }
    result = module.parse_ffprobe_payload("asset_0010", "/tmp/project/sample.mov", payload)
    assert result["media_kind"] == module.MEDIA_KIND_MULTIPLE_AUDIO_STREAMS
    assert result["audio"]["multiple_audio_streams"] is True
    assert result["audio"]["audio_stream_count"] == 2
    assert result["audio"]["preferred_audio_stream_index"] == 2


def test_unsupported_media():
    module = load_module()
    payload = {"format": {}, "streams": []}
    result = module.parse_ffprobe_payload("asset_0011", "/tmp/project/weird.bin", payload)
    assert result["media_probe_state"] == module.STATE_UNSUPPORTED
    assert result["media_kind"] == module.MEDIA_KIND_UNSUPPORTED


def test_missing_container_fields_are_none():
    module = load_module()
    payload = {"format": {}, "streams": [{"codec_type": "video", "index": 0}]}
    result = module.parse_ffprobe_payload("asset_0012", "/tmp/project/sample.mov", payload)
    assert result["container"]["duration_seconds"] is None
    assert result["container"]["start_time_seconds"] is None
    assert result["container"]["format_long_name"] is None
