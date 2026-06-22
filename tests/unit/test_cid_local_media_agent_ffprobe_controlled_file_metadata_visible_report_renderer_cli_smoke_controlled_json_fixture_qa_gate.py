import json
from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture_qa_gate_v1.md"
)
SMOKE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture_v1.md"
)
FIXTURE = Path(
    "tests/fixtures/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_payload_v1.json"
)
SMOKE_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_smoke_controlled_json_fixture.py"
)
CLI = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py")
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_"
    "SMOKE_CONTROLLED_JSON_FIXTURE_QA_GATE_PASS_CLOSED"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.CONTRACT.V1"
)

SAFE_FALSE_FLAGS = [
    "real_media_used",
    "media_processing_performed",
    "scanner_executed",
    "ffprobe_executed",
    "ffmpeg_used",
    "database_write",
    "network_call",
    "saas_upload",
    "audio_extraction_performed",
    "sync_performed",
    "transcription_performed",
    "subtitles_generated",
    "timeline_export_performed",
    "client_facing_demo_authorized",
    "production_use_authorized",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def fixture_payload() -> dict[str, object]:
    parsed = json.loads(read(FIXTURE))
    assert isinstance(parsed, dict)
    return parsed


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_and_next_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [PREVIOUS_PHASE, FUNCTIONAL_RESULT, NEXT_PHASE])


def test_required_existing_files_exist_and_are_referenced() -> None:
    for path in [SMOKE_DOC, FIXTURE, SMOKE_TEST, CLI, RENDERER]:
        assert path.exists(), path
        assert str(path) in read(QA_DOC)


def test_smoke_doc_declares_expected_result_and_next_gate() -> None:
    assert_all_present(read(SMOKE_DOC), [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_SMOKE_CONTROLLED_JSON_FIXTURE_PASS_READY_FOR_QA_GATE",
        QA_PHASE,
    ])


def test_qa_gate_declares_controlled_fixture_to_cli_to_renderer_flow() -> None:
    assert_all_present(read(QA_DOC), [
        "controlled JSON fixture",
        "existing local-only CLI",
        "existing pure renderer",
        "safe visible report output",
        "render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str",
    ])


def test_fixture_is_json_dict_controlled_and_synthetic() -> None:
    payload = fixture_payload()
    assert payload["phase"] == PREVIOUS_PHASE
    assert payload["input_policy"] == "controlled_fixture_only"
    assert payload["controlled_fixture_marker"] == "CID_SYNTHETIC_CONTROLLED_JSON_FIXTURE_ONLY"
    assert payload["input_path_redacted"] == "synthetic_controlled_fixture.mov"
    assert isinstance(payload["metadata"], dict)
    assert isinstance(payload["metadata"]["streams"], list)


def test_fixture_safe_flags_are_false() -> None:
    payload = fixture_payload()
    for flag in SAFE_FALSE_FLAGS:
        assert payload[flag] is False


def test_fixture_has_no_forbidden_privacy_markers() -> None:
    text = read(FIXTURE).lower()
    for marker in [
        "/home/",
        "/mnt/",
        "c:",
        "\\",
        "cliente",
        "rodaje",
        "productora",
        "privado",
        "private absolute",
        "real project",
        "real client",
        "client name",
        "project name",
        "production name",
    ]:
        assert marker not in text


def test_smoke_test_validates_stdout_output_file_and_privacy() -> None:
    text = read(SMOKE_TEST)
    assert_all_present(text, [
        "test_cli_stdout_mode_returns_zero_and_safe_visible_report",
        "assert cli.main([str(FIXTURE)]) == 0",
        "CID Local Media Agent - Controlled FFprobe Metadata Visible Report",
        "synthetic_controlled_fixture.mov",
        "assert_no_private_or_path_leakage(captured.out)",
        "test_cli_output_file_mode_writes_safe_visible_report",
        "for suffix in [\".txt\", \".md\"]",
        "assert_no_private_or_path_leakage(content)",
        "test_fixture_safe_flags_remain_false",
    ])


def test_qa_gate_blocks_forbidden_capabilities() -> None:
    assert_all_present(read(QA_DOC), [
        "real media files",
        "arbitrary folders",
        "directory scanning",
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
    ])


def test_cli_source_has_no_forbidden_imports_or_execution_patterns() -> None:
    source = read(CLI)
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
    for item in denied_imports:
        assert item not in source
    for item in ["sub" + "process", "os.system", "P" + "open(", "check" + "_output(", "os.walk", "glob("]:
        assert item not in source


def test_cli_source_has_no_media_tool_or_protected_import_patterns() -> None:
    source = read(CLI)
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
    for path in [QA_DOC, SMOKE_DOC, FIXTURE, SMOKE_TEST, CLI, RENDERER]:
        assert forbidden_prefix not in read(path)
