import importlib.util
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest


SCRIPT = Path("scripts/editorial_intelligence/audio_extraction/audio_extraction.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_audio_extraction_error", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _probe_result(module):
    return {
        "phase": module.PHASE,
        "asset_id": "asset_0007",
        "media_probe_state": "PROBE_COMPLETED",
        "media_kind": "video_with_audio",
        "source_reference": {
            "internal_local_source_reference": "/tmp/project/secret/folder/take.mov",
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


def _completed(returncode, stdout="", stderr=""):
    return type(
        "CompletedProcess",
        (),
        {"returncode": returncode, "stdout": stdout, "stderr": stderr},
    )()


def test_ffmpeg_nonzero_exit_fails_without_raw_stderr():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(1, stderr="decoder not found")):
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_FAILED
            error = payload["error"]
            assert error["error_code"] == "ffmpeg_nonzero_exit"
            assert error["ffmpeg_exit_code"] == 1
            assert error["timed_out"] is False
            assert "decoder not found" not in str(payload)
            assert "decoder not found" not in error["message_sanitized"]
            assert result.path is None


def test_timeout_raises_timed_out_state():
    module = load_module()
    probe = _probe_result(module)

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["ffmpeg"], timeout=kwargs.get("timeout", 60))

    with patch.object(module.subprocess, "run", side_effect=_raise_timeout):
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_TIMED_OUT
            assert payload["error"]["timed_out"] is True
            assert payload["error"]["error_code"] == "subprocess_error"
            assert result.path is None


def test_subprocess_oserror_fails_cleanly():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", side_effect=OSError("exec format error")):
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
            assert payload["state"] == module.STATE_AUDIO_EXTRACTION_FAILED
            assert payload["error"]["timed_out"] is False
            assert result.path is None


def test_cleanup_after_success_removes_temp_file():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(0)):
        with module.extract_audio(probe) as result:
            assert result.path is not None
            result.path.write_bytes(b"RIFF body")
            assert result.path.exists() is True
    assert result.path is None


def test_cleanup_after_exception_inside_context():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(0)):
        extracted = module.extract_audio(probe)
        with pytest.raises(RuntimeError):
            with extracted as result:
                assert result.path is not None
                result.path.write_bytes(b"RIFF body")
                assert result.path.exists() is True
                raise RuntimeError("boom")
    assert result.path is None


def test_temp_path_uses_os_temp_dir_and_sanitized_name():
    module = load_module()
    probe = _probe_result(module)
    probe["asset_id"] = "bad asset/name"
    with patch.object(module.subprocess, "run", return_value=_completed(0)):
        with module.extract_audio(probe) as result:
            path = result.path
    assert path is not None
    assert "bad asset" not in path.name
    assert "_" in path.name
    assert path.name.endswith(".wav")
    assert path.name.startswith("cid_audio_extract_")


def test_raw_source_path_not_exposed_publicly():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(0)):
        with module.extract_audio(probe) as result:
            payload = result.to_dict()
    label = payload["source_reference"]["sanitized_external_source_label"]
    assert label == "take.mov"
    assert "secret" not in label
    internal = payload["source_reference"]["internal_local_source_reference"]
    assert internal == "/tmp/project/secret/folder/take.mov"


def test_no_raw_source_path_in_sanitized_error():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(1)):
        with module.extract_audio(probe) as result:
            message = result.to_dict()["error"]["message_sanitized"]
    assert "secret" not in message
    assert "/tmp" not in message
    assert message == "ffmpeg exited with a non-zero status"


def test_duration_missing_uses_min_timeout():
    module = load_module()
    probe = _probe_result(module)
    probe["container"]["duration_seconds"] = None
    with patch.object(module.subprocess, "run", return_value=_completed(0)) as mock_run:
        with module.extract_audio(probe):
            pass
    timeout = mock_run.call_args.kwargs["timeout"]
    assert timeout == module.AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS


def test_duration_zero_uses_min_timeout():
    module = load_module()
    probe = _probe_result(module)
    probe["container"]["duration_seconds"] = 0
    with patch.object(module.subprocess, "run", return_value=_completed(0)) as mock_run:
        with module.extract_audio(probe):
            pass
    timeout = mock_run.call_args.kwargs["timeout"]
    assert timeout == module.AUDIO_EXTRACTION_TIMEOUT_MIN_SECONDS


def test_cleanup_error_does_not_crash_on_remove_failure():
    module = load_module()
    probe = _probe_result(module)
    with patch.object(module.subprocess, "run", return_value=_completed(0)):
        extracted = module.extract_audio(probe)
    assert extracted.path is not None
    extracted.path.write_bytes(b"RIFF body")
    with patch.object(module.Path, "unlink", side_effect=OSError("locked")):
        extracted.__exit__(None, None, None)
    assert extracted.path is not None
    extracted.__exit__(None, None, None)
    assert extracted.path is None
