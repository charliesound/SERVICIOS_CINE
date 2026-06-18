from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_contract_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1" in text
    assert "ffprobe Command Wrapper Test Double Contract v1" in text


def test_phase_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not implement the wrapper",
        "does not implement a command runner",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not process media",
    ]
    for item in required:
        assert item in text


def test_injectable_command_runner_boundary_is_required():
    text = read_doc()
    required = [
        "receive a command-runner dependency",
        "explicit boundary",
        "without invoking the operating system",
        "structured results only",
        "injectable command-runner boundary",
    ]
    for item in required:
        assert item in text


def test_required_result_shape_is_complete():
    text = read_doc()
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


def test_required_simulation_modes_cover_failure_paths():
    text = read_doc()
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


def test_determinism_requirements_are_explicit():
    text = read_doc()
    required = [
        "deterministic",
        "same configured mode and input label",
        "same structured result",
        "must not depend on wall-clock timing",
        "filesystem state",
        "installed binaries",
        "network access",
    ]
    for item in required:
        assert item in text


def test_privacy_requirements_block_sensitive_outputs():
    text = read_doc()
    forbidden_outputs = [
        "real media filenames",
        "real directory names",
        "absolute local paths",
        "private user names",
        "raw command strings",
        "real media metadata",
        "source script text",
        "production costs",
        "shooting dates",
        "private project identifiers",
    ]
    for item in forbidden_outputs:
        assert item in text
    assert "Only safe labels and synthetic placeholder values are allowed" in text


def test_wrapper_integration_expectations_are_safe():
    text = read_doc()
    required = [
        "Unit tests must use the test double",
        "outside unit tests",
        "separate explicit gate",
        "success, error mapping, timeout handling",
        "redaction, safe labels, and failure path consistency",
    ]
    for item in required:
        assert item in text


def test_non_goals_block_runtime_and_execution():
    text = read_doc()
    non_goals = [
        "implement a command runner",
        "implement the wrapper",
        "execute ffprobe",
        "execute ffmpeg",
        "add process execution",
        "scan real media",
        "read real media files",
        "modify scanner runtime",
        "modify backend services",
        "modify frontend code",
        "modify billing, workers, queue, storage, or cloud behavior",
    ]
    for item in non_goals:
        assert item in text


def test_acceptance_criteria_are_gated():
    text = read_doc()
    criteria = [
        "only this document and its unit contract test are changed",
        "test double modes cover all required failure paths",
        "privacy constraints are explicit",
        "deterministic behavior is required",
        "future wrapper tests are required to use the test double",
        "no real command execution is authorized",
        "no runtime scanner file is modified",
    ]
    for item in criteria:
        assert item in text


def test_next_phase_is_qa_gate():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1" in text


def test_test_file_does_not_import_external_command_modules():
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
