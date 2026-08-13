from __future__ import annotations

import io
import json

import pytest

from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    PHASE,
    TranscriptSegment,
)
from scripts.local_media_agent import cid_cli
from scripts.local_media_agent.transcript_browse import (
    DEFAULT_BROWSE_LIMIT,
    MAX_BROWSE_RESULTS,
    MAX_SEARCH_RESULTS,
    TranscriptBrowseInputError,
    browse_transcript,
    search_transcript,
)


def _segment(index: int, text: str, start: float, *, timecode: dict | None = None) -> TranscriptSegment:
    return TranscriptSegment(
        phase=PHASE,
        asset_id="synthetic-asset",
        source_audio_stream_index=0,
        segment_index=index,
        text=text,
        stt_start_seconds=start,
        stt_end_seconds=start + 1.0,
        source_start_seconds=start + 10.0,
        source_end_seconds=start + 11.0,
        source_timecode=timecode or {"available": False, "status": "unavailable"},
        provenance={"source_relative_interval": {"start_seconds": start + 10.0}},
        error=None,
        warnings=[],
    )


@pytest.fixture
def segments() -> list[TranscriptSegment]:
    return [
        _segment(0, "Hola, ¿cómo estás?", 0.0),
        _segment(1, "The editor says acción y cut.", 2.0, timecode={"available": True, "status": "available", "source_start_timecode": "00:00:12:00"}),
        _segment(2, "Café con leche", 4.0),
    ]


def test_browse_preserves_order_and_contract_fields(segments):
    results = browse_transcript(segments)
    assert [result.segment_index for result in results] == [0, 1, 2]
    assert results[0].text == segments[0].text
    assert results[0].asset_id == segments[0].asset_id
    assert results[0].segment_ref == segments[0].segment_ref
    assert results[0].source_start_seconds == segments[0].source_start_seconds
    assert results[0].source_end_seconds == segments[0].source_end_seconds
    assert results[1].source_timecode["source_start_timecode"] == "00:00:12:00"


def test_browse_offset_and_limit_are_bounded(segments):
    assert [item.segment_index for item in browse_transcript(segments, offset=1, limit=1)] == [1]
    assert len(browse_transcript(segments, limit=MAX_BROWSE_RESULTS)) == 3
    assert DEFAULT_BROWSE_LIMIT > 0


@pytest.mark.parametrize("offset", [-1, True])
def test_browse_rejects_invalid_offset(segments, offset):
    with pytest.raises(TranscriptBrowseInputError):
        browse_transcript(segments, offset=offset)


@pytest.mark.parametrize("limit", [0, -1, True, MAX_BROWSE_RESULTS + 1])
def test_browse_rejects_invalid_or_unbounded_limit(segments, limit):
    with pytest.raises(TranscriptBrowseInputError):
        browse_transcript(segments, limit=limit)


def test_unavailable_timecode_is_not_fabricated(segments):
    result = browse_transcript(segments, limit=1)[0]
    assert result.source_timecode == {"available": False, "status": "unavailable"}
    assert result.source_start_seconds == 10.0


def test_search_is_case_insensitive_and_preserves_exact_text(segments):
    result = search_transcript(segments, "ACCIÓN")
    assert [item.segment_index for item in result] == [1]
    assert result[0].text == segments[1].text


def test_search_preserves_traceability_and_deterministic_order(segments):
    first = search_transcript(segments, "a")
    second = search_transcript(segments, "a")
    assert [item.to_dict() for item in first] == [item.to_dict() for item in second]
    assert all(item.asset_id and item.segment_ref and item.source_start_seconds is not None and item.source_end_seconds is not None for item in first)


def test_search_is_bounded_and_rejects_empty_query(segments):
    assert len(search_transcript(segments, "a", limit=MAX_SEARCH_RESULTS)) <= MAX_SEARCH_RESULTS
    for query in ("", "   "):
        with pytest.raises(TranscriptBrowseInputError):
            search_transcript(segments, query)


def test_search_does_not_match_across_segment_boundary():
    items = [_segment(0, "alpha", 0.0), _segment(1, "beta", 2.0)]
    assert search_transcript(items, "alphab") == []


def test_mixed_language_and_unicode_text_remains_authoritative(segments):
    assert search_transcript(segments, "café")[0].text == "Café con leche"
    assert search_transcript(segments, "the")[0].text == segments[1].text


def test_cli_browse_and_search_use_explicit_transcript_input(tmp_path, segments):
    input_path = tmp_path / "transcript.json"
    input_path.write_text(json.dumps({"transcript_segments": [segment.to_dict() for segment in segments]}, ensure_ascii=False), encoding="utf-8")

    browse_out, browse_err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(["transcript", "browse", "--input", str(input_path), "--limit", "1"], browse_out, browse_err) == 0
    assert json.loads(browse_out.getvalue())["results"][0]["segment_index"] == 0
    assert browse_err.getvalue() == ""

    search_out, search_err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(["transcript", "search", "--input", str(input_path), "--query", "acción"], search_out, search_err) == 0
    assert json.loads(search_out.getvalue())["results"][0]["segment_index"] == 1
    assert search_err.getvalue() == ""


def test_cli_failures_are_sanitized():
    out, err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(["transcript", "search", "--input", "/missing", "--query", "x"], out, err) == 2
    assert out.getvalue() == ""
    assert err.getvalue() == "CID_CLI_ARGUMENTS_REJECTED\n"
