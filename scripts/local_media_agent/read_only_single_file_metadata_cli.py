#!/usr/bin/env python3
"""Isolated CID Local Media Agent read-only single-file metadata CLI.

This module is intentionally isolated from package entrypoint registration. It
loads the already-audited implementation module next to this file and delegates
all argument handling to its `run_cli` function.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Sequence

_IMPL_MODULE_NAME = "_cid_lma_read_only_single_file_metadata_impl"
_IMPL_FILE_NAME = "read_only_single_file_metadata.py"


def _implementation_path() -> Path:
    return Path(__file__).resolve().with_name(_IMPL_FILE_NAME)


def _load_implementation() -> ModuleType:
    implementation_path = _implementation_path()
    if not implementation_path.is_file():
        raise RuntimeError("READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_NOT_FOUND")

    spec = importlib.util.spec_from_file_location(_IMPL_MODULE_NAME, implementation_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("READ_ONLY_SINGLE_FILE_METADATA_IMPLEMENTATION_LOAD_FAILED")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "run_cli"):
        raise RuntimeError("READ_ONLY_SINGLE_FILE_METADATA_RUN_CLI_NOT_FOUND")

    return module


def main(argv: Sequence[str] | None = None) -> int:
    """Run the isolated CLI and return its deterministic exit code."""

    implementation = _load_implementation()
    return int(implementation.run_cli(argv))


if __name__ == "__main__":
    raise SystemExit(main())
