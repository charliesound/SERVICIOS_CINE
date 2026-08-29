from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from typing import TextIO

from scripts.local_media_agent import read_only_folder_scanner_cli
from scripts.local_media_agent import pilot_flow
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
    "  pilot   Run the local pilot and browse or search its transcript.\n"
    "  editorial-query  Query proven producer editorial evidence (Siruela pilot).\n"
    "  editorial-qa  Run the Editorial QA command.\n"
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

PILOT_HELP_TEXT = (
    "Usage: cid pilot OPERATION --input-root ROOT --selected-media MEDIA "
    "--asset-id ASSET_ID --model-local-path MODEL [OPTIONS]\n"
    "Operations:\n"
    "  browse  Browse ordered transcript segments.\n"
    "  search  Search authoritative text within individual segments.\n"
    "Required options:\n"
    "  --input-root ROOT\n"
    "  --selected-media MEDIA\n"
    "  --asset-id ASSET_ID\n"
    "  --model-local-path MODEL\n"
    "Optional options:\n"
    "  --language-hint LANG\n"
    "  --device cpu|cuda\n"
    "  --ffmpeg-path PATH\n"
    "  --temp-dir PATH\n"
    "  --offset NON_NEGATIVE_INTEGER (browse only)\n"
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

PRODUCER_EDITORIAL_QUERY_HELP_TEXT = (
    "Usage: cid editorial-query --evidence-path EVIDENCE_JSON --query QUERY [--character CHARACTER] [--navigate CANDIDATE_ID] [--editor-handoff OUTPUT] [--json]\n"
    "Options:\n"
    "  --evidence-path EVIDENCE_JSON\n"
    "  --query QUERY\n"
    "  --character CHARACTER\n"
    "  --navigate CANDIDATE_ID  Resolve read-only DaVinci/audio navigation for one result.\n"
    "  --editor-handoff OUTPUT  Write an editor marker package JSON to OUTPUT (requires --navigate).\n"
    "  --json\n"
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

        if args == ["editorial-query", "--help"]:
            out.write(PRODUCER_EDITORIAL_QUERY_HELP_TEXT)
            return EXIT_SUCCESS

        if args == ["transcript", "--help"]:
            out.write(TRANSCRIPT_HELP_TEXT)
            return EXIT_SUCCESS

        if args == ["pilot", "--help"]:
            out.write(PILOT_HELP_TEXT)
            return EXIT_SUCCESS

        if args and args[0] == "editorial-qa":
            from scripts.local_media_agent import editorial_qa_pilot_cli

            return editorial_qa_pilot_cli.run_cli(args[1:], stdout=out, stderr=err)

        if args and args[0] == "editorial-query":
            from scripts.local_media_agent import producer_editorial_query_cli

            return producer_editorial_query_cli.run_cli(args[1:], stdout=out, stderr=err)

        if args and args[0] == "transcript":
            return _run_transcript_cli(args[1:], stdout=out, stderr=err)

        if args and args[0] == "pilot":
            return _run_pilot_cli(args[1:], stdout=out, stderr=err)

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


def _run_pilot_cli(
    args: list[str],
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    if args == ["--help"]:
        stdout.write(PILOT_HELP_TEXT)
        return EXIT_SUCCESS
    if not args or args[0] not in {"browse", "search"}:
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED

    operation = args[0]
    values: dict[str, str] = {}
    allowed_options = {
        "--input-root",
        "--selected-media",
        "--asset-id",
        "--model-local-path",
        "--language-hint",
        "--device",
        "--ffmpeg-path",
        "--temp-dir",
        "--offset",
        "--limit",
        "--query",
    }
    index = 1
    while index < len(args):
        option = args[index]
        if option not in allowed_options:
            stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED
        if option in values or index + 1 >= len(args) or args[index + 1].startswith("--"):
            stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED
        values[option] = args[index + 1]
        index += 2

    required_options = {
        "--input-root",
        "--selected-media",
        "--asset-id",
        "--model-local-path",
    }
    if not required_options.issubset(values):
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    if operation == "browse" and "--query" in values:
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    if operation == "search" and "--offset" in values:
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    if operation == "search" and not values.get("--query", "").strip():
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    if "--device" in values and values["--device"] not in {"cpu", "cuda"}:
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED

    try:
        offset = _pilot_integer_option(values, "--offset", minimum=0, default=0)
        limit_default = DEFAULT_BROWSE_LIMIT if operation == "browse" else DEFAULT_SEARCH_LIMIT
        limit = _pilot_integer_option(values, "--limit", minimum=1, default=limit_default)
        maximum = MAX_BROWSE_RESULTS if operation == "browse" else MAX_SEARCH_RESULTS
        if limit > maximum:
            raise ValueError("RESULT_LIMIT_EXCEEDED")

        request = pilot_flow.PilotFlowRequest(
            input_root=values["--input-root"],
            selected_media_path=values["--selected-media"],
            asset_id=values["--asset-id"],
            model_local_path=values["--model-local-path"],
            language_hint=values.get("--language-hint"),
            device=values.get("--device", "cpu"),
            ffmpeg_path=values.get("--ffmpeg-path"),
            temp_dir=values.get("--temp-dir"),
        )
        pilot_result = pilot_flow.run_pilot_flow(request)
        if not isinstance(pilot_result, dict):
            raise TypeError("invalid pilot result")
        if pilot_result.get("status") != pilot_flow.STATUS_COMPLETED_FLOW:
            stdout.write(json.dumps(pilot_result, ensure_ascii=False, sort_keys=True) + "\n")
            return EXIT_INTERNAL_FAILURE

        payload = run_pilot_transcript_cli(
            pilot_result,
            operation,
            query=values.get("--query"),
            offset=offset,
            limit=limit,
        )
        stdout.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        return EXIT_SUCCESS
    except (KeyError, ValueError, TranscriptBrowseInputError, TypeError):
        stderr.write(CID_CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED


def _pilot_integer_option(
    values: dict[str, str],
    option: str,
    *,
    minimum: int,
    default: int,
) -> int:
    if option not in values:
        return default
    value = int(values[option])
    if value < minimum:
        raise ValueError(f"{option}_INVALID")
    return value


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
