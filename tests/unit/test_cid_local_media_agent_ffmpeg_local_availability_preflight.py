import importlib.util
import json
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from unittest.mock import patch


SCRIPT = Path("scripts/local_media_agent/ffmpeg_local_availability_preflight.py")
DOC = Path("docs/product/local_media_agent/cid_local_media_agent_ffmpeg_local_availability_preflight_v1.md")
PHASE = "CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1"


def load_module():
    spec = importlib.util.spec_from_file_location("ffmpeg_preflight", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def completed(stdout: str, returncode: int = 0):
    return CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_success_when_both_tools_exist():
    module = load_module()

    def which(name):
        return f"/usr/bin/{name}"

    def run(args, **kwargs):
        assert args in [["/usr/bin/ffmpeg", "-version"], ["/usr/bin/ffprobe", "-version"]]
        return completed(f"{Path(args[0]).name} version 6.1\n")

    with patch.object(module.shutil, "which", side_effect=which), patch.object(
        module.subprocess, "run", side_effect=run
    ):
        result = module.run_preflight()

    assert result["phase"] == PHASE
    assert result["result"] == "PASS"
    assert result["ffmpeg"]["available"] is True
    assert result["ffmpeg"]["version_line"] == "ffmpeg version 6.1"
    assert result["ffprobe"]["available"] is True
    assert result["ffprobe"]["version_line"] == "ffprobe version 6.1"


def test_missing_ffmpeg():
    module = load_module()

    def which(name):
        return None if name == "ffmpeg" else "/usr/bin/ffprobe"

    with patch.object(module.shutil, "which", side_effect=which), patch.object(
        module.subprocess, "run", return_value=completed("ffprobe version 6.1\n")
    ):
        result = module.run_preflight()

    assert result["result"] == "MISSING_TOOLS"
    assert result["ffmpeg"] == {"available": False, "path": None, "version_line": None}
    assert result["ffprobe"]["available"] is True


def test_missing_ffprobe():
    module = load_module()

    def which(name):
        return "/usr/bin/ffmpeg" if name == "ffmpeg" else None

    with patch.object(module.shutil, "which", side_effect=which), patch.object(
        module.subprocess, "run", return_value=completed("ffmpeg version 6.1\n")
    ):
        result = module.run_preflight()

    assert result["result"] == "MISSING_TOOLS"
    assert result["ffmpeg"]["available"] is True
    assert result["ffprobe"] == {"available": False, "path": None, "version_line": None}


def test_version_command_failure_handled_safely():
    module = load_module()

    with patch.object(module.shutil, "which", return_value="/usr/bin/ffmpeg"), patch.object(
        module.subprocess, "run", return_value=completed("", returncode=1)
    ):
        result = module.run_preflight()

    assert result["result"] == "MISSING_TOOLS"
    assert result["ffmpeg"]["available"] is False
    assert result["ffmpeg"]["version_line"] is None
    assert result["ffprobe"]["available"] is False


def test_version_command_exception_handled_safely():
    module = load_module()

    with patch.object(module.shutil, "which", return_value="/usr/bin/ffmpeg"), patch.object(
        module.subprocess, "run", side_effect=TimeoutExpired(cmd=["ffmpeg", "-version"], timeout=5)
    ):
        result = module.run_preflight()

    assert result["ffmpeg"]["available"] is False
    assert result["ffprobe"]["available"] is False


def test_no_media_path_arguments_are_accepted():
    module = load_module()
    parser = module.build_parser()

    try:
        parser.parse_args(["--json", "example.mov"])
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("media-like positional argument was accepted")


def test_output_flags_remain_false():
    module = load_module()
    with patch.object(module.shutil, "which", return_value=None):
        result = module.run_preflight()

    for key in [
        "media_processing_performed",
        "scanner_executed",
        "real_media_used",
        "database_write",
        "saas_upload",
        "network_call",
    ]:
        assert result[key] is False


def test_json_cli_output_works(capsys):
    module = load_module()
    with patch.object(module, "run_preflight", return_value={"phase": PHASE, "result": "PASS"}):
        assert module.main(["--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output == {"phase": PHASE, "result": "PASS"}


def test_source_does_not_import_disallowed_runtime_modules():
    source = SCRIPT.read_text(encoding="utf-8")
    for token in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]:
        assert token not in source


def test_documentation_declares_safety_boundaries():
    text = DOC.read_text(encoding="utf-8")
    for term in [
        "only detects local tool availability",
        "No media is processed.",
        "No scanner is executed.",
        "No ffprobe or ffmpeg media probing is authorized.",
        "It is not installer readiness.",
        "It is not client-facing.",
        "LOCAL_MEDIA_AGENT_FFMPEG_LOCAL_AVAILABILITY_PREFLIGHT_PASS_READY_FOR_QA_GATE",
    ]:
        assert term in text
