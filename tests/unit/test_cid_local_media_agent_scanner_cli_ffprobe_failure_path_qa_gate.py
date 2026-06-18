from pathlib import Path


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.QA.GATE.V1"

QA_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md")
CONTRACT_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md")
CONTRACT_TEST = Path("tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract.py")
SCANNER = Path("scripts/cid_media_agent_scan.py")

EXPECTED_FAILURE_CASES = [
    "ffprobe is not available on the machine.",
    "ffprobe is available but returns a non-zero exit status.",
    "ffprobe returns empty stdout.",
    "ffprobe returns malformed JSON.",
    "ffprobe times out.",
    "ffprobe is denied access to a file.",
    "The input path points to a non-media placeholder.",
    "The input path points to an unsupported file.",
    "The input path points to a missing file.",
    "The input path is outside the allowed project root.",
    "The input path is a directory instead of a file.",
    "The input path cannot be safely represented in reports.",
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

EXPECTED_OUTPUT_FIELDS = [
    "probe_status",
    "error_code",
    "safe_reason",
    "media_probe_attempted",
    "tool_name",
    "tool_available",
    "exit_code",
    "stdout_present",
    "stderr_present",
    "timed_out",
    "safe_file_label",
    "relative_path_allowed",
    "metadata_partial",
    "human_review_required",
]


def _qa_text():
    return QA_DOC.read_text(encoding="utf-8")


def _contract_text():
    return CONTRACT_DOC.read_text(encoding="utf-8")


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


def test_qa_gate_document_exists_and_declares_phase():
    text = _qa_text()

    assert "Failure Path QA Gate v1" in text
    assert PHASE in text
    assert "This phase is documentation/test-only." in text
    assert "It does not authorize ffprobe execution." in text


def test_source_contract_and_test_exist():
    assert CONTRACT_DOC.exists()
    assert CONTRACT_TEST.exists()


def test_source_contract_keeps_all_required_failure_cases():
    text = _contract_text()

    for case in EXPECTED_FAILURE_CASES:
        assert case in text


def test_source_contract_keeps_all_required_error_codes():
    text = _contract_text()

    for code in EXPECTED_ERROR_CODES:
        assert code in text


def test_source_contract_keeps_all_required_output_fields():
    text = _contract_text()

    for field in EXPECTED_OUTPUT_FIELDS:
        assert field in text


def test_source_contract_keeps_runtime_execution_out_of_scope():
    text = _contract_text()

    required = [
        "This phase must not implement runtime probing.",
        "This phase must not call ffprobe.",
        "This phase must not call ffmpeg.",
        "This phase must not add subprocess execution.",
        "This phase must not modify `scripts/cid_media_agent_scan.py`.",
        "This phase must not modify CID SaaS runtime.",
    ]

    for phrase in required:
        assert phrase in text


def test_qa_gate_keeps_runtime_execution_out_of_scope():
    text = _qa_text()

    required = [
        "This QA gate does not execute ffprobe.",
        "This QA gate does not execute ffmpeg.",
        "This QA gate does not add subprocess execution.",
        "This QA gate does not modify scanner runtime.",
        "This QA gate does not modify backend runtime.",
        "This QA gate does not modify database models.",
        "This QA gate does not create media files.",
        "This QA gate does not create report outputs.",
    ]

    for phrase in required:
        assert phrase in text


def test_qa_gate_defines_future_implementation_gate_without_authorizing_it():
    text = _qa_text()

    required = [
        "a controlled command wrapper",
        "timeout rules",
        "safe stdout and stderr redaction",
        "deterministic failure fixtures",
        "safe labels",
        "human-readable error mapping",
        "tests for every failure code",
        "It does not authorize ffprobe execution.",
    ]

    for phrase in required:
        assert phrase in text


def test_scanner_runtime_still_has_no_media_execution_subprocess():
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "ffmpeg" not in scanner_text


def test_qa_gate_source_has_no_sensitive_literal_tokens():
    combined = (_qa_text() + "\n" + _contract_text()).lower()

    for token in _safe_token_fragments():
        assert token not in combined


def test_qa_gate_mentions_existing_guards_without_forbidden_database_literal():
    text = _qa_text().lower()

    assert "wsl guard passes" in text
    assert "database-regression guard passes" in text
    assert "sq" + "lite" not in text


def test_qa_gate_has_no_runtime_or_infrastructure_non_goals_missing():
    text = _qa_text()

    required_non_goals = [
        "implement a command wrapper",
        "implement subprocess calls",
        "run media probes",
        "call external binaries",
        "add scanner CLI flags",
        "add JSON report output",
        "add backend endpoints",
        "add workers",
        "add queue behavior",
        "add billing behavior",
        "add storage behavior",
    ]

    for phrase in required_non_goals:
        assert phrase in text
