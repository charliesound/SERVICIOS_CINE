from __future__ import annotations

import hashlib
import importlib
import inspect
import io
import json
from pathlib import Path

import pytest

from scripts.local_media_agent import read_only_folder_scanner_cli as cli

from _cid_historical_contract_snapshot import snapshot_pyproject_text


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.md"
MODULE = ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py"
RUNTIME = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
PYPROJECT = ROOT / "pyproject.toml"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.IMPLEMENTATION.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_CLI_IMPLEMENTATION_GATE_V1_CLOSED"
BASE_HEAD = "bc303c43bd10ce153b49514990ee2e6e0579ab62"
PREVIOUS_TAG = "cid-dev-stable-local-media-agent-read-only-folder-scanner-cli-readiness-gate-v1-20260729"
RUNTIME_SHA = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.CLI.QA.GATE.V1"

CLI_IMPLEMENTATION_SOURCE_COMMIT = "1113c81c7bd7ca60cfe06f1794000bd7c23939d7"

AUTHORIZED_FILES = [
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.md",
    "scripts/local_media_agent/read_only_folder_scanner_cli.py",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_cli_implementation_gate_v1.py",
]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_doc_contains(values: list[str]) -> None:
    text = _text(DOC)
    for value in values:
        assert value in text, f"missing expected value: {value!r}"


def _runtime_sha256() -> str:
    return hashlib.sha256(RUNTIME.read_bytes()).hexdigest()


def _run(argv: list[object]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = cli.run_cli(argv, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _manifest(status: str) -> dict[str, object]:
    return {
        "schema_version": "test.v1",
        "status": status,
        "input_label": "SANITIZED_LOCAL_FOLDER_INPUT",
        "privacy": {},
        "scanner_summary": {"files_seen": 0, "media_candidates": 0, "non_media_files": 0},
        "extension_summary": {},
        "warnings": [],
        "errors": [],
        "depth_summary": {},
    }


def test_identity_scope_and_files_exist() -> None:
    assert DOC.exists()
    assert MODULE.exists()
    assert TEST.exists()
    _assert_doc_contains([PHASE, EXPECTED_RESULT, BASE_HEAD, PREVIOUS_TAG, RUNTIME_SHA, NEXT_PHASE])
    _assert_doc_contains(AUTHORIZED_FILES)


def test_runtime_sha_pyproject_and_no_entrypoint_alias() -> None:
    assert _runtime_sha256() == RUNTIME_SHA
    pyproject = snapshot_pyproject_text(CLI_IMPLEMENTATION_SOURCE_COMMIT)
    assert "read_only_folder_scanner_cli" not in pyproject
    assert "cid scan" not in pyproject
    assert "cid =" not in pyproject


def test_import_does_not_execute_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def forbidden_run_cli(*args, **kwargs):
        calls.append("run")
        return 99

    monkeypatch.setattr(cli, "run_cli", forbidden_run_cli)
    importlib.reload(cli)
    assert calls == []


def test_api_signature_and_main_guard() -> None:
    signature = inspect.signature(cli.run_cli)
    assert list(signature.parameters) == ["argv", "stdout", "stderr"]
    assert signature.parameters["stdout"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert signature.parameters["stderr"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert callable(cli.main)
    source = _text(MODULE)
    assert 'if __name__ == "__main__":' in source
    assert "raise SystemExit(main())" in source


def test_help_output(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def forbidden_runtime(input_root: str):
        nonlocal called
        called = True
        return _manifest("READ_ONLY_FOLDER_SCAN_COMPLETED")

    monkeypatch.setattr(cli, "scan_read_only_folder", forbidden_runtime)
    exit_code, stdout, stderr = _run(["--help"])

    assert exit_code == cli.EXIT_SUCCESS
    assert called is False
    assert stderr == ""
    assert stdout == cli.HELP_TEXT
    assert stdout.endswith("\n")
    assert "/private" not in stdout


def test_help_output_accepts_positional_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden_runtime(input_root: str):
        raise AssertionError("runtime must not be called")

    monkeypatch.setattr(cli, "scan_read_only_folder", forbidden_runtime)
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = cli.run_cli(["--help"], stdout, stderr)

    assert exit_code == cli.EXIT_SUCCESS
    assert stdout.getvalue() == cli.HELP_TEXT
    assert stderr.getvalue() == ""


@pytest.mark.parametrize("argv", [
    [],
    ["--input-root"],
    ["--input-root", "/private/a", "--input-root", "/private/b"],
    ["--unknown"],
    ["/private/positional"],
    ["-h"],
    ["--input-root=/private/path"],
    ["--help", "--input-root", "/private/path"],
    ["--input-root", "/private/path", "extra"],
    ["--input-root", object()],
    ["--input-root", "--help"],
    ["--input-root", "--input-root"],
    ["--input-root", "--unknown"],
    ["--input-root", "-h"],
])
def test_argument_rejections_do_not_call_runtime_or_leak(monkeypatch: pytest.MonkeyPatch, argv: list[object]) -> None:
    def forbidden_runtime(input_root: str):
        raise AssertionError("runtime must not be called")

    monkeypatch.setattr(cli, "scan_read_only_folder", forbidden_runtime)
    exit_code, stdout, stderr = _run(argv)

    assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
    assert stdout == ""
    assert stderr == cli.CLI_ARGUMENTS_REJECTED + "\n"
    assert "/private" not in stderr


def test_valid_value_is_delegated_once_without_transformation(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    private_value = "/tmp/private-input-root"

    def fake_runtime(input_root: str) -> dict[str, object]:
        calls.append(input_root)
        return _manifest("READ_ONLY_FOLDER_SCAN_COMPLETED")

    monkeypatch.setattr(cli, "scan_read_only_folder", fake_runtime)
    exit_code, stdout, stderr = _run(["--input-root", private_value])

    assert calls == [private_value]
    assert exit_code == cli.EXIT_SUCCESS
    assert stderr == ""
    assert json.loads(stdout) == _manifest("READ_ONLY_FOLDER_SCAN_COMPLETED")
    assert stdout.endswith("\n")


@pytest.mark.parametrize("status,expected_exit", [
    ("READ_ONLY_FOLDER_SCAN_COMPLETED", 0),
    ("READ_ONLY_FOLDER_SCAN_COMPLETED_WITH_WARNINGS", 0),
    ("READ_ONLY_FOLDER_SCAN_REJECTED", 2),
    ("READ_ONLY_FOLDER_SCAN_TRUNCATED", 3),
])
def test_status_mapping_json_stdout_and_empty_stderr(
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    expected_exit: int,
) -> None:
    manifest = _manifest(status)
    original = json.loads(json.dumps(manifest, sort_keys=True))
    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: manifest)

    exit_code, stdout, stderr = _run(["--input-root", "/tmp/private"])

    assert exit_code == expected_exit
    assert stderr == ""
    assert stdout.count("\n") == 1
    assert stdout.endswith("\n")
    assert json.loads(stdout) == manifest
    assert manifest == original


def test_manifest_to_json_is_used_and_output_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = _manifest("READ_ONLY_FOLDER_SCAN_COMPLETED")
    calls: list[dict[str, object]] = []

    def fake_json(payload: dict[str, object]) -> str:
        calls.append(payload)
        return "{\"stable\":true}"

    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: manifest)
    monkeypatch.setattr(cli, "manifest_to_json", fake_json)

    first = _run(["--input-root", "/tmp/private"])
    second = _run(["--input-root", "/tmp/private"])

    assert first == second == (cli.EXIT_SUCCESS, "{\"stable\":true}\n", "")
    assert calls == [manifest, manifest]


@pytest.mark.parametrize("manifest", [
    {},
    {"status": None},
    {"status": "UNKNOWN_STATUS"},
    [],
])
def test_invalid_manifest_status_is_internal_failure(monkeypatch: pytest.MonkeyPatch, manifest: object) -> None:
    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: manifest)
    exit_code, stdout, stderr = _run(["--input-root", "/tmp/private-status"])
    assert exit_code == cli.EXIT_INTERNAL_FAILURE
    assert stdout == ""
    assert stderr == cli.CLI_INTERNAL_FAILURE + "\n"
    assert "private-status" not in stderr


def test_runtime_exception_is_internal_failure_without_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_runtime(input_root: str):
        raise RuntimeError("/private/runtime/path")

    monkeypatch.setattr(cli, "scan_read_only_folder", failing_runtime)
    exit_code, stdout, stderr = _run(["--input-root", "/tmp/private-runtime"])
    assert exit_code == cli.EXIT_INTERNAL_FAILURE
    assert stdout == ""
    assert stderr == cli.CLI_INTERNAL_FAILURE + "\n"
    assert "private" not in stderr
    assert "RuntimeError" not in stderr


def test_manifest_to_json_exception_is_internal_failure_without_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: _manifest("READ_ONLY_FOLDER_SCAN_COMPLETED"))

    def failing_json(manifest: dict[str, object]) -> str:
        raise ValueError("/private/json/path")

    monkeypatch.setattr(cli, "manifest_to_json", failing_json)
    exit_code, stdout, stderr = _run(["--input-root", "/tmp/private-json"])
    assert exit_code == cli.EXIT_INTERNAL_FAILURE
    assert stdout == ""
    assert stderr == cli.CLI_INTERNAL_FAILURE + "\n"
    assert "private" not in stderr
    assert "ValueError" not in stderr


def test_keyboard_interrupt_and_system_exit_are_not_caught(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        cli.run_cli(["--input-root", "/tmp/private"], stdout=io.StringIO(), stderr=io.StringIO())

    monkeypatch.setattr(cli, "scan_read_only_folder", lambda input_root: (_ for _ in ()).throw(SystemExit(7)))
    with pytest.raises(SystemExit):
        cli.run_cli(["--input-root", "/tmp/private"], stdout=io.StringIO(), stderr=io.StringIO())


def test_static_audit_has_no_forbidden_imports_or_filesystem_inspection() -> None:
    source = _text(MODULE).lower()
    forbidden = [
        "argparse",
        "pathlib",
        "import os",
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "ffprobe",
        "ffmpeg",
        "open(",
        "path(",
        "resolve",
        "expanduser",
        "exists",
        "is_dir",
        "lstat",
        "iterdir",
        "environ",
        "getenv",
        "write_text",
        "write_bytes",
        "touch(",
        "glob",
    ]
    for value in forbidden:
        assert value not in source


def test_controlled_tmp_path_regression(tmp_path: Path) -> None:
    (tmp_path / "clip.MOV").write_text("abcd", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("xy", encoding="utf-8")
    exit_code, stdout, stderr = _run(["--input-root", str(tmp_path)])
    payload = json.loads(stdout)

    assert exit_code == cli.EXIT_SUCCESS
    assert stderr == ""
    assert stdout.count("\n") == 1
    assert payload["scanner_summary"]["files_seen"] == 2
    assert payload["scanner_summary"]["media_candidates"] == 1
    assert payload["scanner_summary"]["non_media_files"] == 1


def test_main_delegates_to_run_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "run_cli", lambda: 33)
    assert cli.main() == 33
