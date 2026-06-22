from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_contract_v1.md"
)
SOURCE_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_qa_gate_v1.md"
)
SOURCE_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_qa_gate.py"
)
RENDERER = Path("scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer.py")
FUTURE_CLI = Path(
    "scripts/local_media_agent/ffprobe_controlled_file_metadata_visible_report_renderer_cli.py"
)

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.CONTRACT.V1"
)
SOURCE_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.IMPLEMENTATION.QA.GATE.V1"
)
ACCEPTANCE = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_"
    "CLI_CONTRACT_PASS_READY_FOR_QA_GATE"
)
NEXT_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.CONTRACT.QA.GATE.V1"
)
RENDERER_FUNCTION = "render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_all_present(content: str, required: list[str]) -> None:
    for item in required:
        assert item in content


def test_doc_exists_and_phase_is_declared() -> None:
    assert DOC.exists()
    assert PHASE in read(DOC)


def test_source_stable_state_and_source_phase_are_declared() -> None:
    assert_all_present(read(DOC), [
        "48b362b70aa3bb51a630b38f48b761cb9533146c",
        SOURCE_PHASE,
        str(SOURCE_QA_DOC),
        str(SOURCE_QA_TEST),
    ])


def test_renderer_implementation_qa_gate_is_referenced() -> None:
    assert SOURCE_QA_DOC.exists()
    assert SOURCE_QA_TEST.exists()
    assert RENDERER.exists()
    assert_all_present(read(DOC), [
        "Renderer implementation QA gate",
        str(SOURCE_QA_DOC),
        str(SOURCE_QA_TEST),
    ])


def test_future_cli_accepts_only_controlled_metadata_payload() -> None:
    assert_all_present(read(DOC), [
        "already-safe controlled metadata JSON payload",
        "`input_policy` equal to `controlled_fixture_only`",
        "`ffprobe_command_kind` equal to `metadata_json`",
        "`input_path_redacted` as filename-only",
    ])


def test_future_cli_forbids_media_folders_and_scanner_execution() -> None:
    assert_all_present(read(DOC), [
        "real media files as input",
        "arbitrary folders as input",
        "raw media path arguments",
        "folder arguments",
        "scanner execution flags",
        "folder scanning",
    ])


def test_future_cli_forbids_probe_processing_and_deliverables() -> None:
    assert_all_present(read(DOC), [
        "ffprobe execution flags",
        "ffmpeg execution flags",
        "audio extraction flags",
        "sync flags",
        "transcription flags",
        "subtitle flags",
        "timeline export flags",
        "SaaS upload flags",
        "database write flags",
        "installer behavior flags",
        "client-facing readiness flags",
        "public demo readiness flags",
        "sales demo readiness flags",
        "production readiness flags",
    ])


def test_stdout_and_controlled_output_behavior_are_declared() -> None:
    assert_all_present(read(DOC), [
        "safe stdout rendering",
        "Stdout must contain deterministic report text only",
        "explicit output report path only inside a controlled output location",
        "reject arbitrary output folders",
    ])


def test_path_rejection_behavior_is_declared() -> None:
    assert_all_present(read(DOC), [
        "Windows paths",
        "`/mnt/c` paths",
        "UNC paths",
        "Raw media paths",
        "folder paths",
        "unsafe `input_path_redacted` values",
    ])


def test_pure_renderer_function_and_invocation_contract_are_declared() -> None:
    assert_all_present(read(DOC), [
        RENDERER_FUNCTION,
        "The pure renderer function is the only allowed rendering path",
        "must not use another rendering path",
    ])


def test_acceptance_result_and_next_qa_gate_phase_are_declared() -> None:
    assert_all_present(read(DOC), [ACCEPTANCE, NEXT_PHASE])


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


def test_no_process_execution_usage_is_present() -> None:
    source = read(Path(__file__))
    process_name = "sub" + "process"
    for token in [
        process_name,
        "P" + "open(",
        "check" + "_output(",
        "check" + "_call(",
    ]:
        assert token not in source


def test_no_media_tool_execution_pattern_is_present() -> None:
    source = read(Path(__file__))
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


def test_no_runtime_cli_file_is_required() -> None:
    assert "No CLI runtime is implemented in this phase" in read(DOC)
    assert not FUTURE_CLI.exists()
