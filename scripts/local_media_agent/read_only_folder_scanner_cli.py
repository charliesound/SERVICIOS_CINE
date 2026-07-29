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
    "  --help\n"
)

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

    input_root, help_requested = _parse_args(args)
    if help_requested:
        out.write(HELP_TEXT)
        return EXIT_SUCCESS
    if input_root is None:
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED

    try:
        manifest = scan_read_only_folder(input_root)
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


def _parse_args(argv: list[object]) -> tuple[str | None, bool]:
    if argv == ["--help"]:
        return None, True
    if len(argv) != 2:
        return None, False
    flag, value = argv
    if flag != "--input-root":
        return None, False
    if not isinstance(value, str):
        return None, False
    if value.startswith("-"):
        return None, False
    return value, False


if __name__ == "__main__":
    raise SystemExit(main())
