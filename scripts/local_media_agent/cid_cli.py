from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from typing import TextIO

from scripts.local_media_agent import read_only_folder_scanner_cli
from scripts.local_media_agent.pilot_browse_search_handoff import (
    handoff_pilot_transcript_segments,
)
from scripts.local_media_agent.source_moment_navigation import (
    build_source_moment_navigation,
)
from scripts.local_media_agent.transcript_browse import (
    DEFAULT_BROWSE_LIMIT,
    DEFAULT_SEARCH_LIMIT,
    MAX_BROWSE_RESULTS,
    MAX_SEARCH_RESULTS,
    TranscriptBrowseInputError,
    browse_transcript,
    load_transcript_segments,
    search_transcript,
)


EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CID_CLI_ARGUMENTS_REJECTED = "CID_CLI_ARGUMENTS_REJECTED"
CID_CLI_INTERNAL_FAILURE = "CID_CLI_INTERNAL_FAILURE"

UMBRELLA_HELP_TEXT = (
    "Usage: cid COMMAND [OPTIONS]\n"
    "Commands:\n"
    "  scan    Scan one absolute local Linux folder in read-only mode.\n"
    "  transcript  Browse or search an explicit local transcript JSON file.\n"
    "Options:\n"
    "  --help\n"
)

TRANSCRIPT_HELP_TEXT = (
    "Usage: cid transcript OPERATION --input TRANSCRIPT_JSON [OPTIONS]\n"
    "Operations:\n"
    "  browse  Browse ordered transcript segments.\n"
    "  search  Search authoritative text within individual segments.\n"
    "Options:\n"
    "  --input TRANSCRIPT_JSON\n"
    "  --offset NON_NEGATIVE_INTEGER\n"
    "  --limit POSITIVE_INTEGER\n"
    "  --query QUERY (search only)\n"
    "  --help\n"
)


def run_pilot_transcript_cli(
    pilot_result: object,
    operation: str,
    *,
    query: str | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> dict[str, object]:
    """Serialize browse/search results from an in-memory pilot result."""
    try:
        results = handoff_pilot_transcript_segments(
            pilot_result,
            operation,
            query=query,
            offset=offset,
            limit=limit,
        )
        maximum = MAX_BROWSE_RESULTS if operation == "browse" else MAX_SEARCH_RESULTS
        return _transcript_payload(operation, results, maximum)
    except (TranscriptBrowseInputError, TypeError, ValueError):
        raise TranscriptBrowseInputError("PILOT_HANDOFF_INVALID") from None

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

        if args == ["transcript", "--help"]:
            out.write(TRANSCRIPT_HELP_TEXT)
            return EXIT_SUCCESS

        if args and args[0] == "editorial-qa":
            from scripts.local_media_agent import editorial_qa_pilot_cli

            return editorial_qa_pilot_cli.run_cli(args[1:], stdout=out, stderr=err)

        if args and args[0] == "transcript":
            return _run_transcript_cli(args[1:], stdout=out, stderr=err)

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


def _run_transcript_cli(
    args: list[str],
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    if args == ["--help"]:
        stdout.write(TRANSCRIPT_HELP_TEXT)
        return EXIT_SUCCESS
    if not args or args[0] not in {"browse", "search"}:
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED

    operation = args[0]
    values: dict[str, str] = {}
    index = 1
    while index < len(args):
        option = args[index]
        if option == "--help" and index == len(args) - 1:
            stdout.write(TRANSCRIPT_HELP_TEXT)
            return EXIT_SUCCESS
        if option not in {"--input", "--offset", "--limit", "--query"}:
            stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED
        if index + 1 >= len(args) or args[index + 1].startswith("--"):
            stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED
        values[option] = args[index + 1]
        index += 2

    try:
        input_path = values["--input"]
        segments = load_transcript_segments(input_path)
        if operation == "browse":
            offset = int(values.get("--offset", "0"))
            limit = int(values.get("--limit", str(DEFAULT_BROWSE_LIMIT)))
            results = browse_transcript(segments, offset=offset, limit=limit)
            maximum = MAX_BROWSE_RESULTS
        else:
            query = values["--query"]
            limit = int(values.get("--limit", str(DEFAULT_SEARCH_LIMIT)))
            results = search_transcript(segments, query, limit=limit)
            maximum = MAX_SEARCH_RESULTS
        stdout.write(json.dumps(_transcript_payload(operation, results, maximum), ensure_ascii=False, sort_keys=True) + "\n")
        return EXIT_SUCCESS
    except (KeyError, ValueError, TranscriptBrowseInputError, OSError, TypeError):
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED


def _transcript_payload(
    operation: str,
    results: list,
    maximum: int,
) -> dict[str, object]:
    return {
        "operation": operation,
        "result_limit_maximum": maximum,
        "results": [
            {
                **result.to_dict(),
                "source_moment": build_source_moment_navigation(result),
            }
            for result in results
        ],
    }


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
