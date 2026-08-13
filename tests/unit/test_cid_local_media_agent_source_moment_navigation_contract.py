from __future__ import annotations

import io
import json

import pytest

from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    PHASE,
    TranscriptSegment,
)
from scripts.local_media_agent import cid_cli
from scripts.local_media_agent.source_moment_navigation import (
    build_source_moment_navigation,
)
from scripts.local_media_agent.transcript_browse import (
    MAX_BROWSE_RESULTS,
    MAX_SEARCH_RESULTS,
    browse_transcript,
    search_transcript,
)


def _segment(
    index: int,
    text: str,
    start: float,
    *,
    timecode: dict | None = None,
) -> TranscriptSegment:
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
        provenance={},
        error=None,
        warnings=[],
    )


@pytest.fixture
def segments() -> list[TranscriptSegment]:
    return [
        _segment(0, "Hola, ¿cómo estás?", 0.0),
        _segment(
            1,
            "The editor says acción y cut.",
            2.0,
            timecode={
                "available": True,
                "status": "available",
                "source_start_timecode": "00:00:12:00",
                "source_end_timecode": "00:00:13:00",
                "source_fps": {"numerator": 24, "denominator": 1},
            },
        ),
        _segment(2, "Café con leche", 4.0),
        _segment(
            3,
            "Unsupported frame marker",
            6.0,
            timecode={"available": False, "status": "unsupported"},
        ),
        _segment(
            4,
            "Absent frame marker",
            8.0,
            timecode={"available": False, "status": "absent"},
        ),
    ]


def test_source_moment_preserves_identity_timing_and_available_timecode(segments):
    result = browse_transcript(segments)[1]
    source_moment = build_source_moment_navigation(result)

    assert source_moment["asset_id"] == result.asset_id
    assert source_moment["segment_ref"] == result.segment_ref
    assert source_moment["segment_index"] == result.segment_index
    assert source_moment["source_start_seconds"] == result.source_start_seconds
    assert source_moment["source_end_seconds"] == result.source_end_seconds
    assert source_moment["source_timecode_status"] == "available"
    assert source_moment["source_start_timecode"] == "00:00:12:00"
    assert source_moment["source_end_timecode"] == "00:00:13:00"
    assert source_moment["source_fps"] == {"numerator": 24, "denominator": 1}


@pytest.mark.parametrize("status", ["unavailable", "absent", "unsupported"])
def test_source_moment_preserves_distinct_unavailable_statuses(status):
    result = browse_transcript(
        [_segment(0, "status", 0.0, timecode={"available": False, "status": status})]
    )[0]
    source_moment = build_source_moment_navigation(result)

    assert source_moment["source_timecode_status"] == status
    assert "source_start_timecode" not in source_moment
    assert "source_end_timecode" not in source_moment
    assert "source_fps" not in source_moment


def test_source_moment_descriptor_is_deterministic_and_path_free(segments):
    result = browse_transcript(segments)[0]
    first = build_source_moment_navigation(result)
    second = build_source_moment_navigation(result)

    assert first == second
    assert "/" not in first["navigation_descriptor"]
    assert "\\" not in first["navigation_descriptor"]
    assert "open" not in first["navigation_descriptor"].lower()
    assert "http" not in first["navigation_descriptor"].lower()


def test_cli_browse_and_search_attach_source_moment_without_rewriting_text(
    tmp_path, segments
):
    input_path = tmp_path / "transcript.json"
    input_path.write_text(
        json.dumps(
            {"transcript_segments": [segment.to_dict() for segment in segments]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    browse_out, browse_err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(
        ["transcript", "browse", "--input", str(input_path), "--limit", "2"],
        browse_out,
        browse_err,
    ) == 0
    browse_payload = json.loads(browse_out.getvalue())
    assert browse_err.getvalue() == ""
    assert [item["segment_index"] for item in browse_payload["results"]] == [0, 1]
    assert browse_payload["results"][0]["text"] == segments[0].text
    assert browse_payload["results"][0]["source_moment"]["segment_ref"] == segments[0].segment_ref

    search_out, search_err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(
        ["transcript", "search", "--input", str(input_path), "--query", "acción"],
        search_out,
        search_err,
    ) == 0
    search_payload = json.loads(search_out.getvalue())
    assert search_err.getvalue() == ""
    assert search_payload["results"][0]["text"] == segments[1].text
    assert search_payload["results"][0]["source_moment"]["source_timecode_status"] == "available"


def test_existing_browse_search_order_and_bounds_remain_unchanged(segments):
    assert [item.segment_index for item in browse_transcript(segments)] == [0, 1, 2, 3, 4]
    assert [item.segment_index for item in search_transcript(segments, "a")] == [0, 1, 2, 3, 4]
    assert len(browse_transcript(segments, limit=MAX_BROWSE_RESULTS)) == 5
    assert len(search_transcript(segments, "a", limit=MAX_SEARCH_RESULTS)) == 5


def test_language_neutral_text_is_unchanged(segments):
    assert search_transcript(segments, "café")[0].text == "Café con leche"
    assert search_transcript(segments, "the")[0].text == segments[1].text
    assert search_transcript(segments, "acción")[0].text == segments[1].text


def test_cli_invalid_input_remains_sanitized():
    out, err = io.StringIO(), io.StringIO()
    assert cid_cli.run_cli(
        ["transcript", "search", "--input", "/missing", "--query", "x"], out, err
    ) == 2
    assert out.getvalue() == ""
    assert err.getvalue() == "CID_CLI_ARGUMENTS_REJECTED\n"
