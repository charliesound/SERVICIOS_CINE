#!/usr/bin/env python3
"""Offline contract CLI for SemanticSearchResult serialization.

This CLI intentionally does not create Ollama or Qdrant clients. Runtime wiring belongs to a
future local empirical phase.
"""

from __future__ import annotations

import argparse
import json
import sys

from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticSearchResult


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and serialize a semantic search result")
    parser.add_argument("--result-json", required=True)
    args = parser.parse_args(argv)
    try:
        with open(args.result_json, encoding="utf-8") as handle:
            value = json.load(handle)
        result = SemanticSearchResult(**value)
        sys.stdout.write(json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":")) + "\n")
        return 0
    except (OSError, json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
        sys.stderr.write(f"SEMANTIC_INDEX_INVALID_INPUT: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
