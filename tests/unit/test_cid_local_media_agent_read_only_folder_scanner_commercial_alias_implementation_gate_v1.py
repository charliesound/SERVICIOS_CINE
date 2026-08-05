from __future__ import annotations

import ast
import hashlib
import io
import tomllib
from pathlib import Path

import pytest

from scripts.local_media_agent import cid_cli


ROOT = Path(__file__).resolve().parents[2]

PYPROJECT = ROOT / "pyproject.toml"

CID_CLI_PATH = (
    ROOT
    / "scripts/local_media_agent/cid_cli.py"
)

IMPLEMENTATION_DOC = (
    ROOT
    / "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_folder_scanner_"
    "commercial_alias_implementation_gate_v1.md"
)

READINESS_DOC = (
    ROOT
    / "docs/product/local_media_agent/"
    "cid_local_media_agent_read_only_folder_scanner_"
    "commercial_alias_readiness_gate_v1.md"
)

READINESS_TEST = (
    ROOT
    / "tests/unit/"
    "test_cid_local_media_agent_read_only_folder_scanner_"
    "commercial_alias_readiness_gate_v1.py"
)

SCANNER_RUNTIME = (
    ROOT
    / "scripts/local_media_agent/"
    "read_only_folder_scanner.py"
)

SCANNER_CLI = (
    ROOT
    / "scripts/local_media_agent/"
    "read_only_folder_scanner_cli.py"
)

PHASE = (
    "CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_"
    "COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1"
)

EXPECTED_RESULT = (
    "CID_LAPTOP_LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_"
    "COMMERCIAL_ALIAS_IMPLEMENTATION_GATE_V1_"
    "COMPLETED_AND_VERIFIED"
)

EXPECTED_SCRIPTS = {
    "cid-local-media-agent-visible-report-write-enabled-export":
        "scripts.local_media_agent."
        "ffprobe_controlled_file_metadata_visible_report_"
        "controlled_text_artifact_write_enabled_export_cli:main",
    "cid-local-media-agent-controlled-local-demo-runner":
        "scripts.local_media_agent."
        "cid_local_media_agent_write_enabled_export_cli_"
        "installed_controlled_local_demo_runner:main",
    "cid-local-media-agent-read-only-folder-scanner":
        "scripts.local_media_agent."
        "read_only_folder_scanner_cli:main",
    "cid":
        "scripts.local_media_agent.cid_cli:main",
}

EXPECTED_UMBRELLA_HELP = (
    "Usage: cid COMMAND [OPTIONS]\n"
    "Commands:\n"
    "  scan    Scan one absolute local Linux folder in read-only mode.\n"
    "Options:\n"
    "  --help\n"
)

EXPECTED_SCAN_HELP = (
    "Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "Options:\n"
    "  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "  --help\n"
)

EXPECTED_READINESS_DOC_SHA256 = (
    "f2dab63d09b0c3f5bb63ae310be3ea445bf29f76b751f333491df7b5fc462823"
)

EXPECTED_READINESS_TEST_SHA256 = (
    "aeca61cafb75102e2ba3e7bf3207b85f111604dfd432edd419e2c711b7795220"
)

EXPECTED_SCANNER_RUNTIME_SHA256 = (
    "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
)

EXPECTED_SCANNER_CLI_SHA256 = (
    "ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_implementation_document_identity_is_exact() -> None:
    text = IMPLEMENTATION_DOC.read_text(encoding="utf-8")

    assert PHASE in text
    assert EXPECTED_RESULT in text
    assert "No other path is authorized." in text


def test_pyproject_contains_exact_four_scripts() -> None:
    data = tomllib.loads(
        PYPROJECT.read_text(encoding="utf-8")
    )

    scripts = data["project"]["scripts"]

    assert scripts == EXPECTED_SCRIPTS
    assert len(scripts) == 4


def test_cid_entrypoint_mapping_is_exact() -> None:
    data = tomllib.loads(
        PYPROJECT.read_text(encoding="utf-8")
    )

    assert (
        data["project"]["scripts"]["cid"]
        == "scripts.local_media_agent.cid_cli:main"
    )


def test_public_python_api_ast_is_exact() -> None:
    tree = ast.parse(
        CID_CLI_PATH.read_text(encoding="utf-8")
    )

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    assert set(functions) >= {"run_cli", "main"}

    run_cli_node = functions["run_cli"]
    main_node = functions["main"]

    assert [
        argument.arg
        for argument in run_cli_node.args.args
    ] == ["argv", "stdout", "stderr"]

    assert [
        ast.unparse(argument.annotation)
        for argument in run_cli_node.args.args
    ] == [
        "Sequence[str] | None",
        "TextIO | None",
        "TextIO | None",
    ]

    assert ast.unparse(run_cli_node.returns) == "int"

    assert main_node.args.args == []
    assert ast.unparse(main_node.returns) == "int"


def test_main_guard_is_exact() -> None:
    source = CID_CLI_PATH.read_text(encoding="utf-8")

    assert (
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main())\n"
    ) in source


def test_umbrella_help_is_exact() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = cid_cli.run_cli(
        ["--help"],
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert stdout.getvalue() == EXPECTED_UMBRELLA_HELP
    assert stderr.getvalue() == ""


def test_scan_help_is_exact() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    result = cid_cli.run_cli(
        ["scan", "--help"],
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert stdout.getvalue() == EXPECTED_SCAN_HELP
    assert stderr.getvalue() == ""


def test_help_never_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_delegate(*args: object, **kwargs: object) -> int:
        raise AssertionError("delegation was not allowed")

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        forbidden_delegate,
    )

    assert cid_cli.run_cli(
        ["--help"],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0

    assert cid_cli.run_cli(
        ["scan", "--help"],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    ) == 0


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["-h"],
        ["unknown"],
        ["--unknown"],
        ["export"],
        ["--help", "extra"],
    ],
)
def test_invalid_umbrella_invocations_are_sanitized(
    argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_delegate(*args: object, **kwargs: object) -> int:
        raise AssertionError("delegation was not allowed")

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        forbidden_delegate,
    )

    stdout = io.StringIO()
    stderr = io.StringIO()

    result = cid_cli.run_cli(
        argv,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 2
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "CID_CLI_ARGUMENTS_REJECTED\n"
    )


@pytest.mark.parametrize(
    ("argv", "expected_delegated_argv"),
    [
        (["scan"], []),
        (
            ["scan", "--input-root", "/absolute/local/folder"],
            ["--input-root", "/absolute/local/folder"],
        ),
        (
            ["scan", "--unknown", "private-value"],
            ["--unknown", "private-value"],
        ),
    ],
)
def test_scan_arguments_are_passed_without_transformation(
    argv: list[str],
    expected_delegated_argv: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    observed: dict[str, object] = {}

    def fake_delegate(
        delegated_argv: list[str],
        stdout: io.StringIO,
        stderr: io.StringIO,
    ) -> int:
        observed["argv"] = delegated_argv
        observed["stdout"] = stdout
        observed["stderr"] = stderr
        return 3

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        fake_delegate,
    )

    result = cid_cli.run_cli(
        argv,
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 3
    assert observed["argv"] == expected_delegated_argv
    assert observed["stdout"] is stdout
    assert observed["stderr"] is stderr


@pytest.mark.parametrize("exit_code", [0, 1, 2, 3])
def test_delegated_exit_code_is_propagated_exactly(
    exit_code: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_delegate(
        argv: list[str],
        stdout: io.StringIO,
        stderr: io.StringIO,
    ) -> int:
        return exit_code

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        fake_delegate,
    )

    result = cid_cli.run_cli(
        ["scan", "--input-root", "/absolute/local/folder"],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    )

    assert result == exit_code


def test_delegated_stdout_and_stderr_are_preserved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_delegate(
        argv: list[str],
        stdout: io.StringIO,
        stderr: io.StringIO,
    ) -> int:
        stdout.write('{"status":"completed"}\n')
        stderr.write("CONTROLLED_WARNING\n")
        return 0

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        fake_delegate,
    )

    stdout = io.StringIO()
    stderr = io.StringIO()

    result = cid_cli.run_cli(
        ["scan", "--input-root", "/absolute/local/folder"],
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 0
    assert stdout.getvalue() == (
        '{"status":"completed"}\n'
    )
    assert stderr.getvalue() == "CONTROLLED_WARNING\n"


def test_unexpected_delegation_failure_is_sanitized(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing_delegate(
        argv: list[str],
        stdout: io.StringIO,
        stderr: io.StringIO,
    ) -> int:
        raise RuntimeError(
            "/private/path must never be disclosed"
        )

    monkeypatch.setattr(
        cid_cli.read_only_folder_scanner_cli,
        "run_cli",
        failing_delegate,
    )

    stdout = io.StringIO()
    stderr = io.StringIO()

    result = cid_cli.run_cli(
        ["scan", "--input-root", "/private/path"],
        stdout=stdout,
        stderr=stderr,
    )

    assert result == 1
    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        "CID_CLI_INTERNAL_FAILURE\n"
    )
    assert "/private/path" not in stderr.getvalue()


def test_main_returns_run_cli_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        cid_cli,
        "run_cli",
        lambda: 3,
    )

    assert cid_cli.main() == 3


def test_runtime_has_no_forbidden_capability_imports() -> None:
    tree = ast.parse(
        CID_CLI_PATH.read_text(encoding="utf-8")
    )

    imported_roots: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(
                alias.name.split(".", 1)[0]
                for alias in node.names
            )

        if isinstance(node, ast.ImportFrom):
            if node.module:
                imported_roots.add(
                    node.module.split(".", 1)[0]
                )

    forbidden = {
        "asyncio",
        "glob",
        "os",
        "pathlib",
        "shutil",
        "socket",
        "sqlite3",
        "subprocess",
    }

    assert imported_roots.isdisjoint(forbidden)


def test_runtime_does_not_call_scanner_directly() -> None:
    source = CID_CLI_PATH.read_text(encoding="utf-8")

    assert "scan_read_only_folder" not in source

    assert (
        "read_only_folder_scanner_cli.run_cli"
        in source
    )


def test_frozen_files_remain_exact() -> None:
    assert (
        _sha256(READINESS_DOC)
        == EXPECTED_READINESS_DOC_SHA256
    )

    assert (
        _sha256(READINESS_TEST)
        == EXPECTED_READINESS_TEST_SHA256
    )

    assert (
        _sha256(SCANNER_RUNTIME)
        == EXPECTED_SCANNER_RUNTIME_SHA256
    )

    assert (
        _sha256(SCANNER_CLI)
        == EXPECTED_SCANNER_CLI_SHA256
    )
