"""Pure host drive path portability adapter for the read-only folder scanner.

This module performs parsing and classification only. It never opens files,
spawns subprocesses, enumerates mounts, or touches the network, database, or
SaaS. It translates a Windows host drive input such as ``D:\\Folder\\Subfolder``
into the WSL mount candidate ``/mnt/d/Folder/Subfolder`` only when the explicit
``development_wsl_host_drive`` bridge flag is present and the runtime looks like
WSL. All rejections are sanitized error codes without private paths.
"""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath, PureWindowsPath


POSIX_NATIVE = "POSIX_NATIVE"
WINDOWS_NATIVE = "WINDOWS_NATIVE"
WINDOWS_DRIVE_ON_NON_WINDOWS = "WINDOWS_DRIVE_ON_NON_WINDOWS"
WSL_WINDOWS_DEVELOPMENT_BRIDGE = "WSL_WINDOWS_DEVELOPMENT_BRIDGE"
UNC_PATH = "UNC_PATH"
WINDOWS_DEVICE_PATH = "WINDOWS_DEVICE_PATH"
URL_PATH = "URL_PATH"
RELATIVE_PATH = "RELATIVE_PATH"
DIRECT_MNT_INPUT = "DIRECT_MNT_INPUT"

ERROR_INPUT_TYPE_REJECTED = "INPUT_TYPE_REJECTED"
ERROR_INPUT_EMPTY_REJECTED = "INPUT_EMPTY_REJECTED"
ERROR_INPUT_VALIDATION_FAILED = "INPUT_VALIDATION_FAILED"
ERROR_URL_PATH_REJECTED = "URL_PATH_REJECTED"
ERROR_WINDOWS_DEVICE_PATH_REJECTED = "WINDOWS_DEVICE_PATH_REJECTED"
ERROR_UNC_PATH_REJECTED = "UNC_PATH_REJECTED"
ERROR_MOUNT_PATH_REJECTED = "MOUNT_PATH_REJECTED"
ERROR_WSL_LOCALHOST_PATH_REJECTED = "WSL_LOCALHOST_PATH_REJECTED"
ERROR_RELATIVE_PATH_REJECTED = "RELATIVE_PATH_REJECTED"
ERROR_WINDOWS_DRIVE_PATH_REJECTED = "WINDOWS_DRIVE_PATH_REJECTED"
ERROR_WSL_HOST_DRIVE_ARGUMENT_REJECTED = "WSL_HOST_DRIVE_ARGUMENT_REJECTED"
ERROR_WSL_DEVELOPMENT_BRIDGE_UNAVAILABLE_REJECTED = (
    "WSL_DEVELOPMENT_BRIDGE_UNAVAILABLE_REJECTED"
)
ERROR_WSL_HOST_DRIVE_MISMATCH_REJECTED = "WSL_HOST_DRIVE_MISMATCH_REJECTED"
ERROR_WINDOWS_DRIVE_ROOT_REJECTED = "WINDOWS_DRIVE_ROOT_REJECTED"
ERROR_WINDOWS_PATH_TRAVERSAL_REJECTED = "WINDOWS_PATH_TRAVERSAL_REJECTED"
ERROR_WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED = (
    "WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED"
)

_DRIVE_LETTERS = frozenset("abcdefghijklmnopqrstuvwxyz")

_WSL_DRIVE_MOUNT_BASE = PurePosixPath("/mnt")

_WSL_DISTRO_ENV = "WSL_DISTRO_NAME"


def _classify_path(
    raw: str,
    *,
    development_wsl_host_drive: str | None = None,
) -> str:
    """Classify a raw input string into a host path portability category."""
    if _is_url_like(raw):
        return URL_PATH
    if _is_windows_device_path(raw):
        return WINDOWS_DEVICE_PATH
    if _is_unc_path(raw):
        return UNC_PATH
    if raw == "/mnt" or raw.startswith("/mnt/"):
        return DIRECT_MNT_INPUT
    drive_letter = _windows_drive_letter(raw)
    if drive_letter is not None:
        if os.name == "nt":
            return WINDOWS_NATIVE
        if _wsl_bridge_applies(raw, drive_letter, development_wsl_host_drive):
            return WSL_WINDOWS_DEVELOPMENT_BRIDGE
        return WINDOWS_DRIVE_ON_NON_WINDOWS
    if not raw.startswith("/"):
        return RELATIVE_PATH
    return POSIX_NATIVE


def resolve_input_root(
    raw_input_root: str | Path,
    *,
    development_wsl_host_drive: str | None = None,
) -> tuple[Path | None, str | None]:
    """Resolve a raw input root into a validated candidate path or a rejection.

    Returns ``(path, None)`` for a candidate path that the scanner must still
    check against the local filesystem, or ``(None, error_code)`` for a
    sanitized rejection. No filesystem is ever accessed here.
    """
    if not isinstance(raw_input_root, (str, Path)):
        return None, ERROR_INPUT_TYPE_REJECTED

    raw = str(raw_input_root).strip()
    if not raw:
        return None, ERROR_INPUT_EMPTY_REJECTED

    if _is_windows_drive_root(raw):
        return None, ERROR_WINDOWS_DRIVE_ROOT_REJECTED
    if _windows_drive_letter(raw) is not None and _contains_windows_traversal(raw):
        return None, ERROR_WINDOWS_PATH_TRAVERSAL_REJECTED

    if development_wsl_host_drive is not None and os.name == "nt":
        return None, ERROR_WINDOWS_NATIVE_WSL_DEVELOPMENT_FLAG_NOT_ALLOWED

    category = _classify_path(
        raw,
        development_wsl_host_drive=development_wsl_host_drive,
    )

    if category == URL_PATH:
        return None, ERROR_URL_PATH_REJECTED
    if category == WINDOWS_DEVICE_PATH:
        return None, ERROR_WINDOWS_DEVICE_PATH_REJECTED
    if category == UNC_PATH:
        return None, ERROR_UNC_PATH_REJECTED
    if category == DIRECT_MNT_INPUT:
        return None, ERROR_MOUNT_PATH_REJECTED
    if category == WSL_WINDOWS_DEVELOPMENT_BRIDGE:
        translated = _translate_windows_drive(raw)
        if translated is None:
            return None, ERROR_INPUT_VALIDATION_FAILED
        return translated, None
    if category == WINDOWS_DRIVE_ON_NON_WINDOWS:
        return _reject_windows_drive(raw, development_wsl_host_drive)
    if category == WINDOWS_NATIVE:
        return Path(raw), None
    if "wsl.localhost" in raw.lower():
        return None, ERROR_WSL_LOCALHOST_PATH_REJECTED
    if category == RELATIVE_PATH:
        return None, ERROR_RELATIVE_PATH_REJECTED
    if category == POSIX_NATIVE:
        return Path(raw), None
    return None, ERROR_INPUT_VALIDATION_FAILED


def _reject_windows_drive(
    raw: str,
    development_wsl_host_drive: str | None,
) -> tuple[None, str]:
    if development_wsl_host_drive is None:
        return None, ERROR_WINDOWS_DRIVE_PATH_REJECTED
    if not _is_valid_drive_argument(development_wsl_host_drive):
        return None, ERROR_WSL_HOST_DRIVE_ARGUMENT_REJECTED
    if not _is_wsl_runtime():
        return None, ERROR_WSL_DEVELOPMENT_BRIDGE_UNAVAILABLE_REJECTED
    drive_letter = _windows_drive_letter(raw)
    if drive_letter is None or drive_letter.lower() != development_wsl_host_drive.lower():
        return None, ERROR_WSL_HOST_DRIVE_MISMATCH_REJECTED
    return None, ERROR_WINDOWS_DRIVE_PATH_REJECTED


def _translate_windows_drive(raw: str) -> Path | None:
    try:
        pure = PureWindowsPath(raw)
        drive_letter = pure.drive.rstrip(":").lower()
        remainder = pure.parts[1:] if pure.parts else ()
        translated = PurePosixPath(_WSL_DRIVE_MOUNT_BASE) / drive_letter
        for part in remainder:
            if part:
                translated = translated / part
        return Path(translated)
    except ValueError:
        return None


def _wsl_bridge_applies(raw: str, drive_letter: str, flag: str | None) -> bool:
    return (
        flag is not None
        and _is_valid_drive_argument(flag)
        and _is_wsl_runtime()
        and drive_letter.lower() == flag.lower()
    )


def _is_wsl_runtime() -> bool:
    return os.name == "posix" and bool(os.environ.get(_WSL_DISTRO_ENV))


def _is_valid_drive_argument(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 1
        and value.lower() in _DRIVE_LETTERS
    )


def _windows_drive_letter(raw: str) -> str | None:
    if len(raw) >= 2 and raw[1] == ":" and raw[0].lower() in _DRIVE_LETTERS:
        remainder = raw[2:]
        if not remainder or remainder.startswith(("\\", "/")):
            return raw[0].upper()
    return None


def _is_windows_drive_root(raw: str) -> bool:
    try:
        pure = PureWindowsPath(raw)
    except ValueError:
        return False
    return (
        len(pure.drive) == 2
        and pure.drive[1] == ":"
        and pure.drive[0].lower() in _DRIVE_LETTERS
        and len(pure.parts) == 1
    )


def _contains_windows_traversal(raw: str) -> bool:
    try:
        pure = PureWindowsPath(raw)
    except ValueError:
        return False
    return any(part == ".." for part in pure.parts)


def _is_url_like(raw: str) -> bool:
    lowered = raw.lower()
    return "://" in lowered or lowered.startswith(("http:", "https:", "ftp:", "s3:", "gs:"))


def _is_windows_device_path(raw: str) -> bool:
    return raw.startswith(("\\\\?\\", "\\\\.\\"))


def _is_unc_path(raw: str) -> bool:
    return raw.startswith("\\\\") or raw.startswith("//")


__all__ = ["resolve_input_root"]
