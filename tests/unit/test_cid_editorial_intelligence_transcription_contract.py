import importlib.util
import sys
from pathlib import Path

SCRIPT = Path("scripts/editorial_intelligence/transcription/transcription.py")


def load_module():
    name = "cid_editorial_transcription_core"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _segment(index, start, end, text):
    return {
        "segment_index": index,
        "start_seconds": start,
        "end_seconds": end,
        "text": text,
    }


def _request(module, **overrides):
    params = {
        "asset_id": "asset_0042",
        "temporary_audio_path": "/tmp/project/take_audio.wav",
        "source_audio_stream_index": 1,
        "extracted_audio_start_seconds": 0.0,
        "audio_duration_seconds": 60.0,
        "language_hint": "es",
    }
    params.update(overrides)
    return module.TranscriptionRequest(**params)


def test_successful_transcription_completed_with_segments():
    module = load_module()
    segments = [_segment(0, 0.0, 2.5, "Primer segmento."), _segment(1, 2.5, 5.0, "Segundo segmento.")]
    backend = module.FakeTranscriptionBackend(
        segments=segments, detected_language="es", language_probability=0.95
    )
    result = module.transcribe(_request(module), backend)
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_COMPLETED
    assert len(result.segments) == 2
    assert result.segments[0]["text"] == "Primer segmento."
    assert result.segments[1]["text"] == "Segundo segmento."


def test_asset_id_passthrough_exact():
    module = load_module()
    request = _request(module, asset_id="asset_999")
    result = module.transcribe(request, module.FakeTranscriptionBackend())
    assert result.to_dict()["asset_id"] == "asset_999"


def test_source_stream_provenance_preserved():
    module = load_module()
    request = _request(module, source_audio_stream_index=3)
    result = module.transcribe(request, module.FakeTranscriptionBackend())
    assert result.to_dict()["source_audio_stream_index"] == 3


def test_two_segments_with_timestamps():
    module = load_module()
    segments = [_segment(0, 1.0, 2.0, "Hola."), _segment(1, 2.5, 4.25, "Mundo.")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert len(result.segments) == 2
    assert result.segments[0]["start_seconds"] == 1.0
    assert result.segments[1]["end_seconds"] == 4.25


def test_timestamps_monotonic():
    module = load_module()
    segments = [
        _segment(0, 0.0, 1.5, "A"),
        _segment(1, 1.5, 3.0, "B"),
        _segment(2, 3.0, 4.0, "C"),
    ]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    starts = [segment["start_seconds"] for segment in result.segments]
    assert starts == sorted(starts)
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_COMPLETED


def test_language_detection_result():
    module = load_module()
    backend = module.FakeTranscriptionBackend(detected_language="fr", language_probability=0.88)
    result = module.transcribe(_request(module), backend)
    payload = result.to_dict()
    assert payload["detected_language"] == "fr"
    assert payload["language_probability"] == 0.88


def test_language_hint_respected():
    module = load_module()
    received = {}

    class RecordingBackend(module.TranscriptionBackend):
        @property
        def engine_name(self):
            return "recording"

        def transcribe(self, wav_path, *, language_hint=None):
            received["language_hint"] = language_hint
            return {
                "detected_language": None,
                "language_probability": None,
                "segments": iter([]),
            }

    request = _request(module, language_hint="pt")
    result = module.transcribe(request, RecordingBackend())
    assert received["language_hint"] == "pt"
    assert result.to_dict()["detected_language"] == "pt"


def test_empty_transcript_completed():
    module = load_module()
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=[]))
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_COMPLETED
    assert result.segments == []


def test_timestamps_preserved_as_float_seconds():
    module = load_module()
    segments = [_segment(0, 0.5, 2.75, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    segment = result.segments[0]
    assert isinstance(segment["start_seconds"], float)
    assert isinstance(segment["end_seconds"], float)


def test_source_timestamp_mapping_formula():
    module = load_module()
    request = _request(module, extracted_audio_start_seconds=12.5)
    segments = [_segment(0, 1.0, 3.0, "A")]
    result = module.transcribe(request, module.FakeTranscriptionBackend(segments=segments))
    segment = result.segments[0]
    assert segment["source_start_seconds"] == 13.5
    assert segment["source_end_seconds"] == 15.5
    assert segment["start_seconds"] == 1.0
    assert segment["end_seconds"] == 3.0


def test_long_generator_consumed_safely():
    module = load_module()

    class GeneratorBackend(module.TranscriptionBackend):
        @property
        def engine_name(self):
            return "generator"

        def transcribe(self, wav_path, *, language_hint=None):
            def _generate():
                for index in range(10000):
                    yield _segment(index, float(index), float(index) + 1.0, "x")
            return {
                "detected_language": None,
                "language_probability": None,
                "segments": _generate(),
            }

    result = module.transcribe(
        _request(module, audio_duration_seconds=None),
        GeneratorBackend(),
    )
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_COMPLETED
    assert len(result.segments) == 10000
    starts = [segment["start_seconds"] for segment in result.segments]
    assert starts == sorted(starts)
