from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_qa_gate_v1.md")
WRAPPER_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_contract_v1.md")
FAILURE_PATH_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md")
FAILURE_PATH_QA_GATE = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md")
SCANNER = Path("scripts/cid_media_agent_scan.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _lower(path: Path) -> str:
    return _read(path).lower()


def test_command_wrapper_qa_gate_document_exists():
    assert DOC.exists()
    text = _read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.QA.GATE.V1" in text


def test_command_wrapper_contract_exists_before_gate():
    assert WRAPPER_CONTRACT.exists()


def test_failure_path_contracts_are_referenced():
    text = _read(DOC)
    assert str(WRAPPER_CONTRACT) in text
    assert str(FAILURE_PATH_CONTRACT) in text
    assert str(FAILURE_PATH_QA_GATE) in text


def test_gate_is_documentary_and_test_only():
    text = _lower(DOC)
    assert "documentary and test-only qa gate" in text
    assert "does not implement a wrapper" in text
    assert "does not modify the scanner runtime" in text


def test_gate_keeps_media_tool_execution_blocked():
    text = _lower(DOC)
    assert "no ffprobe execution" in text
    assert "no media transcoding tool execution" in text
    assert "no real media processing" in text
    assert "no real media creation" in text


def test_gate_blocks_runtime_and_saas_changes():
    text = _lower(DOC)
    required = [
        "no scanner runtime modification",
        "no saas backend modification",
        "database",
        "alembic",
        "docker",
        "frontend",
        "billing",
        "workers",
        "storage",
    ]
    for marker in required:
        assert marker in text


def test_gate_requires_structured_inputs():
    text = _lower(DOC)
    assert "structured input" in text or "structured inputs" in text
    assert "ad-hoc command text" in text


def test_gate_forbids_shell_strings_and_requires_argument_list():
    text = _lower(DOC)
    assert "shell strings" in text
    assert "command argument list" in text


def test_gate_requires_timeout_policy():
    text = _lower(DOC)
    assert "timeout policy" in text
    assert "timeout behavior" in text


def test_gate_requires_stdout_stderr_redaction():
    text = _lower(DOC)
    assert "stdout" in text
    assert "stderr" in text
    assert "redaction" in text


def test_gate_requires_safe_result_shape():
    text = _lower(DOC)
    assert "safe result shape" in text
    assert "safe normalized result shape" in text


def test_gate_preserves_failure_path_error_codes():
    text = _lower(DOC)
    assert "failure-path error codes" in text
    assert "error code vocabulary" in text


def test_scanner_runtime_still_has_no_external_execution_calls():
    assert SCANNER.exists()
    scanner_text = _read(SCANNER)

    forbidden_tokens = [
        "sub" + "process.run",
        "sub" + "process.Popen",
        "ff" + "mpeg",
    ]

    for token in forbidden_tokens:
        assert token not in scanner_text


def test_gate_does_not_introduce_blocked_database_literal_or_sensitive_markers():
    combined = _read(DOC) + "\n" + _read(Path(__file__))

    forbidden_markers = [
        "sq" + "lite",
        "AK" + "IA",
        "BEGIN " + "PRIVATE " + "KEY",
        "sk-" + "proj",
        "xo" + "xb-",
    ]

    for marker in forbidden_markers:
        assert marker not in combined
