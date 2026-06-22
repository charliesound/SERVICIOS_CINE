from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract_v1.md"
)
CONTRACT_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract.py"
)
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.CONTRACT.QA.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.CONTRACT.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "CLI_CONTRACT_QA_GATE_PASS_CLOSED"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.V1"
)
RENDERER_FUNCTION = "render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_qa_gate_doc_exists_and_phase_is_exact() -> None:
    assert QA_DOC.exists()
    assert QA_PHASE in read(QA_DOC)


def test_previous_phase_functional_result_and_next_phase_are_exact() -> None:
    assert_all_present(read(QA_DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        NEXT_PHASE,
    ])


def test_required_source_files_exist_and_are_referenced() -> None:
    for path in [CONTRACT_DOC, CONTRACT_TEST, RENDERER]:
        assert path.exists(), path
        assert str(path) in read(QA_DOC)


def test_previous_cli_contract_declares_expected_result_and_next_gate() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        PREVIOUS_PHASE,
        "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_CONTRACT_PASS_READY_FOR_QA_GATE",
        QA_PHASE,
    ])


def test_qa_gate_confirms_future_cli_limited_to_controlled_json_and_renderer() -> None:
    assert_all_present(read(QA_DOC), [
        "only accept already controlled JSON payload input",
        "only call the pure renderer",
        "safe controlled metadata into human-readable visible report text",
        RENDERER_FUNCTION,
        "local-only, controlled-payload-only behavior",
    ])


def test_qa_gate_blocks_forbidden_capabilities() -> None:
    assert_all_present(read(QA_DOC), [
        "CLI runtime implementation",
        "real media",
        "arbitrary folders",
        "scanner execution",
        "ffprobe execution",
        "ffmpeg execution",
        "subprocess/process execution",
        "audio extraction",
        "sync",
        "transcription",
        "subtitles",
        "timeline export",
        "network calls",
        "SaaS/DB access",
        "installer",
        "public demo",
        "sales demo",
        "client-facing demo",
        "production use",
    ])


def test_previous_cli_contract_declares_matching_boundaries() -> None:
    assert_all_present(read(CONTRACT_DOC), [
        "No CLI runtime is implemented in this phase",
        "already-safe controlled metadata JSON payload",
        "The pure renderer function is the only allowed rendering path",
        "real media files as input",
        "arbitrary folders as input",
        "scanner execution flags",
        "ffprobe execution flags",
        "ffmpeg execution flags",
        "SaaS upload flags",
        "database write flags",
        "production readiness flags",
    ])


def test_no_wrong_phase_prefix_is_present() -> None:
    for path in [QA_DOC, CONTRACT_DOC, CONTRACT_TEST]:
        forbidden_prefix = "CID." + "LOCAL_AGENT"
        assert forbidden_prefix not in read(path)


def test_no_forbidden_imports_are_present() -> None:
    source = read(Path(__file__))
    forbidden_imports = [
        "import " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ] + [
        "from " + module
        for module in ["requests", "httpx", "socket", "sqlalchemy", "fastapi"]
    ]
    for token in forbidden_imports:
        assert token not in source


def test_no_process_or_media_tool_execution_patterns_are_present() -> None:
    source = read(Path(__file__))
    media_processor = "ff" + "mpeg"
    media_probe = "ff" + "probe"
    for token in [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "sub" + "process.",
        "P" + "open(",
        "check" + "_output(",
        media_processor + " -i",
        media_processor + " -y",
        f'"{media_processor}"',
        f"'{media_processor}'",
        media_probe + " -v",
        f'"{media_probe}"',
        f"'{media_probe}'",
    ]:
        assert token not in source
