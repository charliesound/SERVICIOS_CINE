import importlib.util
import json
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from unittest.mock import patch


SCRIPT = Path("scripts/editorial_intelligence/media_probe/media_probe.py")
CLI = Path("scripts/editorial_intelligence/media_probe/media_probe_cli.py")


def load_module():
    spec = importlib.util.spec_from_file_location("cid_editorial_media_probe_errors", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def completed(stdout: str, returncode: int = 0, stderr: str = ""):
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_malformed_json_is_probe_failed():
    module = load_module()
    result = module.parse_ffprobe_json("asset_0201", "/tmp/project/sample.mov", "{not-json")
    assert result["media_probe_state"] == module.STATE_PROBE_FAILED
    assert result["error"]["error_code"] == "parse_invalid_json"
    assert result["error"]["stage"] == "parse"
    assert result["error"]["message_sanitized"] == "ffprobe returned invalid JSON"
    assert result["error"]["timed_out"] is False


def test_nonzero_ffprobe_exit_is_probe_failed():
    module = load_module()
    with patch.object(module.subprocess, "run", return_value=completed("", returncode=1)):
        result = module.probe_media("asset_0202", "/tmp/project/sample.mov")
    assert result["media_probe_state"] == module.STATE_PROBE_FAILED
    assert result["error"]["error_code"] == "ffprobe_nonzero_exit"
    assert result["error"]["ffprobe_exit_code"] == 1
    assert result["error"]["stage"] == "subprocess"


def test_timeout_is_probe_failed():
    module = load_module()
    def _raise_timeout(*args, **kwargs):
        raise TimeoutExpired(cmd="ffprobe", timeout=10)
    with patch.object(module.subprocess, "run", side_effect=_raise_timeout):
        result = module.probe_media("asset_0203", "/tmp/project/sample.mov")
    assert result["media_probe_state"] == module.STATE_PROBE_FAILED
    assert result["error"]["timed_out"] is True
    assert result["error"]["stage"] == "subprocess"


def test_subprocess_error_oserror_is_probe_failed():
    module = load_module()
    with patch.object(module.subprocess, "run", side_effect=OSError("no ffprobe")):
        result = module.probe_media("asset_0204", "/tmp/project/sample.mov")
    assert result["media_probe_state"] == module.STATE_PROBE_FAILED
    assert result["error"]["error_code"] == "subprocess_error"
    assert result["error"]["timed_out"] is False


def test_sanitized_output_has_no_raw_path_leak():
    module = load_module()
    full_path = "/tmp/private/projects/secret_client/SC001_TK001_CAM_A.mov"
    payload = {"format": {"format_name": "mov"}, "streams": [{"codec_type": "video", "index": 0}]}
    result = module.parse_ffprobe_payload("asset_0205", full_path, payload, size_bytes=1234)
    assert result["source_reference"]["internal_local_source_reference"] == full_path
    assert result["source_reference"]["sanitized_external_source_label"] == "SC001_TK001_CAM_A.mov"
    assert "private/projects/secret_client" not in result["source_reference"]["sanitized_external_source_label"]
    assert "private/projects/secret_client" not in result["error"]["message_sanitized"] if result["error"]["message_sanitized"] else True
    sanitized_only = result["source_reference"]["sanitized_external_source_label"]
    assert "/" not in sanitized_only
    assert "secret_client" not in sanitized_only


def test_error_message_does_not_leak_raw_path():
    module = load_module()
    full_path = "/tmp/private/projects/secret_client/SC001_TK001_CAM_A.mov"
    result = module.parse_ffprobe_json("asset_0206", full_path, "{not-json")
    assert result["error"]["message_sanitized"] == "ffprobe returned invalid JSON"
    assert full_path not in result["error"]["message_sanitized"]


def test_command_built_as_argv_list_no_shell():
    module = load_module()
    command = module.build_ffprobe_command("/tmp/project/sample.mov")
    assert isinstance(command, list)
    assert command[0] == "ffprobe"
    assert "-print_format" in command
    assert "json" in command
    assert command[-1] == "/tmp/project/sample.mov"
    assert any("shell" not in flag for flag in command)


def test_source_does_not_import_disallowed_runtime_modules():
    source = SCRIPT.read_text(encoding="utf-8")
    for token in ["requests", "httpx", "socket", "sqlalchemy", "fastapi", "ollama", "qdrant"]:
        assert token not in source
    assert '"ffmpeg"' not in source
    assert "'ffmpeg'" not in source


def test_source_has_no_shell_invocation():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "shell = True" not in source


def test_cli_wires_to_core():
    cli_source = CLI.read_text(encoding="utf-8")
    assert "probe_media" in cli_source
    assert "--asset-id" in cli_source
