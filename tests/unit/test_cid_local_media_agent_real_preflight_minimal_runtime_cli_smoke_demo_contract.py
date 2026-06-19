from __future__ import annotations

import ast
from pathlib import Path


DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract_v1.md")
TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo_contract.py")
CLI_FILE = Path("scripts/cid_local_media_agent_real_preflight_cli.py")
RUNTIME_FILE = Path("scripts/cid_local_media_agent_real_preflight.py")
CLI_QA_GATE_DOC = Path("docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_qa_gate_v1.md")
FUTURE_SMOKE_DEMO_TEST = Path("tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py")
PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.CONTRACT.V1"


def _doc_text() -> str:
    assert DOC.exists(), f"Missing smoke/demo contract document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_smoke_demo_contract_document_exists():
    assert DOC.exists()


def test_smoke_demo_contract_contains_phase_identifier():
    assert PHASE in _doc_text()


def test_smoke_demo_contract_is_documentation_test_only():
    text = _doc_text().lower()
    assert "documentation/test-only" in text
    assert "does not create smoke/demo runtime code" in text
    assert "does not modify the cli runtime" in text
    assert "does not process media content" in text


def test_smoke_demo_contract_depends_on_closed_cli_qa_gate():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1" in text
    assert "scripts/cid_local_media_agent_real_preflight_cli.py" in text
    assert "scripts/cid_local_media_agent_real_preflight.py" in text
    assert CLI_FILE.exists()
    assert RUNTIME_FILE.exists()
    assert CLI_QA_GATE_DOC.exists()


def test_future_smoke_demo_test_file_is_named_without_creating_it_by_contract_phase():
    text = _doc_text()
    assert "tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo.py" in text
    assert "This current phase must not create that file." in text


def test_future_smoke_demo_implementation_phase_is_named():
    text = _doc_text()
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.SMOKE.DEMO.IMPLEMENTATION.V1" in text
    lowered = text.lower()
    assert "must start from a clean repository precheck" in lowered
    assert "must include tests before or with implementation" in lowered


def test_smoke_demo_purpose_is_limited_to_synthetic_cli_invocation():
    text = _doc_text().lower()
    required = [
        "create temporary synthetic input and output folders",
        "create synthetic placeholder files with safe fake media extensions",
        "invoke the existing cli boundary",
        "verify sanitized json output",
        "verify sanitized text output",
        "verify exit code mapping",
        "verify no private path leakage",
        "verify no raw filename leakage",
        "verify no files are created in the selected output folder",
        "verify no files are created, modified, or deleted in the selected input folder",
    ]
    for item in required:
        assert item in text


def test_synthetic_fixture_boundary_is_enumerated():
    text = _doc_text().lower()
    required = [
        "synthetic placeholder files",
        "`.mov`",
        "`.mp4`",
        "`.mxf`",
        "`.wav`",
        "`.aif`",
        "`.aiff`",
        "`.txt`",
        "`.custom`",
        "must not use real client media",
        "must not use real project folders",
        "must not use private production paths",
        "must not use mounted windows paths",
        "must not use cloud-synced folders",
        "must not use network shares",
    ]
    for item in required:
        assert item in text


def test_required_smoke_demo_cases_are_enumerated():
    text = _doc_text().lower()
    required = [
        "pass case with one accepted synthetic placeholder file",
        "fail case with no accepted extension",
        "blocked case with output folder inside input folder",
        "json output sanitization",
        "text output sanitization",
        "custom accepted extension forwarding",
        "file-count limit forwarding",
        "invalid usage sanitized error",
        "selected output folder remains empty after cli invocation",
        "selected input folder contains only pre-created synthetic fixtures after cli invocation",
    ]
    for item in required:
        assert item in text


def test_cli_invocation_boundary_is_enumerated():
    text = _doc_text().lower()
    required = [
        "scripts/cid_local_media_agent_real_preflight_cli.py",
        "scanner clis",
        "synthetic visible report clis",
        "media probing clis",
        "transcription clis",
        "translation clis",
        "subtitle clis",
        "sync clis",
        "nle export clis",
        "upload clis",
        "saas clis",
        "billing clis",
        "database clis",
    ]
    for item in required:
        assert item in text


def test_required_output_sanitization_checks_are_enumerated():
    text = _doc_text().lower()
    required = [
        "full private paths",
        "raw filenames",
        "client names",
        "project names",
        "absolute paths",
        "relative source paths",
        "environment variables",
        "user account names",
        "hostnames",
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
    ]
    for item in required:
        assert item in text


def test_exit_code_mapping_requirements_are_enumerated():
    text = _doc_text()
    required = [
        "`PREFLIGHT_PASS` -> exit code `0`",
        "`PREFLIGHT_FAIL` -> exit code `2`",
        "`PREFLIGHT_BLOCKED` -> exit code `3`",
        "invalid CLI usage -> exit code `64`",
    ]
    for item in required:
        assert item in text


def test_internal_error_mapping_is_constrained_to_safe_non_leaking_verification():
    text = _doc_text().lower()
    assert "internal-error mapping" in text
    assert "safe monkeypatching" in text
    assert "never by leaking stack traces" in text


def test_no_write_boundary_is_enumerated():
    text = _doc_text().lower()
    required = [
        "does not write inside the selected output folder",
        "does not create, modify, or delete files in the selected input folder",
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


def test_local_only_boundary_is_enumerated():
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
        "the smoke/demo contract document exists",
        "the phase is documentation/test-only",
        "the future smoke/demo test file is named",
        "the future smoke/demo implementation phase is named",
        "the current cli file exists",
        "the current runtime file exists",
        "the current cli qa gate document exists",
        "synthetic fixture boundaries are enumerated",
        "required smoke/demo cases are enumerated",
        "cli invocation boundary is enumerated",
        "output sanitization requirements are enumerated",
        "exit code mapping requirements are enumerated",
        "no-write behavior is required",
        "local-only behavior is required",
        "blocked operations remain blocked",
        "this phase does not create the future smoke/demo test implementation file",
    ]
    for item in required:
        assert item in text


def test_contract_test_does_not_import_cli_runtime_or_future_smoke_demo():
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
        ".".join(["tests", "unit", "test_cid_local_media_agent_real_preflight_minimal_runtime_cli_smoke_demo"]),
    }

    assert imported_modules.isdisjoint(forbidden_imports)


def test_contract_test_does_not_create_future_smoke_demo_implementation_file():
    text = _doc_text()
    assert str(FUTURE_SMOKE_DEMO_TEST).replace("\\", "/") in text
    assert "This current phase must not create that file." in text
