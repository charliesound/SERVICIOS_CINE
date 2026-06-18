from pathlib import Path
import json


PHASE = "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.FAILURE_PATH.CONTRACT.V1"

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_failure_path_contract_v1.md")
SCANNER = Path("scripts/cid_media_agent_scan.py")
PLACEHOLDER_QA = Path("docs/product/local_media_agent/cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_qa_gate_v1.md")
PLACEHOLDER_QA_TEST = Path("tests/unit/test_cid_local_media_agent_scanner_cli_ffprobe_synthetic_placeholders_qa_gate.py")
FIXTURE_ROOT = Path("tests/fixtures/local_media_agent/ffprobe_synthetic")
MANIFEST = FIXTURE_ROOT / "fixture_manifest.json"

EXPECTED_ERROR_CODES = {
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
}

EXPECTED_PLACEHOLDERS = {
    "synthetic_invalid_media_placeholder.bin",
    "synthetic_permission_denied_placeholder.dat",
    "synthetic_unsupported_media_placeholder.txt",
}


def _doc_text():
    return DOC.read_text(encoding="utf-8")


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_failure_path_contract_document_exists_and_declares_phase():
    text = _doc_text()

    assert "ffprobe Failure Path Contract v1" in text
    assert PHASE in text
    assert "This phase is documentation/test-only." in text
    assert "It does not authorize ffprobe execution yet." in text


def test_contract_defines_required_failure_cases():
    text = _doc_text()

    required_cases = [
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

    for case in required_cases:
        assert case in text


def test_contract_reserves_expected_error_codes():
    text = _doc_text()

    for code in EXPECTED_ERROR_CODES:
        assert code in text


def test_contract_defines_safe_future_output_shape():
    text = _doc_text()

    required_fields = [
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

    for field in required_fields:
        assert field in text


def test_contract_keeps_runtime_execution_out_of_scope():
    text = _doc_text()

    required = [
        "This phase must not implement runtime probing.",
        "This phase must not call ffprobe.",
        "This phase must not call ffmpeg.",
        "This phase must not add subprocess execution.",
        "This phase must not modify `scripts/cid_media_agent_scan.py`.",
        "This phase must not add worker code.",
        "This phase must not add backend endpoints.",
        "This phase must not modify CID SaaS runtime.",
    ]

    for phrase in required:
        assert phrase in text


def test_contract_keeps_database_and_infrastructure_out_of_scope():
    text = _doc_text()

    required = [
        "backend runtime",
        "database models",
        "migrations",
        "Docker",
        "frontend",
        "billing",
        "workers",
        "queue execution",
        "external storage",
        "cloud services",
    ]

    for phrase in required:
        assert phrase in text


def test_contract_links_to_existing_synthetic_placeholders_without_creating_media():
    text = _doc_text()

    for name in EXPECTED_PLACEHOLDERS:
        assert name in text

    assert "These files are not real video." in text
    assert "These files are not real audio." in text
    assert "These files must remain tiny synthetic non-media payloads." in text


def test_existing_placeholder_package_remains_valid():
    manifest = _manifest()
    entries = manifest["synthetic_placeholders"]

    assert len(entries) == 3
    assert {entry["relative_path"] for entry in entries} == EXPECTED_PLACEHOLDERS

    for entry in entries:
        assert entry["media_kind"] == "not_media"
        assert entry["must_not_be_valid_media"] is True
        assert entry["must_not_execute_ffprobe"] is True
        assert entry["must_not_execute_ffmpeg"] is True


def test_contract_does_not_introduce_private_path_or_database_literals():
    text = _doc_text().lower()

    forbidden = [
        "/" + "home" + "/",
        "/" + "mnt" + "/",
        "c:" + "\\",
        "\\" + "wsl",
        "." + "env",
        "." + "sq" + "lite",
        "." + "db",
    ]

    for token in forbidden:
        assert token not in text


def test_contract_does_not_modify_scanner_runtime_or_add_execution_calls():
    scanner_text = SCANNER.read_text(encoding="utf-8").lower()

    assert "subprocess.run" not in scanner_text
    assert "subprocess.popen" not in scanner_text
    assert "ffmpeg" not in scanner_text


def test_placeholder_qa_gate_remains_present():
    assert PLACEHOLDER_QA.exists()
    assert PLACEHOLDER_QA_TEST.exists()


def test_future_implementation_gate_is_explicit():
    text = _doc_text()

    required = [
        "a controlled command wrapper contract",
        "timeout handling",
        "safe stderr/stdout redaction",
        "tenant/client privacy rules",
        "no absolute path leakage",
        "deterministic failure fixtures",
        "human-readable safe errors",
        "tests for each failure code",
    ]

    for phrase in required:
        assert phrase in text
