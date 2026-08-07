import importlib.util
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path("scripts/editorial_intelligence/audio_extraction/audio_extraction.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_audio_extraction_stream", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _base_probe(module):
    return {
        "phase": module.PHASE,
        "asset_id": "asset_0009",
        "media_probe_state": "PROBE_COMPLETED",
        "media_kind": "multiple_audio_streams",
        "source_reference": {
            "internal_local_source_reference": "/tmp/project/multi.mov",
            "sanitized_external_source_label": "multi.mov",
        },
        "container": {
            "format_name": "mov",
            "duration_seconds": 60.0,
            "start_time_seconds": 0.0,
            "size_bytes": 1024,
        },
        "audio": {
            "has_audio": True,
            "audio_stream_count": 2,
            "multiple_audio_streams": True,
            "preferred_audio_stream_index": 2,
            "streams": [
                {"stream_index": 1, "codec_name": "aac", "sample_rate": 44100, "channels": 2},
                {"stream_index": 2, "codec_name": "aac", "sample_rate": 48000, "channels": 2},
            ],
        },
    }


def _completed(returncode=0):
    return type(
        "CompletedProcess",
        (),
        {"returncode": returncode, "stdout": "", "stderr": ""},
    )()


def test_preferred_stream_index_respected():
    module = load_module()
    probe = _base_probe(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["audio"]["source_audio_stream_index"] == 2
        command = mock_run.call_args.args[0]
    assert "-map" in command
    assert command[command.index("-map") + 1] == "0:2"


def test_explicit_stream_override_wins():
    module = load_module()
    probe = _base_probe(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe, stream_override=1) as result:
            payload = result.to_dict()
            assert payload["audio"]["source_audio_stream_index"] == 1
        command = mock_run.call_args.args[0]
    assert command[command.index("-map") + 1] == "0:1"


def test_fallback_first_stream_when_preferred_missing():
    module = load_module()
    probe = _base_probe(module)
    probe["audio"]["preferred_audio_stream_index"] = None
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["audio"]["source_audio_stream_index"] == 1
        command = mock_run.call_args.args[0]
    assert command[command.index("-map") + 1] == "0:1"


def test_no_audio_never_invokes_ffmpeg():
    module = load_module()
    probe = _base_probe(module)
    probe["audio"]["has_audio"] = False
    probe["audio"]["audio_stream_count"] = 0
    probe["audio"]["streams"] = []
    probe["audio"]["preferred_audio_stream_index"] = None
    with patch.object(module.subprocess, "run") as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_NOT_APPLICABLE
    mock_run.assert_not_called()


def test_single_audio_stream_uses_explicit_index():
    module = load_module()
    probe = _base_probe(module)
    probe["audio"]["audio_stream_count"] = 1
    probe["audio"]["multiple_audio_streams"] = False
    probe["audio"]["preferred_audio_stream_index"] = 0
    probe["audio"]["streams"] = [
        {"stream_index": 0, "codec_name": "pcm_s16le", "sample_rate": 48000, "channels": 2}
    ]
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["audio"]["source_audio_stream_index"] == 0
        command = mock_run.call_args.args[0]
    assert command[command.index("-map") + 1] == "0:0"


def test_selection_policy_constant_matches_readiness():
    module = load_module()
    assert module.AUDIO_STREAM_SELECTION_POLICY == "REUSE_MEDIA_PROBE_PREFERRED_AUDIO_STREAM_INDEX"


def test_stream_selection_helper_preferred():
    module = load_module()
    audio = {
        "preferred_audio_stream_index": 2,
        "streams": [
            {"stream_index": 1},
            {"stream_index": 2},
        ],
    }
    assert module.select_audio_stream_index(audio) == 2


def test_stream_selection_helper_override():
    module = load_module()
    audio = {
        "preferred_audio_stream_index": 2,
        "streams": [
            {"stream_index": 1},
            {"stream_index": 2},
        ],
    }
    assert module.select_audio_stream_index(audio, override=1) == 1


def test_stream_selection_helper_fallback():
    module = load_module()
    audio = {"preferred_audio_stream_index": None, "streams": [{"stream_index": 3}]}
    assert module.select_audio_stream_index(audio) == 3


def test_stream_selection_helper_empty():
    module = load_module()
    assert module.select_audio_stream_index({"preferred_audio_stream_index": None, "streams": []}) is None
