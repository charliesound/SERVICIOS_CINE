from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_qa_gate_v1.md"
)
CLI = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py")
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")
IMPLEMENTATION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_v1.md"
)
IMPLEMENTATION_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation.py"
)

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "CLI_IMPLEMENTATION_QA_GATE_PASS_CLOSED"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.SMOKE.CONTROLLED.JSON.FIXTURE.V1"
)
RENDERER_FUNCTION = "render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_doc_exists_and_exact_phase_is_declared() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_exact_previous_phase_functional_result_and_next_phase_are_declared() -> None:
    assert_all_present(read(QA_DOC), [PREVIOUS_PHASE, FUNCTIONAL_RESULT, NEXT_PHASE])


def test_required_source_files_exist_and_are_referenced() -> None:
    for path in [CLI, RENDERER, IMPLEMENTATION_DOC, IMPLEMENTATION_TEST]:
        assert path.exists(), path
        assert str(path) in read(QA_DOC)


def test_implementation_doc_declares_expected_result_and_next_gate() -> None:
    assert_all_present(read(IMPLEMENTATION_DOC), [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_IMPLEMENTATION_PASS_READY_FOR_QA_GATE",
        QA_PHASE,
    ])


def test_allowed_behavior_is_limited_to_controlled_json_to_renderer_to_report() -> None:
    assert_all_present(read(QA_DOC), [
        "receive a controlled JSON payload file",
        "reject directory input",
        "reject non-json input",
        "parse JSON safely",
        "require a dict payload",
        "call `render_controlled_ffprobe_metadata_visible_report(payload)`",
        "print returned report text to stdout",
        "optionally write returned report text to a safe `.txt` or `.md` output path",
        "preserve redaction boundaries",
        "fail closed on invalid JSON, missing input, directory input, unsupported suffix, non-dict JSON, unsafe output suffix, or renderer failure",
        "return deterministic exit codes",
        "limited to controlled JSON payload to pure renderer to visible report text",
    ])


def test_blocked_capabilities_are_explicitly_listed() -> None:
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


def test_cli_source_imports_pure_renderer_function() -> None:
    assert_all_present(read(CLI), [
        "from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_renderer import (",
        "render_controlled_ffprobe_metadata_visible_report",
    ])


def test_cli_source_has_expected_safe_entry_points() -> None:
    assert_all_present(read(CLI), [
        "def load_controlled_payload_json(path: Path) -> dict:",
        "def render_visible_report_from_controlled_payload_file(input_path: Path) -> str:",
        "def write_visible_report_text(output_path: Path, report_text: str) -> None:",
        "def main(argv: list[str] | None = None) -> int:",
        "ALLOWED_OUTPUT_SUFFIXES = {\".md\", \".txt\"}",
    ])


def test_cli_source_has_no_process_or_network_imports() -> None:
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


def test_cli_source_has_no_execution_or_scanning_patterns() -> None:
    source = read(CLI)
    denied = [
        "sub" + "process",
        "os.system",
        "P" + "open(",
        "check" + "_output(",
        "check" + "_call(",
        "os.walk",
        "glob(",
    ]
    for item in denied:
        assert item not in source


def test_cli_source_has_no_media_tool_execution_patterns() -> None:
    source = read(CLI)
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


def test_cli_source_has_no_protected_domain_imports() -> None:
    source = read(CLI)
    for token in [
        "src.",
        "src_frontend",
        "stripe",
        "credit",
        "ledger",
        "ai_jobs",
        "docker",
        "alembic",
        "sqlalchemy",
    ]:
        assert token not in source


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [QA_DOC, IMPLEMENTATION_DOC, IMPLEMENTATION_TEST, CLI, RENDERER]:
        assert forbidden_prefix not in read(path)
