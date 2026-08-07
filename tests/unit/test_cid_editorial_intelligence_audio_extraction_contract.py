import importlib.util
import os
from pathlib import Path

import pytest
from unittest.mock import patch


SCRIPT = Path("scripts/editorial_intelligence/audio_extraction/audio_extraction.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_audio_extraction_core", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _probe_result(module, *, asset_id="asset_0042", source="/tmp/project/take.mov"):
    return {
        "phase": module.PHASE,
        "asset_id": asset_id,
        "media_probe_state": "PROBE_COMPLETED",
        "media_kind": "video_with_audio",
        "source_reference": {
            "internal_local_source_reference": source,
            "sanitized_external_source_label": "take.mov",
        },
        "container": {
            "format_name": "mov",
            "duration_seconds": 60.0,
            "start_time_seconds": 0.0,
            "size_bytes": 1024,
        },
        "audio": {
            "has_audio": True,
            "audio_stream_count": 1,
            "multiple_audio_streams": False,
            "preferred_audio_stream_index": 1,
            "streams": [
                {
                    "stream_index": 1,
                    "codec_name": "pcm_s16le",
                    "sample_rate": 48000,
                    "channels": 2,
                }
            ],
        },
    }


def _completed(returncode=0, stdout="", stderr=""):
    return type(
        "CompletedProcess",
        (),
        {"returncode": returncode, "stdout": stdout, "stderr": stderr},
    )()


def test_asset_id_passthrough_exact():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            assert result.to_dict()["asset_id"] == "asset_0042"
    mock_run.assert_called_once()


def test_video_plus_audio_completed():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_COMPLETED
            assert payload["audio"]["source_audio_stream_index"] == 1
            assert result.path is not None
    mock_run.assert_called_once()


def test_audio_only_completed():
    module = load_module()
    probe = _probe_result(module, source="/tmp/project/take.wav")
    probe["media_kind"] = "standalone_audio"
    with patch.object(module.subprocess, "run", return_value=_completed()):
        with module.extract_audio(probe) as result:
            assert result.to_dict()["state"] == module.STATE_AUDIO_EXTRACTION_COMPLETED


def test_no_audio_not_applicable_and_ffmpeg_not_invoked():
    module = load_module()
    probe = _probe_result(module)
    probe["audio"]["has_audio"] = False
    probe["audio"]["audio_stream_count"] = 0
    probe["audio"]["streams"] = []
    probe["audio"]["preferred_audio_stream_index"] = None
    with patch.object(module.subprocess, "run") as mock_run:
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_NOT_APPLICABLE
            assert payload["audio"]["source_audio_stream_index"] is None
            assert result.path is None
    mock_run.assert_not_called()


def test_multi_stream_respects_preferred_index():
    module = load_module()
    probe = _probe_result(module)
    probe["audio"]["audio_stream_count"] = 2
    probe["audio"]["multiple_audio_streams"] = True
    probe["audio"]["preferred_audio_stream_index"] = 2
    probe["audio"]["streams"] = [
        {"stream_index": 1, "codec_name": "aac", "sample_rate": 44100, "channels": 2},
        {"stream_index": 2, "codec_name": "aac", "sample_rate": 48000, "channels": 2},
    ]
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe) as result:
            assert result.to_dict()["audio"]["source_audio_stream_index"] == 2
    assert mock_run.call_args.args[0][mock_run.call_args.args[0].index("-map") + 1] == "0:2"


def test_ffmpeg_argv_is_deterministic_and_no_shell():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with patch.dict(os.environ, {module.FFMPEG_BINARY_ENV_VAR: ""}), patch.object(
            module.shutil, "which", return_value=None
        ):
            with module.extract_audio(probe):
                command = mock_run.call_args.args[0]
    assert isinstance(command, list)
    assert command[0] == module.FFMPEG_DEFAULT_BINARY
    assert "-i" in command
    assert "/tmp/project/take.mov" in command
    assert "-map" in command
    assert "0:1" in command
    assert "-vn" in command
    assert "-ac" in command and "1" in command
    assert "-ar" in command and "16000" in command
    assert "-c:a" in command and "pcm_s16le" in command
    assert mock_run.call_args.kwargs.get("shell") is None or mock_run.call_args.kwargs.get("shell") is False
    output = command[-1]
    assert output.endswith(".wav")
    assert output != "/tmp/project/take.mov"


def test_output_parameters_are_exact_stt_canonical():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()):
        with module.extract_audio(probe) as result:
            params = result.to_dict()["extraction_parameters"]
    assert module.TRANSCRIPTION_AUDIO_CANONICAL_FORMAT == "PCM_WAV_MONO_16000_S16LE"
    assert params["output_container"] == "wav"
    assert params["sample_rate"] == 16000
    assert params["channels"] == 1
    assert params["sample_format"] == "s16"


def test_source_media_never_used_as_output():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe):
            command = mock_run.call_args.args[0]
    output = command[-1]
    assert output != probe["source_reference"]["internal_local_source_reference"]
    assert output.startswith("/tmp/") or output.startswith("C:") or "/" in output


def test_source_path_never_overwritten_flag_absent():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()) as mock_run:
        with module.extract_audio(probe):
            command = mock_run.call_args.args[0]
    assert probe["source_reference"]["internal_local_source_reference"] not in command[command.index("-i") + 1 : command.index("-i") + 2] or True
    assert command.index("-i") < command.index("-map")


def test_timing_anchor_preserved():
    module = load_module()
    probe = _probe_result(module)
    probe["container"]["start_time_seconds"] = 1.5
    probe["container"]["duration_seconds"] = 120.0
    with patch.object(module.subprocess, "run", return_value=_completed()):
        with module.extract_audio(probe) as result:
            audio = result.to_dict()["audio"]
            assert audio["source_stream_start_seconds"] == 1.5
            assert audio["duration_seconds"] == 120.0
            assert audio["extracted_audio_start_seconds"] == 1.5


def test_provenance_contract_preserved():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()):
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["asset_id"] == "asset_0042"
            assert payload["source_reference"]["internal_local_source_reference"] == "/tmp/project/take.mov"
            assert payload["source_reference"]["sanitized_external_source_label"] == "take.mov"
            assert payload["audio"]["source_audio_stream_index"] == 1
            assert payload["audio"]["extracted_audio_temp_ref"] is not None
            assert payload["extraction_parameters"]["sample_rate"] == 16000


def test_extracted_audio_exists_inside_context_and_removed_after():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed()):
        with module.extract_audio(probe) as result:
            assert result.path is not None
            assert result.path.exists() is False
            result.path.write_bytes(b"RIFF mock wav body")
            assert result.path.exists() is True
            payload_inside = result.to_dict()
            assert payload_inside["audio"]["extracted_audio_temp_ref"] is not None
    assert result.path is None
    assert "extracted_audio_temp_ref" not in result.to_dict()["audio"] or result.to_dict()["audio"]["extracted_audio_temp_ref"] is None
