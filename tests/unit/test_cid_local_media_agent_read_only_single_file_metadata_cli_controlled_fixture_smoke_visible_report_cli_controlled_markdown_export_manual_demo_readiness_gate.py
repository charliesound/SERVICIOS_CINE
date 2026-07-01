from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_readiness_gate_v1.md"
DEMO_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate_v1.md"
DEMO_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate.py"
DEMO_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate_v1.md"
DEMO_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py"
WRAPPER_SMOKE_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py"
IMPLEMENTATION_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py"
IMPLEMENTATION_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
INTEGRATION = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py"
RENDERER = ROOT / "scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
MANUAL_DEMO_EXPORT = ROOT / "tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.MANUAL_DEMO.READINESS.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_MANUAL_DEMO_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "0f220e872ff5f0804dbffe2f8b5934787d5d775f"
READY_STATUS = "READY_FOR_MANUAL_CONTROLLED_FIXTURE_DEMO_ONLY"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_manual_demo_readiness_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_readiness_document_declares_phase_result_base_and_status() -> None:
    body = read_text(DOC)
    for item in [
        PHASE,
        RESULT,
        BASE_HEAD,
        READY_STATUS,
        "Doc/test-only readiness gate",
        "not a customer demo gate",
        "not a real media gate",
    ]:
        assert item in body


def test_required_prior_and_runtime_artifacts_exist() -> None:
    for path in [
        DEMO_QA_DOC,
        DEMO_QA_TEST,
        DEMO_DOC,
        DEMO_TEST,
        WRAPPER_SMOKE_QA_TEST,
        WRAPPER_SMOKE_TEST,
        IMPLEMENTATION_QA_TEST,
        IMPLEMENTATION_TEST,
        WRAPPER,
        IMPLEMENTATION,
        INTEGRATION,
        RENDERER,
    ]:
        assert path.exists(), path


def test_manual_demo_commands_are_documented_and_controlled() -> None:
    body = read_text(DOC)
    for item in [
        "python scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "--target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt",
        "--fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1",
        f"--expected-sha256 {EXPECTED_SHA256}",
        "--expected-bytes 239",
        f"--allowed-relative-path {ALLOWED_RELATIVE_PATH}",
        "--visible-report-markdown",
        "--visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md",
        "mkdir -p tests/tmp/local_media_agent/controlled_visible_report_exports",
        "rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports",
        "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK",
    ]:
        assert item in body


def test_manual_demo_expected_evidence_and_verification_are_documented() -> None:
    body = read_text(DOC)
    for item in [
        "CID Local Media Agent - Controlled Fixture Smoke Visible Report",
        "controlled_plain_text_marker_v1",
        ALLOWED_RELATIVE_PATH,
        str(EXPECTED_BYTES),
        EXPECTED_SHA256,
        "test -f tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md",
        "grep -F",
        "sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/manual_demo_visible_report.md",
    ]:
        assert item in body


def test_manual_demo_safety_checklist_forbids_wrong_inputs_and_outputs() -> None:
    body = read_text(DOC)
    for item in [
        "Confirm current directory is /opt/SERVICIOS_CINE.",
        "Confirm virtual environment is active.",
        "Confirm git status is clean.",
        "Confirm the demo uses only the controlled fixture.",
        "Confirm the output file is inside tests/tmp/local_media_agent/controlled_visible_report_exports.",
        "Confirm the output suffix is .md.",
        "Confirm no real media path is used.",
        "Confirm no customer material path is used.",
        "Confirm no repo-root report path is used.",
    ]:
        assert item in body


def test_wrapper_remains_delegating_and_export_free() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert "--visible-report-markdown" not in body
    assert "--visible-report-output" not in body
    assert "--result-json" not in body


def test_implementation_parser_still_exposes_demo_flags() -> None:
    module = load_implementation_module()
    help_text = module.build_parser().format_help()
    assert "--visible-report-markdown" in help_text
    assert "--visible-report-output" in help_text
    assert "--result-json" in help_text


def test_readiness_phase_does_not_use_subprocess_or_create_demo_artifact() -> None:
    body = read_text(Path(__file__))
    forbidden_subprocess = "subprocess" + ".run("
    forbidden_shell_false = "shell=" + "False"
    assert forbidden_subprocess not in body
    assert forbidden_shell_false not in body
    assert not MANUAL_DEMO_EXPORT.exists()


def test_controlled_fixture_integrity_and_support_files_remain_unchanged() -> None:
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    assert (FIXTURE_ROOT / "README.md").exists()
    assert (FIXTURE_ROOT / "manifest.controlled.json").exists()


def test_readiness_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    for command in [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_manual_demo_readiness_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_controlled_demo_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]:
        assert command in body
