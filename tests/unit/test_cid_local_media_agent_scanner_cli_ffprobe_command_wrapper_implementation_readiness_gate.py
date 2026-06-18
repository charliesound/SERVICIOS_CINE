from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_implementation_readiness_gate_v1.md")

FAILURE_PATH_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md")
FAILURE_PATH_QA_GATE = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_qa_gate_v1.md")
WRAPPER_CONTRACT = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_contract_v1.md")
WRAPPER_QA_GATE = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_command_wrapper_qa_gate_v1.md")

SCANNER = Path("scripts/cid_media_agent_scan.py")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _lower(path: Path) -> str:
    return _read(path).lower()


def test_implementation_readiness_gate_document_exists():
    assert DOC.exists()
    text = _read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.IMPLEMENTATION.READINESS.GATE.V1" in text


def test_previous_contract_chain_exists():
    for path in [
        FAILURE_PATH_CONTRACT,
        FAILURE_PATH_QA_GATE,
        WRAPPER_CONTRACT,
        WRAPPER_QA_GATE,
    ]:
        assert path.exists(), f"Missing required prior artifact: {path}"


def test_previous_contract_chain_is_referenced_by_readiness_gate():
    text = _read(DOC)
    for path in [
        FAILURE_PATH_CONTRACT,
        FAILURE_PATH_QA_GATE,
        WRAPPER_CONTRACT,
        WRAPPER_QA_GATE,
    ]:
        assert str(path) in text


def test_gate_is_documentary_and_test_only():
    text = _lower(DOC)
    assert "documentary and test-only readiness gate" in text
    assert "does not implement the wrapper" in text
    assert "does not modify scanner runtime" in text


def test_gate_blocks_media_tool_execution_and_media_processing():
    text = _lower(DOC)
    required = [
        "no ffprobe execution",
        "no ffmpeg execution",
        "no real media processing",
        "no real media creation",
        "no private pilot material",
        "no client footage",
        "no production footage",
    ]
    for marker in required:
        assert marker in text


def test_gate_blocks_runtime_and_saas_changes():
    text = _lower(DOC)
    required = [
        "no process execution code added to runtime",
        "no scanner runtime modification",
        "no saas backend modification",
        "database",
        "alembic",
        "docker",
        "frontend",
        "billing",
        "workers",
        "storage",
        "cloud changes",
    ]
    for marker in required:
        assert marker in text


def test_gate_requires_structured_inputs_for_future_phase():
    text = _lower(DOC)
    assert "structured inputs remain mandatory" in text
    assert "must not accept arbitrary command text" in text


def test_gate_requires_command_argument_list_for_future_phase():
    text = _lower(DOC)
    assert "command argument list remains mandatory" in text
    assert "shell command strings remain forbidden" in text


def test_gate_requires_timeout_policy_for_future_phase():
    text = _lower(DOC)
    assert "timeout remains mandatory" in text
    assert "bounded timeout" in text
    assert "safe normalized failure result" in text


def test_gate_requires_output_redaction_for_future_phase():
    text = _lower(DOC)
    assert "stdout and stderr redaction remains mandatory" in text
    assert "reports, logs, ui, json, markdown" in text


def test_gate_preserves_failure_path_error_codes_for_future_phase():
    text = _lower(DOC)
    assert "failure-path error codes remain mandatory" in text
    assert "preserve the error code vocabulary" in text


def test_gate_requires_safe_result_shape_for_future_phase():
    text = _lower(DOC)
    assert "safe result shape remains mandatory" in text
    assert "normalized safe result object" in text


def test_gate_does_not_authorize_implementation():
    text = _lower(DOC)
    assert "does not authorize implementation" in text
    assert "implementation must be opened as a separate phase" in text
    assert "human approval" in text


def test_gate_recommends_test_double_contract_next():
    text = _read(DOC)
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.COMMAND.WRAPPER.TEST.DOUBLE.CONTRACT.V1" in text
    assert "test-double boundary" in text


def test_scanner_runtime_still_has_no_external_execution_tokens():
    assert SCANNER.exists()
    scanner_text = _read(SCANNER)

    forbidden_tokens = [
        "sub" + "process.run",
        "sub" + "process.Popen",
        "ff" + "mpeg",
    ]

    for token in forbidden_tokens:
        assert token not in scanner_text


def test_readiness_gate_does_not_introduce_blocked_database_literal_or_sensitive_markers():
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
