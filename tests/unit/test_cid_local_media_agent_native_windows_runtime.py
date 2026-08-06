"""Native Windows runtime contract tests for the read-only folder scanner path adapter.

These tests use a controlled ``os.name == "nt"`` simulation. They never claim
empirical Windows validation and never touch real media or ``/mnt``.
"""

from __future__ import annotations

import ast
import hashlib
import os
from pathlib import Path

import pytest

from scripts.local_media_agent import host_path_adapter as adapter


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "scripts/local_media_agent/host_path_adapter.py"
SCANNER = ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
SCANNER_CLI = ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"
CID_CLI = ROOT / "scripts/local_media_agent/cid_cli.py"

WSL_DISTRO_ENV = "WSL_DISTRO_NAME"
SAMPLE_DISTRO = "Ubuntu-24.04-CID"

FROZEN_SCANNER_SHA256 = "1d0dc95cff6d69cf973780452eea3087cc86af0ff5b07a63595157d77f3722c7"
FROZEN_SCANNER_CLI_SHA256 = "1d8df7aeaf9a94df112f7f55ffcbdf95564188c9bafcf5dc1359aebffa49a2f6"
FROZEN_CID_CLI_SHA256 = "f48ce145afef969a2fc2866ce1b40f50cd699f3ea3d2bfa96d1454337de399b2"


def _activate_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os, "name", "nt")


def _activate_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(WSL_DISTRO_ENV, SAMPLE_DISTRO)


def _deactivate_wsl(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(WSL_DISTRO_ENV, raising=False)


def _import_roots(tree: ast.Module) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


# ---------------------------------------------------------- 1-10 Windows native


def test_windows_native_accepts_absolute_drive_path_without_wsl_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\CLIENT_SELECTED_FOLDER")
    assert error is None
    assert path is not None
    assert str(path) == "D:\\CLIENT_SELECTED_FOLDER"


def test_windows_native_accepts_conceptual_c_drive_without_fixed_drive(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("C:\\Media\\Clips")
    assert error is None
    assert str(path) == "C:\\Media\\Clips"


def test_windows_native_accepts_conceptual_d_drive_without_fixed_drive(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Media\\Clips")
    assert error is None
    assert str(path) == "D:\\Media\\Clips"


def test_windows_native_preserves_paths_with_spaces(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\MATERIAL RODAJE")
    assert error is None
    assert str(path) == "D:\\MATERIAL RODAJE"
    assert "MATERIAL RODAJE" in str(path)


def test_windows_native_does_not_require_development_wsl_host_drive(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder", development_wsl_host_drive=None)
    assert error is None
    assert path is not None


def test_windows_native_does_not_translate_input_to_mnt(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder\\Subfolder")
    assert error is None
    assert str(path) == "D:\\Folder\\Subfolder"
    assert "/mnt" not in str(path)
    assert not str(path).startswith("/mnt")


def test_windows_native_rejects_wsl_development_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder", development_wsl_host_drive="D")
    assert path is None
    assert error == "WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED"


def test_windows_native_rejection_uses_stable_sanitized_identifier(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder", development_wsl_host_drive="D")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED
    assert error == "WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED"


def test_windows_native_rejection_omits_path_folder_and_drive_letter(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\SECRET_FOLDER", development_wsl_host_drive="D")
    assert path is None
    assert error is not None
    assert "SECRET_FOLDER" not in error
    assert "D:\\" not in error
    assert "\\" not in error
    assert "/mnt" not in error


def test_windows_native_rejection_happens_before_filesystem_access(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_windows(monkeypatch)

    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("filesystem access attempted during rejection")

    for attr in ("exists", "is_dir", "lstat", "resolve", "iterdir"):
        monkeypatch.setattr(Path, attr, _boom)

    path, error = adapter.resolve_input_root("D:\\Anything", development_wsl_host_drive="D")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED


# ----------------------------------------------------------- 11-17 WSL and POSIX


def test_wsl_keeps_controlled_translation_with_matching_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mount_base = tmp_path / "mnt"
    monkeypatch.setattr(adapter, "_WSL_DRIVE_MOUNT_BASE", mount_base)
    _activate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder\\Subfolder", development_wsl_host_drive="D")
    assert error is None
    assert path == mount_base / "d" / "Folder" / "Subfolder"


def test_wsl_rejects_drive_letter_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder", development_wsl_host_drive="C")
    assert path is None
    assert error == adapter.ERROR_WSL_HOST_DRIVE_MISMATCH_REJECTED


def test_wsl_still_requires_flag_for_windows_host_path(monkeypatch: pytest.MonkeyPatch) -> None:
    _activate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("D:\\Folder")
    assert path is None
    assert error == adapter.ERROR_WINDOWS_DRIVE_PATH_REJECTED


def test_direct_mnt_input_still_rejected() -> None:
    path, error = adapter.resolve_input_root("/mnt/c/anything")
    assert path is None
    assert error == adapter.ERROR_MOUNT_PATH_REJECTED


def test_posix_native_accepts_absolute_posix_path(monkeypatch: pytest.MonkeyPatch) -> None:
    _deactivate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("/CLIENT_SELECTED_FOLDER")
    assert error is None
    assert str(path) == "/CLIENT_SELECTED_FOLDER"


def test_posix_native_does_not_require_wsl_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    _deactivate_wsl(monkeypatch)
    path, error = adapter.resolve_input_root("/absolute/local/folder", development_wsl_host_drive=None)
    assert error is None
    assert path is not None


def test_relative_path_still_rejected() -> None:
    path, error = adapter.resolve_input_root("relative/path")
    assert path is None
    assert error == adapter.ERROR_RELATIVE_PATH_REJECTED


# ----------------------------------------------------------- 18-20 static safety


def test_adapter_has_no_subprocess_socket_requests_or_urllib() -> None:
    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    roots = _import_roots(tree)
    forbidden = {"subprocess", "socket", "requests", "httpx", "urllib"}
    assert roots.isdisjoint(forbidden)
    source = ADAPTER.read_text(encoding="utf-8").lower()
    assert "subprocess(" not in source


def test_adapter_has_no_database_saas_ffprobe_or_ffmpeg() -> None:
    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    roots = _import_roots(tree)
    forbidden = {"sqlalchemy", "psycopg", "psycopg2", "sqlite3", "requests", "httpx", "urllib"}
    assert roots.isdisjoint(forbidden)
    source = ADAPTER.read_text(encoding="utf-8").lower()
    assert "ffprobe" not in source
    assert "ffmpeg" not in source


def test_frozen_runtime_files_remain_unchanged_by_hash() -> None:
    assert hashlib.sha256(SCANNER.read_bytes()).hexdigest() == FROZEN_SCANNER_SHA256
    assert hashlib.sha256(SCANNER_CLI.read_bytes()).hexdigest() == FROZEN_SCANNER_CLI_SHA256
    assert hashlib.sha256(CID_CLI.read_bytes()).hexdigest() == FROZEN_CID_CLI_SHA256
