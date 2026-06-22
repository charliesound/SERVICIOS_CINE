import importlib.util
import json
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_v1.md"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "CLI_IMPLEMENTATION_PASS_READY_FOR_QA_GATE"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1"
)


def load_module():
    spec = importlib.util.spec_from_file_location("renderer_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def controlled_payload() -> dict[str, object]:
    return {
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": "second_fixture_controlled.mov",
        "ffprobe_command_kind": "metadata_json",
        "result": "FFPROBE_METADATA_PREFLIGHT_PASS",
        "metadata": {"format": None, "streams": []},
        "media_processing_performed": False,
        "scanner_executed": False,
        "real_media_used": False,
        "ffmpeg_used": False,
        "audio_extraction_performed": False,
        "sync_generated": False,
        "transcription_generated": False,
        "subtitles_generated": False,
        "timeline_export_generated": False,
        "database_write": False,
        "saas_upload": False,
        "network_call": False,
    }


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def test_doc_declares_exact_phase_previous_result_and_next_phase() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [PHASE, PREVIOUS_PHASE, FUNCTIONAL_RESULT, NEXT_PHASE]:
        assert required in text


def test_cli_module_exists_and_exposes_expected_functions() -> None:
    module = load_module()
    for name in [
        "load_controlled_payload_json",
        "render_visible_report_from_controlled_payload_file",
        "write_visible_report_text",
        "main",
    ]:
        assert hasattr(module, name)


def test_cli_can_render_from_controlled_json_payload_file(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, controlled_payload())
    report = module.render_visible_report_from_controlled_payload_file(input_path)
    assert "CID Local Media Agent - Controlled FFprobe Metadata Visible Report" in report
    assert "second_fixture_controlled.mov" in report


def test_cli_stdout_mode_returns_zero_and_emits_report(tmp_path: Path, capsys) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, controlled_payload())
    assert module.main([str(input_path)]) == 0
    captured = capsys.readouterr()
    assert "CID Local Media Agent - Controlled FFprobe Metadata Visible Report" in captured.out
    assert captured.err == ""


def test_cli_output_file_mode_writes_text_or_markdown(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, controlled_payload())
    for suffix in [".txt", ".md"]:
        output_path = tmp_path / f"report{suffix}"
        assert module.main([str(input_path), "--output", str(output_path)]) == 0
        assert "CID Local Media Agent - Controlled FFprobe Metadata Visible Report" in output_path.read_text(encoding="utf-8")


def test_invalid_json_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    input_path.write_text("{not-json", encoding="utf-8")
    assert module.main([str(input_path)]) != 0


def test_missing_input_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    assert module.main([str(tmp_path / "missing.json")]) != 0


def test_directory_input_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    assert module.main([str(tmp_path)]) != 0


def test_non_json_input_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.txt"
    input_path.write_text("{}", encoding="utf-8")
    assert module.main([str(input_path)]) != 0


def test_non_dict_json_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, [])
    assert module.main([str(input_path)]) != 0


def test_missing_required_payload_fields_fail_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, {"input_policy": "controlled_fixture_only"})
    assert module.main([str(input_path)]) != 0


def test_unsafe_output_suffix_fails_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    output_path = tmp_path / "report.html"
    write_json(input_path, controlled_payload())
    assert module.main([str(input_path), "--output", str(output_path)]) != 0
    assert not output_path.exists()


def test_renderer_failures_fail_closed(tmp_path: Path) -> None:
    module = load_module()
    input_path = tmp_path / "payload.json"
    write_json(input_path, controlled_payload())
    with patch.object(module, "render_controlled_ffprobe_metadata_visible_report", side_effect=RuntimeError("boom")):
        assert module.main([str(input_path)]) != 0


def test_implementation_has_no_forbidden_imports_or_execution_patterns() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    forbidden_imports = [
        "import " + module
        for module in [
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "ftplib",
            "glob",
            "shutil",
            "sqlalchemy",
            "fastapi",
        ]
    ] + [
        "from " + module
        for module in [
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "ftplib",
            "glob",
            "shutil",
            "sqlalchemy",
            "fastapi",
        ]
    ]
    for token in forbidden_imports:
        assert token not in source
    for token in ["os.system", "multiprocessing", "os.walk", "Popen(", "check_output(", "check_call("]:
        assert token not in source


def test_no_literal_media_tool_execution_patterns_are_present() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    media_processor = "ff" + "mpeg"
    media_probe = "ff" + "probe"
    for token in [
        media_processor + " -i",
        media_processor + " -y",
        media_processor + " -nostdin",
        f'"{media_processor}"',
        f"'{media_processor}'",
        media_probe + " -v",
        f'"{media_probe}"',
        f"'{media_probe}'",
    ]:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, SCRIPT]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
