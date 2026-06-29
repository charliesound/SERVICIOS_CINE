from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export import (
    DEFAULT_FILENAME,
    WRITE_AUTHORIZATION,
    export_controlled_visible_report_text_artifact,
)


PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT."
    "CLI.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)

CLI_CONTRACT_VERSION = "1.0"

COMMAND_NAME = "cid-local-media-agent-visible-report-write-enabled-export"

MODULE_NAME = (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli.py"
)

DRY_RUN_AUTHORIZATION = "CONTROLLED_DRY_RUN_ACCEPTED"

FORBIDDEN_UNSAFE_ALIASES = frozenset(
    {
        "--output",
        "--output-path",
        "--artifact-path",
        "--overwrite",
        "--force",
        "--create-dir",
        "--mkdir",
        "--production",
        "--client",
        "--public-demo",
        "--ffprobe",
        "--ffmpeg",
        "--network",
        "--database",
    }
)

ALLOWED_OPTION_STRINGS = frozenset(
    {
        "--visible-report-text",
        "--controlled-output-root",
        "--write-authorization",
        "--result-json",
        "--dry-run",
        "-h",
        "--help",
    }
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=COMMAND_NAME,
        description=(
            "Internal controlled fixture-owned visible report text artifact export CLI. "
            "No production, client-facing, scanner, ffprobe, FFmpeg, network, SaaS, or database execution."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--visible-report-text",
        dest="visible_report_text",
        default=None,
        help="Controlled visible report text to export.",
    )
    parser.add_argument(
        "--controlled-output-root",
        dest="controlled_output_root",
        default=None,
        help="Fixture-owned controlled output root.",
    )
    parser.add_argument(
        "--write-authorization",
        dest="write_authorization",
        default=None,
        help="Exact controlled write authorization token.",
    )
    parser.add_argument(
        "--result-json",
        dest="result_json_requested",
        action="store_true",
        help="Print deterministic result JSON to stdout.",
    )
    parser.add_argument(
        "--dry-run",
        dest="dry_run_requested",
        action="store_true",
        help="Validate arguments without creating an artifact.",
    )
    return parser


def _base_result(
    *,
    mode: str,
    dry_run_requested: bool,
    write_requested: bool,
    result_json_requested: bool,
    visible_report_text: str | None,
    controlled_output_root: str | None,
    write_authorization: str | None,
) -> dict[str, Any]:
    intended_bytes = (
        len(visible_report_text.encode("utf-8"))
        if visible_report_text is not None
        else 0
    )

    return {
        "phase": PHASE_ID,
        "cli_contract_version": CLI_CONTRACT_VERSION,
        "command_name": COMMAND_NAME,
        "module_name": MODULE_NAME,
        "mode": mode,
        "dry_run_requested": dry_run_requested,
        "write_requested": write_requested,
        "result_json_requested": result_json_requested,
        "write_performed": False,
        "artifact_created_on_disk": False,
        "controlled_output_root": controlled_output_root,
        "artifact_path": None,
        "filename": DEFAULT_FILENAME,
        "extension": ".txt",
        "write_authorization": write_authorization,
        "bytes_intended": intended_bytes,
        "bytes_written": 0,
        "content_sha256_before_write": None,
        "content_sha256_after_write": None,
        "overwrite_policy": "NO_OVERWRITE",
        "verification_status": "NOT_VERIFIED",
        "safety_flags": {
            "fixture_owned_output_root_required": True,
            "single_artifact_only": True,
            "directory_creation_performed": False,
            "overwrite_performed": False,
            "scanner_execution_performed": False,
            "ffprobe_execution_performed": False,
            "ffmpeg_execution_performed": False,
            "external_process_execution_performed": False,
            "network_access_performed": False,
            "saas_or_database_access_performed": False,
            "client_facing_or_production_usage_authorized": False,
        },
        "warnings": [],
        "errors": [],
        "exit_code": 1,
    }


def _reject(
    *,
    errors: list[str],
    result_json_requested: bool,
    visible_report_text: str | None = None,
    controlled_output_root: str | None = None,
    write_authorization: str | None = None,
    mode: str = "rejected",
    dry_run_requested: bool = False,
    write_requested: bool = False,
    exit_code: int = 2,
) -> dict[str, Any]:
    result = _base_result(
        mode=mode,
        dry_run_requested=dry_run_requested,
        write_requested=write_requested,
        result_json_requested=result_json_requested,
        visible_report_text=visible_report_text,
        controlled_output_root=controlled_output_root,
        write_authorization=write_authorization,
    )
    result["verification_status"] = "REJECTED"
    result["errors"] = list(errors)
    result["exit_code"] = exit_code
    return result


def _parser_result_json_requested(argv: Sequence[str] | None) -> bool:
    if argv is None:
        return False
    return "--result-json" in argv


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)


def execute(argv: Sequence[str] | None = None) -> dict[str, Any]:
    result_json_requested = _parser_result_json_requested(argv)

    try:
        args = parse_args(argv)
    except SystemExit as exc:
        exit_code = int(exc.code) if isinstance(exc.code, int) else 2
        return _reject(
            errors=["argument parsing failed"],
            result_json_requested=result_json_requested,
            exit_code=exit_code,
        )

    visible_report_text = args.visible_report_text
    controlled_output_root = args.controlled_output_root
    write_authorization = args.write_authorization
    result_json_requested = bool(args.result_json_requested)
    dry_run_requested = bool(args.dry_run_requested)

    if dry_run_requested:
        result = _base_result(
            mode="dry_run",
            dry_run_requested=True,
            write_requested=False,
            result_json_requested=result_json_requested,
            visible_report_text=visible_report_text,
            controlled_output_root=controlled_output_root,
            write_authorization=write_authorization,
        )
        result["verification_status"] = "DRY_RUN_ONLY"
        result["exit_code"] = 0
        return result

    errors: list[str] = []

    if visible_report_text is None:
        errors.append("missing visible report text")
    elif visible_report_text == "":
        errors.append("empty visible report text")

    if controlled_output_root is None:
        errors.append("missing controlled output root")

    if write_authorization is None:
        errors.append("missing write authorization")
    elif write_authorization == DRY_RUN_AUTHORIZATION:
        errors.append("dry-run authorization is not valid for controlled write")
    elif write_authorization != WRITE_AUTHORIZATION:
        errors.append("unknown write authorization")

    if errors:
        return _reject(
            errors=errors,
            result_json_requested=result_json_requested,
            visible_report_text=visible_report_text,
            controlled_output_root=controlled_output_root,
            write_authorization=write_authorization,
            mode="controlled_write_rejected",
            write_requested=True,
            exit_code=1,
        )

    export_result = export_controlled_visible_report_text_artifact(
        visible_report_text=visible_report_text,
        controlled_output_root=Path(controlled_output_root),
        write_authorization=write_authorization,
    )

    result = _base_result(
        mode="controlled_write",
        dry_run_requested=False,
        write_requested=True,
        result_json_requested=result_json_requested,
        visible_report_text=visible_report_text,
        controlled_output_root=controlled_output_root,
        write_authorization=write_authorization,
    )
    cli_safety_flags = dict(result["safety_flags"])
    result.update(export_result)
    result["safety_flags"] = {
        **cli_safety_flags,
        **dict(export_result.get("safety_flags", {})),
    }
    result["extension"] = ".txt"
    result["phase"] = PHASE_ID
    result["cli_contract_version"] = CLI_CONTRACT_VERSION
    result["command_name"] = COMMAND_NAME
    result["module_name"] = MODULE_NAME
    result["mode"] = "controlled_write"
    result["dry_run_requested"] = False
    result["write_requested"] = True
    result["result_json_requested"] = result_json_requested
    result["exit_code"] = 0 if result.get("verification_status") == "VERIFIED" else 1
    return result


def _json_default(value: Any) -> str:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(
        result,
        sort_keys=True,
        ensure_ascii=False,
        default=_json_default,
    )


def main(argv: Sequence[str] | None = None) -> int:
    result = execute(argv)
    if result.get("result_json_requested"):
        print(result_to_json(result))
    return int(result["exit_code"])


__all__ = [
    "ALLOWED_OPTION_STRINGS",
    "CLI_CONTRACT_VERSION",
    "COMMAND_NAME",
    "DEFAULT_FILENAME",
    "DRY_RUN_AUTHORIZATION",
    "FORBIDDEN_UNSAFE_ALIASES",
    "MODULE_NAME",
    "PHASE_ID",
    "WRITE_AUTHORIZATION",
    "build_parser",
    "execute",
    "main",
    "parse_args",
    "result_to_json",
]
