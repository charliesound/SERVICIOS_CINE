from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TextIO

from scripts.local_media_agent import read_only_folder_scanner_cli


EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CID_CLI_ARGUMENTS_REJECTED = "CID_CLI_ARGUMENTS_REJECTED"
CID_CLI_INTERNAL_FAILURE = "CID_CLI_INTERNAL_FAILURE"

UMBRELLA_HELP_TEXT = (
    "Usage: cid COMMAND [OPTIONS]\n"
    "Commands:\n"
    "  scan    Scan one absolute local Linux folder in read-only mode.\n"
    "Options:\n"
    "  --help\n"
)

SCAN_HELP_TEXT = (
    "Usage: cid scan --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "Options:\n"
    "  --input-root ABSOLUTE_LOCAL_LINUX_FOLDER\n"
    "  --help\n"
)

EDITORIAL_QA_HELP_TEXT = (
    "Usage: cid editorial-qa --question QUESTION --corpus-id CORPUS_ID [--top-k TOP_K] [--diagnostic-output PATH]\n"
    "Options:\n"
    "  --question QUESTION\n"
    "  --corpus-id CORPUS_ID\n"
    "  --top-k TOP_K\n"
    "  --diagnostic-output PATH\n"
    "  --help\n"
)


def run_cli(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr

    try:
        args = list(sys.argv[1:] if argv is None else argv)

        if args == ["--help"]:
            out.write(UMBRELLA_HELP_TEXT)
            return EXIT_SUCCESS

        if args == ["scan", "--help"]:
            out.write(SCAN_HELP_TEXT)
            return EXIT_SUCCESS

        if args == ["editorial-qa", "--help"]:
            out.write(EDITORIAL_QA_HELP_TEXT)
            return EXIT_SUCCESS

        if args and args[0] == "editorial-qa":
            from scripts.local_media_agent import editorial_qa_pilot_cli

            return editorial_qa_pilot_cli.run_cli(args[1:], stdout=out, stderr=err)

        if not args or args[0] != "scan":
            err.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED

        return read_only_folder_scanner_cli.run_cli(
            args[1:],
            stdout=out,
            stderr=err,
        )
    except Exception:
        err.write(CID_CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
