"""CID CLI command: producer editorial evidence query (Siruela pilot)."""

from __future__ import annotations

import argparse
import json
import sys
from typing import TextIO

from scripts.local_media_agent.producer_editorial_query import (
    ProducerQueryError,
    query_producer_evidence,
    render_producer_evidence,
    resolve_navigation_by_candidate_id,
)


EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CLI_ARGUMENTS_REJECTED = "CID_PRODUCER_EDITORIAL_QUERY_ARGUMENTS_REJECTED"
CLI_INTERNAL_FAILURE = "CID_PRODUCER_EDITORIAL_QUERY_INTERNAL_FAILURE"


class _ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _ControlledArgumentParser(
        prog="cid editorial-query",
        description="Query proven producer editorial evidence (read-only, deterministic).",
    )
    parser.add_argument("--evidence-path", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--character")
    parser.add_argument("--navigate")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def run_cli(
    argv: list[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    try:
        args = _build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))
        if not args.query.strip():
            err.write(CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED
        result = query_producer_evidence(
            args.evidence_path,
            args.query,
            character=args.character if args.character else None,
        )
        navigate = args.navigate if args.navigate else None
        if navigate is not None:
            navigation = resolve_navigation_by_candidate_id(result, navigate)
            out.write(
                json.dumps(navigation, ensure_ascii=False, sort_keys=True) + "\n"
            )
            return EXIT_SUCCESS
        if args.as_json:
            payload = {
                "project": result.project,
                "query": result.query,
                "topic": result.topic,
                "character": result.character,
                "status": result.status,
                "total": result.total,
                "mapped": result.mapped,
                "audio_only": result.audio_only,
                "topics_available": list(result.topics_available),
                "results": [item.to_dict() for item in result.results],
            }
            out.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        else:
            out.write(render_producer_evidence(result))
        return EXIT_SUCCESS
    except (ProducerQueryError, ValueError, TypeError):
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    except Exception:
        err.write(CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
