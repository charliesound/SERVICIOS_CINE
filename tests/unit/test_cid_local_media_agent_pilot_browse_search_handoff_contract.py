from __future__ import annotations

import io
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


def _pilot_cli_args(operation: str = "browse") -> list[str]:
    return [
        "pilot",
        operation,
        "--input-root",
        "/authorized/root",
        "--selected-media",
        "/authorized/root/interview.MOV",
        "--asset-id",
        "pilot-asset",
        "--model-local-path",
        "/authorized/model",
    ]


def test_pilot_cli_help_is_visible():
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(["pilot", "--help"], out, err) == 0
    assert "Usage: cid pilot OPERATION" in out.getvalue()
    assert "browse" in out.getvalue()
    assert "search" in out.getvalue()
    assert "--input-root ROOT" in out.getvalue()
    assert err.getvalue() == ""

    assert run_cli(["pilot", "unsupported"], io.StringIO(), io.StringIO()) == 2
    assert run_cli(["pilot", "browse"], io.StringIO(), io.StringIO()) == 2


def test_pilot_cli_orchestrates_a_valid_pilot_request(monkeypatch, pilot_result):
    captured = []

    def fake_run(request):
        captured.append(request)
        return pilot_result

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", fake_run)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 0
    assert captured[0].input_root == "/authorized/root"
    assert captured[0].selected_media_path == "/authorized/root/interview.MOV"
    assert captured[0].asset_id == "pilot-asset"
    assert captured[0].model_local_path == "/authorized/model"
    assert json.loads(out.getvalue())["operation"] == "browse"
    assert err.getvalue() == ""


def test_pilot_failure_blocks_handoff(monkeypatch):
    failure = {
        "status": "PILOT_FLOW_TRANSCRIPTION_FAILED",
        "failed_stage": "transcription",
        "error": {"error_code": "MODEL_NOT_AVAILABLE", "message_sanitized": "MODEL_NOT_AVAILABLE"},
    }
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: failure)
    monkeypatch.setattr(
        "scripts.local_media_agent.cid_cli.handoff_pilot_transcript_segments",
        lambda *args, **kwargs: pytest.fail("failed pilot entered handoff"),
    )
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 1
    assert json.loads(out.getvalue())["status"] == "PILOT_FLOW_TRANSCRIPTION_FAILED"
    assert err.getvalue() == ""


def test_output_integrity_failure_blocks_handoff(monkeypatch):
    failure = {
        "status": "PILOT_FLOW_OUTPUT_INTEGRITY_FAILED",
        "failed_stage": "output_preflight",
        "error": {"error_code": "TRANSCRIPT_SEGMENTS_EMPTY", "message_sanitized": "TRANSCRIPT_SEGMENTS_EMPTY"},
    }
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: failure)
    monkeypatch.setattr(
        "scripts.local_media_agent.cid_cli.handoff_pilot_transcript_segments",
        lambda *args, **kwargs: pytest.fail("integrity failure entered handoff"),
    )
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 1
    assert json.loads(out.getvalue())["status"] == "PILOT_FLOW_OUTPUT_INTEGRITY_FAILED"
    assert err.getvalue() == ""


def test_validated_pilot_result_is_passed_directly_to_handoff(monkeypatch, pilot_result):
    original_handoff = __import__(
        "scripts.local_media_agent.cid_cli", fromlist=["handoff_pilot_transcript_segments"]
    ).handoff_pilot_transcript_segments
    captured = []

    def fake_handoff(value, operation, **kwargs):
        captured.append(value)
        return original_handoff(value, operation, **kwargs)

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.handoff_pilot_transcript_segments", fake_handoff)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 0
    assert captured == [pilot_result]
    assert err.getvalue() == ""


def test_pilot_cli_browse_is_user_reachable(monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args("browse") + ["--offset", "1", "--limit", "1"], out, err) == 0
    payload = json.loads(out.getvalue())
    assert payload["operation"] == "browse"
    assert [item["segment_index"] for item in payload["results"]] == [1]
    assert err.getvalue() == ""


def test_pilot_cli_search_is_user_reachable(monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args("search") + ["--query", "acción"], out, err) == 0
    payload = json.loads(out.getvalue())
    assert payload["operation"] == "search"
    assert payload["results"][0]["text"] == "The editor says acción and cut"
    assert err.getvalue() == ""


def test_pilot_cli_preserves_search_query_and_rejects_browse_query(monkeypatch, pilot_result):
    original_handoff = __import__(
        "scripts.local_media_agent.cid_cli", fromlist=["handoff_pilot_transcript_segments"]
    ).handoff_pilot_transcript_segments
    captured = []

    def fake_handoff(value, operation, **kwargs):
        captured.append(kwargs.get("query"))
        return original_handoff(value, operation, **kwargs)

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.handoff_pilot_transcript_segments", fake_handoff)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args("search") + ["--query", "  acción  "], out, err) == 0
    assert captured == ["  acción  "]
    assert run_cli(_pilot_cli_args() + ["--query", "acción"], io.StringIO(), io.StringIO()) == 2


def test_pilot_cli_preserves_search_traceability(monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args("search") + ["--query", "acción"], out, err) == 0
    result = json.loads(out.getvalue())["results"][0]
    assert result["asset_id"] == "pilot-asset"
    assert result["segment_ref"] == "pilot-asset::0::1"
    assert result["source_start_seconds"] == 12.0
    assert result["source_end_seconds"] == 13.0
    assert result["source_timecode"]["status"] == "available"
    assert result["text"] == "The editor says acción and cut"
    assert "stt_start_seconds" not in result
    assert "provenance" not in result


def test_pilot_cli_does_not_rescan(monkeypatch, pilot_result):
    calls = []

    def fake_run(request):
        calls.append("pilot")
        return pilot_result

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", fake_run)
    monkeypatch.setattr(
        "scripts.local_media_agent.cid_cli.read_only_folder_scanner_cli.run_cli",
        lambda *args, **kwargs: pytest.fail("pilot command rescanned"),
    )
    assert run_cli(_pilot_cli_args(), io.StringIO(), io.StringIO()) == 0
    assert calls == ["pilot"]


def test_pilot_cli_does_not_retranscribe(monkeypatch, pilot_result):
    calls = []

    def fake_run(request):
        calls.append(request.asset_id)
        return pilot_result

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", fake_run)
    assert run_cli(_pilot_cli_args(), io.StringIO(), io.StringIO()) == 0
    assert calls == ["pilot-asset"]


def test_pilot_cli_does_not_write_intermediate_json(tmp_path, monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    before = set(tmp_path.iterdir())

    assert run_cli(_pilot_cli_args(), io.StringIO(), io.StringIO()) == 0
    assert set(tmp_path.iterdir()) == before


def test_pilot_cli_does_not_reload_transcript(monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    monkeypatch.setattr(
        "scripts.local_media_agent.cid_cli.load_transcript_segments",
        lambda *args, **kwargs: pytest.fail("pilot command reloaded transcript"),
    )

    assert run_cli(_pilot_cli_args(), io.StringIO(), io.StringIO()) == 0


def test_pilot_cli_failure_output_is_sanitized(monkeypatch):
    failure = {
        "status": "PILOT_FLOW_SCAN_FAILED",
        "failed_stage": "scan",
        "error": {"error_code": "SCAN_ORCHESTRATION_FAILED", "message_sanitized": "SCAN_ORCHESTRATION_FAILED"},
    }
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: failure)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 1
    assert "SCAN_ORCHESTRATION_FAILED" in out.getvalue()
    assert "Traceback" not in out.getvalue()
    assert "/private/" not in out.getvalue()
    assert err.getvalue() == ""


def test_pilot_cli_does_not_expose_raw_traceback(monkeypatch):
    def failing_run(request):
        raise RuntimeError("Traceback secret /private/repository/root")

    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", failing_run)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args(), out, err) == 1
    assert out.getvalue() == ""
    assert err.getvalue() == "CID_CLI_INTERNAL_FAILURE\n"
    assert "secret" not in err.getvalue()


def test_existing_cli_commands_remain_backward_compatible(tmp_path, pilot_result):
    input_path = tmp_path / "transcript.json"
    input_path.write_text(json.dumps(pilot_result, ensure_ascii=False), encoding="utf-8")
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(["--help"], out, err) == 0
    assert "scan" in out.getvalue()
    assert "transcript" in out.getvalue()

    out, err = io.StringIO(), io.StringIO()
    assert run_cli(["transcript", "browse", "--input", str(input_path)], out, err) == 0
    assert json.loads(out.getvalue())["results"][0]["segment_index"] == 0
    assert err.getvalue() == ""


def test_gap008_reload_and_persistence_options_remain_absent(monkeypatch, pilot_result):
    monkeypatch.setattr("scripts.local_media_agent.cid_cli.pilot_flow.run_pilot_flow", lambda request: pilot_result)
    out, err = io.StringIO(), io.StringIO()

    assert run_cli(_pilot_cli_args() + ["--reload"], out, err) == 2
    assert out.getvalue() == ""
    assert err.getvalue() == "CID_CLI_ARGUMENTS_REJECTED\n"
