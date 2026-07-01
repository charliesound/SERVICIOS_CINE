from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import shutil
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate_v1.md"
IMPLEMENTATION = ROOT / "scripts/local_media_agent/read_only_single_file_metadata.py"
WRAPPER = ROOT / "scripts/local_media_agent/read_only_single_file_metadata_cli.py"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_readiness_gate.py"
CONTRACT_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py"
WRAPPER_SMOKE_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py"
VISIBLE_REPORT_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py"
CLI_CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py"
FIXTURE_ROOT = ROOT / "tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1"
FIXTURE = FIXTURE_ROOT / "media/controlled_plain_text_marker.txt"
EXPORT_ROOT = ROOT / "tests/tmp/local_media_agent/controlled_visible_report_exports"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.IMPLEMENTATION.GATE.V1"
RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_IMPLEMENTATION_GATE_V1_CLOSED"
BASE_HEAD = "53ad71047f39ca0c928460263a4a1b9bf1538f59"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-readiness-gate-v1-20260701"
FUTURE_FLAG = "--visible-report-output"
VISIBLE_FLAG = "--visible-report-markdown"
JSON_FLAG = "--result-json"
EXPECTED_BYTES = 239
EXPECTED_SHA256 = "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a"
ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
EXPORT_OK = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK"
EXPORT_REJECTED = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_REJECTED"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_implementation_module():
    spec = importlib.util.spec_from_file_location("cid_lma_controlled_markdown_export_impl", IMPLEMENTATION)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_argv() -> list[str]:
    return [
        "--target-path",
        str(FIXTURE),
        "--fixture-root",
        str(FIXTURE_ROOT),
        "--expected-sha256",
        EXPECTED_SHA256,
        "--expected-bytes",
        str(EXPECTED_BYTES),
        "--allowed-relative-path",
        ALLOWED_RELATIVE_PATH,
    ]


def run_cli_and_capture(argv: list[str]) -> tuple[int, str]:
    module = load_implementation_module()
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        exit_code = module.run_cli(argv)
    return exit_code, stdout.getvalue()


def reset_export_root() -> None:
    shutil.rmtree(EXPORT_ROOT, ignore_errors=True)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)


def cleanup_export_root() -> None:
    shutil.rmtree(EXPORT_ROOT, ignore_errors=True)


def export_path(name: str = "controlled_visible_report.md") -> Path:
    return EXPORT_ROOT / name


def test_document_declares_phase_result_base_scope_and_output_root() -> None:
    assert DOC.exists()
    body = read_text(DOC)
    required = [
        PHASE,
        RESULT,
        BASE_HEAD,
        BASE_TAG,
        FUTURE_FLAG,
        VISIBLE_FLAG,
        "tests/tmp/local_media_agent/controlled_visible_report_exports",
        "scripts/local_media_agent/read_only_single_file_metadata.py",
        "scripts/local_media_agent/read_only_single_file_metadata_cli.py",
        "No real material.",
        "No customer material.",
    ]
    for item in required:
        assert item in body


def test_related_artifacts_exist() -> None:
    for path in [
        IMPLEMENTATION,
        WRAPPER,
        READINESS_TEST,
        CONTRACT_QA_TEST,
        WRAPPER_SMOKE_QA_TEST,
        VISIBLE_REPORT_CONTRACT_TEST,
        CLI_CONTRACT_TEST,
    ]:
        assert path.exists(), path


def test_parser_accepts_controlled_output_path_and_keeps_current_help_contract() -> None:
    module = load_implementation_module()
    parser = module.build_parser()
    parsed = parser.parse_args(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(export_path())])
    assert parsed.visible_report_path == str(export_path())

    help_text = parser.format_help()
    assert FUTURE_FLAG in help_text
    assert VISIBLE_FLAG in help_text
    assert JSON_FLAG in help_text


def test_wrapper_remains_delegating_and_does_not_implement_export() -> None:
    body = read_text(WRAPPER)
    assert "implementation.run_cli(argv)" in body
    assert "ArgumentParser" not in body
    assert "add_argument" not in body
    assert FUTURE_FLAG not in body
    assert VISIBLE_FLAG not in body


def test_default_json_and_markdown_stdout_behaviors_remain_unchanged() -> None:
    cleanup_export_root()

    status_code, status_stdout = run_cli_and_capture(base_argv())
    json_code, json_stdout = run_cli_and_capture(base_argv() + [JSON_FLAG])
    markdown_code, markdown_stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG])

    assert status_code == 0
    assert status_stdout == "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK\n"

    assert json_code == 0
    payload = json.loads(json_stdout)
    assert payload["ok"] is True
    assert payload["metadata"]["bytes"] == EXPECTED_BYTES
    assert payload["metadata"]["sha256"] == EXPECTED_SHA256
    assert "Controlled Fixture Smoke Visible Report" not in json_stdout

    assert markdown_code == 0
    assert markdown_stdout.startswith("# CID Local Media Agent - Controlled Fixture Smoke Visible Report")
    assert EXPECTED_SHA256 in markdown_stdout
    assert ALLOWED_RELATIVE_PATH in markdown_stdout

    assert not EXPORT_ROOT.exists()


def test_valid_controlled_export_writes_exact_markdown_and_status_stdout() -> None:
    reset_export_root()
    try:
        markdown_code, markdown_stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG])
        output = export_path()

        export_code, export_stdout = run_cli_and_capture(
            base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(output)]
        )

        assert markdown_code == 0
        assert export_code == 0
        assert export_stdout == f"{EXPORT_OK}\n"
        assert output.exists()
        assert output.read_text(encoding="utf-8") == markdown_stdout
    finally:
        cleanup_export_root()


def test_export_requires_visible_report_markdown() -> None:
    reset_export_root()
    try:
        output = export_path()
        code, stdout = run_cli_and_capture(base_argv() + [FUTURE_FLAG, str(output)])
        assert code == 2
        assert stdout == f"{EXPORT_REJECTED}:VISIBLE_REPORT_MARKDOWN_REQUIRED\n"
        assert not output.exists()
    finally:
        cleanup_export_root()


def test_existing_output_file_is_rejected_by_default() -> None:
    reset_export_root()
    try:
        output = export_path()
        output.write_text("existing", encoding="utf-8")
        code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(output)])
        assert code == 2
        assert "VISIBLE_REPORT_OUTPUT_EXISTS_OVERWRITE_REJECTED" in stdout
        assert output.read_text(encoding="utf-8") == "existing"
    finally:
        cleanup_export_root()


def test_missing_parent_directory_is_rejected_without_write() -> None:
    reset_export_root()
    try:
        output = EXPORT_ROOT / "missing" / "report.md"
        code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(output)])
        assert code == 2
        assert "VISIBLE_REPORT_OUTPUT_PARENT_NOT_FOUND" in stdout
        assert not output.exists()
    finally:
        cleanup_export_root()


def test_non_md_suffix_is_rejected_without_write() -> None:
    reset_export_root()
    try:
        output = EXPORT_ROOT / "report.txt"
        code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(output)])
        assert code == 2
        assert "VISIBLE_REPORT_OUTPUT_SUFFIX_REJECTED" in stdout
        assert not output.exists()
    finally:
        cleanup_export_root()


def test_paths_outside_controlled_root_are_rejected_without_write() -> None:
    reset_export_root()
    try:
        output = ROOT / "visible_report.md"
        code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(output)])
        assert code == 2
        assert "VISIBLE_REPORT_OUTPUT_OUTSIDE_CONTROLLED_ROOT_REJECTED" in stdout
        assert not output.exists()
    finally:
        cleanup_export_root()


def test_paths_inside_fixture_and_tests_fixtures_are_rejected() -> None:
    reset_export_root()
    try:
        fixture_output = FIXTURE_ROOT / "generated_report.md"
        tests_fixtures_output = ROOT / "tests/fixtures/generated_report.md"

        code_fixture, stdout_fixture = run_cli_and_capture(
            base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(fixture_output)]
        )
        code_tests, stdout_tests = run_cli_and_capture(
            base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(tests_fixtures_output)]
        )

        assert code_fixture == 2
        assert "VISIBLE_REPORT_OUTPUT_INSIDE_CONTROLLED_FIXTURE_REJECTED" in stdout_fixture
        assert not fixture_output.exists()

        assert code_tests == 2
        assert "VISIBLE_REPORT_OUTPUT_INSIDE_TESTS_FIXTURES_REJECTED" in stdout_tests
        assert not tests_fixtures_output.exists()
    finally:
        cleanup_export_root()


def test_windows_style_path_is_rejected_without_write() -> None:
    reset_export_root()
    try:
        code, stdout = run_cli_and_capture(base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, "C:\\temp\\report.md"])
        assert code == 2
        assert "VISIBLE_REPORT_OUTPUT_WINDOWS_STYLE_PATH_REJECTED" in stdout
    finally:
        cleanup_export_root()


def test_symlink_parent_and_symlink_file_are_rejected() -> None:
    reset_export_root()
    real_parent = EXPORT_ROOT / "real_parent"
    link_parent = EXPORT_ROOT / "link_parent"
    symlink_file = EXPORT_ROOT / "symlink_report.md"

    try:
        real_parent.mkdir()
        link_parent.symlink_to(real_parent, target_is_directory=True)
        symlink_file.symlink_to(EXPORT_ROOT / "target_report.md")

        code_parent, stdout_parent = run_cli_and_capture(
            base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(link_parent / "report.md")]
        )
        code_file, stdout_file = run_cli_and_capture(
            base_argv() + [VISIBLE_FLAG, FUTURE_FLAG, str(symlink_file)]
        )

        assert code_parent == 2
        assert "VISIBLE_REPORT_OUTPUT_PARENT_SYMLINK_REJECTED" in stdout_parent

        assert code_file == 2
        assert "VISIBLE_REPORT_OUTPUT_FILE_SYMLINK_REJECTED" in stdout_file
    finally:
        cleanup_export_root()


def test_rejected_metadata_does_not_write_report() -> None:
    reset_export_root()
    try:
        output = export_path()
        argv = base_argv()
        sha_index = argv.index("--expected-sha256") + 1
        argv[sha_index] = "0" * 64

        code, stdout = run_cli_and_capture(argv + [VISIBLE_FLAG, FUTURE_FLAG, str(output)])

        assert code == 2
        assert "METADATA_NOT_ACCEPTED" in stdout
        assert not output.exists()
    finally:
        cleanup_export_root()


def test_controlled_fixture_integrity_and_support_files_remain_unchanged() -> None:
    assert FIXTURE.exists()
    data = FIXTURE.read_bytes()
    assert len(data) == EXPECTED_BYTES
    assert hashlib.sha256(data).hexdigest() == EXPECTED_SHA256
    assert (FIXTURE_ROOT / "README.md").exists()
    assert (FIXTURE_ROOT / "manifest.controlled.json").exists()


def test_pyproject_does_not_register_export_console_script() -> None:
    if not PYPROJECT.exists():
        return
    body = read_text(PYPROJECT)
    forbidden_refs = [
        "visible-report-output",
        "controlled-markdown-export",
        "controlled_markdown_export",
        "scripts.local_media_agent.read_only_single_file_metadata",
        "scripts.local_media_agent.read_only_single_file_metadata_cli",
    ]
    for ref in forbidden_refs:
        assert ref not in body


def test_document_declares_required_validation_commands() -> None:
    body = read_text(DOC)
    commands = [
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_gate.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py",
        "pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py",
        "bash scripts/dev/guard_wsl_repo.sh",
        "Mandatory PostgreSQL-only regression guard.",
    ]
    for command in commands:
        assert command in body
