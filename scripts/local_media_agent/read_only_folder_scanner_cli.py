from __future__ import annotations

import sys
from collections.abc import Mapping, Sequence
from typing import TextIO

from scripts.local_media_agent.read_only_folder_scanner import (
    STATUS_COMPLETED,
    STATUS_COMPLETED_WITH_WARNINGS,
    STATUS_REJECTED,
    STATUS_TRUNCATED,
    manifest_to_json,
    scan_read_only_folder,
)


EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2
EXIT_TRUNCATED = 3

CLI_ARGUMENTS_REJECTED = "CLI_ARGUMENTS_REJECTED"
CLI_INTERNAL_FAILURE = "CLI_INTERNAL_FAILURE"

HELP_TEXT = (
    "Usage: python -m scripts.local_media_agent.read_only_folder_scanner_cli --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "Options:\n"
    "  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "  --development-wsl-host-drive DRIVE_LETTER\n"
    "  --help\n"
)

_DRIVE_LETTERS = "abcdefghijklmnopqrstuvwxyz"

_EXIT_BY_STATUS = {
    STATUS_COMPLETED: EXIT_SUCCESS,
    STATUS_COMPLETED_WITH_WARNINGS: EXIT_SUCCESS,
    STATUS_REJECTED: EXIT_ARGUMENTS_REJECTED,
    STATUS_TRUNCATED: EXIT_TRUNCATED,
}


def run_cli(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    args = list(sys.argv[1:] if argv is None else argv)

    input_root, development_wsl_host_drive, help_requested = _parse_args(args)
    if help_requested:
        out.write(HELP_TEXT)
        return EXIT_SUCCESS
    if input_root is None:
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED

    try:
        if development_wsl_host_drive is None:
            manifest = scan_read_only_folder(input_root)
        else:
            manifest = scan_read_only_folder(
                input_root,
                development_wsl_host_drive=development_wsl_host_drive,
            )
        if not isinstance(manifest, Mapping):
            raise ValueError("invalid manifest")
        status = manifest.get("status")
        if not isinstance(status, str):
            raise ValueError("invalid status")
        exit_code = _EXIT_BY_STATUS.get(status)
        if exit_code is None:
            raise ValueError("unknown status")
        payload = manifest_to_json(manifest)
        out.write(payload + "\n")
        return exit_code
    except Exception:
        err.write(CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


def _parse_args(argv: list[object]) -> tuple[str | None, str | None, bool]:
    if argv == ["--help"]:
        return None, None, True
    if len(argv) == 2:
        flag, value = argv
        if flag != "--input-root":
            return None, None, False
        if not isinstance(value, str):
            return None, None, False
        if value.startswith("-"):
            return None, None, False
        return value, None, False
    if len(argv) == 4:
        return _parse_pair(argv)
    return None, None, False


def _parse_pair(argv: list[object]) -> tuple[str | None, str | None, bool]:
    first_flag, first_value, second_flag, second_value = argv
    if first_flag not in ("--input-root", "--development-wsl-host-drive"):
        return None, None, False
    if second_flag not in ("--input-root", "--development-wsl-host-drive"):
        return None, None, False
    if first_flag == second_flag:
        return None, None, False
    if not all(isinstance(value, str) for value in (first_value, second_value)):
        return None, None, False

    input_root = None
    development_wsl_host_drive = None
    for flag, value in ((first_flag, first_value), (second_flag, second_value)):
        if flag == "--input-root":
            if value.startswith("-"):
                return None, None, False
            input_root = value
        else:
            if not _is_valid_drive_letter(value):
                return None, None, False
            development_wsl_host_drive = value
    if input_root is None:
        return None, None, False
    return input_root, development_wsl_host_drive, False


def _is_valid_drive_letter(value: str) -> bool:
    return len(value) == 1 and value.lower() in _DRIVE_LETTERS


if __name__ == "__main__":
    raise SystemExit(main())
