from __future__ import annotations

import hashlib
import json

import pytest

from scripts.editorial_intelligence.srt_export import SrtExportError, render_srt
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


def segment(index=1, asset="asset", stream=0, text="text", start=601.25, end=602.75):
    return TranscriptSegment(
        phase="CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1",
        asset_id=asset,
        source_audio_stream_index=stream,
        segment_index=index,
        text=text,
        stt_start_seconds=1.25,
        stt_end_seconds=2.75,
        source_start_seconds=start,
        source_end_seconds=end,
        source_timecode={"available": False},
        provenance={"internal_source_reference": "/home/private/example.wav"},
        error=None,
        warnings=[],
    )


def test_source_vs_stt_regression_exact_output():
    result = render_srt([segment()])
    assert result.srt_text == "1\n00:10:01,250 --> 00:10:02,750\ntext\n"
    assert "00:00:01,250" not in result.srt_text


def test_raw_paths_and_internal_provenance_are_not_embedded():
    result = render_srt([segment(text="private interview text")])
    assert "/home/private/example.wav" not in result.srt_text
    assert "internal_source_reference" not in result.srt_text
    assert "asset" not in result.srt_text


def test_same_input_same_bytes_and_sha256():
    values = [segment(text="Árbol\nniño")]
    first = render_srt(values).srt_text.encode("utf-8")
    second = render_srt(values).srt_text.encode("utf-8")
    assert first == second
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_mixed_asset_error_is_structured_and_sanitized():
    with pytest.raises(SrtExportError) as error:
        render_srt([segment(asset="a"), segment(index=2, asset="b")])
    assert error.value.error_code == "SRT_MIXED_ASSET_INPUT"
    assert "/home" not in error.value.message_sanitized


def test_multi_stream_error_is_structured():
    with pytest.raises(SrtExportError) as error:
        render_srt([segment(stream=0), segment(index=2, stream=1)])
    assert error.value.error_code == "SRT_INVALID_INPUT"


def test_future_provenance_remains_external_and_text_is_not_rewritten():
    text = "Puntuación: ¿Qué? Ñandú -->"
    result = render_srt([segment(text=text)])
    assert text in result.srt_text
    assert "segment_ref" not in result.srt_text
    assert "source_timecode" not in result.srt_text


def test_result_shape_is_minimal_and_serializable():
    result = render_srt([segment()])
    payload = {
        "status": result.status,
        "asset_id": result.asset_id,
        "cue_count": result.cue_count,
        "srt_text": result.srt_text,
        "warnings": list(result.warnings),
        "error": result.error,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert "SRT_COMPLETED" in encoded
    assert payload["cue_count"] == 1


def test_no_smpte_fps_or_timecode_dependency_in_output():
    output = render_srt([segment()]).srt_text
    assert "fps" not in output.lower()
    assert ";" not in output
    assert "source_timecode" not in output
