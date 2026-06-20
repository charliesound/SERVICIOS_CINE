from pathlib import Path


QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_qa_gate_v1.md"
)
CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_runtime_cli_integration_contract_v1.md"
)
CONTRACT_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "runtime_cli_integration_contract.py"
)
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")
RUNTIME_QA_TEST = Path(
    "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_"
    "controlled_runtime_implementation_qa_gate.py"
)
PLANNED_CLI = Path("scripts/local_media_agent/visible_report_runtime_cli.py")
PLANNED_CLI_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_and_files_under_qa_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert CONTRACT_DOC.exists()
    assert CONTRACT_TEST.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()
    assert RUNTIME_QA_TEST.exists()

    text = _text(QA_GATE_DOC)
    for required_path in (
        "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_runtime_cli_integration_contract_v1.md",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_runtime_cli_integration_contract.py",
        "scripts/local_media_agent/visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator_controlled_runtime_implementation_qa_gate.py",
    ):
        assert required_path in text


def test_source_traceability_is_complete() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    qa_required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE",
        "df5cb486638cd3511db4020d37470bfb65df3ba8",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-runtime-cli-integration-contract-v1-20260620",
    ]

    contract_required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.RUNTIME.CLI.INTEGRATION.CONTRACT.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE",
    ]

    for item in qa_required:
        assert item in qa_text

    for item in contract_required:
        assert item in contract_text


def test_qa_gate_is_docs_test_only_and_non_runtime() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "This QA gate is docs/test-only.",
        "This QA gate does not implement a CLI command.",
        "This QA gate does not modify the existing runtime generator.",
        "This QA gate does not execute the scanner.",
        "This QA gate does not use real client media.",
        "This QA gate does not execute ffprobe or ffmpeg.",
        "This QA gate does not perform network calls, SaaS upload, or database writes.",
        "This QA gate does not generate synchronization, transcription, subtitles, translations, or timeline exports.",
    ]

    for item in required:
        assert item in qa_text


def test_future_cli_is_still_not_implemented() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    assert "scripts/local_media_agent/visible_report_runtime_cli.py" in qa_text
    assert "tests/unit/test_cid_local_media_agent_visible_report_runtime_cli.py" in qa_text
    assert "This contract does not create those files." in contract_text
    assert not PLANNED_CLI.exists()
    assert not PLANNED_CLI_TEST.exists()


def test_existing_renderer_interface_and_delegation_are_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)
    source = _text(RUNTIME_GENERATOR)

    interface = "generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path"
    delegation = "generate_visible_report(scanner_result, output_root)"

    assert interface in qa_text
    assert interface in contract_text
    assert f"def {interface}:" in source
    assert delegation in qa_text
    assert delegation in contract_text
    assert "The CLI contract must not authorize a wider runtime interface." in qa_text


def test_cli_command_shape_is_explicit_and_local_only() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    required = [
        "python scripts/local_media_agent/visible_report_runtime_cli.py --scanner-result-json <controlled_json_path> --output-root <authorized_output_root>",
        "The contract must require explicit arguments.",
        "The contract must forbid implicit current working directory input discovery.",
        "The contract must forbid URL input, SaaS identifiers, environment secrets, and remote fetch behavior.",
    ]

    for item in required:
        assert item in qa_text

    for item in (
        "The command must require explicit arguments.",
        "The command must not use implicit current working directory input discovery.",
        "The command must not accept URLs.",
        "The command must not accept SaaS identifiers.",
        "The command must not read environment secrets.",
    ):
        assert item in contract_text


def test_cli_arguments_are_bounded() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    required_flags = [
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

    for flag in required_flags:
        assert flag in qa_text
        assert flag in contract_text


def test_input_contract_is_controlled_json_only() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    required = [
        "already-created controlled scanner result JSON file",
        "local JSON parsing",
        "mutation",
        "inference",
        "silent correction",
        "warning hiding",
        "conversion of roadmap modules into generated deliverables",
    ]

    for item in required:
        assert item in qa_text

    for item in (
        "The future CLI must accept only an already-created controlled scanner result JSON file.",
        "The future CLI must parse JSON locally.",
        "mutate scanner result data",
        "infer missing facts",
        "silently correct invalid counts",
        "hide warnings",
        "convert roadmap modules into generated deliverables",
    ):
        assert item in contract_text


def test_output_contract_is_one_visible_report_only() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

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
        assert item in qa_text
        assert item in contract_text


def test_validation_order_is_locked() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

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

    for text in (qa_text, contract_text):
        cursor = -1
        for item in ordered:
            position = text.find(item)
            assert position > cursor
            cursor = position

    assert "Any failed validation step must stop execution and prevent report artifact creation." in qa_text
    assert "Any failed validation step must stop execution and prevent report artifact creation." in contract_text


def test_failure_contract_is_fail_closed() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    required = [
        "missing required arguments",
        "unsupported flags",
        "unsafe input path",
        "unsafe output path",
        "missing JSON",
        "invalid JSON",
        "non-object JSON root",
        "runtime generator validation failure",
        "unauthorized output path",
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
        assert item in qa_text

    for item in (
        "required arguments are missing",
        "unsupported flags are provided",
        "input path is unsafe",
        "output path is unsafe",
        "JSON is missing",
        "JSON is invalid",
        "JSON root is not an object",
        "runtime generator validation fails",
        "output path is not authorized",
    ):
        assert item in contract_text


def test_privacy_and_determinism_are_preserved() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

    required = [
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
        "deterministic for the same controlled JSON input and output root",
        "wall-clock timestamps",
        "machine identifiers",
        "local absolute paths into report content",
        "environment-dependent ordering",
    ]

    for item in required:
        assert item in qa_text
        assert item in contract_text


def test_explicit_non_goals_block_product_overclaiming() -> None:
    qa_text = _text(QA_GATE_DOC)
    contract_text = _text(CONTRACT_DOC)

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
        assert item in contract_text


def test_validation_evidence_and_gate_result_are_declared() -> None:
    qa_text = _text(QA_GATE_DOC)

    required = [
        "runtime CLI integration contract test passing",
        "runtime generator test passing",
        "controlled runtime implementation QA gate test passing",
        "implementation readiness tests passing",
        "runtime generator contract tests passing",
        "Python compile passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_RUNTIME_CLI_INTEGRATION_CONTRACT_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_IMPLEMENTATION_READINESS",
    ]

    for item in required:
        assert item in qa_text
