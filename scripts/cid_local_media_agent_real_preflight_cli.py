from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from typing import Sequence, TextIO

from cid_local_media_agent_real_preflight import (
    PREFLIGHT_BLOCKED,
    PREFLIGHT_FAIL,
    PREFLIGHT_PASS,
    RealPreflightRequest,
    run_real_preflight_check,
)


EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_BLOCKED = 3
EXIT_USAGE = 64
EXIT_INTERNAL_ERROR = 70

_ALLOWED_FORMATS = ("json", "text")


class _CliUsageError(Exception):
    pass


class _SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _CliUsageError("Invalid CLI usage.")


def build_parser() -> argparse.ArgumentParser:
    parser = _SafeArgumentParser(
        prog="cid-real-preflight",
        description="Run a sanitized local real preflight check.",
        add_help=True,
    )
    parser.add_argument("--input-folder", required=True)
    parser.add_argument("--output-folder", required=True)
    parser.add_argument("--max-file-count", type=int, default=25)
    parser.add_argument("--max-total-size-bytes", type=int, default=10 * 1024 * 1024 * 1024)
    parser.add_argument("--max-scan-depth", type=int, default=3)
    parser.add_argument(
        "--accepted-extension",
        action="append",
        default=None,
    )
    parser.add_argument(
        "--no-follow-symlinks",
        action="store_true",
        default=False,
    )
    parser.add_argument("--format", choices=_ALLOWED_FORMATS, default="json")
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    out = stdout if stdout is not None else sys.stdout
    err = stderr if stderr is not None else sys.stderr

    try:
        parser = build_parser()
        args = parser.parse_args(list(argv) if argv is not None else None)
    except _CliUsageError:
        err.write("CLI_USAGE_ERROR: invalid arguments.\n")
        return EXIT_USAGE

    try:
        request = RealPreflightRequest(
            input_folder_path=args.input_folder,
            output_folder_path=args.output_folder,
            max_file_count=args.max_file_count,
            max_total_size_bytes=args.max_total_size_bytes,
            max_scan_depth=args.max_scan_depth,
            accepted_extensions=tuple(args.accepted_extension)
            if args.accepted_extension
            else (".mov", ".mp4", ".mxf", ".wav", ".aif", ".aiff"),
            follow_symlinks=False,
        )

        result = run_real_preflight_check(request)
        exit_code = _exit_code_for_status(result.status)
        payload = _payload_from_result(result, exit_code)

        if args.format == "json":
            out.write(json.dumps(payload, sort_keys=True) + "\n")
        else:
            out.write(_format_text_payload(payload) + "\n")

        return exit_code
    except Exception:
        err.write("CLI_INTERNAL_ERROR: sanitized output could not be produced.\n")
        return EXIT_INTERNAL_ERROR


def _exit_code_for_status(status: str) -> int:
    if status == PREFLIGHT_PASS:
        return EXIT_PASS
    if status == PREFLIGHT_FAIL:
        return EXIT_FAIL
    if status == PREFLIGHT_BLOCKED:
        return EXIT_BLOCKED
    return EXIT_INTERNAL_ERROR


def _payload_from_result(result, exit_code: int) -> dict:
    payload = asdict(result)
    payload["exit_code"] = exit_code
    return payload


def _format_text_payload(payload: dict) -> str:
    lines = [
        f"status={payload['status']}",
        f"exit_code={payload['exit_code']}",
        f"input={payload['sanitized_input_folder_label']}",
        f"output={payload['sanitized_output_folder_label']}",
        f"media_file_count={payload['media_file_count']}",
        f"size_bucket={payload['total_selected_media_size_bucket']}",
        f"maximum_detected_scan_depth={payload['maximum_detected_scan_depth']}",
    ]

    failed = payload.get("failed_check_identifiers") or []
    if failed:
        lines.append("failed_check_identifiers=" + ",".join(failed))

    remediation = payload.get("remediation_items") or []
    if remediation:
        lines.append("remediation_items=" + " | ".join(remediation))

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
