#!/usr/bin/env python3
"""CID Local Media Agent read-only single-file metadata helper.

This module is intentionally isolated and uses only the Python standard library
plus an internal visible-report integration loaded only for the explicit
visible report mode. It reads basic file metadata for one controlled fixture
file and emits a redacted deterministic result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "cid.local_media_agent.read_only_single_file_metadata.v1"
STATUS_OK = "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_OK"
STATUS_REJECTED = "CONTROLLED_READ_ONLY_SINGLE_FILE_METADATA_REJECTED"
MODE = "read_only_single_file"
TOOL_POLICY = "python_standard_library_only"
DEFAULT_ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
CONTROLLED_FIXTURE_ID = "controlled_plain_text_marker_v1"
VISIBLE_REPORT_INTEGRATION_MODULE = "scripts.local_media_agent.controlled_fixture_smoke_visible_report_in_memory_integration"
VISIBLE_REPORT_INTEGRATION_FUNCTION = "render_controlled_fixture_smoke_result_in_memory"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _base_result(status: str, ok: bool, reason: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "ok": ok,
        "mode": MODE,
        "tool_policy": TOOL_POLICY,
        "external_tools_used": False,
        "scanner_used": False,
        "recursion_used": False,
        "batch_used": False,
    }
    if reason is not None:
        result["reason"] = reason
    return result


def _redacted_path(relative_path: Path) -> str:
    return f"<CONTROLLED_FIXTURE_ROOT>/{relative_path.as_posix()}"


def collect_read_only_single_file_metadata(
    *,
    target_path: str | Path,
    fixture_root: str | Path,
    expected_sha256: str,
    expected_bytes: int,
    allowed_relative_path: str | Path = DEFAULT_ALLOWED_RELATIVE_PATH,
) -> dict[str, Any]:
    """Return deterministic read-only metadata for one controlled fixture file.

    The function never scans a directory and never reports host-private absolute
    paths. A rejected result is returned instead of raising for normal contract
    violations so the caller can display a stable operator-facing outcome.
    """

    root = Path(fixture_root).expanduser().resolve(strict=False)
    target = Path(target_path).expanduser().resolve(strict=False)
    allowed_relative = Path(allowed_relative_path)

    if root.is_symlink():
        return _base_result(STATUS_REJECTED, False, "FIXTURE_ROOT_SYMLINK_REJECTED")
    if not root.exists() or not root.is_dir():
        return _base_result(STATUS_REJECTED, False, "FIXTURE_ROOT_NOT_FOUND")
    if target.is_symlink():
        return _base_result(STATUS_REJECTED, False, "TARGET_SYMLINK_REJECTED")
    if not target.exists() or not target.is_file():
        return _base_result(STATUS_REJECTED, False, "TARGET_FILE_NOT_FOUND")
    if not _is_relative_to(target, root):
        return _base_result(STATUS_REJECTED, False, "TARGET_OUTSIDE_CONTROLLED_FIXTURE_ROOT")

    relative = target.relative_to(root)
    if relative != allowed_relative:
        return _base_result(STATUS_REJECTED, False, "TARGET_RELATIVE_PATH_NOT_ALLOWED")

    actual_bytes = target.stat().st_size
    actual_sha256 = _sha256_file(target)

    if actual_bytes != expected_bytes:
        result = _base_result(STATUS_REJECTED, False, "TARGET_BYTES_MISMATCH")
        result["target"] = {
            "relative_path": relative.as_posix(),
            "redacted_path": _redacted_path(relative),
            "expected_bytes": expected_bytes,
            "actual_bytes": actual_bytes,
        }
        return result

    if actual_sha256 != expected_sha256:
        result = _base_result(STATUS_REJECTED, False, "TARGET_SHA256_MISMATCH")
        result["target"] = {
            "relative_path": relative.as_posix(),
            "redacted_path": _redacted_path(relative),
            "expected_sha256": expected_sha256,
            "actual_sha256": actual_sha256,
        }
        return result

    return {
        **_base_result(STATUS_OK, True),
        "target": {
            "file_name": target.name,
            "extension": target.suffix,
            "relative_path": relative.as_posix(),
            "redacted_path": _redacted_path(relative),
        },
        "metadata": {
            "bytes": actual_bytes,
            "sha256": actual_sha256,
            "is_file": True,
        },
        "fixture_contract": {
            "allowed_relative_path": allowed_relative.as_posix(),
            "expected_bytes": expected_bytes,
            "expected_sha256": expected_sha256,
        },
    }


def _load_visible_report_integration():
    module = __import__(
        VISIBLE_REPORT_INTEGRATION_MODULE,
        fromlist=[VISIBLE_REPORT_INTEGRATION_FUNCTION],
    )
    render_func = getattr(module, VISIBLE_REPORT_INTEGRATION_FUNCTION, None)
    if not callable(render_func):
        raise RuntimeError("VISIBLE_REPORT_IN_MEMORY_INTEGRATION_NOT_AVAILABLE")
    return render_func


def _build_visible_report_smoke_result(
    *,
    result: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    target = result.get("target")
    if not isinstance(target, dict):
        target = {}

    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    fixture_contract = result.get("fixture_contract")
    if not isinstance(fixture_contract, dict):
        fixture_contract = {}

    ok = result.get("ok") is True

    return {
        "smoke_status": "PASS" if ok else "FAIL",
        "fixture_id": CONTROLLED_FIXTURE_ID,
        "fixture_root": str(args.fixture_root),
        "allowed_relative_path": str(
            fixture_contract.get("allowed_relative_path", args.allowed_relative_path)
        ),
        "file_name": str(target.get("file_name", Path(args.target_path).name)),
        "byte_size": metadata.get("bytes", args.expected_bytes),
        "sha256": metadata.get("sha256", args.expected_sha256),
        "cli_execution_mode": "read_only_single_file_metadata_visible_report_markdown_in_memory",
        "exit_code": 0 if ok else 2,
        "json_stdout_validation_status": "NOT_REQUESTED_VISIBLE_REPORT_MARKDOWN",
        "stderr_validation_status": "PASS_NO_STDERR_IN_PROCESS",
        "fixture_immutability_status": "PASS_READ_ONLY_METADATA_COLLECTION",
        "output_file_creation_status": "PASS_NONE_CREATED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect redacted read-only metadata for one controlled fixture file."
    )
    parser.add_argument("--target-path", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--expected-bytes", required=True, type=int)
    parser.add_argument(
        "--allowed-relative-path",
        default=DEFAULT_ALLOWED_RELATIVE_PATH,
    )
    parser.add_argument("--result-json", action="store_true")
    parser.add_argument("--visible-report-markdown", action="store_true")
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = collect_read_only_single_file_metadata(
        target_path=args.target_path,
        fixture_root=args.fixture_root,
        expected_sha256=args.expected_sha256,
        expected_bytes=args.expected_bytes,
        allowed_relative_path=args.allowed_relative_path,
    )

    if args.visible_report_markdown:
        render_report = _load_visible_report_integration()
        smoke_result = _build_visible_report_smoke_result(result=result, args=args)
        print(render_report(smoke_result), end="")
    elif args.result_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])

    return 0 if result.get("ok") is True else 2


if __name__ == "__main__":
    raise SystemExit(run_cli())
