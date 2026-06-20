#!/usr/bin/env python3
"""Local-only ffmpeg/ffprobe availability preflight.

This module checks whether the ffmpeg and ffprobe executables are present and
can answer a version command. It never accepts media paths and never probes or
processes media files.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from typing import Any


PHASE = "CID.LOCAL_MEDIA_AGENT.FFMPEG.LOCAL.AVAILABILITY.PREFLIGHT.V1"


def _version_line(binary_path: str) -> str | None:
    """Return the first version output line for a binary, or None on failure."""

    try:
        completed = subprocess.run(
            [binary_path, "-version"],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if completed.returncode != 0:
        return None

    output = completed.stdout or completed.stderr or ""
    for line in output.splitlines():
        if line.strip():
            return line.strip()
    return None


def _check_tool(tool_name: str) -> dict[str, Any]:
    tool_path = shutil.which(tool_name)
    if tool_path is None:
        return {
            "available": False,
            "path": None,
            "version_line": None,
        }

    version_line = _version_line(tool_path)
    return {
        "available": version_line is not None,
        "path": tool_path,
        "version_line": version_line,
    }


def run_preflight() -> dict[str, Any]:
    """Run the local tool availability preflight without media input."""

    ffmpeg = _check_tool("ffmpeg")
    ffprobe = _check_tool("ffprobe")
    result = "PASS" if ffmpeg["available"] and ffprobe["available"] else "MISSING_TOOLS"

    return {
        "phase": PHASE,
        "result": result,
        "ffmpeg": ffmpeg,
        "ffprobe": ffprobe,
        "media_processing_performed": False,
        "scanner_executed": False,
        "real_media_used": False,
        "database_write": False,
        "saas_upload": False,
        "network_call": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Local-only ffmpeg/ffprobe availability preflight. No media paths accepted."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the preflight result as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    print(json.dumps(run_preflight(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
