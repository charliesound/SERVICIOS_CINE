from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_v1.md"
)
SOURCE_QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_controlled_runtime_implementation_qa_gate_v1.md"
)
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")
RUNTIME_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "controlled_runtime_implementation_qa_gate.py"
)
PLANNED_CLI = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
PLANNED_CLI_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py")


def _text(path: Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_doc_exists_and_source_files_exist() -> None:
    assert DOC.exists()
    assert SOURCE_QA_GATE_DOC.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()
    assert RUNTIME_QA_TEST.exists()


def test_source_traceability_is_complete() -> None:
    text = _text()

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_RUNTIME_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT",
        "1bf737f9b04eb785944733fa7b6ae267ce1db045",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-runtime-implementation-qa-gate-v1-20260620",
    ]

    for item in required:
        assert item in text


def test_contract_is_docs_test_only_and_non_runtime() -> None:
    text = _text()

    required = [
        "This phase is docs/test-only.",
        "This phase does not implement a CLI command.",
        "This phase does not modify the existing runtime generator.",
        "This phase does not execute the scanner.",
        "This phase does not use real client media.",
        "This phase does not execute ffprobe or ffmpeg.",
        "This phase does not perform network calls, SaaS upload, or database writes.",
        "This phase does not generate synchronization, transcription, subtitles, or timeline exports.",
    ]

    for item in required:
        assert item in text


def test_existing_runtime_interface_is_preserved() -> None:
    text = _text()
    source = RUNTIME_GENERATOR.read_text(encoding="utf-8")

    interface = "generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path"
    assert interface in text
    assert f"def {interface}:" in source

    for required_path in (
        "scripts/local_media_agent/visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py",
    ):
        assert required_path in text


def test_future_cli_files_are_planned_but_not_created() -> None:
    text = _text()

    assert "scripts/local_media_agent/visible_report_runtime_cli.py" in text
    assert "tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py" in text
    assert "This contract does not create those files." in text
    assert not PLANNED_CLI.exists()
    assert not PLANNED_CLI_TEST.exists()


def test_future_cli_command_shape_is_explicit_and_argument_driven() -> None:
    text = _text()

    required = [
        "python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>",
        "The command must require explicit arguments.",
        "The command must not use implicit current working directory input discovery.",
        "The command must not scan folders.",
        "The command must not probe media.",
        "The command must not fetch remote input.",
        "The command must not accept URLs.",
        "The command must not accept SaaS identifiers.",
        "The command must not read environment secrets.",
    ]

    for item in required:
        assert item in text


def test_required_and_forbidden_future_cli_arguments_are_declared() -> None:
    text = _text()

    required_flags = [
        "--scanner-result-json",
        "--output-root",
    ]
    optional_flags = [
        "--dry-run",
        "--strict",
        "--print-output-path",
    ]
    forbidden_flags = [
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

    for flag in required_flags + optional_flags + forbidden_flags:
        assert flag in text


def test_future_cli_input_contract_delegates_to_runtime_without_mutation_or_inference() -> None:
    text = _text()

    required = [
        "The future CLI must accept only an already-created controlled scanner result JSON file.",
        "The future CLI must parse JSON locally.",
        "generate_visible_report(scanner_result, output_root)",
        "mutate scanner result data",
        "infer missing facts",
        "silently correct invalid counts",
        "hide warnings",
        "convert roadmap modules into generated deliverables",
    ]

    for item in required:
        assert item in text


def test_future_cli_output_contract_is_limited_to_visible_report_only() -> None:
    text = _text()

    required = [
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


def test_future_cli_validation_order_is_declared() -> None:
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

    assert "Any failed validation step must stop execution and prevent report artifact creation." in text


def test_future_cli_failure_contract_is_fail_closed() -> None:
    text = _text()

    required = [
        "required arguments are missing",
        "unsupported flags are provided",
        "input path is unsafe",
        "output path is unsafe",
        "JSON is missing",
        "JSON is invalid",
        "JSON root is not an object",
        "runtime generator validation fails",
        "output path is not authorized",
        "non-zero process return code",
        "concise stderr error",
        "no report artifact written",
        "partial report writes",
        "fallback to scanner execution",
        "fallback to sample data",
        "fallback to current working directory discovery",
        "silent success",
        "client-facing report claims",
    ]

    for item in required:
        assert item in text


def test_future_cli_privacy_and_determinism_contracts_are_strict() -> None:
    text = _text()

    privacy_markers = [
        "local user names",
        "machine names",
        "absolute system paths",
        "repository paths",
        "real client material",
        "real shoot names",
        "private project titles",
        "private filenames from real shoots",
        "/mnt/",
        "Windows drive paths",
        "UNC paths",
        "DESKTOP-",
        "harliesound",
        "SERVICIOS_CINE",
    ]
    determinism_markers = [
        "deterministic for the same controlled JSON input and output root",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths into report content",
        "environment-dependent ordering",
        "The runtime renderer remains responsible for deterministic Markdown content.",
    ]

    for item in privacy_markers + determinism_markers:
        assert item in text


def test_explicit_non_goals_block_scope_creep() -> None:
    text = _text()

    forbidden_scope = [
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

    for item in forbidden_scope:
        assert item in text


def test_contract_result_is_declared() -> None:
    text = _text()

    assert (
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE"
        in text
    )
