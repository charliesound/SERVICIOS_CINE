from __future__ import annotations

import math

import pytest

from scripts.local_media_agent.ffprobe_metadata_extraction import _parse_ffprobe


def test_format_raw_duration_is_preferred_and_preserved() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "12.345678"},
            "streams": [{"codec_type": "video", "duration": "99.125"}],
        }
    )

    assert result["duration_raw"] == "12.345678"
    assert result["duration_origin"] == "format"
    assert result["duration_seconds"] == 12.346


@pytest.mark.parametrize("invalid", [None, "", "0", "-1", "nan", "inf"])
def test_first_video_stream_duration_fallback_requires_finite_positive(
    invalid: str | None,
) -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": invalid},
            "streams": [
                {"codec_type": "video", "duration": "20.000001"},
                {"codec_type": "video", "duration": "30.5"},
            ],
        }
    )

    assert result["duration_raw"] == "20.000001"
    assert result["duration_origin"] == "video_stream"
    if invalid in (None, ""):
        assert result["duration_seconds"] is None
    elif invalid == "nan":
        assert math.isnan(result["duration_seconds"])
    else:
        assert result["duration_seconds"] == float(invalid)


def test_invalid_format_and_first_video_duration_yield_no_duration() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "nan"},
            "streams": [
                {"codec_type": "video", "duration": "0"},
                {"codec_type": "video", "duration": "30"},
            ],
        }
    )

    assert result["duration_raw"] is None
    assert result["duration_origin"] is None
    assert math.isnan(result["duration_seconds"])


def test_video_stream_emits_exact_sar_dar_and_rotation() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1920",
                    "height": "1080",
                    "sample_aspect_ratio": "4:3",
                    "display_aspect_ratio": "16:9",
                    "tags": {"rotate": "90"},
                }
            ],
        }
    )

    assert result["video"]["sample_aspect_ratio"] == {"numerator": 4, "denominator": 3}
    assert result["video"]["display_aspect_ratio"] == {"numerator": 16, "denominator": 9}
    assert result["video"]["rotation"] == 90


def test_absent_rationals_are_null_and_not_invented() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "sample_aspect_ratio": "0:1",
                    "display_aspect_ratio": "N/A",
                }
            ],
        }
    )

    assert result["video"]["sample_aspect_ratio"] is None
    assert result["video"]["display_aspect_ratio"] is None


def test_rotation_normalized_and_prefers_explicit_metadata() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1080",
                    "height": "1920",
                    "tags": {"rotate": "270"},
                }
            ],
        }
    )

    assert result["video"]["rotation"] == 270


def test_no_rotation_inferred_from_width_height() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1080",
                    "height": "1920",
                }
            ],
        }
    )

    assert result["video"]["rotation"] is None
