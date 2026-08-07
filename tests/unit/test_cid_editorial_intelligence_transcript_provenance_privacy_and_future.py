import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path("scripts/editorial_intelligence/transcript_provenance/transcript_segment.py")


def load_module():
    name = "cid_editorial_transcript_provenance_privacy"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _transcription_payload(module, anchor=0.0):
    return {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPTION.V1",
        "status": "TRANSCRIPTION_COMPLETED",
        "asset_id": "asset_0042",
        "source_audio_stream_index": 0,
        "audio_duration_seconds": 60.0,
        "segments": [
            {
                "segment_index": 0,
                "start_seconds": 0.0,
                "end_seconds": 2.5,
                "text": "Primer segmento con algo de contexto.",
                "source_start_seconds": round(anchor + 0.0, 6),
                "source_end_seconds": round(anchor + 2.5, 6),
            }
        ],
    }


def _build_segment(module, anchor=0.0):
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module, anchor=anchor)
    )
    return segments[0]


def test_public_citation_no_raw_source_path():
    module = load_module()
    segment = _build_segment(module)
    citation = module.build_editorial_citation(segment, text_excerpt="Primer segmento")
    serialized = json.dumps(citation)
    assert "/data/" not in serialized
    assert "tmp" not in serialized
    assert ".wav" not in serialized


def test_future_citation_representation():
    module = load_module()
    segment = _build_segment(module)
    citation = module.build_editorial_citation(segment, text_excerpt="Primer segmento")
    assert citation["asset_id"] == "asset_0042"
    assert citation["segment_ref"] == "asset_0042::0::0"
    assert citation["text_excerpt"] == "Primer segmento"
    assert citation["source_start_seconds"] == 0.0
    assert citation["source_end_seconds"] == 2.5
    assert citation["source_start_timecode"] is None
    assert citation["source_end_timecode"] is None


def test_serialization_deterministic():
    module = load_module()
    segment = _build_segment(module)
    first = segment.to_dict()
    second = segment.to_dict()
    assert first == second
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert list(first.keys()) == [
        "phase",
        "asset_id",
        "source_audio_stream_index",
        "segment_index",
        "text",
        "stt_start_seconds",
        "stt_end_seconds",
        "source_start_seconds",
        "source_end_seconds",
        "source_timecode",
        "provenance",
        "error",
        "warnings",
    ]


def test_future_srt_fields_sufficient():
    module = load_module()
    segment = _build_segment(module)
    assert isinstance(segment.stt_start_seconds, float)
    assert isinstance(segment.stt_end_seconds, float)
    assert isinstance(segment.source_start_seconds, float)
    assert isinstance(segment.source_end_seconds, float)
    assert segment.stt_start_seconds <= segment.stt_end_seconds


def test_future_semantic_citation_fields_sufficient():
    module = load_module()
    segment = _build_segment(module)
    assert segment.asset_id == "asset_0042"
    assert segment.segment_ref == "asset_0042::0::0"
    assert isinstance(segment.text, str)
    assert segment.source_start_seconds >= 0
    assert segment.source_end_seconds >= segment.source_start_seconds


def test_future_qa_citation_has_asset_segment_interval():
    module = load_module()
    segment = _build_segment(module, anchor=12.5)
    citation = module.build_editorial_citation(segment)
    assert citation["asset_id"] == "asset_0042"
    assert citation["segment_ref"] == "asset_0042::0::0"
    assert citation["source_start_seconds"] == 12.5
    assert citation["source_end_seconds"] == 15.0


def test_citation_excludes_internal_source_reference():
    module = load_module()
    extraction_payload = {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.AUDIO_EXTRACTION.V1",
        "asset_id": "asset_0042",
        "source_reference": {
            "internal_local_source_reference": "/data/project/private/take_a.mp4",
            "sanitized_external_source_label": "take_a.mp4",
        },
        "audio": {
            "source_audio_stream_index": 0,
            "extracted_audio_start_seconds": 0.0,
            "duration_seconds": 60.0,
        },
    }
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module),
        audio_extraction_payload=extraction_payload,
    )
    segment = segments[0]
    assert segment.provenance["internal_source_reference"] == "/data/project/private/take_a.mp4"
    citation = module.build_editorial_citation(segment, text_excerpt="Primer")
    serialized = json.dumps(citation)
    assert "private" not in serialized
    assert "/data/project" not in serialized
    assert "internal_source_reference" not in citation


def test_privacy_path_redaction_synthetic():
    module = load_module()
    fake_path = "/home/fakeuser/recordings/privacy_review/interview_a.mp4"
    extraction_payload = {
        "phase": "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.AUDIO_EXTRACTION.V1",
        "asset_id": "asset_0042",
        "source_reference": {
            "internal_local_source_reference": fake_path,
            "sanitized_external_source_label": "interview_a.mp4",
        },
        "audio": {
            "source_audio_stream_index": 0,
            "extracted_audio_start_seconds": 0.0,
            "duration_seconds": 60.0,
        },
    }
    segments = module.transcription_result_to_transcript_segments(
        _transcription_payload(module),
        audio_extraction_payload=extraction_payload,
    )
    segment = segments[0]
    assert segment.provenance["internal_source_reference"] == fake_path
    citation = module.build_editorial_citation(segment)
    serialized = json.dumps(citation)
    assert fake_path not in serialized
    assert "fakeuser" not in serialized
