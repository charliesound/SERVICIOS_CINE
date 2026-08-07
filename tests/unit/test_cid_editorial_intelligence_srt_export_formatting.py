from __future__ import annotations

from decimal import Decimal

import pytest

from scripts.editorial_intelligence.srt_export import SrtExportError, render_srt
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


def segment(index, start, end, text="x"):
    return TranscriptSegment(
        phase="CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1",
        asset_id="asset",
        source_audio_stream_index=0,
        segment_index=index,
        text=text,
        stt_start_seconds=0.0,
        stt_end_seconds=1.0,
        source_start_seconds=start,
        source_end_seconds=end,
        source_timecode={"available": False},
        provenance={},
        error=None,
        warnings=[],
    )


def test_floor_start_and_ceil_end_with_binary_sensitive_decimal():
    result = render_srt([segment(1, 1.2341, 1.2341)])
    assert "00:00:01,234 --> 00:00:01,235" in result.srt_text


def test_minimum_duration_warning_is_deterministic():
    result = render_srt([segment(1, 5, 5)])
    assert "00:00:05,000 --> 00:00:05,001" in result.srt_text
    assert result.warnings == ("segment 1: minimum cue duration applied",)


def test_zero_one_hour_and_long_hour_formatting():
    result = render_srt([segment(0, 0, 0), segment(1, 3600, 3600), segment(2, 360000, 360000)])
    assert "00:00:00,000 --> 00:00:00,001" in result.srt_text
    assert "01:00:00,000 --> 01:00:00,001" in result.srt_text
    assert "100:00:00,000 --> 100:00:00,001" in result.srt_text


def test_crlf_and_cr_normalize_to_lf():
    result = render_srt([segment(1, 0, 1, text="a\r\nb\rc")])
    assert "a\nb\nc" in result.srt_text
    assert "\r" not in result.srt_text


def test_unicode_utf8_and_no_bom():
    output = render_srt([segment(1, 0, 1, text="Árbol, niño, 東京")]).srt_text
    encoded = output.encode("utf-8")
    assert encoded.startswith(b"1\n")
    assert b"\xc3\x81rbol" in encoded


def test_final_newline_and_standard_block():
    output = render_srt([segment(1, 0, 1)]).srt_text
    assert output.endswith("\n")
    assert output.splitlines() == ["1", "00:00:00,000 --> 00:00:01,000", "x"]


def test_nonfinite_decimal_inputs_rejected():
    for value in (float("inf"), float("-inf"), float("nan")):
        with pytest.raises(SrtExportError):
            render_srt([segment(1, value, 1)])


def test_empty_collection_is_valid_deterministic_result():
    result = render_srt([])
    assert result.status == "SRT_COMPLETED"
    assert result.cue_count == 0
    assert result.srt_text == ""
    assert result.asset_id is None


def test_decimal_oracle_policy_is_not_binary_round():
    assert Decimal(str(1.2341)) * 1000 == Decimal("1234.1")
    assert "00:00:01,234 --> 00:00:01,235" in render_srt([segment(1, 1.2341, 1.2341)]).srt_text
