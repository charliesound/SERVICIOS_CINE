from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_media_agent.visible_report_runtime_generator import generate_visible_report

FORBIDDEN_FLAGS = {
    "--scan",
    "--ffprobe",
    "--ffmpeg",
    "--sync",
    "--transcribe",
    "--subtitle",
    "--export-davinci",
    "--export-avid",
    "--upload",
    "--database-write",
    "--network",
    "--client-facing",
}


class CliError(Exception):
    """Controlled CLI failure with a concise operator-facing message."""


class ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliError(message)


def _build_parser() -> argparse.ArgumentParser:
    parser = ControlledArgumentParser(
        prog="visible_report_runtime_cli",
        description="Generate a CID Local Media Agent visible report from a controlled scanner result JSON.",
    )
    parser.add_argument("--scanner-result-json", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--print-output-path", action="store_true")
    return parser


def _reject_forbidden_flags(argv: Sequence[str]) -> None:
    for token in argv:
        flag = token.split("=", 1)[0]
        if flag in FORBIDDEN_FLAGS:
            raise CliError(f"unsupported flag for controlled visible report CLI: {flag}")


def _is_url_like(raw_path: str) -> bool:
    lowered = raw_path.lower()
    return "://" in lowered or lowered.startswith(("http:", "https:", "ftp:", "s3:", "gs:"))


def _is_windows_drive_path(raw_path: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:(?:[\\/].*)?$", raw_path))


def _is_unc_path(raw_path: str) -> bool:
    return raw_path.startswith("\\\\") or raw_path.startswith("//")


def _is_mounted_windows_path(raw_path: str) -> bool:
    return raw_path == "/mnt" or raw_path.startswith("/mnt/")


def _is_repo_path(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(REPO_ROOT)
        return True
    except ValueError:
        return False


def _safe_path(raw_path: str, *, role: str, reject_repo: bool) -> Path:
    if not raw_path:
        raise CliError(f"{role} path is required")

    if _is_url_like(raw_path):
        raise CliError(f"{role} path must be local and must not be URL-like")

    if _is_windows_drive_path(raw_path):
        raise CliError(f"{role} path must not be a Windows drive path")

    if _is_unc_path(raw_path):
        raise CliError(f"{role} path must not be a UNC path")

    if _is_mounted_windows_path(raw_path):
        raise CliError(f"{role} path must not use mounted Windows paths")

    path = Path(raw_path).expanduser().resolve(strict=False)

    if reject_repo and _is_repo_path(path):
        raise CliError(f"{role} path must not be inside the repository")

    return path


def _load_scanner_result(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise CliError("scanner result JSON file does not exist")

    if path.is_dir():
        raise CliError("scanner result JSON path must be a file, not a directory")

    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"scanner result JSON is invalid: {exc.msg}") from exc

    if not isinstance(parsed, dict):
        raise CliError("scanner result JSON root must be an object")

    return parsed


def main(argv: Sequence[str] | None = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)

    try:
        _reject_forbidden_flags(argv_list)
        args = _build_parser().parse_args(argv_list)

        scanner_result_path = _safe_path(
            args.scanner_result_json,
            role="scanner result JSON",
            reject_repo=True,
        )
        output_root = _safe_path(
            args.output_root,
            role="output root",
            reject_repo=True,
        )

        scanner_result = _load_scanner_result(scanner_result_path)

        if args.dry_run:
            return 0

        report_path = generate_visible_report(scanner_result, output_root)

        if args.print_output_path:
            print(report_path)

        return 0

    except CliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
