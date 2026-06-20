#!/usr/bin/env python3
"""Controlled-file ffprobe metadata preflight.

This module permits ffprobe metadata JSON reads only for explicitly controlled
fixture paths. It never scans folders, never accepts arbitrary media paths, and
never invokes ffmpeg.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.V1"
TMP_CONTROLLED_ROOT = Path("/tmp/cid_local_media_agent_controlled_ffprobe")
REPO_CONTROLLED_ROOT = Path("tests/fixtures/local_media_agent/controlled_media")


def _safe_flags() -> dict[str, bool]:
    return {
        "media_processing_performed": False,
        "scanner_executed": False,
        "real_media_used": False,
        "ffmpeg_used": False,
        "audio_extraction_performed": False,
        "sync_generated": False,
        "transcription_generated": False,
        "subtitles_generated": False,
        "timeline_export_generated": False,
        "database_write": False,
        "saas_upload": False,
        "network_call": False,
    }


def _base_result(input_path: Path, result: str) -> dict[str, Any]:
    return {
        "phase": PHASE,
        "result": result,
        "input_policy": "controlled_fixture_only",
        "input_path_redacted": input_path.name,
        "ffprobe_command_kind": "metadata_json",
        "metadata": {
            "format": None,
            "streams": [],
        },
        **_safe_flags(),
    }


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def is_controlled_fixture_path(input_path: str | Path) -> bool:
    path = Path(input_path).resolve(strict=False)
    repo_root = Path.cwd().resolve(strict=False)
    repo_controlled_root = (repo_root / REPO_CONTROLLED_ROOT).resolve(strict=False)
    tmp_controlled_root = TMP_CONTROLLED_ROOT.resolve(strict=False)
    return _is_relative_to(path, tmp_controlled_root) or _is_relative_to(path, repo_controlled_root)


def build_ffprobe_command(input_path: str | Path) -> list[str]:
    path = Path(input_path).resolve(strict=False)
    if not is_controlled_fixture_path(path):
        raise ValueError("input path is outside controlled fixture roots")
    return [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]


def run_preflight(input_path: str | Path) -> dict[str, Any]:
    path = Path(input_path)
    command = build_ffprobe_command(path)

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return _base_result(path, "FFPROBE_METADATA_PREFLIGHT_FAILED")

    if completed.returncode != 0:
        return _base_result(path, "FFPROBE_METADATA_PREFLIGHT_FAILED")

    try:
        parsed = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return _base_result(path, "FFPROBE_METADATA_PREFLIGHT_FAILED")

    result = _base_result(path, "FFPROBE_METADATA_PREFLIGHT_PASS")
    result["metadata"] = {
        "format": parsed.get("format"),
        "streams": parsed.get("streams", []),
    }
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Controlled-file ffprobe metadata preflight. No arbitrary media paths accepted."
    )
    parser.add_argument("--input", required=True, help="Controlled fixture input path.")
    parser.add_argument("--json", action="store_true", required=True, help="Print JSON output.")
    parser.add_argument(
        "--controlled-fixture",
        action="store_true",
        required=True,
        help="Required acknowledgement that the input is a controlled fixture.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not is_controlled_fixture_path(args.input):
        parser.error("--input must be under a controlled fixture root")

    print(json.dumps(run_preflight(args.input), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
