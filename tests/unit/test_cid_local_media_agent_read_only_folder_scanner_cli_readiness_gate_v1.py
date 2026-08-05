from __future__ import annotations

from pathlib import Path

from _cid_historical_contract_snapshot import expected_absent_paths


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py"
FUTURE_CLI = ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.READINESS.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_CLI_READINESS_GATE_V1_CLOSED"
BASE_HEAD = "685dedcfd8808dd1294d6e1a864c48f3728bdac7"
PREVIOUS_TAG = "cid-dev-stable-local-media-agent-read-only-folder-scanner-qa-closure-review-gate-v1-20260729"
RUNTIME_SHA = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.CLOSURE.REVIEW.GATE.V1"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.IMPLEMENTATION.GATE.V1"

CLI_READINESS_SOURCE_COMMIT = "bc303c43bd10ce153b49514990ee2e6e0579ab62"

AUTHORIZED_FILES = [
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.md",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_readiness_gate_v1.py",
]


def _text() -> str:
    assert DOC.exists(), f"missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def _assert_all_present(values: list[str]) -> None:
    text = _text()
    for value in values:
        assert value in text, f"missing expected value: {value!r}"


def test_files_exist_and_future_cli_does_not_exist() -> None:
    assert DOC.exists()
    assert TEST.exists()
    assert (
        "scripts/local_media_agent/read_only_folder_scanner_cli.py"
        in expected_absent_paths(CLI_READINESS_SOURCE_COMMIT)
    )


def test_identity_base_state_and_previous_phase_are_documented() -> None:
    _assert_all_present([
        PHASE,
        EXPECTED_RESULT,
        BASE_HEAD,
        PREVIOUS_TAG,
        RUNTIME_SHA,
        PREVIOUS_PHASE,
    ])


def test_scope_is_exactly_two_new_files_and_no_runtime_packaging() -> None:
    _assert_all_present(AUTHORIZED_FILES)
    _assert_all_present([
        "This phase is readiness-only, documentation-only, and contract-only.",
        "This phase is limited to exactly two new files:",
        "This phase does not modify `scripts/local_media_agent/read_only_folder_scanner.py`.",
        "This phase does not create `scripts/local_media_agent/read_only_folder_scanner_cli.py`.",
        "This phase does not modify `pyproject.toml`.",
        "This phase does not create entrypoints, packaging, or the commercial alias `cid scan`.",
    ])


def test_future_module_and_invocation_are_documented() -> None:
    _assert_all_present([
        "`scripts/local_media_agent/read_only_folder_scanner_cli.py`",
        "python -m scripts.local_media_agent.read_only_folder_scanner_cli --input-root /absolute/local/linux/folder",
        "The commercial alias `cid scan` is expressly deferred to a future packaging and entrypoints phase.",
    ])


def test_v1_arguments_and_absences_are_documented() -> None:
    _assert_all_present([
        "`--input-root ABSOLUTE_LOCAL_LINUX_FOLDER`",
        "`--help`",
        "positional arguments",
        "multiple folders",
        "stdin",
        "output path",
        "alternate output format",
        "pretty print",
        "configuration through environment variables",
        "configuration files",
        "exclusions",
        "filters",
        "configurable depth",
        "configurable limits",
        "symlink following",
        "parallel execution",
    ])


def test_delegation_and_no_duplicate_validation_are_documented() -> None:
    _assert_all_present([
        "`scan_read_only_folder(input_root)`",
        "must not duplicate runtime path validation",
        "must not resolve, normalize, inspect, traverse, or call `lstat` by itself",
        "remain runtime rejections, not duplicated CLI validation",
    ])


def test_future_api_streams_and_main_guard_are_documented() -> None:
    _assert_all_present([
        "def run_cli(",
        "argv: Sequence[str] | None = None",
        "stdout: TextIO | None = None",
        "stderr: TextIO | None = None",
        "def main() -> int",
        "if __name__ == \"__main__\":",
        "raise SystemExit(main())",
        "must not execute during import",
    ])


def test_stdout_and_stderr_contracts_are_documented() -> None:
    _assert_all_present([
        "stdout must contain exclusively the manifest produced by the runtime",
        "must use `manifest_to_json` or `emit_manifest_json`",
        "write exactly one JSON object",
        "stdout must end with exactly one newline",
        "stderr must be empty",
        "`CLI_ARGUMENTS_REJECTED`",
        "`CLI_INTERNAL_FAILURE`",
        "must not show tracebacks",
    ])


def test_exit_code_mapping_is_exactly_documented() -> None:
    _assert_all_present([
        "Exit code `0`",
        "`READ_ONLY_FOLDER_SCAN_COMPLETED`",
        "`READ_ONLY_FOLDER_SCAN_COMPLETED_WITH_WARNINGS`",
        "`--help`",
        "Exit code `2`",
        "missing, duplicated, unknown, or invalid CLI arguments",
        "`READ_ONLY_FOLDER_SCAN_REJECTED`",
        "Exit code `3`",
        "`READ_ONLY_FOLDER_SCAN_TRUNCATED`",
        "Exit code `1`",
        "controlled unexpected internal failure of the CLI wrapper",
        "must not transform `READ_ONLY_FOLDER_SCAN_REJECTED` or `READ_ONLY_FOLDER_SCAN_TRUNCATED` into success",
    ])


def test_argument_behaviors_are_documented() -> None:
    _assert_all_present([
        "Missing `--input-root`:",
        "Repeated `--input-root`:",
        "Unknown argument:",
        "Positional argument:",
        "`--help`:",
        "Input accepted by parser but rejected by runtime:",
        "Completed with warnings:",
        "Truncated result:",
        "Unexpected wrapper exception:",
        "no runtime;",
        "stderr fixed to `CLI_ARGUMENTS_REJECTED`;",
        "stderr fixed to `CLI_INTERNAL_FAILURE`;",
    ])


def test_privacy_security_and_forbidden_capabilities_are_documented() -> None:
    _assert_all_present([
        "local Linux only",
        "read-only",
        "stdlib-only",
        "no symlink following",
        "no byte reads",
        "no hashes",
        "no MIME detection",
        "no magic-byte inspection",
        "no ffprobe",
        "no ffmpeg",
        "no subprocess",
        "no shell execution",
        "no network",
        "no DB",
        "no SaaS",
        "no writes",
        "no private paths or private names in stdout or stderr",
        "sanitized manifest",
        "fail-closed limits",
        "must not expand globs",
        "expand `~`",
        "read environment variables",
        "change the working directory",
        "write cache",
        "create folders",
        "create logs",
    ])


def test_next_phase_is_exact() -> None:
    _assert_all_present([
        "## Next allowed phase",
        NEXT_PHASE,
    ])
