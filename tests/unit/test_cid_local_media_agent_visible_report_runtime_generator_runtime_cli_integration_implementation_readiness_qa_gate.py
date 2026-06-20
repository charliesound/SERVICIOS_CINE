from pathlib import Path


QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_implementation_readiness_qa_gate_v1.md"
)
READINESS_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_implementation_readiness_v1.md"
)
READINESS_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "runtime_cli_integration_implementation_readiness.py"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_v1.md"
)
CONTRACT_QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_qa_gate_v1.md"
)
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")
PLANNED_CLI = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
PLANNED_CLI_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_and_files_under_qa_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert READINESS_DOC.exists()
    assert READINESS_TEST.exists()
    assert CONTRACT_DOC.exists()
    assert CONTRACT_QA_DOC.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()

    text = _text(QA_GATE_DOC)
    for item in (
        "visible_report_runtime_generator_runtime_cli_integration_implementation_readiness_v1.md",
        "test_cid_local_media_agent_visible_report_runtime_generator_runtime_cli_integration_implementation_readiness.py",
        "visible_report_runtime_generator_runtime_cli_integration_contract_v1.md",
        "visible_report_runtime_generator_runtime_cli_integration_contract_qa_gate_v1.md",
        "scripts/local_media_agent/visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py",
    ):
        assert item in text


def test_source_traceability_is_complete() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

    qa_required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_READINESS_QA_GATE",
        "00e6d7765cc1f8eadd8e1555fc1f55d0f4bd594e",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-implementation-readiness-v1-20260620",
    ]

    readiness_required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.IMPLEMENTATION.READINESS.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_PASS_READY_FOR_IMPLEMENTATION_READINESS_QA_GATE",
    ]

    for item in qa_required:
        assert item in qa_text

    for item in readiness_required:
        assert item in readiness_text


def test_qa_gate_is_docs_test_only_and_non_runtime() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "This QA gate is docs/test-only.",
        "This QA gate does not implement the CLI.",
        "This QA gate does not modify the runtime generator.",
        "This QA gate does not execute the scanner.",
        "This QA gate does not use real client media.",
        "This QA gate does not execute ffprobe or ffmpeg.",
        "This QA gate does not perform network calls, SaaS upload, or database writes.",
        "This QA gate does not generate synchronization, transcription, subtitles, translations, or timeline exports.",
    ]

    for item in required:
        assert item in qa_text


def test_future_cli_is_still_absent() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

    assert "scripts/local_media_agent/visible_report_runtime_cli.py" in qa_text
    assert "tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py" in qa_text
    assert "This readiness phase must not create those files." in readiness_text
    assert not PLANNED_CLI.exists()
    assert not PLANNED_CLI_TEST.exists()


def test_renderer_dependency_remains_narrow() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)
    source = _text(RUNTIME_GENERATOR)

    call = "generate_visible_report(scanner_result, output_root)"
    assert call in qa_text
    assert call in readiness_text
    assert "The future CLI must not duplicate renderer logic." in qa_text
    assert "The future CLI must not bypass runtime validation." in qa_text
    assert "The future CLI must not widen the renderer interface." in qa_text
    assert "The CLI must not duplicate renderer logic." in readiness_text
    assert "The CLI must not bypass runtime validation." in readiness_text
    assert "The CLI must not widen the renderer interface." in readiness_text
    assert "def generate_visible_report(" in source


def test_entry_point_and_command_shape_are_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

    required = [
        "main(argv: Sequence[str] | None = None) -> int",
        "The future CLI must be import-safe.",
        "execute rendering",
        "read files",
        "write files",
        "python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>",
        "The command must require explicit arguments.",
        "The command must not discover input implicitly.",
    ]

    for item in required:
        assert item in qa_text

    for item in (
        "main(argv: Sequence[str] | None = None) -> int",
        "The CLI must be import-safe.",
        "Importing the CLI module must not execute rendering.",
        "Importing the CLI module must not read files.",
        "Importing the CLI module must not write files.",
    ):
        assert item in readiness_text


def test_flags_are_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

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
        assert flag in qa_text
        assert flag in readiness_text

    assert "The future CLI must reject unsupported flags before reading input JSON." in qa_text
    assert "The future CLI must reject unsupported flags before reading input JSON." in readiness_text


def test_input_and_output_readiness_are_strict() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

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
        "require an explicit output root",
        "delegate final report path authorization to the runtime renderer",
        "produce only the runtime renderer artifact",
        "report the created output path only after successful generation",
        "05_reports/cid_local_media_agent_visible_report_v1.md",
    ]

    for item in required:
        assert item in qa_text
        assert item in readiness_text


def test_forbidden_outputs_and_runtime_expansion_are_blocked() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

    forbidden = [
        "scan folders",
        "discover input implicitly",
        "infer missing scanner facts",
        "correct invalid counts",
        "hide warnings",
        "replace invalid input with sample data",
        "fetch remote input",
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

    for item in forbidden:
        assert item in qa_text
        assert item in readiness_text


def test_validation_order_is_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

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

    for text in (qa_text, readiness_text):
        cursor = -1
        for item in ordered:
            position = text.find(item)
            assert position > cursor
            cursor = position

    assert "A failed step must stop execution." in qa_text
    assert "A failed step must not create a report artifact." in qa_text


def test_failure_success_and_future_unit_test_scope_are_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

    qa_required = [
        "return a non-zero exit code",
        "write a concise error to stderr",
        "avoid partial report writes",
        "avoid fallback to scanner execution",
        "avoid fallback to sample data",
        "avoid fallback to current working directory discovery",
        "avoid reporting success if no report was created",
        "return exit code `0`",
        "create exactly one visible report artifact through the renderer",
        "write under `05_reports/`",
        "optionally print the created report path if `--print-output-path` is supplied",
        "avoid printing private local paths inside report content",
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

    readiness_required = [
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

    for item in qa_required:
        assert item in qa_text

    for item in readiness_required:
        assert item in readiness_text

def test_explicit_non_goals_are_preserved() -> None:
    qa_text = _text(QA_GATE_DOC)
    readiness_text = _text(READINESS_DOC)

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
        assert item in qa_text
        assert item in readiness_text


def test_validation_evidence_and_result_are_declared() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "runtime CLI integration implementation readiness test passing",
        "runtime CLI integration contract test passing",
        "runtime CLI integration contract QA gate test passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate test passing",
        "supporting readiness and contract tests passing",
        "Python compile passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS_QA_GATE_PASS_READY_FOR_CONTROLLED_CLI_IMPLEMENTATION",
    ]

    for item in required:
        assert item in qa_text
