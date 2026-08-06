from __future__ import annotations

import ast
import io
import json
import os
from pathlib import Path

import pytest

from scripts.local_media_agent import host_path_adapter as adapter
from scripts.local_media_agent import read_only_folder_scanner as scanner
from scripts.local_media_agent import read_only_folder_scanner_cli as cli


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts/local_media_agent/host_path_adapter.py"
SCANNER = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
CLI = ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"

WSL_DISTRO_ENV = "WSL_DISTRO_NAME"
SAMPLE_DISTRO = "Ubuntu-24.04-CID"


def _activate_wsl_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    mount_base = tmp_path / "mnt"
    monkeypatch.setattr(adapter, "_WSL_DRIVE_MOUNT_BASE", mount_base)
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    return mount_base


def _deactivate_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(WSL_DISTRO_ENV, raising=False)


def _guard_filesystem(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("filesystem access attempted during pure resolution")

    for attr in ("exists", "is_dir", "lstat", "resolve", "iterdir"):
        monkeypatch.setattr(Path, attr, _boom)


def _manifest() -> dict[str, object]:
    return {
        "schema_version": "test.v1",
        "status": "READ_ONLY_FOLDER_SCAN_COMPLETED",
        "input_label": "SANITIZED_LOCAL_FOLDER_INPUT",
        "privacy": {},
        "scanner_summary": {"files_seen": 0, "media_candidates": 0, "non_media_files": 0},
        "extension_summary": {},
        "warnings": [],
        "errors": [],
        "depth_summary": {},
    }


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = cli.run_cli(argv, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _ast_module(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _count_call_name(tree: ast.Module, name: str) -> int:
    return sum(
        isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == name
        for node in ast.walk(tree)
    )


def _imported_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


# ---------------------------------------------------------------- classification


def test_classify_posix_native_absolute_path() -> None:
    assert adapter._classify_path("/absolute/local/folder") == adapter.POSIX_NATIVE


def test_classify_relative_path() -> None:
    assert adapter._classify_path("relative/path") == adapter.RELATIVE_PATH


def test_classify_unc_path() -> None:
    assert adapter._classify_path("\\\\server\\share") == adapter.UNC_PATH


def test_classify_windows_device_path() -> None:
    assert adapter._classify_path("\\\\?\\C:\\system") == adapter.WINDOWS_DEVICE_PATH


def test_classify_url_path() -> None:
    assert adapter._classify_path("https://example.invalid/folder") == adapter.URL_PATH


def test_classify_direct_mnt_input() -> None:
    assert adapter._classify_path("/mnt/c/example") == adapter.DIRECT_MNT_INPUT
    assert adapter._classify_path("/mnt") == adapter.DIRECT_MNT_INPUT


def test_classify_windows_drive_on_non_windows_without_flag() -> None:
    assert adapter._classify_path("C:\\Users\\example") == adapter.WINDOWS_DRIVE_ON_NON_WINDOWS


def test_classify_wsl_bridge_when_drive_matches_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    assert (
        adapter._classify_path("D:\\Folder", development_wsl_host_drive="D")
        == adapter.WSL_WINDOWS_DEVELOPMENT_BRIDGE
    )


def test_classify_stays_drive_on_non_windows_on_drive_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    assert (
        adapter._classify_path("D:\\Folder", development_wsl_host_drive="C")
        == adapter.WINDOWS_DRIVE_ON_NON_WINDOWS
    )


def test_classify_windows_native_when_os_is_nt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "name", "nt")
    assert adapter._classify_path("D:\\Folder") == adapter.WINDOWS_NATIVE


def test_classify_lowercase_drive_letter_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    assert (
        adapter._classify_path("d:\\Media\\Clips", development_wsl_host_drive="D")
        == adapter.WSL_WINDOWS_DEVELOPMENT_BRIDGE
    )


# ---------------------------------------------------------- resolve, pure layer


def test_resolve_rejects_non_text_input_types() -> None:
    for value in (None, 123, object()):
        path, error = adapter.resolve_input_root(value)
        assert path is None
        assert error == adapter.ERROR_INPUT_TYPE_REJECTED


def test_resolve_rejects_empty_and_blank_input() -> None:
    for value in ("", "   "):
        path, error = adapter.resolve_input_root(value)
        assert path is None
        assert error == adapter.ERROR_INPUT_EMPTY_REJECTED


def test_resolve_rejects_url_with_url_code() -> None:
    path, error = adapter.resolve_input_root("https://example.invalid/folder")
    assert path is None
    assert error == adapter.ERROR_URL_PATH_REJECTED


def test_resolve_rejects_unc_with_unc_code() -> None:
    path, error = adapter.resolve_input_root("\\\\server\\share")
    assert path is None
    assert error == adapter.ERROR_UNC_PATH_REJECTED


def test_resolve_rejects_device_path_with_code() -> None:
    path, error = adapter.resolve_input_root("\\\\?\\C:\\system")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_DEVICE_PATH_REJECTED


def test_resolve_rejects_direct_mnt_with_mount_code() -> None:
    path, error = adapter.resolve_input_root("/mnt/c/private")
    assert path is None
    assert error == adapter.ERROR_MOUNT_PATH_REJECTED


def test_resolve_rejects_wsl_localhost_posix() -> None:
    path, error = adapter.resolve_input_root("/home/wsl.localhost/example")
    assert path is None
    assert error == adapter.ERROR_WSL_LOCALHOST_PATH_REJECTED


def test_resolve_rejects_relative_path() -> None:
    path, error = adapter.resolve_input_root("relative/path")
    assert path is None
    assert error == adapter.ERROR_RELATIVE_PATH_REJECTED


def test_resolve_rejects_windows_drive_without_flag() -> None:
    path, error = adapter.resolve_input_root("C:\\Users\\example")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_DRIVE_PATH_REJECTED


def test_resolve_rejects_windows_drive_with_invalid_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    path, error = adapter.resolve_input_root("D:\\x", development_wsl_host_drive="DD")
    assert path is None
    assert error == adapter.ERROR_WSL_HOST_DRIVE_ARGUMENT_REJECTED


def test_resolve_rejects_windows_drive_when_not_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    _deactivate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\x", development_wsl_host_drive="D")
    assert path is None
    assert error == adapter.ERROR_WSL_DEVELOPMENT_BRIDGE_UNAVAILABLE_REJECTED


def test_resolve_rejects_windows_drive_on_drive_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    path, error = adapter.resolve_input_root("D:\\x", development_wsl_host_drive="C")
    assert path is None
    assert error == adapter.ERROR_WSL_HOST_DRIVE_MISMATCH_REJECTED


def test_resolve_returns_posix_candidate_unchanged() -> None:
    path, error = adapter.resolve_input_root("/absolute/local/folder")
    assert error is None
    assert path == Path("/absolute/local/folder")


def test_resolve_accepts_path_object_input(tmp_path: Path) -> None:
    path, error = adapter.resolve_input_root(tmp_path)
    assert error is None
    assert path == tmp_path


def test_resolve_is_parsing_only_no_filesystem_access(tmp_path: Path) -> None:
    missing = tmp_path / "never_created"
    path, error = adapter.resolve_input_root(str(missing))
    assert error is None
    assert path == missing
    assert path.exists() is False


# ---------------------------------------------------------------- WSL translation


def test_windows_drive_translated_to_mnt_letter(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mount_base = _activate_wsl_bridge(monkeypatch, tmp_path)
    path, error = adapter.resolve_input_root("D:\\Folder\\Subfolder", development_wsl_host_drive="D")
    assert error is None
    assert path == mount_base / "d" / "Folder" / "Subfolder"
    assert str(path).startswith(str(mount_base))


def test_translated_path_accepts_forward_and_back_slashes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mount_base = _activate_wsl_bridge(monkeypatch, tmp_path)
    path, error = adapter.resolve_input_root("D:/Folder/Subfolder", development_wsl_host_drive="D")
    assert error is None
    assert path == mount_base / "d" / "Folder" / "Subfolder"


def test_wsl_bridge_rejects_drive_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    _guard_filesystem(monkeypatch)
    for raw_input in ("D:", "D:\\", "D:/", "d:\\", "d:/"):
        path, error = adapter.resolve_input_root(raw_input, development_wsl_host_drive="D")
        assert path is None
        assert error == adapter.ERROR_WINDOWS_DRIVE_ROOT_REJECTED
    path, error = adapter.resolve_input_root("D:\\")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_DRIVE_ROOT_REJECTED


def test_wsl_bridge_rejects_drive_relative_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    path, error = adapter.resolve_input_root("D:foo", development_wsl_host_drive="D")
    assert path is None
    assert error == adapter.ERROR_RELATIVE_PATH_REJECTED


def test_wsl_bridge_rejects_internal_traversal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    _guard_filesystem(monkeypatch)
    for raw_input in ("D:\\Folder\\..\\Sub", "D:\\Folder\\Sub\\..", "D:/Folder/../Sub", "d:\\folder\\..\\sub"):
        path, error = adapter.resolve_input_root(raw_input, development_wsl_host_drive="D")
        assert path is None
        assert error == adapter.ERROR_WINDOWS_PATH_TRAVERSAL_REJECTED


def test_wsl_bridge_rejects_escaping_traversal(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    _guard_filesystem(monkeypatch)
    for raw_input in ("D:\\..\\etc", "D:\\..\\..\\etc", "D:\\..\\..\\..\\var"):
        path, error = adapter.resolve_input_root(raw_input, development_wsl_host_drive="D")
        assert path is None
        assert error == adapter.ERROR_WINDOWS_PATH_TRAVERSAL_REJECTED


def test_adapter_public_api_exposes_only_resolve_input_root() -> None:
    assert adapter.__all__ == ["resolve_input_root"]
    assert callable(adapter.resolve_input_root)
    assert not hasattr(adapter, "classify_path")
    assert hasattr(adapter, "_classify_path")


def test_translated_path_preserves_unicode_folders(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    mount_base = _activate_wsl_bridge(monkeypatch, tmp_path)
    path, error = adapter.resolve_input_root("D:\\Mi Proyecto\\café.mov", development_wsl_host_drive="D")
    assert error is None
    assert path == mount_base / "d" / "Mi Proyecto" / "café.mov"


def test_wsl_bridge_requires_explicit_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    path, error = adapter.resolve_input_root("D:\\Folder")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_DRIVE_PATH_REJECTED


# ---------------------------------------------------------------- scanner integration


def test_scanner_bridge_scans_synthetic_mount(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    authorized = tmp_path / "mnt" / "d" / "authorized-root"
    authorized.mkdir(parents=True)
    (authorized / "clip.MOV").write_text("abcd", encoding="utf-8")
    (authorized / "notes.txt").write_text("xy", encoding="utf-8")

    manifest = scanner.scan_read_only_folder("D:\\authorized-root", development_wsl_host_drive="D")

    assert manifest["status"] == scanner.STATUS_COMPLETED
    assert manifest["scanner_summary"]["files_seen"] == 2
    assert manifest["scanner_summary"]["media_candidates"] == 1
    assert manifest["scanner_summary"]["non_media_files"] == 1
    assert manifest["errors"] == []


def test_scanner_bridge_manifest_is_sanitized(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    authorized = tmp_path / "mnt" / "d" / "secret_media"
    authorized.mkdir(parents=True)
    (authorized / "private_name.MOV").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder("D:\\secret_media", development_wsl_host_drive="D")
    payload = scanner.manifest_to_json(manifest)

    assert str(tmp_path) not in payload
    assert "secret_media" not in payload
    assert "private_name" not in payload
    assert "D:\\" not in payload


def test_scanner_bridge_privacy_flags_are_all_false(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    authorized = tmp_path / "mnt" / "d" / "privacy_root"
    authorized.mkdir(parents=True)
    (authorized / "a.mov").write_text("x", encoding="utf-8")

    manifest = scanner.scan_read_only_folder("D:\\privacy_root", development_wsl_host_drive="D")

    assert all(value is False for value in manifest["privacy"].values())
    assert manifest["privacy"]["subprocess_used"] is False
    assert manifest["privacy"]["network_used"] is False
    assert manifest["privacy"]["file_contents_opened"] is False


def test_scanner_rejects_windows_input_without_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    manifest = scanner.scan_read_only_folder("D:\\CID_DO_NOT_ACCESS")
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == ["WINDOWS_DRIVE_PATH_REJECTED"]
    assert manifest["scanner_summary"]["files_seen"] == 0


def test_scanner_rejects_direct_mnt_even_with_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    manifest = scanner.scan_read_only_folder("/mnt/d/anything", development_wsl_host_drive="D")
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == ["MOUNT_PATH_REJECTED"]


@pytest.mark.parametrize(
    ("raw_input", "expected_error"),
    [
        ("C:\\Users\\example", "WINDOWS_DRIVE_PATH_REJECTED"),
        ("\\\\server\\share", "UNC_PATH_REJECTED"),
        ("\\\\?\\C:\\system", "WINDOWS_DEVICE_PATH_REJECTED"),
        ("/mnt/c/example", "MOUNT_PATH_REJECTED"),
        ("https://example.invalid/folder", "URL_PATH_REJECTED"),
        ("/home/wsl.localhost/example", "WSL_LOCALHOST_PATH_REJECTED"),
        ("relative/path", "RELATIVE_PATH_REJECTED"),
    ],
)
def test_scanner_preserves_historical_and_new_rejection_codes(
    raw_input: str, expected_error: str
) -> None:
    manifest = scanner.scan_read_only_folder(raw_input)
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == [expected_error]
    assert manifest["scanner_summary"]["files_seen"] == 0


def test_scanner_rejects_windows_drive_with_mismatched_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    manifest = scanner.scan_read_only_folder("D:\\x", development_wsl_host_drive="C")
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == ["WSL_HOST_DRIVE_MISMATCH_REJECTED"]


def test_scanner_rejects_windows_drive_when_bridge_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    _deactivate_wsl(monkeypatch)
    manifest = scanner.scan_read_only_folder("D:\\x", development_wsl_host_drive="D")
    assert manifest["status"] == scanner.STATUS_REJECTED
    assert manifest["errors"] == ["WSL_DEVELOPMENT_BRIDGE_UNAVAILABLE_REJECTED"]


# ---------------------------------------------------------------- CLI


def test_cli_help_includes_development_flag() -> None:
    exit_code, stdout, stderr = _run_cli(["--help"])
    assert exit_code == cli.EXIT_SUCCESS
    assert stderr == ""
    assert "--development-wsl-host-drive DRIVE_LETTER" in stdout
    assert "/private" not in stdout


def test_cli_rejects_missing_input_root_with_flag() -> None:
    exit_code, stdout, stderr = _run_cli(["--development-wsl-host-drive", "D"])
    assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
    assert stdout == ""
    assert stderr == cli.CLI_ARGUMENTS_REJECTED + "\n"


def test_cli_rejects_invalid_drive_letter() -> None:
    for bad_value in ("DD", "", "1", "--x"):
        exit_code, stdout, stderr = _run_cli(
            ["--development-wsl-host-drive", bad_value, "--input-root", "/tmp/private-root"]
        )
        assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
        assert stdout == ""
        assert stderr == cli.CLI_ARGUMENTS_REJECTED + "\n"
        assert "private" not in stderr


def test_cli_rejects_duplicate_flags() -> None:
    exit_code, stdout, stderr = _run_cli(
        ["--development-wsl-host-drive", "D", "--development-wsl-host-drive", "C"]
    )
    assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
    assert stderr == cli.CLI_ARGUMENTS_REJECTED + "\n"


def test_cli_rejects_flag_without_input_root_value() -> None:
    exit_code, stdout, stderr = _run_cli(
        ["--input-root", "/tmp/x", "--development-wsl-host-drive"]
    )
    assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
    assert stderr == cli.CLI_ARGUMENTS_REJECTED + "\n"


def test_cli_delegates_drive_keyword_only_when_flag_present(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict[str, object]] = []

    def fake_runtime(input_root: str, **kwargs: object) -> dict[str, object]:
        calls.append({"root": input_root, "kwargs": kwargs})
        return _manifest()

    monkeypatch.setattr(cli, "scan_read_only_folder", fake_runtime)

    exit_code, stdout, stderr = _run_cli(["--input-root", "/tmp/x"])
    assert exit_code == cli.EXIT_SUCCESS
    assert calls == [{"root": "/tmp/x", "kwargs": {}}]

    exit_code, stdout, stderr = _run_cli(
        ["--development-wsl-host-drive", "D", "--input-root", "/tmp/x"]
    )
    assert exit_code == cli.EXIT_SUCCESS
    assert calls[1] == {"root": "/tmp/x", "kwargs": {"development_wsl_host_drive": "D"}}


def test_cli_runtime_rejection_is_sanitized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)
    exit_code, stdout, stderr = _run_cli(["--input-root", "D:\\CID_DO_NOT_ACCESS"])
    assert exit_code == cli.EXIT_ARGUMENTS_REJECTED
    assert stderr == ""
    assert stdout.count("\n") == 1
    payload = json.loads(stdout)
    assert payload["status"] == scanner.STATUS_REJECTED
    assert payload["errors"] == ["WINDOWS_DRIVE_PATH_REJECTED"]
    assert "CID_DO_NOT_ACCESS" not in stdout
    assert "D:\\" not in stdout


def test_cli_wsl_bridge_end_to_end_synthetic(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _activate_wsl_bridge(monkeypatch, tmp_path)
    authorized = tmp_path / "mnt" / "d" / "e2e-root"
    authorized.mkdir(parents=True)
    (authorized / "shot01.MOV").write_text("abcd", encoding="utf-8")

    exit_code, stdout, stderr = _run_cli(
        ["--development-wsl-host-drive", "D", "--input-root", "D:\\e2e-root"]
    )

    assert exit_code == cli.EXIT_SUCCESS
    assert stderr == ""
    assert stdout.endswith("\n")
    assert stdout.count("\n") == 1
    payload = json.loads(stdout)
    assert payload["scanner_summary"]["files_seen"] == 1
    assert payload["scanner_summary"]["media_candidates"] == 1
    assert str(tmp_path) not in stdout


# ---------------------------------------------------------------- safety invariants


def test_adapter_ast_has_zero_open_calls() -> None:
    tree = _ast_module(ADAPTER)
    assert _count_call_name(tree, "open") == 0
    assert _count_call_name(tree, "read_text") == 0
    assert _count_call_name(tree, "read_bytes") == 0


def test_adapter_ast_has_zero_subprocess_and_filesystem_enumeration() -> None:
    tree = _ast_module(ADAPTER)
    roots = _imported_roots(tree)
    forbidden_imports = {"subprocess", "socket", "requests", "httpx", "urllib", "sqlalchemy", "psycopg", "sqlite3"}
    assert roots.isdisjoint(forbidden_imports)
    source = ADAPTER.read_text(encoding="utf-8").lower()
    for token in ["subprocess(", "listdir", "iterdir(", "mount(", "scandir"]:
        assert token not in source


def test_adapter_ast_has_zero_network_and_database_imports() -> None:
    tree = _ast_module(ADAPTER)
    roots = _imported_roots(tree)
    assert not {"socket", "requests", "httpx", "urllib"}.intersection(roots)
    assert not {"sqlalchemy", "psycopg", "sqlite3"}.intersection(roots)


def test_scanner_ast_has_zero_open_and_subprocess() -> None:
    tree = _ast_module(SCANNER)
    assert _count_call_name(tree, "open") == 0
    roots = _imported_roots(tree)
    assert "subprocess" not in roots


def test_cli_ast_has_zero_subprocess() -> None:
    tree = _ast_module(CLI)
    roots = _imported_roots(tree)
    assert "subprocess" not in roots


def test_adapter_is_pure_no_side_effects_on_import() -> None:
    source = ADAPTER.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' not in source
    assert "raise SystemExit" not in source
    assert "print(" not in source


def test_bridge_never_uses_real_mnt_mount_base_in_tests(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mount_base = _activate_wsl_bridge(monkeypatch, tmp_path)
    path, error = adapter.resolve_input_root("D:\\only\\tmp", development_wsl_host_drive="D")
    assert error is None
    assert path is not None
    assert str(path).startswith(str(mount_base))
    assert not str(path).startswith("/mnt")
