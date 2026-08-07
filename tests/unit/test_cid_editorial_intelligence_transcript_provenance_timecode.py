import importlib.util
import sys
from pathlib import Path

SCRIPT = Path("scripts/editorial_intelligence/transcript_provenance/transcript_segment.py")


def load_module():
    name = "cid_editorial_transcript_provenance_timecode"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _probe_with_timecode(value, status="present", present=True):
    return {
        "TIMECODE_PRESENT": present,
        "embedded_timecode": value,
        "embedded_timecode_status": status,
        "embedded_timecode_source": "stream_tag" if present else None,
        "embedded_timecode_candidates": (
            [{"source": "stream_tag", "key": "timecode", "value": value, "stream_index": 0}]
            if present
            else []
        ),
    }


def _transcription_payload(module):
    return {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPTION.V1",
        "status": "TRANSCRIPTION_COMPLETED",
        "asset_id": "asset_0042",
        "source_audio_stream_index": 0,
        "audio_duration_seconds": 60.0,
        "segments": [
            {
                "segment_index": 0,
                "start_seconds": 0.0,
                "end_seconds": 2.5,
                "text": "Primer segmento.",
                "source_start_seconds": 0.0,
                "source_end_seconds": 2.5,
            }
        ],
    }


def test_25_fps_non_drop_timecode_parse():
    module = load_module()
    assert module.parse_ndf_timecode("01:02:03:04") == (1, 2, 3, 4)
    assert module.timecode_to_frames("01:00:00:00", 25, 1) == 90000
    assert module.format_ndf_timecode(90000, 25, 1) == "01:00:00:00"


def test_24_fps_non_drop_timecode_parse():
    module = load_module()
    assert module.parse_ndf_timecode("00:00:01:00") == (0, 0, 1, 0)
    assert module.timecode_to_frames("00:00:01:00", 24, 1) == 24
    assert module.format_ndf_timecode(24, 24, 1) == "00:00:01:00"


def test_30000_over_1001_exact_rational_case():
    module = load_module()
    nominal = module.nominal_frames_per_second(30000, 1001)
    assert nominal == 30
    assert module.timecode_to_frames("01:00:00:00", 30000, 1001) == 108000
    assert module.format_ndf_timecode(108000, 30000, 1001) == "01:00:00:00"


def test_embedded_timecode_absent():
    module = load_module()
    probe = _probe_with_timecode(None, status="absent", present=False)
    status = module.build_source_timecode(probe)
    assert status["available"] is False
    assert status["status"] == module.SOURCE_TIMECODE_STATUS_ABSENT


def test_malformed_embedded_timecode():
    module = load_module()
    probe = _probe_with_timecode("not-a-timecode", status="present", present=True)
    status = module.build_source_timecode(probe)
    assert status["available"] is False
    assert status["status"] == module.SOURCE_TIMECODE_STATUS_UNSUPPORTED
    assert status["source_start_timecode"] is None
    assert status["source_end_timecode"] is None


def test_missing_fps_degrades():
    module = load_module()
    media_probe = {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.REAL_MEDIA_METADATA_PROBE.V1",
        "asset_id": "asset_0042",
        "video": {"has_video": True, "video_stream_count": 1, "streams": []},
        "audio": {"has_audio": True, "audio_stream_count": 1, "streams": []},
        "timecode": _probe_with_timecode("01:00:00:00", status="present", present=True),
    }
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module),
        media_probe_payload=media_probe,
    )
    segment = segments[0]
    assert segment.source_timecode["status"] == module.SOURCE_TIMECODE_STATUS_UNSUPPORTED
    assert segment.source_timecode["source_start_timecode"] is None
    assert segment.source_timecode["source_fps"] is None


def test_rational_fps_exactness_numerator_denominator():
    module = load_module()
    start = module.seconds_to_start_frame(100.0, 30000, 1001)
    assert start == 2997
    end = module.seconds_to_end_frame(100.0, 30000, 1001)
    assert end == 2998


def test_start_frame_rounding_floor():
    module = load_module()
    assert module.seconds_to_start_frame(2.5, 25, 1) == 62
    assert module.SEGMENT_START_FRAME_ROUNDING_POLICY == "floor"


def test_end_frame_rounding_ceil():
    module = load_module()
    assert module.seconds_to_end_frame(2.5, 25, 1) == 63
    assert module.SEGMENT_END_FRAME_ROUNDING_POLICY == "ceil"


def test_semicolon_drop_frame_candidate_unsupported():
    module = load_module()
    assert module.classify_timecode_format("00:00:00;00") == module.TIMECODE_FORMAT_DROP_FRAME_CANDIDATE
    probe = _probe_with_timecode("00:00:00;00", status="present", present=True)
    status = module.build_source_timecode(probe)
    assert status["status"] == module.SOURCE_TIMECODE_STATUS_UNSUPPORTED
    assert status["source_start_timecode"] is None
    assert "drop-frame" in status["reason"]


def test_no_fabricated_smpte_from_ambiguous_probe():
    module = load_module()
    media_probe = {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.REAL_MEDIA_METADATA_PROBE.V1",
        "asset_id": "asset_0042",
        "video": {
            "has_video": True,
            "video_stream_count": 1,
            "streams": [
                {
                    "stream_index": 0,
                    "avg_frame_rate": {"original": "30000/1001", "numerator": 30000, "denominator": 1001},
                    "r_frame_rate": {"original": "30000/1001", "numerator": 30000, "denominator": 1001},
                }
            ],
        },
        "audio": {"has_audio": True, "audio_stream_count": 1, "streams": []},
        "timecode": _probe_with_timecode("01:00:00:00", status="present", present=True),
    }
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module),
        media_probe_payload=media_probe,
    )
    segment = segments[0]
    assert segment.source_timecode["source_start_timecode"] is None
    assert segment.source_timecode["source_end_timecode"] is None
    assert segment.source_timecode["available"] is False
    assert segment.source_start_seconds == 0.0
    assert segment.source_end_seconds == 2.5


def test_rational_30000_over_1001_regression():
    module = load_module()
    exact_start = module.seconds_to_start_frame(100.0, 30000, 1001)
    int_approx_start = 100 * int(29.97)
    assert exact_start == 2997
    assert exact_start != int_approx_start
    exact_discriminator = module.seconds_to_start_frame(367.0, 30000, 1001)
    float_approx_discriminator = int(367.0 * 29.97)
    assert exact_discriminator == 10999
    assert exact_discriminator != float_approx_discriminator


def test_ndf_timecode_roundtrip_explicit_safe_input():
    module = load_module()
    assert module.parse_ndf_timecode("00:00:00:00") == (0, 0, 0, 0)
    derived = module.derive_ndf_timecode("01:00:00:00", 25, 25, 1)
    assert derived == "01:00:01:00"
