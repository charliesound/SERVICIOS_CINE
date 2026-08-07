import builtins
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPT = Path("scripts/editorial_intelligence/transcription/transcription.py")


def load_module():
    name = "cid_editorial_transcription_error"
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


def _no_faster_whisper_import(monkeypatch, module):
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "faster_whisper" or name.startswith("faster_whisper."):
            raise ImportError("faster-whisper not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    return module


def test_engine_not_available_state(tmp_path, monkeypatch):
    module = load_module()
    _no_faster_whisper_import(monkeypatch, module)
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    backend = module.FasterWhisperTranscriptionBackend(str(model_dir), device="cpu")
    result = module.transcribe(_request(module), backend)
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_ENGINE_NOT_AVAILABLE
    assert payload["error"]["error_code"] == module.ERROR_CODE_ENGINE_NOT_AVAILABLE


def test_model_not_available_state(tmp_path):
    module = load_module()
    backend = module.FasterWhisperTranscriptionBackend(str(tmp_path / "missing_model"))
    result = module.transcribe(_request(module), backend)
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_MODEL_NOT_AVAILABLE
    assert payload["error"]["error_code"] == module.ERROR_CODE_MODEL_NOT_AVAILABLE


def test_backend_failure_state():
    module = load_module()

    class FailingBackend(module.TranscriptionBackend):
        @property
        def engine_name(self):
            return "failing"

        def transcribe(self, wav_path, *, language_hint=None):
            raise module.TranscriptionBackendError("backend_error", "backend failed")

    result = module.transcribe(_request(module), FailingBackend())
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_FAILED
    assert payload["error"]["error_code"] == "backend_error"


def test_unexpected_backend_exception_sanitized():
    module = load_module()

    class ExplodingBackend(module.TranscriptionBackend):
        @property
        def engine_name(self):
            return "exploding"

        def transcribe(self, wav_path, *, language_hint=None):
            raise RuntimeError("secret raw detail must not leak")

    result = module.transcribe(_request(module), ExplodingBackend())
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_FAILED
    assert payload["error"]["message_sanitized"] == "backend failed unexpectedly"
    assert "secret raw detail" not in json.dumps(payload)


def test_invalid_audio_input_state():
    module = load_module()
    result = module.transcribe(
        _request(module, temporary_audio_path=""),
        module.FakeTranscriptionBackend(),
    )
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_INVALID_AUDIO_INPUT
    assert payload["error"]["error_code"] == module.ERROR_CODE_INVALID_AUDIO_INPUT


def test_no_raw_audio_path_leak():
    module = load_module()
    raw_path = "/tmp/project/take_audio.wav"
    result = module.transcribe(
        _request(module, temporary_audio_path=raw_path),
        module.FakeTranscriptionBackend(segments=[_segment(0, 0.0, 1.0, "A")]),
    )
    serialized = json.dumps(result.to_dict())
    assert raw_path not in serialized


def test_no_network_imports_in_module():
    module = load_module()
    source = Path(module.__file__).read_text(encoding="utf-8")
    for token in ("import socket", "import urllib", "import requests", "import httpx", "http.client"):
        assert token not in source, token


def test_no_model_auto_download_in_module():
    module = load_module()
    source = Path(module.__file__).read_text(encoding="utf-8")
    for token in ("snapshot_download", "hf_hub", "download_from_hub", "from_pretrained"):
        assert token not in source, token


def test_audio_wav_consumed_while_file_exists(tmp_path):
    module = load_module()
    wav = tmp_path / "derivative.wav"
    wav.write_bytes(b"RIFF-fake")
    captured = {}

    class CaptureBackend(module.TranscriptionBackend):
        @property
        def engine_name(self):
            return "capture"

        def transcribe(self, wav_path, *, language_hint=None):
            captured["wav_path"] = str(wav_path)
            return {
                "detected_language": None,
                "language_probability": None,
                "segments": iter([]),
            }

    request = _request(module, temporary_audio_path=str(wav))
    result = module.transcribe(request, CaptureBackend())
    assert captured["wav_path"] == str(wav)
    assert wav.exists()
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_COMPLETED


def test_no_diarization_or_speaker_inference():
    module = load_module()
    source = Path(module.__file__).read_text(encoding="utf-8")
    for token in ("pyannote", "speaker", "diarization"):
        assert token not in source, token
    result = module.transcribe(
        _request(module),
        module.FakeTranscriptionBackend(segments=[_segment(0, 0.0, 1.0, "A")]),
    )
    assert "speaker" not in json.dumps(result.to_dict())


def test_negative_segment_index_rejected():
    module = load_module()
    segments = [_segment(-1, 0.0, 1.0, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_negative_start_rejected():
    module = load_module()
    segments = [_segment(0, -0.5, 1.0, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_end_before_start_rejected():
    module = load_module()
    segments = [_segment(0, 3.0, 1.0, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_non_string_text_rejected():
    module = load_module()
    segments = [_segment(0, 0.0, 1.0, 12345)]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_segment_exceeding_duration_tolerance_rejected():
    module = load_module()
    segments = [_segment(0, 0.0, 63.5, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_segment_within_duration_tolerance_accepted():
    module = load_module()
    segments = [_segment(0, 0.0, 62.0, "A")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_COMPLETED


def test_non_ascending_index_order_rejected():
    module = load_module()
    segments = [_segment(1, 0.0, 1.0, "A"), _segment(0, 1.0, 2.0, "B")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED


def test_non_monotonic_timestamps_rejected():
    module = load_module()
    segments = [_segment(0, 3.0, 4.0, "A"), _segment(1, 1.0, 2.0, "B")]
    result = module.transcribe(_request(module), module.FakeTranscriptionBackend(segments=segments))
    assert result.to_dict()["status"] == module.STATE_TRANSCRIPTION_FAILED
