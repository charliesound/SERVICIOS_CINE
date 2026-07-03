from __future__ import annotations

import argparse
import json
from typing import Any, Sequence, TextIO

from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_exporter import (
    export_controlled_sanitized_markdown_report,
)


COMMAND_NAME = "cid-controlled-sanitized-report-export"
EXIT_SUCCESS = 0
EXIT_CONTROLLED_ERROR = 2
EXIT_USAGE = 64


class _CliUsageError(Exception):
    pass


class _ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _CliUsageError("invalid CLI usage")


def _build_parser() -> argparse.ArgumentParser:
    parser = _ControlledArgumentParser(
        prog=COMMAND_NAME,
        description="Export a validated sanitized Markdown report through the controlled exporter.",
    )
    parser.add_argument("--markdown-text", required=True)
    parser.add_argument("--output-path", required=True)
    parser.add_argument("--export-opt-in", action="store_true", default=False)
    return parser


def _emit_json(payload: dict[str, Any], stdout: TextIO | None) -> None:
    output = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    if stdout is None:
        print(output, end="")
    else:
        stdout.write(output)


def run_controlled_sanitized_report_export_cli(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
) -> int:
    try:
        args = _build_parser().parse_args(list(argv) if argv is not None else None)
    except _CliUsageError:
        _emit_json(
            {
                "command": COMMAND_NAME,
                "error": "invalid CLI usage",
                "export_performed": False,
                "verification_status": "CLI_USAGE_ERROR",
            },
            stdout,
        )
        return EXIT_USAGE

    result = export_controlled_sanitized_markdown_report(
        args.markdown_text,
        args.output_path,
        args.export_opt_in,
    )
    payload = {
        "command": COMMAND_NAME,
        "result": result.to_dict(),
        "verification_status": result.verification_status,
        "export_performed": result.export_performed,
        "artifact_created_on_disk": result.artifact_created_on_disk,
        "errors": list(result.errors),
    }
    _emit_json(payload, stdout)

    if result.verification_status == "VERIFIED" and result.export_performed is True:
        return EXIT_SUCCESS
    return EXIT_CONTROLLED_ERROR


def main(argv: Sequence[str] | None = None) -> int:
    return run_controlled_sanitized_report_export_cli(argv)


if __name__ == "__main__":
    raise SystemExit(main())
