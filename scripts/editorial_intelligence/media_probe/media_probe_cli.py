#!/usr/bin/env python3
"""CID Editorial Intelligence - Real Media Metadata Probe CLI.

Thin wrapper around the media probe core. Emits structured JSON for a single
source media reference. Intended to be invoked per asset from the local media
agent scanner outputs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.editorial_intelligence.media_probe.media_probe import PHASE
from scripts.editorial_intelligence.media_probe.media_probe import probe_media

CLI_NAME = "cid-editorial-media-probe"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe a single local media reference.")
    parser.add_argument("--asset-id", required=True, help="asset_id passthrough from the scanner.")
    parser.add_argument("--source", required=True, help="Absolute path to the local media source.")
    parser.add_argument("--size-bytes", type=int, default=None, help="Optional size in bytes from the scanner.")
    parser.add_argument("--timeout", type=int, default=10, help="ffprobe subprocess timeout in seconds.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = probe_media(
        asset_id=args.asset_id,
        source_path=args.source,
        size_bytes=args.size_bytes,
        timeout=args.timeout,
    )
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
