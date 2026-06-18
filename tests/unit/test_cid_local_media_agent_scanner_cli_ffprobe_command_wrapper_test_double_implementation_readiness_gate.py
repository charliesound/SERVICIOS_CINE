from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_implementation_readiness_gate_v1.md"
)

CONTRACT_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract_v1.md"
)

QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_qa_gate_v1.md"
)

CONTRACT_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_contract.py"
)

QA_GATE_TEST = Path(
    "tests/unit/"
    "test_cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_qa_gate.py"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_gate_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.IMPLEMENTATION.READINESS.GATE.V1" in text
    assert "ffprobe Command Wrapper Test Double Implementation Readiness Gate v1" in text


def test_phase_does_not_implement_anything():
    text = read(DOC)
    required = [
        "does not implement the test double",
        "does not implement the command wrapper",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add subprocess usage",
        "does not modify scanner runtime",
    ]
    for item in required:
        assert item in text


def test_inputs_review_completed_contract_and_qa_phases():
    text = read(DOC)
    phases = [
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.SANITIZED.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.IMPLEMENTATION.READINESS.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.QA.GATE.V1",
    ]
    for phase in phases:
        assert phase in text


def test_readiness_conditions_are_explicit():
    text = read(DOC)
    conditions = [
        "The test double contract exists",
        "The test double QA gate exists",
        "The sanitized contract test passes",
        "The test double QA gate test passes",
        "Required failure path modes are represented",
        "Required structured result fields are represented",
        "The injectable command-runner boundary remains explicit",
        "Unit tests are required to use the test double",
        "Real executable access remains outside unit tests",
        "Real executable access remains behind a separate explicit gate",
        "Privacy constraints remain explicit",
        "Determinism requirements remain explicit",
        "Runtime scanner changes remain blocked",
        "Real command execution remains blocked",
    ]
    for item in conditions:
        assert item in text


def test_future_implementation_constraints_block_runtime_and_process_execution():
    text = read(DOC)
    constraints = [
        "must remain minimal and local to test support",
        "must not execute external commands",
        "must not import the subprocess module",
        "must not call the operating system shell",
        "must not run ffprobe",
        "must not run ffmpeg",
        "must not read real media files",
        "must not scan real client folders",
        "must not change `scripts/cid_media_agent_scan.py`",
        "must not change files under `src/`",
        "must not change backend, frontend, Alembic, Docker, billing, workers, queue, storage, or cloud behavior",
    ]
    for item in constraints:
        assert item in text


def test_required_future_output_shape_is_complete():
    text = read(DOC)
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


def test_required_future_simulation_modes_are_complete():
    text = read(DOC)
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


def test_non_goals_are_explicit():
    text = read(DOC)
    non_goals = [
        "implement the test double",
        "implement the wrapper",
        "introduce command execution",
        "introduce subprocess usage",
        "introduce shell usage",
        "execute ffprobe",
        "execute ffmpeg",
        "process media",
        "read media metadata",
        "change runtime scanner behavior",
        "change SaaS runtime behavior",
        "change database behavior",
        "change deployment behavior",
    ]
    for item in non_goals:
        assert item in text


def test_gate_result_is_planning_only():
    text = read(DOC)
    required = [
        "READY_FOR_FUTURE_TEST_DOUBLE_IMPLEMENTATION_PLANNING_ONLY",
        "does not mean real command execution is approved",
        "does not mean scanner runtime changes are approved",
        "does not mean ffprobe execution is approved",
    ]
    for item in required:
        assert item in text


def test_next_phase_is_minimal_implementation_plan():
    text = read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1" in text


def test_referenced_files_exist():
    assert CONTRACT_DOC.exists()
    assert QA_GATE_DOC.exists()
    assert CONTRACT_TEST.exists()
    assert QA_GATE_TEST.exists()


def test_contract_and_qa_gate_keep_runtime_blockers():
    combined = read(CONTRACT_DOC) + "\n" + read(QA_GATE_DOC)
    required = [
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not modify scanner runtime",
        "Unit tests must use the test double",
        "Real executable access",
        "separate explicit gate",
    ]
    for item in required:
        assert item in combined


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
