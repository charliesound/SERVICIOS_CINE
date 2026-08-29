"""CID CLI command: consume a marker package into a DaVinci FCPXML reference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from scripts.local_media_agent.davinci_marker_reference import build_davinci_reference

EXIT_SUCCESS = 0
EXIT_INTERNAL_FAILURE = 1
EXIT_ARGUMENTS_REJECTED = 2

CLI_ARGUMENTS_REJECTED = "CID_DAVINCI_REFERENCE_ARGUMENTS_REJECTED"
CLI_INTERNAL_FAILURE = "CID_DAVINCI_REFERENCE_INTERNAL_FAILURE"


class _ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = _ControlledArgumentParser(
        prog="cid davinci-reference",
        description="Convert an editor marker package into a DaVinci FCPXML reference (read-only).",
    )
    parser.add_argument("--editor-handoff", required=True)
    parser.add_argument("--media-path", required=True)
    parser.add_argument("--frame-duration", required=True)
    parser.add_argument("--source-timecode-start", required=True)
    parser.add_argument("--source-duration", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--event-name", default="CID Editorial Reference")
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
        package_path = Path(args.editor_handoff)
        package = json.loads(package_path.read_text(encoding="utf-8"))
        reference = build_davinci_reference(
            package,
            media_path=args.media_path,
            frame_duration=args.frame_duration,
            source_timecode_start=args.source_timecode_start,
            source_duration=args.source_duration,
            event_name=args.event_name,
        )
        if not reference["davinci_reference_available"]:
            out.write(
                json.dumps(
                    {
                        "davinci_reference_available": False,
                        "davinci_reference_reason": reference["davinci_reference_reason"],
                        "candidate_id": reference["candidate_id"],
                        "output_written": None,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
                + "\n"
            )
            return EXIT_SUCCESS
        output_path = Path(args.output)
        output_path.write_bytes(reference["fcpxml"])
        out.write(
            json.dumps(
                {
                    "davinci_reference_available": True,
                    "candidate_id": reference["candidate_id"],
                    "video_clip": reference["video_clip"],
                    "source_in_seconds": reference["source_in_seconds"],
                    "source_out_seconds": reference["source_out_seconds"],
                    "marker_name": reference["marker_name"],
                    "output_written": str(output_path),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
            + "\n"
        )
        return EXIT_SUCCESS
    except (ValueError, TypeError, OSError):
        err.write(CLI_ARGUMENTS_REJECTED + "\n")
        return EXIT_ARGUMENTS_REJECTED
    except Exception:
        err.write(CLI_INTERNAL_FAILURE + "\n")
        return EXIT_INTERNAL_FAILURE


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
