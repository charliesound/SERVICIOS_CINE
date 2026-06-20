import importlib.util
import json
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_preflight.py")
DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_preflight_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1"


def load_module():
    spec = importlib.util.spec_from_file_location("ffprobe_controlled_preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def completed(stdout: str, returncode: int = 0):
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_controlled_tmp_path_is_accepted():
    module = load_module()
    assert module.is_controlled_fixture_path("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")


def test_repo_controlled_fixture_path_is_accepted():
    module = load_module()
    assert module.is_controlled_fixture_path("tests/fixtures/local_media_agent/controlled_media/sample.mov")


def test_uncontrolled_path_is_rejected():
    module = load_module()
    assert not module.is_controlled_fixture_path("/tmp/not_controlled/sample.mov")
    try:
        module.build_ffprobe_command("/tmp/not_controlled/sample.mov")
    except ValueError as exc:
        assert "controlled fixture" in str(exc)
    else:
        raise AssertionError("uncontrolled path was accepted")


def test_missing_controlled_flag_is_rejected():
    module = load_module()
    parser = module.build_parser()
    try:
        parser.parse_args(["--input", "/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov", "--json"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("missing --controlled-fixture was accepted")


def test_unexpected_positional_args_are_rejected():
    module = load_module()
    parser = module.build_parser()
    try:
        parser.parse_args([
            "--input",
            "/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov",
            "--json",
            "--controlled-fixture",
            "extra.mov",
        ])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("unexpected positional arg was accepted")


def test_ffprobe_command_construction_is_correct():
    module = load_module()
    command = module.build_ffprobe_command("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")
    assert command[:-1] == [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
    ]
    assert command[-1].endswith("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")


def test_successful_metadata_parsing():
    module = load_module()
    payload = {"format": {"duration": "1.0"}, "streams": [{"codec_type": "video"}]}

    with patch.object(module.subprocess, "run", return_value=completed(json.dumps(payload))):
        result = module.run_preflight("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")

    assert result["phase"] == PHASE
    assert result["result"] == "FFPROBE_METADATA_PREFLIGHT_PASS"
    assert result["input_policy"] == "controlled_fixture_only"
    assert result["input_path_redacted"] == "sample.mov"
    assert result["ffprobe_command_kind"] == "metadata_json"
    assert result["metadata"]["format"] == {"duration": "1.0"}
    assert result["metadata"]["streams"] == [{"codec_type": "video"}]


def test_ffprobe_failure_handled_safely():
    module = load_module()
    with patch.object(module.subprocess, "run", return_value=completed("", returncode=1)):
        result = module.run_preflight("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")

    assert result["result"] == "FFPROBE_METADATA_PREFLIGHT_FAILED"
    assert result["metadata"] == {"format": None, "streams": []}


def test_output_does_not_leak_full_paths():
    module = load_module()
    payload = {"format": {}, "streams": []}
    full_path = "/tmp/cid_local_media_agent_controlled_ffprobe/nested/sample.mov"

    with patch.object(module.subprocess, "run", return_value=completed(json.dumps(payload))):
        result = module.run_preflight(full_path)

    serialized = json.dumps(result)
    assert result["input_path_redacted"] == "sample.mov"
    assert full_path not in serialized


def test_safe_flags_remain_false():
    module = load_module()
    with patch.object(module.subprocess, "run", return_value=completed('{"format": {}, "streams": []}')):
        result = module.run_preflight("/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov")

    for key in [
        "media_processing_performed",
        "scanner_executed",
        "real_media_used",
        "ffmpeg_used",
        "audio_extraction_performed",
        "sync_generated",
        "transcription_generated",
        "subtitles_generated",
        "timeline_export_generated",
        "database_write",
        "saas_upload",
        "network_call",
    ]:
        assert result[key] is False


def test_source_does_not_import_disallowed_runtime_modules_or_call_ffmpeg():
    source = SCRIPT.read_text(encoding="utf-8")
    for token in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]:
        assert token not in source
    assert '"ffmpeg"' not in source
    assert "'ffmpeg'" not in source


def test_cli_json_output_works(capsys):
    module = load_module()
    with patch.object(module, "run_preflight", return_value={"phase": PHASE, "result": "ok"}):
        assert module.main([
            "--input",
            "/tmp/cid_local_media_agent_controlled_ffprobe/sample.mov",
            "--json",
            "--controlled-fixture",
        ]) == 0

    assert json.loads(capsys.readouterr().out) == {"phase": PHASE, "result": "ok"}


def test_documentation_declares_safety_boundaries():
    text = DOC.read_text(encoding="utf-8")
    for term in [
        "controlled-file `ffprobe` metadata preflight",
        "real media use",
        "scanner execution",
        "`ffmpeg` usage",
        "audio extraction",
        "synchronization",
        "transcription",
        "subtitle creation",
        "timeline export",
        "SaaS upload",
        "database write",
        "installer behavior",
        "client-facing use",
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_PREFLIGHT_PASS_READY_FOR_QA_GATE",
    ]:
        assert term in text
