from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_implementation_readiness_v1.md"
)
SOURCE_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_qa_gate_v1.md"
)
SOURCE_QA_GATE_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "runtime_cli_integration_contract_qa_gate.py"
)
SOURCE_CONTRACT_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "runtime_cli_integration_contract.py"
)
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")
PLANNED_CLI = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
PLANNED_CLI_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_doc_and_source_files_exist() -> None:
    assert DOC.exists()
    assert SOURCE_QA_GATE_DOC.exists()
    assert SOURCE_QA_GATE_TEST.exists()
    assert SOURCE_CONTRACT_TEST.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()


def test_source_traceability_is_complete() -> None:
    text = _text()

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS",
        "028088a77322ca3f3dfb14dcccf44bd9db7a501a",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-contract-qa-gate-v1-20260620",
    ]

    for item in required:
        assert item in text


def test_readiness_is_docs_test_only_and_non_runtime() -> None:
    text = _text()

    required = [
        "This phase is docs/test-only.",
        "This phase does not implement the CLI.",
        "This phase does not modify the runtime generator.",
        "This phase does not execute the scanner.",
        "This phase does not use real client media.",
        "This phase does not execute ffprobe or ffmpeg.",
        "This phase does not perform network calls, SaaS upload, or database writes.",
        "This phase does not generate synchronization, transcription, subtitles, translations, or timeline exports.",
    ]

    for item in required:
        assert item in text


def test_future_cli_files_are_planned_but_absent() -> None:
    text = _text()

    assert "scripts/local_media_agent/visible_report_runtime_cli.py" in text
    assert "tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py" in text
    assert "This readiness phase must not create those files." in text
    assert not PLANNED_CLI.exists()
    assert not PLANNED_CLI_TEST.exists()


def test_existing_renderer_dependency_is_locked() -> None:
    text = _text()
    source = RUNTIME_GENERATOR.read_text(encoding="utf-8")

    interface_call = "generate_visible_report(scanner_result, output_root)"
    assert interface_call in text
    assert "scripts/local_media_agent/visible_report_runtime_generator.py" in text
    assert "The CLI must not duplicate renderer logic." in text
    assert "The CLI must not bypass runtime validation." in text
    assert "The CLI must not widen the renderer interface." in text
    assert "def generate_visible_report(" in source


def test_future_cli_entry_point_is_declared() -> None:
    text = _text()

    required = [
        "python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>",
        "main(argv: Sequence[str] | None = None) -> int",
        "The CLI must be import-safe.",
        "Importing the CLI module must not execute rendering.",
        "Importing the CLI module must not read files.",
        "Importing the CLI module must not write files.",
    ]

    for item in required:
        assert item in text


def test_required_optional_and_forbidden_flags_are_declared() -> None:
    text = _text()

    flags = [
        "--scanner-result-json",
        "--output-root",
        "--dry-run",
        "--strict",
        "--print-output-path",
        "--scan",
        "--ffprobe",
        "--ffmpeg",
        "--sync",
        "--transcribe",
        "--subtitle",
        "--export-davinci",
        "--export-avid",
        "--upload",
        "--database-write",
        "--network",
        "--client-facing",
    ]

    for flag in flags:
        assert flag in text

    assert "The future CLI must reject unsupported flags before reading input JSON." in text


def test_input_readiness_requirements_are_complete() -> None:
    text = _text()

    required = [
        "accept only one already-created controlled scanner result JSON file",
        "require the JSON path to be explicit",
        "reject URL-like inputs",
        "reject mounted Windows paths",
        "reject Windows drive paths",
        "reject UNC paths",
        "reject repository paths as input",
        "reject missing files",
        "reject directories",
        "reject invalid JSON",
        "reject JSON roots that are not objects",
        "parse JSON locally",
        "pass parsed data to the renderer unchanged",
        "scan folders",
        "discover input implicitly",
        "infer missing scanner facts",
        "correct invalid counts",
        "hide warnings",
        "replace invalid input with sample data",
        "fetch remote input",
    ]

    for item in required:
        assert item in text


def test_output_readiness_requirements_are_complete() -> None:
    text = _text()

    required = [
        "require an explicit output root",
        "delegate final report path authorization to the runtime renderer",
        "produce only the runtime renderer artifact",
        "report the created output path only after successful generation",
        "05_reports/cid_local_media_agent_visible_report_v1.md",
        "00_project/",
        "01_media_catalog/",
        "02_audio_sync/",
        "03_transcription/",
        "04_subtitles/",
        "06_exports/",
        "database records",
        "SaaS records",
        "scanner outputs",
        "media derivatives",
    ]

    for item in required:
        assert item in text


def test_validation_order_is_locked() -> None:
    text = _text()

    ordered = [
        "1. CLI argument presence",
        "2. unsupported flag rejection",
        "3. input JSON path safety",
        "4. output root path safety",
        "5. JSON file existence",
        "6. JSON parse success",
        "7. parsed object type",
        "8. delegation to `generate_visible_report`",
        "9. runtime validation result",
        "10. final output path reporting",
    ]

    cursor = -1
    for item in ordered:
        position = text.find(item)
        assert position > cursor
        cursor = position

    assert "A failed step must stop execution." in text
    assert "A failed step must not create a report artifact." in text


def test_failure_and_success_behavior_are_ready() -> None:
    text = _text()

    required = [
        "return a non-zero exit code for failures",
        "write a concise error to stderr for failures",
        "must not write a partial report",
        "must not fall back to scanner execution",
        "must not fall back to sample data",
        "must not fall back to current working directory discovery",
        "must not report success if no report was created",
        "return exit code `0`",
        "create exactly one visible report artifact through the renderer",
        "write under `05_reports/`",
        "optionally print the created report path if `--print-output-path` is supplied",
        "avoid printing private local paths inside report content",
    ]

    for item in required:
        assert item in text


def test_future_unit_test_readiness_is_declared() -> None:
    text = _text()

    required = [
        "missing required arguments",
        "unsupported forbidden flag",
        "URL-like input rejection",
        "unsafe input path rejection",
        "unsafe output root rejection",
        "missing JSON file",
        "invalid JSON",
        "JSON root not object",
        "successful delegation to `generate_visible_report`",
        "runtime validation error propagation",
        "output path print behavior",
        "import-safe behavior",
        "no planned scope creep flags",
    ]

    for item in required:
        assert item in text


def test_explicit_non_goals_block_scope_creep() -> None:
    text = _text()

    non_goals = [
        "CLI implementation in this phase",
        "scanner execution",
        "scanner implementation changes",
        "real media scanning",
        "public demo use",
        "client-facing demo use",
        "ffprobe execution",
        "ffmpeg execution",
        "waveform sync",
        "timecode sync",
        "clap sync",
        "transcription",
        "translation",
        "subtitle generation",
        "DaVinci Resolve export",
        "Avid export",
        "SaaS upload",
        "database writes",
        "network calls",
        "frontend/backend SaaS changes",
    ]

    for item in non_goals:
        assert item in text


def test_readiness_decision_and_result_are_declared() -> None:
    text = _text()

    required = [
        "current repo state is clean before implementation",
        "future CLI file is still absent",
        "future CLI test file is still absent",
        "runtime CLI integration contract test passes",
        "runtime CLI integration contract QA gate test passes",
        "runtime generator test passes",
        "controlled runtime implementation QA gate test passes",
        "supporting readiness and contract tests pass",
        "WSL/repo guard passes",
        "database backend regression guard passes",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_READINESS_QA_GATE",
    ]

    for item in required:
        assert item in text
