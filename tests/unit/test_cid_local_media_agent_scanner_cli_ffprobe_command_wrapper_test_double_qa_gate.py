from pathlib import Path


QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_qa_gate_v1.md"
)

CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract_v1.md"
)

CONTRACT_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract.py"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_document_exists():
    assert QA_DOC.exists()


def test_phase_identity_is_declared():
    text = read(QA_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1" in text
    assert "ffprobe Command Wrapper Test Double QA Gate v1" in text


def test_qa_gate_is_documentation_and_test_only():
    text = read(QA_DOC)
    required = [
        "documentation/test-only",
        "does not implement the test double",
        "does not implement the wrapper",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add subprocess usage",
        "does not modify scanner runtime",
    ]
    for item in required:
        assert item in text


def test_qa_gate_audits_contract_and_sanitized_phase():
    text = read(QA_DOC)
    required = [
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.SANITIZED.V1",
        str(CONTRACT_DOC),
        str(CONTRACT_TEST),
    ]
    for item in required:
        assert item in text


def test_required_qa_findings_are_declared():
    text = read(QA_DOC)
    findings = [
        "The test double boundary is explicit",
        "The future command runner is injectable",
        "Unit tests must use the test double",
        "Real executable access remains outside unit tests",
        "Real executable access requires a separate explicit gate",
        "All required simulation modes are declared",
        "All failure path vocabulary is covered",
        "The result shape is structured and safe",
        "Determinism is required",
        "Privacy restrictions are explicit",
        "Raw commands must remain hidden",
        "Redaction must be required",
        "Safe report labels must be required",
        "Real media metadata must not be emitted",
        "Real filenames and absolute paths must not be emitted",
        "No implementation is authorized by this gate",
        "No runtime scanner file is modified by this gate",
    ]
    for item in findings:
        assert item in text


def test_required_simulation_coverage_is_complete():
    text = read(QA_DOC)
    modes = [
        "SUCCESS_VALID_JSON",
        "FFPROBE_NOT_AVAILABLE",
        "FFPROBE_NON_ZERO_EXIT",
        "FFPROBE_EMPTY_STDOUT",
        "FFPROBE_INVALID_JSON",
        "FFPROBE_TIMEOUT",
        "FFPROBE_ACCESS_DENIED",
        "INPUT_NOT_MEDIA",
        "INPUT_UNSUPPORTED",
        "INPUT_MISSING",
        "INPUT_OUTSIDE_ALLOWED_ROOT",
        "INPUT_IS_DIRECTORY",
        "SAFE_REPORT_LABEL_REQUIRED",
    ]
    for mode in modes:
        assert mode in text


def test_runtime_prohibition_is_explicit():
    text = read(QA_DOC)
    prohibited = [
        "command execution",
        "ffprobe execution",
        "ffmpeg execution",
        "subprocess usage",
        "shell execution",
        "reading real media files",
        "scanning real client folders",
        "changing `scripts/cid_media_agent_scan.py`",
        "changing files under `src/`",
        "backend, frontend, Alembic, Docker, billing, workers, queue, storage, or cloud behavior",
    ]
    for item in prohibited:
        assert item in text


def test_acceptance_decision_does_not_authorize_runtime():
    text = read(QA_DOC)
    required = [
        "does not authorize real ffprobe execution",
        "does not authorize scanner runtime changes",
        "only authorizes a future test-double implementation planning phase",
        "separate explicit gate",
    ]
    for item in required:
        assert item in text


def test_contract_file_still_exists():
    assert CONTRACT_DOC.exists()


def test_contract_test_file_still_exists():
    assert CONTRACT_TEST.exists()


def test_contract_contains_required_boundary_language():
    text = read(CONTRACT_DOC)
    required = [
        "receive a command-runner dependency",
        "explicit boundary",
        "without invoking the operating system",
        "structured results only",
        "injectable command-runner boundary",
    ]
    for item in required:
        assert item in text


def test_contract_contains_required_result_shape():
    text = read(CONTRACT_DOC)
    fields = [
        "tool_name",
        "requested_args",
        "exit_code",
        "stdout_text",
        "stderr_text",
        "duration_ms",
        "timed_out",
        "error_kind",
        "safe_report_label",
        "redaction_applied",
        "raw_command_hidden",
        "created_by_test_double",
    ]
    for field in fields:
        assert field in text


def test_contract_contains_all_failure_modes():
    text = read(CONTRACT_DOC)
    modes = [
        "SUCCESS_VALID_JSON",
        "FFPROBE_NOT_AVAILABLE",
        "FFPROBE_NON_ZERO_EXIT",
        "FFPROBE_EMPTY_STDOUT",
        "FFPROBE_INVALID_JSON",
        "FFPROBE_TIMEOUT",
        "FFPROBE_ACCESS_DENIED",
        "INPUT_NOT_MEDIA",
        "INPUT_UNSUPPORTED",
        "INPUT_MISSING",
        "INPUT_OUTSIDE_ALLOWED_ROOT",
        "INPUT_IS_DIRECTORY",
        "SAFE_REPORT_LABEL_REQUIRED",
    ]
    for mode in modes:
        assert mode in text


def test_contract_privacy_requirements_are_present():
    text = read(CONTRACT_DOC)
    required = [
        "real media filenames",
        "real directory names",
        "absolute local paths",
        "private user names",
        "raw command strings",
        "real media metadata",
        "Only safe labels and synthetic placeholder values are allowed",
    ]
    for item in required:
        assert item in text


def test_contract_test_no_longer_self_matches_import_os_literal():
    text = read(CONTRACT_TEST)

    raw_import_os = '"import ' + 'o' + 's",'
    raw_from_os = '"from ' + 'o' + 's",'
    sanitized_import_os = '"import " + "o" + "s",'
    sanitized_from_os = '"from " + "o" + "s",'

    assert raw_import_os not in text
    assert raw_from_os not in text
    assert sanitized_import_os in text
    assert sanitized_from_os in text


def test_next_phase_is_readiness_gate():
    text = read(QA_DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.IMPLEMENTATION.READINESS.GATE.V1" in text


def test_qa_gate_test_file_does_not_import_external_command_modules():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "o" + "s",
        "from " + "o" + "s",
        "P" + "open(",
        "shell" + "=",
    ]
    for item in forbidden:
        assert item not in source
