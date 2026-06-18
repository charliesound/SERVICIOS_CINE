from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_test_double_minimal_implementation_plan_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_plan_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.V1" in text
    assert "ffprobe Command Wrapper Test Double Minimal Implementation Plan v1" in text


def test_phase_is_planning_only():
    text = read_doc()
    required = [
        "planning-only phase",
        "does not implement the test double",
        "does not implement the command wrapper",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not add subprocess usage",
        "does not modify scanner runtime",
        "does not process media",
    ]
    for item in required:
        assert item in text


def test_future_implementation_target_is_test_support_only():
    text = read_doc()
    required = [
        "pure-Python test support helper",
        "deterministic",
        "in-process",
        "side-effect free",
        "must not call the operating system",
        "must not inspect installed binaries",
        "must not read real media files",
        "must not scan folders",
        "must not import the subprocess module",
        "must not execute external commands",
    ]
    for item in required:
        assert item in text


def test_future_location_blocks_runtime_paths():
    text = read_doc()
    required = [
        "tests/support/local_media_agent/ffprobe_command_runner_test_double.py",
        "must not be placed in runtime scanner code",
        "scripts/cid_media_agent_scan.py",
        "files under `src/`",
        "backend code",
        "frontend code",
        "Alembic migrations",
        "Docker files",
        "billing code",
        "workers",
        "queue",
        "storage",
        "cloud integration",
    ]
    for item in required:
        assert item in text


def test_required_future_result_shape_is_complete():
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


def test_required_future_modes_are_complete():
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


def test_minimal_future_behavior_is_safe_and_deterministic():
    text = read_doc()
    required = [
        "generate synthetic stdout only for `SUCCESS_VALID_JSON`",
        "generate synthetic stderr only when needed",
        "keep `raw_command_hidden` true",
        "keep `redaction_applied` true",
        "require a safe report label",
        "avoid real paths",
        "avoid real filenames",
        "avoid real media metadata",
        "avoid nondeterministic timing",
        "use fixed synthetic duration values",
        "same output for the same mode and safe label",
    ]
    for item in required:
        assert item in text


def test_required_future_unit_tests_are_defined():
    text = read_doc()
    required = [
        "one success result",
        "every failure mode",
        "deterministic repeated calls",
        "safe label requirement",
        "hidden raw command",
        "redaction flag",
        "no private path leakage",
        "no real media metadata leakage",
        "no subprocess module import",
        "no ffprobe execution",
        "no ffmpeg execution",
        "no scanner runtime changes",
    ]
    for item in required:
        assert item in text


def test_explicit_non_authorization_is_complete():
    text = read_doc()
    forbidden = [
        "creating the test double implementation now",
        "implementing the command wrapper",
        "executing ffprobe",
        "executing ffmpeg",
        "adding subprocess usage",
        "touching scanner runtime",
        "touching SaaS runtime",
        "touching database behavior",
        "touching deployment behavior",
        "touching installer behavior",
        "scanning real client media",
    ]
    for item in forbidden:
        assert item in text


def test_acceptance_criteria_keep_phase_documental():
    text = read_doc()
    criteria = [
        "phase remains documentation/test-only",
        "only this document and its unit test are changed",
        "future implementation remains constrained to test support",
        "no runtime file is changed",
        "no external command execution is introduced",
        "no subprocess usage is introduced",
        "no media processing is introduced",
        "all required result fields are preserved",
        "all required modes are preserved",
        "next phase remains explicit and gated",
    ]
    for item in criteria:
        assert item in text


def test_next_phase_is_plan_qa_gate():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.MINIMAL.IMPLEMENTATION.PLAN.QA.GATE.V1" in text


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
