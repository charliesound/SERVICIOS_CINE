import importlib.util
from pathlib import Path


SCRIPT = Path("scripts/editorial_intelligence/media_probe/media_probe.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_media_probe_fps", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_float_only_allowed_is_false():
    module = load_module()
    assert module.FLOAT_ONLY_ALLOWED is False


def test_fps_25_1_rational():
    module = load_module()
    rational = module.parse_rational("25/1")
    assert rational["original"] == "25/1"
    assert rational["numerator"] == 25
    assert rational["denominator"] == 1
    assert module.effective_fps_from_rational(rational) == 25.0


def test_fps_30000_over_1001_ntsc_not_rounded():
    module = load_module()
    rational = module.parse_rational("30000/1001")
    assert rational["original"] == "30000/1001"
    assert rational["numerator"] == 30000
    assert rational["denominator"] == 1001
    assert rational["numerator"] != 30
    assert rational["denominator"] != 1
    effective = module.effective_fps_from_rational(rational)
    assert effective is not None
    assert abs(effective - 29.97) < 0.01


def test_fps_24000_over_1001_rational():
    module = load_module()
    rational = module.parse_rational("24000/1001")
    assert rational["original"] == "24000/1001"
    assert rational["numerator"] == 24000
    assert rational["denominator"] == 1001


def test_fps_zero_over_zero_invalid_without_exception():
    module = load_module()
    rational = module.parse_rational("0/0")
    assert rational["numerator"] == 0
    assert rational["denominator"] == 0
    assert module.effective_fps_from_rational(rational) is None


def test_fps_na_invalid_without_exception():
    module = load_module()
    rational = module.parse_rational("N/A")
    assert rational["original"] == "N/A"
    assert rational["numerator"] is None
    assert rational["denominator"] is None


def test_fps_empty_and_missing_without_exception():
    module = load_module()
    assert module.parse_rational("") is None
    assert module.parse_rational(None) is None
    assert module.parse_rational(0) == {"original": "0", "numerator": 0, "denominator": 1}


def test_rational_fields_present_in_video_stream():
    module = load_module()
    payload = {
        "format": {"format_name": "mov"},
        "streams": [
            {
                "codec_type": "video",
                "index": 0,
                "avg_frame_rate": "30000/1001",
                "r_frame_rate": "30000/1001",
                "time_base": "1/1001",
                "start_pts": "0",
                "start_time": "0.000000",
            },
        ],
    }
    result = module.parse_ffprobe_payload("asset_0101", "/tmp/project/sample.mov", payload)
    video = result["video"]["streams"][0]
    assert video["avg_frame_rate"]["original"] == "30000/1001"
    assert video["avg_frame_rate"]["numerator"] == 30000
    assert video["avg_frame_rate"]["denominator"] == 1001
    assert video["r_frame_rate"]["original"] == "30000/1001"
    assert video["time_base"] == "1/1001"
    assert video["start_pts"] == 0
    assert video["start_time"] == 0.0
