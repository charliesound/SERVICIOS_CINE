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
