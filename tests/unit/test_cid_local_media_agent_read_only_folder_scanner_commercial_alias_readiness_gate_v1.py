from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

from _cid_historical_contract_snapshot import expected_absent_paths, snapshot_pyproject, snapshot_sha256


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py"

PYPROJECT_PATH = ROOT / "pyproject.toml"
SCANNER_RUNTIME_PATH = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
SCANNER_CLI_PATH = ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"
CID_CLI_PATH = ROOT / "scripts/local_media_agent/cid_cli.py"

PHASE = "CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_READINESS_GATE_V1"
EXPECTED_RESULT = "CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_READINESS_GATE_V1_CLOSED"
NEXT_PHASE = "CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1"

BASE_HEAD = "46602631609558ba81eb7f00a1c0c15a435e17b2"
BASE_TREE = "4e9489d60be18226754133b22dfe2ec9d3730d35"
BASE_PARENT = "1113c81c7bd7ca60cfe06f1794000bd7c23939d7"
BASE_TAG = "cid-dev-stable-local-media-agent-read-only-folder-scanner-package-entrypoint-v1-20260805"

FUTURE_MODULE = "scripts/local_media_agent/cid_cli.py"
FUTURE_ENTRYPOINT = "cid = \"scripts.local_media_agent.cid_cli:main\""
FUTURE_INVOCATION = "cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER"

AUTHORIZED_FILES = {
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.md",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_commercial_alias_readiness_gate_v1.py",
}

EXPECTED_SCRIPT_ENTRY_COUNT = 3

EXPECTED_SCRIPT_ENTRIES = {
    "cid-local-media-agent-visible-report-write-enabled-export": "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main",
    "cid-local-media-agent-controlled-local-demo-runner": "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main",
    "cid-local-media-agent-read-only-folder-scanner": "scripts.local_media_agent.read_only_folder_scanner_cli:main",
}

EXPECTED_PYPROJECT_SHA256 = "5fbbe0668ce9ad6e64fa28325dd0208a9e2c739c1cd1dc43000716c9c5e301b4"
EXPECTED_SCANNER_RUNTIME_SHA256 = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
EXPECTED_SCANNER_CLI_SHA256 = "ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d"
RECONCILED_SCANNER_RUNTIME_SHA256 = "1d0dc95cff6d69cf973780452eea3087cc86af0ff5b07a63595157d77f3722c7"
RECONCILED_SCANNER_CLI_SHA256 = "1d8df7aeaf9a94df112f7f55ffcbdf95564188c9bafcf5dc1359aebffa49a2f6"

ALIAS_READINESS_SOURCE_COMMIT = "b8f4d11d574ff2edc12ba7ccd995c8d27cc61af4"


def _text() -> str:
    assert DOC.exists(), f"missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def _assert_all_present(text: str, required: list[str]) -> None:
    for value in required:
        assert value in text, f"Expected string not found: {value!r}"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase_identity_document_and_result_exist() -> None:
    text = _text()

    assert DOC.exists()
    assert TEST.exists()
    _assert_all_present(text, [PHASE, EXPECTED_RESULT])


def test_expected_closure_result_is_exact() -> None:
    text = _text()

    assert EXPECTED_RESULT in text


def test_base_state_head_tree_parent_and_tag_are_documented() -> None:
    text = _text()

    _assert_all_present(text, [
        BASE_HEAD,
        BASE_TREE,
        BASE_PARENT,
        BASE_TAG,
        "origin/main",
        "The repository must be clean before starting.",
    ])


def test_scope_is_limited_to_two_authorized_new_files() -> None:
    text = _text()

    _assert_all_present(text, [
        "This phase is readiness-only, documentation-only and static-QA-only.",
        "This phase creates exactly two new files:",
        "This phase does not modify any existing file.",
        "This phase does not create any other file.",
    ])
    for path in AUTHORIZED_FILES:
        assert path in text


def test_current_three_entrypoints_are_documented() -> None:
    text = _text()

    _assert_all_present(text, [
        "currently contains exactly three installed scripts",
        "cid-local-media-agent-visible-report-write-enabled-export",
        "cid-local-media-agent-controlled-local-demo-runner",
        "cid-local-media-agent-read-only-folder-scanner",
    ])


def test_current_absence_of_cid_is_documented() -> None:
    text = _text()

    _assert_all_present(text, [
        "Currently there is no:",
        "`[project.scripts]` entry named `cid`",
        "`scripts/local_media_agent/cid_cli.py`",
        "installed command `cid`",
        "commercial subcommand `cid scan`",
        "The commercial alias was explicitly deferred",
    ])


def test_future_cid_module_entrypoint_and_invocation_are_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        FUTURE_MODULE,
        FUTURE_ENTRYPOINT,
        FUTURE_INVOCATION,
    ])


def test_future_python_api_is_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        "def run_cli(",
        "argv: Sequence[str] | None = None",
        "stdout: TextIO | None = None",
        "stderr: TextIO | None = None",
        ") -> int:",
        "def main() -> int:",
    ])


def test_main_guard_is_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        'if __name__ == "__main__":',
        "raise SystemExit(main())",
    ])


def test_umbrella_help_contract_is_fixed() -> None:
    text = _text()

    _assert_all_present(text, [
        "The invocation `cid --help` must:",
        "return exit code 0",
        "not execute the scanner",
        "write exclusively a fixed commercial help",
        "not contain private paths",
        "not write files",
        "Usage: cid COMMAND [OPTIONS]",
        "scan    Scan one absolute local Linux folder in read-only mode.",
        "Options:",
        "--help",
    ])


def test_scan_help_contract_is_fixed() -> None:
    text = _text()

    _assert_all_present(text, [
        "The invocation `cid scan --help` must:",
        "return exit code 0",
        "not execute the scanner",
        "write exclusively a fixed subcommand help",
        "use the commercial syntax `cid scan`",
        "not show the internal `python -m` invocation",
        "not contain private paths",
        "not write files",
        "Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER",
        "--input-root ABSOLUTE_LOCAL_LINUX_FOLDER",
        "--help",
    ])


def test_delegation_to_scanner_cli_run_cli_is_required() -> None:
    text = _text()

    _assert_all_present(text, [
        "scripts.local_media_agent.read_only_folder_scanner_cli.run_cli",
        "remove only the initial `scan` token",
        "pass the remaining arguments without transformation",
        '["--input-root", "/absolute/local/folder"]',
        "stdout=stdout",
        "stderr=stderr",
    ])


def test_direct_delegation_to_scan_read_only_folder_is_forbidden() -> None:
    text = _text()

    _assert_all_present(text, [
        "must NOT call directly:",
        "scan_read_only_folder",
    ])


def test_umbrella_adapter_must_not_transform_arguments() -> None:
    text = _text()

    _assert_all_present(text, [
        "resolve paths",
        "normalize paths",
        "convert to `Path`",
        "expand `~`",
        "expand globs",
        "inspect the filesystem",
        "check existence",
        "duplicate validation",
        "read environment variables",
        "change the current directory",
        "alter stdout",
        "alter stderr",
        "alter the manifest",
        "alter the exit code",
    ])


def test_delegated_contract_is_preserved() -> None:
    text = _text()

    _assert_all_present(text, [
        "scanner CLI parser",
        "JSON manifest",
        "serialization",
        "stdout",
        "stderr",
        "exit codes",
        "privacy",
        "sanitization",
        "fail-closed limits",
        "read-only behavior",
    ])


def test_exit_codes_propagation_is_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        "0 for completed or completed with warnings",
        "2 for rejected arguments or rejected scan",
        "3 for truncated scan",
        "1 for controlled internal failure of the existing CLI",
    ])


def test_umbrella_invalid_invocations_are_rejected() -> None:
    text = _text()

    _assert_all_present(text, [
        "`cid` without arguments",
        "`cid -h`",
        "`cid unknown`",
        "`cid --unknown`",
        "any subcommand other than `scan`",
        "umbrella help combined with additional tokens",
    ])


def test_arguments_rejected_error_contract_is_sanitized() -> None:
    text = _text()

    _assert_all_present(text, [
        "CID_CLI_ARGUMENTS_REJECTED",
        "stdout must remain empty",
        "followed by a single newline",
        "exit code 2",
        "no traceback",
        "the rejected argument must not be reproduced",
    ])


def test_internal_failure_error_contract_is_sanitized() -> None:
    text = _text()

    _assert_all_present(text, [
        "CID_CLI_INTERNAL_FAILURE",
        "keep stdout empty",
        "return exit code 1",
        "show no traceback, exception, argument or path",
    ])


def test_privacy_and_security_boundaries_are_preserved() -> None:
    text = _text()

    _assert_all_present(text, [
        "local Linux execution",
        "read-only",
        "no modification of material",
        "no reading of file contents",
        "no media hashes",
        "no MIME",
        "no magic bytes",
        "no ffprobe",
        "no ffmpeg",
        "no subprocess",
        "no shell",
        "no network",
        "no database",
        "no SaaS",
        "no writes",
        "no logs",
        "no cache",
        "no private paths in messages",
        "no private names in errors",
        "no symlink following",
        "no acceptance of Windows, UNC, `/mnt` or `wsl.localhost` paths",
        "no overwriting",
        "no parallel processing",
    ])


def test_prohibited_runtime_capabilities_are_blocked() -> None:
    text = _text()

    _assert_all_present(text, [
        "ffprobe",
        "ffmpeg",
        "subprocess",
        "shell",
        "network",
        "database",
        "SaaS",
        "Docker",
        "Alembic",
    ])


def test_prohibited_creation_is_explicit() -> None:
    text = _text()

    _assert_all_present(text, [
        "This phase does not authorize creating:",
        "`scripts/local_media_agent/cid_cli.py`",
        "the `cid` entrypoint",
        "any runtime module",
        "any installer",
        "any commercial configuration",
        "any license",
        "any external integration",
    ])


def test_prohibited_modification_is_explicit() -> None:
    text = _text()

    _assert_all_present(text, [
        "This phase does not authorize modifying:",
        "`pyproject.toml`",
        "`read_only_folder_scanner.py`",
        "`read_only_folder_scanner_cli.py`",
        "any existing test",
        "any existing document",
    ])


def test_next_allowed_phase_is_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        "The only next phase allowed by this readiness gate is:",
        NEXT_PHASE,
        "minimal, isolated, reversible, read-only, stdout-only",
    ])


def test_phase_does_not_authorize_implementation() -> None:
    text = _text()

    _assert_all_present(text, [
        "This phase does NOT implement the `cid` command.",
        "This phase does NOT modify packaging.",
        "This phase does NOT execute the scanner.",
        "This phase does NOT grant implementation permission.",
    ])


def test_current_pyproject_scripts_has_no_cid_entry() -> None:
    scripts = snapshot_pyproject(ALIAS_READINESS_SOURCE_COMMIT)["project"]["scripts"]

    assert isinstance(scripts, dict)
    assert "cid" not in scripts


def test_cid_cli_module_is_absent_on_disk() -> None:
    assert "scripts/local_media_agent/cid_cli.py" in expected_absent_paths(ALIAS_READINESS_SOURCE_COMMIT)


def test_current_pyproject_scripts_has_exactly_three_entries() -> None:
    scripts = snapshot_pyproject(ALIAS_READINESS_SOURCE_COMMIT)["project"]["scripts"]

    assert isinstance(scripts, dict)
    assert len(scripts) == EXPECTED_SCRIPT_ENTRY_COUNT


def test_current_pyproject_scripts_mappings_are_exact() -> None:
    scripts = snapshot_pyproject(ALIAS_READINESS_SOURCE_COMMIT)["project"]["scripts"]

    assert scripts == EXPECTED_SCRIPT_ENTRIES


def test_frozen_pyproject_hash_is_exact() -> None:
    assert snapshot_sha256(ALIAS_READINESS_SOURCE_COMMIT) == EXPECTED_PYPROJECT_SHA256


def test_frozen_scanner_runtime_hash_is_exact() -> None:
    assert _sha256_of(SCANNER_RUNTIME_PATH) == RECONCILED_SCANNER_RUNTIME_SHA256


def test_frozen_scanner_cli_hash_is_exact() -> None:
    assert _sha256_of(SCANNER_CLI_PATH) == RECONCILED_SCANNER_CLI_SHA256


def test_frozen_hashes_are_documented_in_document() -> None:
    text = _text()

    _assert_all_present(text, [
        EXPECTED_PYPROJECT_SHA256,
        EXPECTED_SCANNER_RUNTIME_SHA256,
        EXPECTED_SCANNER_CLI_SHA256,
    ])
