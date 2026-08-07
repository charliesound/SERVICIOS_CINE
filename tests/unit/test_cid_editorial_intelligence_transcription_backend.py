import builtins
import importlib.util
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path("scripts/editorial_intelligence/transcription/transcription.py")


def load_module():
    name = "cid_editorial_transcription_backend"
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


def test_module_import_does_not_load_faster_whisper(monkeypatch):
    monkeypatch.delitem(sys.modules, "faster_whisper", raising=False)
    load_module()
    assert "faster_whisper" not in sys.modules


def test_backend_abstraction_not_instantiable():
    module = load_module()
    with pytest.raises(TypeError):
        module.TranscriptionBackend()


def test_fake_backend_contract():
    module = load_module()
    segments = [_segment(0, 0.0, 1.0, "A"), _segment(1, 1.0, 2.0, "B")]
    backend = module.FakeTranscriptionBackend(
        segments=segments, detected_language="es", language_probability=0.95
    )
    assert backend.engine_name == "fake"
    output = backend.transcribe("/tmp/x.wav", language_hint="es")
    assert output["detected_language"] == "es"
    assert output["language_probability"] == 0.95
    assert list(output["segments"]) == segments


def test_engine_name_and_sanitized_identifier():
    module = load_module()
    assert (
        module.FasterWhisperTranscriptionBackend("/local/models/whisper-small").engine_name
        == module.TRANSCRIPTION_ENGINE
    )
    assert (
        module.FasterWhisperTranscriptionBackend("/local/models/whisper-small")
        .model_identifier_sanitized
        == "whisper-small"
    )
    assert module.FasterWhisperTranscriptionBackend("").model_identifier_sanitized is None


def test_model_reference_remote_name_rejected():
    module = load_module()
    for name in ("tiny", "small", "large-v3", "turbo"):
        backend = module.FasterWhisperTranscriptionBackend(name)
        with pytest.raises(module.TranscriptionBackendError) as excinfo:
            backend.transcribe("/tmp/x.wav")
        assert excinfo.value.error_code == module.ERROR_CODE_MODEL_NOT_AVAILABLE


def test_model_reference_bare_name_rejected():
    module = load_module()
    backend = module.FasterWhisperTranscriptionBackend("whisper_model")
    with pytest.raises(module.TranscriptionBackendError) as excinfo:
        backend.transcribe("/tmp/x.wav")
    assert excinfo.value.error_code == module.ERROR_CODE_MODEL_NOT_AVAILABLE


def test_model_reference_empty_rejected():
    module = load_module()
    backend = module.FasterWhisperTranscriptionBackend("")
    with pytest.raises(module.TranscriptionBackendError) as excinfo:
        backend.transcribe("/tmp/x.wav")
    assert excinfo.value.error_code == module.ERROR_CODE_MODEL_NOT_AVAILABLE


def test_model_reference_missing_dir_rejected(tmp_path):
    module = load_module()
    backend = module.FasterWhisperTranscriptionBackend(str(tmp_path / "does_not_exist"))
    with pytest.raises(module.TranscriptionBackendError) as excinfo:
        backend.transcribe("/tmp/x.wav")
    assert excinfo.value.error_code == module.ERROR_CODE_MODEL_NOT_AVAILABLE


def test_model_reference_valid_dir_accepted(tmp_path):
    module = load_module()
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    backend = module.FasterWhisperTranscriptionBackend(str(model_dir))
    backend._validate_local_model_reference()


def test_compute_type_defaults_and_override():
    module = load_module()
    assert (
        module.FasterWhisperTranscriptionBackend("x", device="cpu").compute_type
        == module.CPU_COMPUTE_TYPE
    )
    assert (
        module.FasterWhisperTranscriptionBackend("x", device="cuda").compute_type
        == module.CUDA_COMPUTE_TYPE
    )
    assert (
        module.FasterWhisperTranscriptionBackend("x", device="cuda", compute_type="int8").compute_type
        == "int8"
    )


def test_faster_whisper_lazy_import_error(tmp_path, monkeypatch):
    module = load_module()
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    real_import = builtins.__import__

    def _blocked(name, *args, **kwargs):
        if name == "faster_whisper" or name.startswith("faster_whisper."):
            raise ImportError("faster-whisper not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _blocked)
    backend = module.FasterWhisperTranscriptionBackend(str(model_dir))
    with pytest.raises(module.TranscriptionBackendError) as excinfo:
        backend.transcribe(str(tmp_path / "derivative.wav"))
    assert excinfo.value.error_code == module.ERROR_CODE_ENGINE_NOT_AVAILABLE


def _install_fake_faster_whisper(monkeypatch, module):
    fake = types.ModuleType("faster_whisper")
    recorded = {}

    class FakeInfo:
        language = "en"
        language_probability = 0.9

    class FakeSegment:
        def __init__(self, segment_id, start, end, text):
            self.id = segment_id
            self.start = start
            self.end = end
            self.text = text

    class FakeWhisperModel:
        def __init__(self, *args, **kwargs):
            recorded["init_args"] = args
            recorded["init_kwargs"] = kwargs

        def transcribe(self, path, **kwargs):
            recorded["transcribe_path"] = path
            recorded["transcribe_kwargs"] = kwargs
            return iter([FakeSegment(0, 0.0, 1.5, "Hello world.")]), FakeInfo()

    fake.WhisperModel = FakeWhisperModel
    monkeypatch.setitem(sys.modules, "faster_whisper", fake)
    return recorded


def test_faster_whisper_adapter_happy_path(tmp_path, monkeypatch):
    module = load_module()
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    recorded = _install_fake_faster_whisper(monkeypatch, module)
    backend = module.FasterWhisperTranscriptionBackend(str(model_dir), device="cpu")
    output = backend.transcribe(str(tmp_path / "derivative.wav"))

    assert recorded["init_args"][0] == str(model_dir)
    assert recorded["init_kwargs"] == {"device": "cpu", "compute_type": "int8"}
    assert recorded["transcribe_path"] == str(tmp_path / "derivative.wav")
    assert recorded["transcribe_kwargs"]["language"] is None
    assert recorded["transcribe_kwargs"]["task"] == module.TRANSCRIPTION_TASK
    assert recorded["transcribe_kwargs"]["word_timestamps"] is False
    assert recorded["transcribe_kwargs"]["vad_filter"] is True
    assert output["detected_language"] == "en"
    assert output["language_probability"] == 0.9
    segments = list(output["segments"])
    assert segments == [
        {"segment_index": 0, "start_seconds": 0.0, "end_seconds": 1.5, "text": "Hello world."}
    ]


def test_faster_whisper_end_to_end_via_core(tmp_path, monkeypatch):
    module = load_module()
    model_dir = tmp_path / "model"
    model_dir.mkdir()
    _install_fake_faster_whisper(monkeypatch, module)
    backend = module.FasterWhisperTranscriptionBackend(str(model_dir), device="cpu")
    request = _request(module, extracted_audio_start_seconds=10.0)
    result = module.transcribe(request, backend)
    payload = result.to_dict()
    assert payload["status"] == module.STATE_TRANSCRIPTION_COMPLETED
    assert payload["detected_language"] == "en"
    assert len(result.segments) == 1
    assert result.segments[0]["source_start_seconds"] == 10.0
