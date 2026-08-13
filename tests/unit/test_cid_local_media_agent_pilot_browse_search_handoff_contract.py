from __future__ import annotations

import json

import pytest

from scripts.local_media_agent.cid_cli import run_pilot_transcript_cli, run_cli
from scripts.local_media_agent.pilot_browse_search_handoff import (
    handoff_pilot_transcript_segments,
)
from scripts.editorial_intelligence.transcript_provenance.transcript_segment import PHASE
from scripts.local_media_agent.transcript_browse import (
    MAX_BROWSE_RESULTS,
    MAX_SEARCH_RESULTS,
    TranscriptBrowseInputError,
)


def _segment(index: int, text: str, start: float, status: str = "unavailable") -> dict:
    return {
        "phase": PHASE,
        "asset_id": "pilot-asset",
        "source_audio_stream_index": 0,
        "segment_index": index,
        "text": text,
        "stt_start_seconds": start,
        "stt_end_seconds": start + 1.0,
        "source_start_seconds": start + 10.0,
        "source_end_seconds": start + 11.0,
        "source_timecode": {"available": status == "available", "status": status, **(
            {"source_start_timecode": "00:00:12:00"} if status == "available" else {}
        )},
        "provenance": {},
        "error": None,
        "warnings": [],
    }


@pytest.fixture
def pilot_result() -> dict:
    return {"status": "PILOT_FLOW_COMPLETED", "transcript_segments": [
        _segment(0, "Hola, ¿cómo estás?", 0.0),
        _segment(1, "The editor says acción and cut", 2.0, "available"),
        _segment(2, "Café con leche", 4.0),
    ]}


def test_mapping_and_equivalent_list_are_accepted(pilot_result):
    mapping = handoff_pilot_transcript_segments(pilot_result, "browse")
    listed = handoff_pilot_transcript_segments(pilot_result["transcript_segments"], "browse")
    assert [item.segment_index for item in mapping] == [0, 1, 2]
    assert [item.to_dict() for item in mapping] == [item.to_dict() for item in listed]


def test_in_memory_browse_and_search_preserve_source_moment(pilot_result):
    browse = run_pilot_transcript_cli(pilot_result, "browse")
    search = run_pilot_transcript_cli(pilot_result, "search", query="acción")
    assert browse["results"][0]["source_moment"]["segment_ref"] == "pilot-asset::0::0"
    assert search["results"][0]["source_moment"]["source_start_timecode"] == "00:00:12:00"
    assert search["results"][0]["text"] == "The editor says acción and cut"


def test_handoff_preserves_traceability_timing_and_status(pilot_result):
    result = handoff_pilot_transcript_segments(pilot_result, "browse")[1]
    assert result.asset_id == "pilot-asset"
    assert result.segment_ref == "pilot-asset::0::1"
    assert result.segment_index == 1
    assert result.source_start_seconds == 12.0
    assert result.source_end_seconds == 13.0
    assert result.source_timecode["status"] == "available"


def test_handoff_is_deterministic_and_preserves_matching_and_bounds(pilot_result):
    first = run_pilot_transcript_cli(pilot_result, "search", query="a")
    second = run_pilot_transcript_cli(pilot_result, "search", query="a")
    assert first == second
    assert [item["segment_index"] for item in first["results"]] == [0, 1, 2]
    assert first["result_limit_maximum"] == MAX_SEARCH_RESULTS
    assert run_pilot_transcript_cli(pilot_result, "browse", limit=MAX_BROWSE_RESULTS)["result_limit_maximum"] == MAX_BROWSE_RESULTS


def test_explicit_json_cli_path_remains_supported(tmp_path, pilot_result):
    path = tmp_path / "transcript.json"
    path.write_text(json.dumps(pilot_result, ensure_ascii=False), encoding="utf-8")
    out = __import__("io").StringIO()
    err = __import__("io").StringIO()
    assert run_cli(["transcript", "browse", "--input", str(path)], out, err) == 0
    assert json.loads(out.getvalue())["results"][0]["segment_index"] == 0
    assert err.getvalue() == ""

    out = __import__("io").StringIO()
    err = __import__("io").StringIO()
    assert run_cli(
        ["transcript", "search", "--input", str(path), "--query", "acción"],
        out,
        err,
    ) == 0
    assert json.loads(out.getvalue())["results"][0]["segment_index"] == 1
    assert err.getvalue() == ""


@pytest.mark.parametrize("value", [None, {"transcript_segments": "bad"}, {"transcript_segments": [{}]}])
def test_invalid_handoff_input_is_sanitized(value):
    with pytest.raises(TranscriptBrowseInputError):
        run_pilot_transcript_cli(value, "browse")


def test_language_neutral_fixtures_remain_authoritative(pilot_result):
    result = handoff_pilot_transcript_segments(pilot_result, "search", query="café")[0]
    assert result.text == "Café con leche"
    assert handoff_pilot_transcript_segments(pilot_result, "search", query="the")[0].text.startswith("The")


def test_handoff_does_not_write_an_intermediate_file(tmp_path, pilot_result):
    before = set(tmp_path.iterdir())
    run_pilot_transcript_cli(pilot_result, "browse")
    assert set(tmp_path.iterdir()) == before


def test_existing_source_moment_descriptor_is_reused(pilot_result):
    result = run_pilot_transcript_cli(pilot_result, "browse")["results"][1]
    assert result["source_moment"]["navigation_descriptor"] == (
        "asset_id=pilot-asset; segment_ref=pilot-asset::0::1; "
        "interval=12.0-13.0s; timecode_status=available"
    )
