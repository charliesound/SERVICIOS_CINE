from pathlib import Path


QA_GATE_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_controlled_runtime_implementation_qa_gate_v1.md"
)
IMPLEMENTATION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_"
    "visible_report_runtime_generator_controlled_runtime_implementation_v1.md"
)
RUNTIME_GENERATOR = Path("scripts/local_media_agent/visible_report_runtime_generator.py")
RUNTIME_TEST = Path("tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py")


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qa_gate_doc_and_files_under_qa_exist() -> None:
    assert QA_GATE_DOC.exists()
    assert IMPLEMENTATION_DOC.exists()
    assert RUNTIME_GENERATOR.exists()
    assert RUNTIME_TEST.exists()

    text = _text(QA_GATE_DOC)
    for required_path in (
        "scripts/local_media_agent/visible_report_runtime_generator.py",
        "tests/unit/test_cid_local_media_agent_visible_report_runtime_generator.py",
        "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_demo_visible_report_runtime_generator_controlled_runtime_implementation_v1.md",
    ):
        assert required_path in text


def test_source_traceability_is_complete() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.VISIBLE.REPORT.RUNTIME.GENERATOR.CONTROLLED.RUNTIME.IMPLEMENTATION.V1",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_RUNTIME_IMPLEMENTATION_READY_FOR_QA",
        "9c00290f9c9f961cb1537b4075daa17eda952960",
        "cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-demo-visible-report-runtime-generator-controlled-runtime-implementation-v1-20260620",
    ]

    for item in required:
        assert item in text


def test_qa_gate_remains_docs_test_only_and_non_expansive() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "This QA gate is docs/test-only.",
        "This QA gate does not modify runtime behavior.",
        "This QA gate does not execute the scanner.",
        "This QA gate does not use real client media.",
        "This QA gate does not execute ffprobe or ffmpeg.",
        "This QA gate does not perform network calls, SaaS upload, or database writes.",
        "The implementation must not expand the current Local Media Agent baseline.",
    ]

    for item in required:
        assert item in text


def test_public_interface_remains_narrow() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)

    interface = "generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path"
    assert interface in qa_text
    assert f"def {interface}:" in source

    for item in (
        "accept already-created controlled scanner result data",
        "validate all required facts before rendering",
        "write one authorized local report artifact only after validation passes",
        "return the created local report path",
        "fail closed before writing output if validation fails",
    ):
        assert item in qa_text


def test_runtime_generator_has_no_external_runtime_service_imports() -> None:
    source = _text(RUNTIME_GENERATOR)

    forbidden_fragments = [
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import urllib",
        "from urllib",
        "import socket",
        "from socket",
        "sqlalchemy",
        "psycopg",
        "fastapi",
    ]

    for fragment in forbidden_fragments:
        assert fragment not in source

    assert "report_path.write_text(markdown, encoding=\"utf-8\")" in source
    assert "report_path.parent.mkdir(parents=True, exist_ok=True)" in source


def test_required_input_schema_is_enforced_by_runtime() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)

    required_groups = [
        "report_identity",
        "privacy_evidence",
        "scanner_summary",
        "accepted_media",
        "rejected_non_media",
        "human_review",
        "warnings",
        "created_output_artifacts",
        "roadmap_modules_not_generated",
    ]

    assert "_REQUIRED_GROUPS" in source
    for group in required_groups:
        assert group in qa_text
        assert group in source

    assert "Missing required input groups" in source


def test_controlled_scanner_fact_baseline_is_enforced() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)

    expected_pairs = {
        '"status": "completed_with_warnings"': "Scanner status: completed_with_warnings",
        '"candidate_media_count": 5': "Candidate media count: 5",
        '"accepted_media_count": 4': "Accepted media count: 4",
        '"rejected_non_media_count": 3': "Rejected non-media count: 3",
        '"human_review_required_count": 1': "Human review required count: 1",
        '"warnings_count": 1': "Warnings count: 1",
        '"ffprobe_preflight": "skipped"': "ffprobe preflight: skipped",
    }

    assert "_EXPECTED_SCANNER_FACTS" in source
    for source_item, qa_item in expected_pairs.items():
        assert source_item in source
        assert qa_item in qa_text

    assert "must not infer missing facts" in qa_text
    assert "must not hide warnings" in qa_text
    assert "must not silently correct inconsistent counts" in qa_text


def test_validation_order_is_visible_in_runtime_source() -> None:
    source = _text(RUNTIME_GENERATOR)

    ordered_markers = [
        "# 1. input object type",
        "# 2. required top-level groups",
        "# 3. report identity values",
        "# 4. local-only privacy evidence",
        "# 5. forbidden local-environment markers",
        "# 6. scanner fact completeness",
        "# 7. accepted and rejected media count consistency",
        "# 8. human review and warning visibility",
        "# 9. current-output versus roadmap-output separation",
        "# 10. deterministic rendering safety",
        "# 11. final output path authorization",
    ]

    cursor = -1
    for marker in ordered_markers:
        position = source.find(marker)
        assert position > cursor
        cursor = position


def test_output_contract_remains_limited_to_05_reports() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)

    assert 'REPORT_FAMILY = "05_reports"' in source
    assert 'OUTPUT_FILENAME = "cid_local_media_agent_visible_report_v1.md"' in source
    assert "allowed_report_family" in source
    assert "report_filename" in source
    assert "05_reports/" in qa_text

    forbidden_families = [
        "00_project",
        "01_media_catalog",
        "02_audio_sync",
        "03_transcription",
        "04_subtitles",
        "06_exports",
    ]

    for family in forbidden_families:
        assert family in qa_text
        assert family in source


def test_required_report_sections_are_preserved() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)
    runtime_test = _text(RUNTIME_TEST)

    sections = [
        "Executive Summary",
        "Local-Only Privacy Confirmation",
        "Controlled Demo Input Summary",
        "Scanner Result Summary",
        "Accepted Media",
        "Rejected Non-Media",
        "Human Review Required",
        "Warnings",
        "Created Output Artifacts",
        "Roadmap Modules Not Yet Generated",
        "Producer Interpretation",
        "Next Technical Actions",
    ]

    for section in sections:
        assert section in qa_text
        assert section in source
        assert section in runtime_test

    assert "test_report_sections_are_preserved_in_required_order" in runtime_test


def test_privacy_and_output_root_safety_are_enforced() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)
    runtime_test = _text(RUNTIME_TEST)

    privacy_flags = [
        "original_media_left_client_system",
        "saas_upload_performed",
        "network_call_performed",
        "database_write_performed",
    ]

    for flag in privacy_flags:
        assert flag in qa_text
        assert flag in source
        assert flag in runtime_test

    for marker in (
        "Windows drive output path is not allowed.",
        "UNC output path is not allowed.",
        "Mounted Windows output path is not allowed.",
        "Refusing to write to filesystem root.",
        "Refusing to write inside a protected project output family.",
        "Refusing to write inside the repository.",
    ):
        assert marker in source


def test_determinism_is_covered() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)
    runtime_test = _text(RUNTIME_TEST)

    assert "deterministic report content" in qa_text
    assert "sort deterministically" in qa_text
    assert "sorted(items, key=lambda value: str(value" in source
    assert "test_generation_is_deterministic_for_same_controlled_input" in runtime_test

    volatile_markers = ["created_at", "updated_at", "timestamp", "machine", "hostname", "user", "absolute_path"]
    for marker in volatile_markers:
        assert marker in source


def test_fail_closed_cases_are_covered_by_runtime_test() -> None:
    qa_text = _text(QA_GATE_DOC)
    runtime_test = _text(RUNTIME_TEST)

    required_tests = [
        "test_missing_required_group_fails_closed_without_output",
        "test_inconsistent_counts_fail_closed_without_output",
        "test_privacy_violation_fails_closed_without_output",
        "test_unsafe_local_marker_fails_closed_without_output",
        "test_protected_output_family_fails_closed_without_output",
    ]

    for test_name in required_tests:
        assert test_name in runtime_test

    for item in (
        "missing required group",
        "inconsistent counts",
        "unsafe privacy evidence",
        "unsafe local marker",
        "protected output family",
    ):
        assert item in qa_text


def test_roadmap_modules_remain_not_generated() -> None:
    qa_text = _text(QA_GATE_DOC)
    source = _text(RUNTIME_GENERATOR)
    runtime_test = _text(RUNTIME_TEST)

    required = [
        "audio_sync",
        "transcription",
        "subtitles",
        "timeline_exports",
        "saas_upload",
        "database_records",
        "not_generated",
    ]

    for item in required:
        assert item in source
        assert item in runtime_test

    assert "The report must not be presented as sync, transcription, subtitle, or export output." in source
    assert "The report must not be presented as sync, transcription, subtitle, or export output." in runtime_test
    assert "The report must not be presented as sync, transcription, subtitle, or export output." in qa_text


def test_qa_gate_requires_validation_evidence_and_declares_result() -> None:
    text = _text(QA_GATE_DOC)

    required = [
        "runtime generator unit test passing",
        "implementation readiness tests passing",
        "runtime generator contract tests passing",
        "Python compile passing",
        "diff check passing",
        "WSL/repo guard passing",
        "database backend regression guard passing",
        "LOCAL_MEDIA_AGENT_VISIBLE_REPORT_RUNTIME_GENERATOR_CONTROLLED_RUNTIME_IMPLEMENTATION_QA_GATE_PASS_READY_FOR_RUNTIME_CLI_INTEGRATION_CONTRACT",
    ]

    for item in required:
        assert item in text
