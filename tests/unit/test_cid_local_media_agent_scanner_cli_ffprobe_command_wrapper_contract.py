from pathlib import Path


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.CONTRACT.V1"

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_contract_v1.md")
FAILURE_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md")
FAILURE_QA_GATE = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md")
SCANNER = Path("scripts/cid_media_agent_scan.py")

EXPECTED_INPUTS = [
    "project_root",
    "candidate_relative_path",
    "timeout_seconds",
    "allowed_probe_fields",
    "redaction_policy",
    "max_stdout_bytes",
    "max_stderr_bytes",
    "human_review_required_by_default",
]

EXPECTED_RESULT_FIELDS = [
    "wrapper_status",
    "probe_status",
    "error_code",
    "safe_reason",
    "safe_file_label",
    "candidate_relative_path",
    "tool_name",
    "tool_available",
    "media_probe_attempted",
    "timeout_seconds",
    "timed_out",
    "exit_code",
    "stdout_present",
    "stderr_present",
    "stdout_bytes_retained",
    "stderr_bytes_retained",
    "metadata_partial",
    "redaction_applied",
    "human_review_required",
]

EXPECTED_ERROR_CODES = [
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


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def _safe_token_fragments():
    return [
        "/" + "home" + "/",
        "/" + "mnt" + "/",
        "c:" + "\\",
        "\\" + "wsl",
        "." + "env",
        "." + "sq" + "lite",
        "." + "db",
    ]


def test_wrapper_contract_document_exists_and_declares_phase():
    text = _doc_text()

    assert "ffprobe Command Wrapper Contract v1" in text
    assert PHASE in text
    assert "This phase is documentation/test-only." in text
    assert "It does not authorize ffprobe execution." in text


def test_wrapper_contract_references_failure_path_contracts():
    text = _doc_text()

    assert FAILURE_CONTRACT.exists()
    assert FAILURE_QA_GATE.exists()
    assert str(FAILURE_CONTRACT) in text
    assert str(FAILURE_QA_GATE) in text


def test_wrapper_contract_keeps_runtime_out_of_scope():
    text = _doc_text()

    required = [
        "This phase does not execute ffprobe.",
        "This phase does not execute ffmpeg.",
        "This phase does not add subprocess execution.",
        "This phase does not modify scanner runtime.",
        "This phase does not inspect real client media.",
        "This phase does not create media files.",
    ]

    for phrase in required:
        assert phrase in text


def test_wrapper_contract_defines_structured_inputs_only():
    text = _doc_text()

    for field in EXPECTED_INPUTS:
        assert field in text

    forbidden_acceptance = [
        "The wrapper must not accept shell strings.",
        "The wrapper must not accept arbitrary command fragments.",
        "The wrapper must not accept user-provided executable paths.",
        "The wrapper must not accept network URLs.",
    ]

    for phrase in forbidden_acceptance:
        assert phrase in text


def test_wrapper_contract_defines_command_policy_without_implementation():
    text = _doc_text()

    required = [
        "A later implementation must build commands as an argument list.",
        "A later implementation must not use shell execution.",
        "A later implementation must not interpolate user text into a shell command.",
        "A later implementation must not inherit unsafe environment behavior.",
        "A later implementation must not follow paths outside the approved root.",
        "A later implementation must not write media-derived data outside the approved output root.",
    ]

    for phrase in required:
        assert phrase in text


def test_wrapper_contract_defines_timeout_policy():
    text = _doc_text()

    required = [
        "default timeout",
        "maximum timeout",
        "timeout error code",
        "timeout safe reason",
        "timeout cleanup behavior",
        "no retry by default",
        "Timeouts must map to `FFPROBE_TIMEOUT`.",
    ]

    for phrase in required:
        assert phrase in text


def test_wrapper_contract_defines_redaction_policy():
    text = _doc_text()

    required = [
        "absolute local paths",
        "private user folder fragments",
        "mounted host path fragments",
        "environment file names",
        "local database file names",
        "executable paths",
        "raw command lines",
        "raw stderr by default",
        "raw stdout by default",
        "oversized output",
        "Only safe relative labels may be retained.",
    ]

    for phrase in required:
        assert phrase in text


def test_wrapper_contract_defines_safe_result_shape():
    text = _doc_text()

    for field in EXPECTED_RESULT_FIELDS:
        assert field in text


def test_wrapper_contract_preserves_failure_path_error_codes():
    text = _doc_text()

    for code in EXPECTED_ERROR_CODES:
        assert code in text


def test_wrapper_contract_keeps_real_media_and_client_material_blocked():
    text = _doc_text()

    required = [
        "No real video is authorized.",
        "No real audio is authorized.",
        "No client material is authorized.",
        "create real media fixtures",
    ]

    for phrase in required:
        assert phrase in text


def test_future_implementation_gate_requires_safe_wrapper_tests():
    text = _doc_text()

    required = [
        "no shell execution",
        "deterministic argument list",
        "timeout handling",
        "stdout redaction",
        "stderr redaction",
        "path-policy rejection",
        "unsupported input",
        "invalid input",
        "tool unavailable",
        "safe result shape",
        "no absolute path leakage",
        "no command-line leakage",
        "human-readable safe errors",
    ]

    for phrase in required:
        assert phrase in text


def test_scanner_runtime_still_has_no_media_execution_subprocess():
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "ffmpeg" not in scanner_text


def test_wrapper_contract_has_no_sensitive_literal_tokens():
    text = _doc_text().lower()

    for token in _safe_token_fragments():
        assert token not in text


def test_wrapper_contract_non_goals_cover_runtime_and_infrastructure():
    text = _doc_text()

    required = [
        "implement a wrapper function",
        "call external binaries",
        "run media probes",
        "add scanner CLI flags",
        "add JSON report generation",
        "modify scanner runtime",
        "modify backend runtime",
        "modify database models",
        "add migrations",
        "modify Docker",
        "modify frontend",
        "add workers",
        "add queue behavior",
        "add billing behavior",
        "add storage behavior",
        "create real media fixtures",
    ]

    for phrase in required:
        assert phrase in text
