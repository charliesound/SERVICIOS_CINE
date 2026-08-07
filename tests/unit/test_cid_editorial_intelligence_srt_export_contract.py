from __future__ import annotations

from decimal import Decimal

import pytest

from scripts.editorial_intelligence.srt_export import (
    SRT_COMPLETED,
    SrtExportError,
    render_srt,
)
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


def make_segment(index, start, end, *, asset="asset", stream=0, text="Text", stt_start=None):
    return TranscriptSegment(
        phase="CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1",
        asset_id=asset,
        source_audio_stream_index=stream,
        segment_index=index,
        text=text,
        stt_start_seconds=start if stt_start is None else stt_start,
        stt_end_seconds=end,
        source_start_seconds=start,
        source_end_seconds=end,
        source_timecode={"available": False},
        provenance={},
        error=None,
        warnings=[],
    )


def test_basic_source_timeline_and_sequential_numbering():
    result = render_srt([make_segment(17, 1.25, 2.75)])
    assert result.status == SRT_COMPLETED
    assert result.cue_count == 1
    assert result.srt_text == "1\n00:00:01,250 --> 00:00:02,750\nText\n"


def test_source_vs_stt_timeline_regression():
    segment = make_segment(1, 601.25, 602.75, stt_start=1.25)
    result = render_srt([segment])
    assert "00:10:01,250 --> 00:10:02,750" in result.srt_text
    assert "00:00:01,250 --> 00:00:02,750" not in result.srt_text


def test_source_relative_fields_are_primary_not_stt_fields():
    segment = make_segment(1, 601.25, 602.75, stt_start=1.25)
    assert render_srt([segment]).srt_text.startswith("1\n00:10:01,250")


def test_decimal_rounding_and_timestamp_examples():
    assert "00:00:00,000 --> 00:00:00,001" in render_srt([make_segment(1, 0, 0)]).srt_text
    assert "00:00:01,234 --> 00:00:01,235" in render_srt([make_segment(1, 1.234, 1.2341)]).srt_text
    assert "00:01:01,005 --> 01:00:00,000" in render_srt([make_segment(1, 61.005, 3600)]).srt_text
    assert Decimal("1.005") == Decimal(str(1.005))


def test_long_hours_do_not_wrap():
    assert "100:00:00,000" in render_srt([make_segment(1, 360000, 360001)]).srt_text


def test_gap_and_overlap_are_preserved():
    result = render_srt([make_segment(0, 0, 1), make_segment(1, 2, 3), make_segment(2, 2.5, 4)])
    assert result.cue_count == 3
    assert "00:00:02,000 --> 00:00:03,000" in result.srt_text
    assert "00:00:02,500 --> 00:00:04,000" in result.srt_text


def test_multiline_unicode_and_arrow_text_are_preserved():
    text = "Primera línea\nSegunda línea ñ → -->"
    result = render_srt([make_segment(1, 0, 1, text=text)])
    assert text in result.srt_text


def test_empty_text_skips_with_warning():
    result = render_srt([make_segment(1, 0, 1, text="   ")])
    assert result.cue_count == 0
    assert result.srt_text == ""
    assert result.warnings


def test_invalid_time_ranges_nan_inf_and_controls_rejected():
    with pytest.raises(SrtExportError):
        render_srt([make_segment(1, -1, 1)])
    with pytest.raises(SrtExportError):
        render_srt([make_segment(1, 2, 1)])
    with pytest.raises(SrtExportError):
        render_srt([make_segment(1, float("nan"), 1)])
    with pytest.raises(SrtExportError):
        render_srt([make_segment(1, 0, 1, text="bad\x00text")])


def test_mixed_assets_and_streams_rejected():
    with pytest.raises(SrtExportError) as asset_error:
        render_srt([make_segment(0, 0, 1), make_segment(1, 1, 2, asset="other")])
    assert asset_error.value.error_code == "SRT_MIXED_ASSET_INPUT"
    with pytest.raises(SrtExportError):
        render_srt([make_segment(0, 0, 1), make_segment(1, 1, 2, stream=1)])


def test_nonmonotonic_input_is_not_silently_reordered():
    with pytest.raises(SrtExportError):
        render_srt([make_segment(0, 2, 3), make_segment(1, 1, 2)])


def test_deterministic_output_and_external_provenance_boundary():
    segments = [make_segment(4, 0, 1, text="A")]
    first = render_srt(segments)
    second = render_srt(segments)
    assert first == second
    assert "asset" not in first.srt_text
    assert "segment_ref" not in first.srt_text
