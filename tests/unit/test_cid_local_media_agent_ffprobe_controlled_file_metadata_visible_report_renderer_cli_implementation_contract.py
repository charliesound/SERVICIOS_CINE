from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_implementation_contract_v1.md"
)
PREVIOUS_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract_qa_gate_v1.md"
)
PREVIOUS_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract_qa_gate.py"
)
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")
FUTURE_CLI = Path(
    "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.CONTRACT.QA.GATE.V1"
)
FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "CLI_IMPLEMENTATION_CONTRACT_PASS_READY_FOR_QA_GATE"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.IMPLEMENTATION.CONTRACT.QA.GATE.V1"
)
RENDERER_FUNCTION = "render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_doc_exists_and_exact_phase_is_declared() -> None:
    assert DOC.exists()
    assert PHASE in read(DOC)


def test_exact_previous_phase_functional_result_and_next_phase_are_declared() -> None:
    assert_all_present(read(DOC), [
        PREVIOUS_PHASE,
        FUNCTIONAL_RESULT,
        NEXT_PHASE,
    ])


def test_previous_cli_qa_gate_and_renderer_are_referenced() -> None:
    assert PREVIOUS_QA_DOC.exists()
    assert PREVIOUS_QA_TEST.exists()
    assert RENDERER.exists()
    assert_all_present(read(DOC), [
        str(RENDERER),
        RENDERER_FUNCTION,
    ])
    assert PREVIOUS_PHASE in read(PREVIOUS_QA_DOC)


def test_allowed_behavior_is_limited_to_controlled_json_to_renderer_to_report() -> None:
    assert_all_present(read(DOC), [
        "controlled JSON payload file only",
        "input payload must already be safe and controlled",
        "receive a path to a controlled JSON payload",
        "parse that JSON safely",
        "pass the parsed dict to `render_controlled_ffprobe_metadata_visible_report(payload)`",
        "print or write the returned human-readable visible report text",
        "preserve redaction boundaries",
    ])


def test_fail_closed_conditions_are_declared() -> None:
    assert_all_present(read(DOC), [
        "invalid JSON",
        "missing required controlled payload fields",
        "unsafe input path",
        "unsupported input type",
        "fail closed",
    ])


def test_blocked_capabilities_are_explicitly_listed() -> None:
    assert_all_present(read(DOC), [
        "accept real media files",
        "accept arbitrary folders",
        "scan directories",
        "execute ffprobe",
        "execute ffmpeg",
        "execute subprocess/process commands",
        "perform audio extraction",
        "perform sync",
        "perform transcription",
        "generate subtitles",
        "export timelines",
        "call network services",
        "access SaaS/DB",
        "create installers",
        "be public-demo ready",
        "be sales-demo ready",
        "be client-facing ready",
        "be production-ready",
    ])


def test_no_cli_runtime_file_is_created() -> None:
    assert "No CLI runtime is implemented in this phase" in read(DOC)
    assert not FUTURE_CLI.exists()


def test_no_wrong_phase_prefix_is_present() -> None:
    forbidden_prefix = "CID." + "LOCAL_AGENT"
    for path in [DOC, PREVIOUS_QA_DOC, PREVIOUS_QA_TEST]:
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
