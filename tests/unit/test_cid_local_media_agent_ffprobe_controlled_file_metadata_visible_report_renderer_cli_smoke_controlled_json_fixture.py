import importlib.util
import json
from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture_v1.md"
)
CLI = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py")
FIXTURE = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "SMOKE_CONTROLLED_JSON_FIXTURE_PASS_READY_FOR_QA_GATE"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.QA.GATE.V1"
)

SAFE_FALSE_FLAGS = [
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
]


def load_cli():
    spec = importlib.util.spec_from_file_location("renderer_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fixture_payload() -> dict[str, object]:
    parsed = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def assert_no_private_or_path_leakage(text: str) -> None:
    forbidden = [
        "/tmp/",
        "/home/",
        "/mnt/",
        "C:\\",
        "\\\\",
        "client_name",
        "client name",
        "real client",
        "project_name",
        "project name",
        "real project",
        "production name",
        "harliesound",
        "SERVICIOS_CINE",
        "private material",
        "rodaje",
    ]
    lowered = text.lower()
    for marker in forbidden:
        assert marker.lower() not in lowered


def test_doc_declares_exact_phase_previous_result_and_next_phase() -> None:
    text = DOC.read_text(encoding="utf-8")
    for required in [PHASE, PREVIOUS_PHASE, FUNCTIONAL_RESULT, NEXT_PHASE]:
        assert required in text


def test_cli_and_fixture_exist() -> None:
    assert CLI.exists()
    assert FIXTURE.exists()


def test_fixture_is_json_dict_and_controlled() -> None:
    payload = fixture_payload()
    assert payload["phase"] == PHASE
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["ffprobe_command_kind"] == "metadata_json"
    assert payload["controlled_fixture_marker"] == "CID_SYNTHETIC_CONTROLLED_JSON_FIXTURE_ONLY"
    assert payload["input_path_redacted"] == "synthetic_controlled_fixture.mov"
    assert isinstance(payload["metadata"], dict)
    assert isinstance(payload["metadata"]["streams"], list)


def test_fixture_safe_flags_remain_false() -> None:
    payload = fixture_payload()
    for flag in SAFE_FALSE_FLAGS:
        assert payload[flag] is False
    for flag in [
        "public_demo_authorized",
        "sales_demo_authorized",
        "client_facing_demo_authorized",
        "production_use_authorized",
    ]:
        assert payload[flag] is False


def test_fixture_does_not_contain_forbidden_real_private_markers() -> None:
    assert_no_private_or_path_leakage(FIXTURE.read_text(encoding="utf-8"))


def test_cli_stdout_mode_returns_zero_and_safe_visible_report(capsys) -> None:
    cli = load_cli()
    assert cli.main([str(FIXTURE)]) == 0
    captured = capsys.readouterr()
    assert "CID Local Media Agent - Controlled FFprobe Metadata Visible Report" in captured.out
    assert "synthetic_controlled_fixture.mov" in captured.out
    assert "controlled_fixture_only" in captured.out
    assert "scanner execution: false" in captured.out
    assert captured.err == ""
    assert_no_private_or_path_leakage(captured.out)


def test_cli_output_file_mode_writes_safe_visible_report(tmp_path: Path) -> None:
    cli = load_cli()
    for suffix in [".txt", ".md"]:
        output = tmp_path / f"visible_report{suffix}"
        assert cli.main([str(FIXTURE), "--output", str(output)]) == 0
        content = output.read_text(encoding="utf-8")
        assert "CID Local Media Agent - Controlled FFprobe Metadata Visible Report" in content
        assert "synthetic_controlled_fixture.mov" in content
        assert "scanner execution: false" in content
        assert_no_private_or_path_leakage(content)


def test_doc_declares_blocked_boundaries() -> None:
    text = DOC.read_text(encoding="utf-8")
    for term in [
        "real media file use",
        "arbitrary folder use",
        "scanner execution",
        "ffprobe execution",
        "ffmpeg execution",
        "subprocess/process execution",
        "audio extraction",
        "sync",
        "transcription",
        "subtitle generation",
        "timeline export",
        "network calls",
        "SaaS/DB access",
        "installer creation",
        "public demo",
        "sales demo",
        "client-facing demo",
        "production use",
    ]:
        assert term in text


def test_cli_source_has_no_forbidden_imports_or_execution_patterns() -> None:
    source = CLI.read_text(encoding="utf-8")
    denied_imports = [
        "import " + name
        for name in [
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "ftplib",
            "glob",
            "sqlalchemy",
            "fastapi",
        ]
    ] + [
        "from " + name
        for name in [
            "subprocess",
            "socket",
            "requests",
            "urllib",
            "http",
            "ftplib",
            "glob",
            "sqlalchemy",
            "fastapi",
        ]
    ]
    for token in denied_imports:
        assert token not in source
    for token in [
        "sub" + "process",
        "os.system",
        "P" + "open(",
        "check" + "_output(",
        "check" + "_call(",
        "os.walk",
        "glob(",
    ]:
        assert token not in source


def test_cli_source_has_no_media_tool_or_protected_import_patterns() -> None:
    source = CLI.read_text(encoding="utf-8")
    media_processor = "ff" + "mpeg"
    media_probe = "ff" + "probe"
    for token in [
        media_processor + " -i",
        media_processor + " -y",
        f'"{media_processor}"',
        f"'{media_processor}'",
        media_probe + " -v",
        f'"{media_probe}"',
        f"'{media_probe}'",
        "src.",
        "src_frontend",
        "stripe",
        "credit",
        "ledger",
        "ai_jobs",
        "docker",
        "alembic",
    ]:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, FIXTURE, CLI]:
        assert forbidden_prefix not in path.read_text(encoding="utf-8")
