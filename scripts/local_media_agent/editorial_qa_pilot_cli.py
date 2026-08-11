from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TextIO

from scripts.editorial_intelligence.semantic_index.runtime import build_local_semantic_index
from services.editorial_qa_orchestration import EditorialQAOrchestrator, EditorialQARequest
from services.llm.editorial_qa import EditorialQAGenerationProvider
from services.llm.editorial_qa_pilot_provider import (
    SeptemberPilotV3EditorialQAGenerationProvider,
)


EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CLI_ARGUMENTS_REJECTED = "EDITORIAL_QA_CLI_ARGUMENTS_REJECTED"
CLI_INTERNAL_FAILURE = "EDITORIAL_QA_CLI_INTERNAL_FAILURE"


class _ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _ControlledArgumentParser(
        prog="cid editorial-qa",
        description="Run the September Pilot Editorial QA command.",
    )
    parser.add_argument("--question", required=True)
    parser.add_argument("--corpus-id", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--diagnostic-output")
    return parser


def build_pilot_orchestrator(
    *,
    retriever=None,
    generation_provider: EditorialQAGenerationProvider | None = None,
    diagnostic_sink=None,
) -> EditorialQAOrchestrator:
    selected_retriever = retriever or build_local_semantic_index()
    selected_provider = generation_provider or SeptemberPilotV3EditorialQAGenerationProvider()
    return EditorialQAOrchestrator(
        selected_retriever,
        selected_provider,
        diagnostic_sink=diagnostic_sink,
    )


def _write_diagnostics(path: str, snapshot: dict[str, object]) -> None:
    Path(path).write_text(
        json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def run_cli(
    argv: list[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    *,
    retriever=None,
    generation_provider: EditorialQAGenerationProvider | None = None,
    orchestrator_factory=build_pilot_orchestrator,
) -> int:
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    try:
        args = _build_parser().parse_args(list(sys.argv[1:] if argv is None else argv))
        if not args.question.strip() or not args.corpus_id.strip():
            err.write(CLI_ARGUMENTS_REJECTED + "\n")
            return EXIT_ARGUMENTS_REJECTED

        orchestrator = orchestrator_factory(
            retriever=retriever,
            generation_provider=generation_provider,
            diagnostic_sink=(
                lambda snapshot: _write_diagnostics(args.diagnostic_output, snapshot)
                if args.diagnostic_output
                else None
            ),
        )
        result = asyncio.run(
            orchestrator.answer_question(
                EditorialQARequest(
                    question=args.question,
                    corpus_id=args.corpus_id,
                    top_k=args.top_k,
                )
            )
        )
        out.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")
        return EXIT_SUCCESS
    except (ValueError, TypeError):
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    except Exception:
        err.write(CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
