import importlib.util
import sys
from pathlib import Path

SCRIPT = Path("scripts/editorial_intelligence/transcript_provenance/transcript_segment.py")


def load_module():
    name = "cid_editorial_transcript_provenance_core"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _segment(index, start, end, text, anchor):
    return {
        "segment_index": index,
        "start_seconds": start,
        "end_seconds": end,
        "text": text,
        "source_start_seconds": round(anchor + start, 6),
        "source_end_seconds": round(anchor + end, 6),
    }


def _transcription_payload(
    module,
    asset_id="asset_0042",
    stream_index=0,
    anchor=0.0,
    duration=60.0,
    segments=None,
):
    if segments is None:
        segments = [_segment(0, 0.0, 2.5, "Primer segmento.", anchor)]
    return {
        "phase": module.PHASE.replace("TRANSCRIPT_SEGMENT", "TRANSCRIPTION"),
        "status": "TRANSCRIPTION_COMPLETED",
        "asset_id": asset_id,
        "source_audio_stream_index": stream_index,
        "detected_language": "es",
        "language_probability": 0.95,
        "audio_duration_seconds": duration,
        "timeout_seconds": None,
        "error": None,
        "warnings": [],
        "segments": segments,
    }


def _extraction_payload(module, anchor, asset_id="asset_0042", duration=60.0):
    return {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.AUDIO_EXTRACTION.V1",
        "asset_id": asset_id,
        "source_reference": {
            "internal_local_source_reference": "/data/project/take_a.mp4",
            "sanitized_external_source_label": "take_a.mp4",
        },
        "audio": {
            "source_audio_stream_index": 0,
            "extracted_audio_start_seconds": anchor,
            "source_stream_start_seconds": anchor,
            "duration_seconds": duration,
            "channels_derived_from_source": 1,
        },
        "warnings": [],
    }


def test_basic_segment_from_transcription():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module)
    )
    assert len(segments) == 1
    assert segments[0].to_dict()["phase"] == module.PHASE


def test_asset_id_passthrough_exact():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module, asset_id="asset_999")
    )
    assert segments[0].asset_id == "asset_999"


def test_source_stream_passthrough():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module, stream_index=3)
    )
    assert segments[0].source_audio_stream_index == 3


def test_stt_relative_times_preserved():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module)
    )
    segment = segments[0]
    assert segment.stt_start_seconds == 0.0
    assert segment.stt_end_seconds == 2.5


def test_extraction_anchor_zero_mapping():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module, anchor=0.0)
    )
    segment = segments[0]
    assert segment.source_start_seconds == segment.stt_start_seconds
    assert segment.source_end_seconds == segment.stt_end_seconds
    assert segment.provenance["extraction_anchor_seconds"] == 0.0


def test_nonzero_extraction_anchor_mapping():
    module = load_module()
    payload = _transcription_payload(module, anchor=12.5)
    extraction = _extraction_payload(module, anchor=12.5)
    segments = module.transcription_result_to_transcript_segments(
        payload,
        audio_extraction_payload=extraction,
    )
    segment = segments[0]
    assert segment.stt_start_seconds == 0.0
    assert segment.source_start_seconds == 12.5
    assert segment.source_end_seconds == 15.0
    assert segment.provenance["extraction_anchor_seconds"] == 12.5


def test_segment_monotonicity_enforced():
    module = load_module()
    segments_raw = [
        _segment(0, 0.0, 1.0, "A", 0.0),
        _segment(1, 2.0, 3.0, "B", 0.0),
        _segment(2, 1.5, 3.0, "C", 0.0),
    ]
    try:
        module.transcription_result_to_transcript_segments(
            _transcription_payload(module, segments=segments_raw)
        )
    except module.TranscriptSegmentError as exc:
        assert exc.error_code == module.ERROR_CODE_SEGMENTS_NOT_MONOTONIC
        return
    raise AssertionError("monotonicity violation not rejected")


def test_invalid_segment_rejected():
    module = load_module()
    segments_raw = [
        {
            "segment_index": 0,
            "start_seconds": -1.0,
            "end_seconds": 2.0,
            "text": "bad",
        }
    ]
    try:
        module.transcription_result_to_transcript_segments(
            _transcription_payload(module, segments=segments_raw)
        )
    except module.TranscriptSegmentError as exc:
        assert exc.error_code == module.ERROR_CODE_INVALID_SEGMENT
        return
    raise AssertionError("invalid segment not rejected")


def test_internal_provenance_preserved():
    module = load_module()
    extraction = _extraction_payload(module, anchor=0.0)
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module),
        audio_extraction_payload=extraction,
    )
    provenance = segments[0].provenance
    assert provenance["internal_source_reference"] == "/data/project/take_a.mp4"
    assert provenance["source_reference_sanitized"] == "take_a.mp4"
    assert provenance["asset_id"] == "asset_0042"
    assert provenance["segment_index"] == 0
    assert provenance["stt_relative_interval"] == {
        "start_seconds": 0.0,
        "end_seconds": 2.5,
    }
    assert provenance["source_relative_interval"] == {
        "start_seconds": 0.0,
        "end_seconds": 2.5,
    }
    assert provenance["source_timecode_interval"] is None


def test_audio_only_no_timecode_valid():
    module = load_module()
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module)
    )
    segment = segments[0]
    assert segment.source_timecode["available"] is False
    assert segment.source_timecode["status"] == module.SOURCE_TIMECODE_STATUS_UNAVAILABLE
    assert segment.to_dict()["error"] is None


def test_source_relative_offset_not_applied_twice():
    module = load_module()
    payload = _transcription_payload(module, anchor=12.5)
    extraction = _extraction_payload(module, anchor=12.5)
    segments = module.transcription_result_to_transcript_segments(
        payload,
        audio_extraction_payload=extraction,
    )
    segment = segments[0]
    assert segment.source_start_seconds == 12.5
    assert segment.source_end_seconds == 15.0
    assert segment.source_start_seconds != 25.0
    assert segment.provenance["extraction_anchor_seconds"] == 12.5


def test_container_start_time_not_applied_as_second_offset():
    module = load_module()
    payload = _transcription_payload(module, anchor=12.5)
    extraction = _extraction_payload(module, anchor=12.5)
    media_probe = {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.REAL_MEDIA_METADATA_PROBE.V1",
        "asset_id": "asset_0042",
        "container": {"start_time_seconds": 100.0},
        "source_reference": {
            "internal_local_source_reference": "/data/project/take_a.mp4",
            "sanitized_external_source_label": "take_a.mp4",
        },
    }
    segments = module.transcription_result_to_transcript_segments(
        payload,
        audio_extraction_payload=extraction,
        media_probe_payload=media_probe,
    )
    segment = segments[0]
    assert segment.source_start_seconds == 12.5
    assert segment.source_end_seconds == 15.0
    assert segment.source_start_seconds != 112.5
