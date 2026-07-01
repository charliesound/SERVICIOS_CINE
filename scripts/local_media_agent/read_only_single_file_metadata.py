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
STATUS_EXPORT_OK = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK"
STATUS_EXPORT_REJECTED = "CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_REJECTED"
MODE = "read_only_single_file"
TOOL_POLICY = "python_standard_library_only"
DEFAULT_ALLOWED_RELATIVE_PATH = "media/controlled_plain_text_marker.txt"
CONTROLLED_FIXTURE_ID = "controlled_plain_text_marker_v1"
CONTROLLED_EXPORT_ROOT_RELATIVE = Path("tests/tmp/local_media_agent/controlled_visible_report_exports")
CONTROLLED_FIXTURE_ROOT_RELATIVE = Path("tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1")
TEST_FIXTURES_ROOT_RELATIVE = Path("tests/fixtures")
VISIBLE_REPORT_INTEGRATION_MODULE = "scripts.local_media_agent.controlled_fixture_smoke_visible_report_in_memory_integration"
VISIBLE_REPORT_INTEGRATION_FUNCTION = "render_controlled_fixture_smoke_result_in_memory"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def _is_windows_style_path(path_text: str) -> bool:
    return "\\" in path_text or (len(path_text) >= 2 and path_text[1] == ":")


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


def _controlled_roots() -> tuple[Path, Path, Path]:
    repo_root = _repo_root()
    output_root = (repo_root / CONTROLLED_EXPORT_ROOT_RELATIVE).resolve(strict=False)
    fixture_root = (repo_root / CONTROLLED_FIXTURE_ROOT_RELATIVE).resolve(strict=False)
    tests_fixtures_root = (repo_root / TEST_FIXTURES_ROOT_RELATIVE).resolve(strict=False)
    return output_root, fixture_root, tests_fixtures_root


def _resolve_controlled_report_export_path(path_text: str) -> tuple[bool, Path | None, str | None]:
    if _is_windows_style_path(path_text):
        return False, None, "VISIBLE_REPORT_OUTPUT_WINDOWS_STYLE_PATH_REJECTED"

    repo_root = _repo_root().resolve(strict=False)
    output_root, fixture_root, tests_fixtures_root = _controlled_roots()

    raw_path = Path(path_text).expanduser()
    candidate = raw_path if raw_path.is_absolute() else repo_root / raw_path
    parent = candidate.parent

    if candidate.resolve(strict=False) == repo_root:
        return False, None, "VISIBLE_REPORT_OUTPUT_REPOSITORY_ROOT_REJECTED"

    if candidate.suffix.lower() != ".md":
        return False, None, "VISIBLE_REPORT_OUTPUT_SUFFIX_REJECTED"

    if not parent.exists() or not parent.is_dir():
        return False, None, "VISIBLE_REPORT_OUTPUT_PARENT_NOT_FOUND"

    if parent.is_symlink():
        return False, None, "VISIBLE_REPORT_OUTPUT_PARENT_SYMLINK_REJECTED"

    if candidate.is_symlink():
        return False, None, "VISIBLE_REPORT_OUTPUT_FILE_SYMLINK_REJECTED"

    resolved = candidate.resolve(strict=False)

    if _is_relative_to(resolved, fixture_root):
        return False, None, "VISIBLE_REPORT_OUTPUT_INSIDE_CONTROLLED_FIXTURE_REJECTED"

    if _is_relative_to(resolved, tests_fixtures_root):
        return False, None, "VISIBLE_REPORT_OUTPUT_INSIDE_TESTS_FIXTURES_REJECTED"

    if not _is_relative_to(resolved, output_root):
        return False, None, "VISIBLE_REPORT_OUTPUT_OUTSIDE_CONTROLLED_ROOT_REJECTED"

    if resolved.exists():
        return False, None, "VISIBLE_REPORT_OUTPUT_EXISTS_OVERWRITE_REJECTED"

    return True, resolved, None


def _write_controlled_visible_report_markdown(path: Path, markdown_text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(markdown_text)


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
    parser.add_argument(
        "--visible-report-output",
        dest="visible_report_path",
        metavar="PATH",
        help="Write the visible Markdown report to a controlled .md output path.",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.visible_report_path is not None and not args.visible_report_markdown:
        print(f"{STATUS_EXPORT_REJECTED}:VISIBLE_REPORT_MARKDOWN_REQUIRED")
        return 2

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
        markdown_text = render_report(smoke_result)

        if args.visible_report_path is not None:
            if result.get("ok") is not True:
                print(f"{STATUS_EXPORT_REJECTED}:METADATA_NOT_ACCEPTED")
                return 2

            export_ok, export_path, export_reason = _resolve_controlled_report_export_path(
                str(args.visible_report_path)
            )
            if not export_ok or export_path is None:
                print(f"{STATUS_EXPORT_REJECTED}:{export_reason}")
                return 2

            _write_controlled_visible_report_markdown(export_path, markdown_text)
            print(STATUS_EXPORT_OK)
        else:
            print(markdown_text, end="")
    elif args.result_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])

    return 0 if result.get("ok") is True else 2


if __name__ == "__main__":
    raise SystemExit(run_cli())
