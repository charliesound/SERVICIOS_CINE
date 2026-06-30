from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Sequence

from scripts.local_media_agent import (
    ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli as export_cli,
)


RUNNER_NAME = "cid-local-media-agent-visible-report-write-enabled-export-controlled-local-demo-runner"
COMMAND_NAME = export_cli.COMMAND_NAME
WRITE_AUTHORIZATION = export_cli.WRITE_AUTHORIZATION
DRY_RUN_AUTHORIZATION = export_cli.DRY_RUN_AUTHORIZATION
OPERATIONAL_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"

DEFAULT_VISIBLE_REPORT_TEXT = (
    "CID Local Media Agent controlled local demo visible report. "
    "Fixture-only technical demo. No real media, scanner, ffprobe, FFmpeg, network, SaaS, or database execution."
)

TARGET_ARTIFACT_NAME = "controlled_visible_report.controlled.txt"


class ControlledLocalDemoRunnerError(RuntimeError):
    """Raised when the controlled local demo runner detects an unsafe or invalid state."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _fixture_owned_demo_root() -> Path:
    base = Path(tempfile.gettempdir()) / "pytest-of-harliesound"
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="cid-lma-controlled-demo-", dir=base))


def _is_inside_repo(path: Path) -> bool:
    repo = _repo_root().resolve()
    candidate = path.resolve()
    try:
        candidate.relative_to(repo)
    except ValueError:
        return False
    return True


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _capture_cli_main(argv: Sequence[str]) -> tuple[int, str]:
    buffer = io.StringIO()

    with contextlib.redirect_stdout(buffer):
        try:
            exit_code = export_cli.main(list(argv))
        except SystemExit as exc:
            code = exc.code
            if code is None:
                exit_code = 0
            elif isinstance(code, int):
                exit_code = code
            else:
                exit_code = 1

    return exit_code, buffer.getvalue()


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ControlledLocalDemoRunnerError(f"CLI stdout is not deterministic JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ControlledLocalDemoRunnerError("CLI JSON payload is not an object")

    return payload


def run_controlled_local_demo(*, keep_output: bool = False) -> dict[str, Any]:
    command_path = shutil.which(COMMAND_NAME)
    if command_path is None:
        raise ControlledLocalDemoRunnerError("installed command is not available in the active environment")

    output_root = _fixture_owned_demo_root()

    if _is_inside_repo(output_root):
        raise ControlledLocalDemoRunnerError("controlled demo output root must not be inside the repository")

    help_exit_code, help_stdout = _capture_cli_main(["--help"])
    if help_exit_code != 0:
        raise ControlledLocalDemoRunnerError("installed help invocation failed")
    for expected in ["--visible-report-text", "--controlled-output-root", "--write-authorization", "--result-json", "--dry-run"]:
        if expected not in help_stdout:
            raise ControlledLocalDemoRunnerError(f"installed help is missing expected argument: {expected}")

    dry_run_exit_code, dry_run_stdout = _capture_cli_main(
        [
            "--visible-report-text",
            DEFAULT_VISIBLE_REPORT_TEXT,
            "--controlled-output-root",
            str(output_root),
            "--write-authorization",
            DRY_RUN_AUTHORIZATION,
            "--result-json",
            "--dry-run",
        ]
    )
    dry_run_payload = _parse_json_stdout(dry_run_stdout)
    if dry_run_exit_code != 0 or dry_run_payload.get("verification_status") != "DRY_RUN_ONLY":
        raise ControlledLocalDemoRunnerError("controlled dry-run step failed")
    if dry_run_payload.get("artifact_created_on_disk") is not False:
        raise ControlledLocalDemoRunnerError("dry-run created an artifact unexpectedly")

    write_exit_code, write_stdout = _capture_cli_main(
        [
            "--visible-report-text",
            DEFAULT_VISIBLE_REPORT_TEXT,
            "--controlled-output-root",
            str(output_root),
            "--write-authorization",
            WRITE_AUTHORIZATION,
            "--result-json",
        ]
    )
    write_payload = _parse_json_stdout(write_stdout)
    if write_exit_code != 0 or write_payload.get("verification_status") != "VERIFIED":
        raise ControlledLocalDemoRunnerError("controlled write step failed")

    artifact_path = output_root / TARGET_ARTIFACT_NAME
    if not artifact_path.exists():
        raise ControlledLocalDemoRunnerError("controlled write artifact was not created")
    if _is_inside_repo(artifact_path):
        raise ControlledLocalDemoRunnerError("controlled write artifact must not be inside the repository")

    negative_root = output_root / "negative-path"
    negative_root.mkdir(parents=False, exist_ok=False)

    negative_exit_code, negative_stdout = _capture_cli_main(
        [
            "--visible-report-text",
            DEFAULT_VISIBLE_REPORT_TEXT,
            "--controlled-output-root",
            str(negative_root),
            "--write-authorization",
            DRY_RUN_AUTHORIZATION,
            "--result-json",
        ]
    )
    negative_payload = _parse_json_stdout(negative_stdout)
    if negative_exit_code == 0:
        raise ControlledLocalDemoRunnerError("negative path unexpectedly returned success")
    if negative_payload.get("verification_status") != "REJECTED":
        raise ControlledLocalDemoRunnerError("negative path did not reject as expected")
    if negative_payload.get("write_performed") is not False:
        raise ControlledLocalDemoRunnerError("negative path performed a write unexpectedly")
    if (negative_root / TARGET_ARTIFACT_NAME).exists():
        raise ControlledLocalDemoRunnerError("negative path created an unauthorized artifact")

    artifact_sha256 = _sha256(artifact_path)
    artifact_bytes = artifact_path.stat().st_size

    summary = {
        "runner_name": RUNNER_NAME,
        "operational_boundary": OPERATIONAL_BOUNDARY,
        "status": "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED",
        "command_name": COMMAND_NAME,
        "command_path": command_path,
        "help_exit_code": help_exit_code,
        "dry_run_exit_code": dry_run_exit_code,
        "write_exit_code": write_exit_code,
        "negative_exit_code": negative_exit_code,
        "output_root": str(output_root),
        "artifact_path": str(artifact_path),
        "artifact_name": artifact_path.name,
        "artifact_sha256": artifact_sha256,
        "artifact_bytes": artifact_bytes,
        "keep_output": keep_output,
        "steps": [
            "installed_command_availability_check",
            "installed_help_invocation",
            "installed_dry_run_result_json_invocation",
            "installed_controlled_write_single_txt_artifact",
            "installed_negative_path_fail_closed",
        ],
        "safety": {
            "demo_runner_only": True,
            "fixture_owned_output_root": True,
            "writes_inside_repository": False,
            "real_media_used": False,
            "scanner_used": False,
            "ffprobe_used": False,
            "ffmpeg_used": False,
            "network_used": False,
            "saas_used": False,
            "database_used": False,
            "installer_used": False,
            "client_demo": False,
            "public_demo": False,
            "single_artifact_write": True,
            "overwrite_used": False,
        },
        "dry_run": dry_run_payload,
        "write": write_payload,
        "negative_path": negative_payload,
    }

    if not keep_output:
        shutil.rmtree(output_root, ignore_errors=True)
        summary["output_root_removed"] = True
        summary["artifact_available_after_runner"] = False
    else:
        summary["output_root_removed"] = False
        summary["artifact_available_after_runner"] = artifact_path.exists()

    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=RUNNER_NAME,
        description=(
            "Internal controlled local demo runner for the installed CID Local Media Agent write-enabled export CLI. "
            "No production, client-facing, real media, scanner, ffprobe, FFmpeg, network, SaaS, database, or installer execution."
        ),
    )
    parser.add_argument(
        "--result-json",
        action="store_true",
        help="Print deterministic controlled demo summary JSON to stdout.",
    )
    parser.add_argument(
        "--keep-output",
        action="store_true",
        help="Keep the fixture-owned temporary output root for manual inspection.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        summary = run_controlled_local_demo(keep_output=args.keep_output)
    except ControlledLocalDemoRunnerError as exc:
        payload = {
            "runner_name": RUNNER_NAME,
            "operational_boundary": OPERATIONAL_BOUNDARY,
            "status": "CONTROLLED_LOCAL_DEMO_RUNNER_FAILED_CLOSED",
            "error": str(exc),
        }
        if args.result_json:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(f"{payload['status']}: {payload['error']}")
        return 1

    if args.result_json:
        print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    else:
        print(f"{summary['status']}")
        print(f"command_path={summary['command_path']}")
        print(f"artifact_sha256={summary['artifact_sha256']}")
        print(f"output_root_removed={summary['output_root_removed']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
