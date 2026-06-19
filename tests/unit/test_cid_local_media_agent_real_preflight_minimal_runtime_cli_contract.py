from __future__ import annotations

import ast
from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_contract_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_contract.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
RUNTIME_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_qa_gate_v1.md")
FUTURE_CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
FUTURE_CLI_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.CONTRACT.V1"


def _doc_text() -> str:
    assert DOC.exists(), f"Missing CLI contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_cli_contract_document_exists():
    assert DOC.exists()


def test_cli_contract_contains_phase_identifier():
    assert PHASE in _doc_text()


def test_cli_contract_is_documentation_test_only():
    text = _doc_text().lower()
    assert "documentation/test-only" in text
    assert "does not create cli runtime code" in text
    assert "does not modify the existing real preflight runtime" in text


def test_cli_contract_depends_on_minimal_runtime_qa_gate():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1" in text
    assert "scripts/cid_local_media_agent_real_preflight.py" in text
    assert RUNTIME_FILE.exists()
    assert RUNTIME_QA_GATE_DOC.exists()


def test_future_cli_target_and_test_files_are_named_without_creating_them_in_contract_phase():
    text = _doc_text()
    assert "scripts/cid_local_media_agent_real_preflight_cli.py" in text
    assert "tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli.py" in text
    assert "This current phase must not create that file." in text


def test_future_cli_implementation_phase_is_named():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.IMPLEMENTATION.V1" in text
    lowered = text.lower()
    assert "must start from a clean repository precheck" in lowered
    assert "must include tests before or with implementation" in lowered


def test_future_cli_purpose_is_limited_to_runtime_invocation():
    text = _doc_text().lower()
    required = [
        "receive an input folder argument",
        "receive an output folder argument",
        "build a `realpreflightrequest`",
        "call `run_real_preflight_check`",
        "print a sanitized result payload",
        "return an exit code mapped from the result status",
    ]
    for item in required:
        assert item in text


def test_allowed_cli_arguments_are_enumerated():
    text = _doc_text()
    required = [
        "`--input-folder`",
        "`--output-folder`",
        "`--max-file-count`",
        "`--max-total-size-bytes`",
        "`--max-scan-depth`",
        "`--accepted-extension`",
        "`--no-follow-symlinks`",
        "`--format`",
    ]
    for item in required:
        assert item in text


def test_cli_output_formats_are_limited():
    text = _doc_text().lower()
    assert "the default output format must be json" in text
    assert "`json`" in text
    assert "`text`" in text
    assert "must not include private paths or raw filenames" in text


def test_forbidden_cli_arguments_are_enumerated():
    text = _doc_text().lower()
    required = [
        "media probing flags",
        "media decoding flags",
        "scanner flags",
        "report generation flags",
        "transcription flags",
        "translation flags",
        "subtitle flags",
        "sync flags",
        "waveform flags",
        "thumbnail flags",
        "timecode flags",
        "nle export flags",
        "upload flags",
        "cloud transfer flags",
        "packaging flags",
        "installer flags",
        "licensing flags",
        "saas flags",
        "backend flags",
        "frontend flags",
        "database flags",
        "billing flags",
    ]
    for item in required:
        assert item in text


def test_exit_code_mapping_is_enumerated():
    text = _doc_text()
    required = [
        "`PREFLIGHT_PASS` -> exit code `0`",
        "`PREFLIGHT_FAIL` -> exit code `2`",
        "`PREFLIGHT_BLOCKED` -> exit code `3`",
        "invalid CLI usage -> exit code `64`",
        "unexpected internal error before sanitized output can be produced -> exit code `70`",
    ]
    for item in required:
        assert item in text


def test_allowed_cli_json_payload_fields_are_enumerated():
    text = _doc_text()
    required = [
        "`status`",
        "`sanitized_input_folder_label`",
        "`sanitized_output_folder_label`",
        "`media_file_count`",
        "`total_selected_media_size_bucket`",
        "`maximum_detected_scan_depth`",
        "`accepted_extension_counts`",
        "`ignored_extension_counts`",
        "`rejected_extension_counts`",
        "`failed_check_identifiers`",
        "`remediation_items`",
        "`exit_code`",
    ]
    for item in required:
        assert item in text


def test_prohibited_cli_output_fields_are_enumerated():
    text = _doc_text().lower()
    required = [
        "full private paths",
        "raw filenames",
        "client names",
        "project names",
        "media hashes",
        "media content",
        "stream metadata",
        "codec metadata",
        "timecode metadata",
        "embedded metadata",
        "transcript text",
        "subtitle text",
        "waveform data",
        "frame data",
        "thumbnail data",
        "absolute paths",
        "relative source paths",
        "environment variables",
        "user account names",
        "hostnames",
    ]
    for item in required:
        assert item in text


def test_stderr_privacy_boundary_is_enumerated():
    text = _doc_text().lower()
    allowed = [
        "generic usage errors",
        "generic validation failure labels",
        "result status",
        "exit code",
        "generic remediation messages",
    ]
    forbidden = [
        "private paths",
        "raw filenames",
        "stack traces by default",
        "environment dumps",
        "local usernames",
        "hostnames",
        "media-derived metadata",
        "media-derived content",
    ]
    for item in allowed + forbidden:
        assert item in text


def test_cli_runtime_boundary_requires_approved_runtime_call():
    text = _doc_text()
    assert "run_real_preflight_check(request: RealPreflightRequest)" in text
    lowered = text.lower()
    assert "must not duplicate traversal logic outside the runtime" in lowered
    assert "may parse arguments and convert them into a request object" in lowered
    assert "may serialize the sanitized result object" in lowered


def test_cli_runtime_boundary_blocks_forbidden_import_areas():
    text = _doc_text().lower()
    required = [
        "scanner modules",
        "synthetic visible report modules",
        "media probing wrappers",
        "transcription modules",
        "translation modules",
        "sync modules",
        "subtitle modules",
        "nle export modules",
        "saas modules",
        "database modules",
        "billing modules",
        "licensing modules",
        "upload modules",
        "network clients",
        "process execution helpers",
    ]
    for item in required:
        assert item in text


def test_cli_no_write_boundary_is_enumerated():
    text = _doc_text().lower()
    required = [
        "the selected input folder",
        "the selected output folder",
        "reports",
        "manifests",
        "indexes",
        "caches",
        "thumbnails",
        "waveform data",
        "transcripts",
        "subtitles",
        "sidecars",
        "nle export files",
        "temporary files inside selected folders",
    ]
    for item in required:
        assert item in text


def test_cli_local_only_boundary_is_enumerated():
    text = _doc_text().lower()
    required = [
        "upload files",
        "transfer files to cloud services",
        "call remote apis",
        "send telemetry",
        "connect to saas services",
        "connect to databases",
        "invoke desktop apps",
        "invoke nle apps",
        "invoke media tools",
    ]
    for item in required:
        assert item in text


def test_cli_import_boundary_is_standard_library_limited():
    text = _doc_text().lower()
    required = [
        "argument parsing",
        "json serialization",
        "exit code handling",
        "importing the approved runtime module",
        "exact allowed imports before implementation",
    ]
    for item in required:
        assert item in text


def test_operations_remain_blocked():
    text = _doc_text().lower()
    required = [
        "media decoding",
        "stream probing",
        "codec probing",
        "container probing",
        "real file probing tools",
        "media conversion tools",
        "frame extraction",
        "thumbnail generation",
        "waveform generation",
        "audio analysis",
        "speech recognition",
        "transcription",
        "translation",
        "subtitle generation",
        "sync analysis",
        "clap detection",
        "timecode extraction",
        "scanner integration",
        "report generation",
        "synthetic visible report integration",
        "davinci resolve integration",
        "avid integration",
        "nle export",
        "edl generation",
        "xml generation",
        "aaf generation",
        "otio generation",
        "timeline generation",
        "upload",
        "cloud transfer",
        "desktop packaging",
        "installer creation",
        "licensing activation",
        "saas integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "billing changes",
    ]
    for item in required:
        assert item in text


def test_acceptance_criteria_are_contractual():
    text = _doc_text().lower()
    required = [
        "the cli contract document exists",
        "the phase is documentation/test-only",
        "the future cli target file is named",
        "the future cli test file is named",
        "the future cli implementation phase is named",
        "allowed cli arguments are enumerated",
        "forbidden cli arguments are enumerated",
        "result-to-exit-code mapping is enumerated",
        "sanitized cli output payload is enumerated",
        "prohibited cli output fields are enumerated",
        "stderr privacy boundary is enumerated",
        "cli runtime boundary is enumerated",
        "no-write behavior is required",
        "local-only behavior is required",
        "import boundaries are defined",
        "blocked operations remain blocked",
        "the existing runtime file remains present",
        "the existing runtime qa gate remains present",
        "no cli source file is created by this phase",
    ]
    for item in required:
        assert item in text


def test_contract_test_does_not_import_future_cli_or_runtime_modules():
    tree = ast.parse(TEST.read_text(encoding="utf-8"))
    imported_modules = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)

    forbidden_imports = {
        ".".join(["scripts", "cid_local_media_agent_real_preflight_cli"]),
        ".".join(["scripts", "cid_local_media_agent_real_preflight"]),
        ".".join(["scripts", "cid_media_agent_scan"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_cli"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_preflight_check"]),
        ".".join(["scripts", "cid_local_media_agent_synthetic_visible_report_renderer"]),
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_future_cli_source_files_were_not_authorized_by_contract_phase_creation():
    doc_text = _doc_text()
    assert "scripts/cid_local_media_agent_real_preflight_cli.py" in doc_text
    assert "tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli.py" in doc_text
    assert "This current phase must not create that file." in doc_text
