from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_renderer import (
    render_controlled_ffprobe_metadata_visible_report,
)


ALLOWED_OUTPUT_SUFFIXES = {".md", ".txt"}
CONTROLLED_INPUT_POLICY = "controlled_fixture_only"
METADATA_COMMAND_KIND = "metadata_json"


class ControlledCliError(ValueError):
    """Raised for controlled CLI failures without leaking private details."""


class ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ControlledCliError(message)


def load_controlled_payload_json(path: Path) -> dict:
    _validate_input_path(path)
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ControlledCliError("input JSON is invalid") from exc

    if not isinstance(parsed, dict):
        raise ControlledCliError("input JSON root must be an object")


    _validate_controlled_payload(parsed)
    return parsed


def render_visible_report_from_controlled_payload_file(input_path: Path) -> str:
    payload = load_controlled_payload_json(input_path)
    try:
        return render_controlled_ffprobe_metadata_visible_report(payload)
    except Exception as exc:
        raise ControlledCliError("renderer failed safely") from exc


def write_visible_report_text(output_path: Path, report_text: str) -> None:
    _validate_output_path(output_path)
    output_path.write_text(report_text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        report_text = render_visible_report_from_controlled_payload_file(Path(args.input_json))
        if args.output is not None:
            write_visible_report_text(Path(args.output), report_text)
        else:
            sys.stdout.write(report_text)
        return 0
    except ControlledCliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = ControlledArgumentParser(
        prog="ffprobe_controlled_file_metadata_visible_report_renderer_cli",
        description="Render a visible report from a controlled metadata JSON payload.",
    )
    parser.add_argument("input_json", help="Controlled metadata JSON payload file.")
    parser.add_argument("--output", help="Optional .txt or .md report output file.")
    return parser


def _validate_input_path(path: Path) -> None:
    _reject_unsafe_path_text(path)
    if not path.exists():
        raise ControlledCliError("input JSON file does not exist")
    if path.is_dir():
        raise ControlledCliError("input path must be a JSON file, not a directory")
    if path.suffix.lower() != ".json":
        raise ControlledCliError("input path must use .json suffix")


def _validate_output_path(path: Path) -> None:
    _reject_unsafe_path_text(path)
    if path.exists() and path.is_dir():
        raise ControlledCliError("output path must be a file, not a directory")
    if path.suffix.lower() not in ALLOWED_OUTPUT_SUFFIXES:
        raise ControlledCliError("output path must use .txt or .md suffix")
    if not path.parent.exists() or not path.parent.is_dir():
        raise ControlledCliError("output parent directory must exist")


def _validate_controlled_payload(payload: dict[str, Any]) -> None:
    required = ["input_policy", "ffprobe_command_kind", "input_path_redacted", "metadata"]
    missing = [key for key in required if key not in payload]
    if missing:
        raise ControlledCliError("input JSON is missing required controlled payload fields")
    if payload.get("input_policy") != CONTROLLED_INPUT_POLICY:
        raise ControlledCliError("input policy is not controlled")
    if payload.get("ffprobe_command_kind") != METADATA_COMMAND_KIND:
        raise ControlledCliError("metadata command kind is not controlled")
    if not isinstance(payload.get("metadata"), dict):
        raise ControlledCliError("metadata must be an object")


def _reject_unsafe_path_text(path: Path) -> None:
    raw = str(path)
    normalized = raw.replace("\\", "/")
    if raw.startswith(("//", "\\\\")):
        raise ControlledCliError("UNC paths are not allowed")
    if len(raw) >= 2 and raw[1] == ":":
        raise ControlledCliError("Windows drive paths are not allowed")
    if normalized == "/mnt/c" or normalized.startswith("/mnt/c/"):
        raise ControlledCliError("mounted Windows paths are not allowed")


if __name__ == "__main__":
    raise SystemExit(main())
