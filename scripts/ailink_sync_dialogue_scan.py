#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ailink_tools.sync_dialogue.exports import (
    write_matches_csv,
    write_media_csv,
    write_scan_json,
)
from ailink_tools.sync_dialogue.local_scanner import scan_folder
from ailink_tools.sync_dialogue.matching import suggest_matches
from ailink_tools.sync_dialogue.report_html import write_report_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan local media for AILink Sync Dialogue.")
    parser.add_argument("--input", required=True, help="Input project or shoot-day folder")
    parser.add_argument("--output-dir", required=True, help="Output folder for JSON and CSV")
    parser.add_argument("--no-probe", action="store_true", help="Skip ffprobe metadata extraction")
    parser.add_argument("--json-name", default="scan_result.json", help="JSON output filename")
    parser.add_argument("--csv-name", default="media_files.csv", help="CSV output filename")
    parser.add_argument(
        "--matches-name",
        default="match_suggestions.csv",
        help="Match suggestions CSV output filename",
    )
    parser.add_argument("--html-name", default="report.html", help="HTML report output filename")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output_dir).expanduser()

    if not input_path.exists():
        print("error: input path does not exist", file=sys.stderr)
        return 2
    if not input_path.is_dir():
        print("error: input path must be a directory", file=sys.stderr)
        return 2

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        scan_result = scan_folder(input_path, probe=not args.no_probe)
        result = replace(scan_result, match_suggestions=suggest_matches(scan_result))
        json_path = write_scan_json(result, output_dir / args.json_name)
        csv_path = write_media_csv(result, output_dir / args.csv_name)
        matches_path = write_matches_csv(result, output_dir / args.matches_name)
        html_path = write_report_html(result, output_dir / args.html_name)
    except Exception as exc:
        print(f"error: scan failed: {exc}", file=sys.stderr)
        return 3

    print(f"total files: {result.total_files}")
    print(f"video count: {result.video_count}")
    print(f"audio count: {result.audio_count}")
    print(f"unsupported count: {result.unsupported_count}")
    print(f"match suggestions count: {len(result.match_suggestions)}")
    print(f"output json path: {json_path}")
    print(f"output csv path: {csv_path}")
    print(f"output matches path: {matches_path}")
    print(f"output html path: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
