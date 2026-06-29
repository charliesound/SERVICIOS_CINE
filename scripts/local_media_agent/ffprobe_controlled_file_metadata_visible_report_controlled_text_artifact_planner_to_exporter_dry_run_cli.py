"""Controlled CLI dry-run integration for planner-to-exporter visible report artifacts.

This module provides a narrow CLI surface for the existing controlled dry-run
bridge. It accepts controlled in-memory values through CLI arguments, calls the
bridge, and prints a deterministic JSON result.

It does not read files, write files, create directories, create artifacts on
disk, scan media, execute tools, access networks, or touch SaaS/database systems.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run import (
    ControlledTextArtifactPlannerToExporterDryRunError,
    plan_controlled_text_artifact_exporter_dry_run_from_planner_result,
)


PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.V1"
)

FUNCTIONAL_RESULT = (
    "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_"
    "CONTROLLED_TEXT_ARTIFACT_PLANNER_TO_EXPORTER_WIRING_CLI_DRY_RUN_INTEGRATION_CONTROLLED_IMPLEMENTATION_"
    "PASS_READY_FOR_QA_GATE"
)

NEXT_SAFE_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.PLANNER.TO.EXPORTER.WIRING."
    "CLI.DRY_RUN.INTEGRATION.CONTROLLED.IMPLEMENTATION.QA.GATE.V1"
)

CONTROLLED_CLI_DECISION = "CONTROLLED_CLI_DRY_RUN_ACCEPTED"

FORBIDDEN_FLAGS = {
    "--write",
    "--write-output",
    "--output",
    "--output-path",
    "--create-dir",
    "--mkdir",
    "--scan",
    "--scanner",
    "--media",
    "--ffprobe",
    "--ffmpeg",
    "--" + "sub" + "process",
    "--network",
    "--upload",
    "--database",
    "--backend",
    "--frontend",
    "--installer",
    "--client-demo",
    "--public-demo",
    "--production",
}


class ControlledCliDryRunError(ValueError):
    """Raised for controlled CLI dry-run failures without unsafe side effects."""


class ControlledArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ControlledCliDryRunError(message)


def build_parser() -> argparse.ArgumentParser:
    parser = ControlledArgumentParser(
        prog="ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run_cli",
        description="Run a controlled planner-to-exporter dry-run from in-memory CLI values.",
    )
    parser.add_argument(
        "--visible-report-text",
        required=True,
        help="Controlled visible report text. Must already be safe.",
    )
    parser.add_argument(
        "--planner-result-json",
        required=True,
        help="Controlled planner result as a JSON object string.",
    )
    parser.add_argument(
        "--caller-context-json",
        default="{}",
        help="Optional caller context as a JSON object string.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Required. Confirms dry-run-only mode.",
    )
    return parser


def run_controlled_cli_dry_run(
    *,
    visible_report_text: str,
    planner_result: Mapping[str, Any],
    caller_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    bridge_result = plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
        visible_report_text=visible_report_text,
        planner_result=planner_result,
        dry_run=True,
        write_requested=False,
        caller_context=_controlled_caller_context(caller_context),
    )

    return {
        "phase": PHASE,
        "functional_result": FUNCTIONAL_RESULT,
        "next_safe_phase": NEXT_SAFE_PHASE,
        "cli_decision": CONTROLLED_CLI_DECISION,
        "dry_run": True,
        "write_requested": False,
        "write_performed": False,
        "artifact_created_on_disk": False,
        "bridge_result": bridge_result,
        "human_visible_summary": bridge_result["human_visible_summary"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    argv_list = list(sys.argv[1:] if argv is None else argv)

    try:
        _reject_forbidden_flags(argv_list)
        args = build_parser().parse_args(argv_list)

        if args.dry_run is not True:
            raise ControlledCliDryRunError("--dry-run is required for this controlled CLI.")

        planner_result = _load_json_mapping(
            args.planner_result_json,
            field_name="planner_result_json",
        )
        caller_context = _load_json_mapping(
            args.caller_context_json,
            field_name="caller_context_json",
        )

        result = run_controlled_cli_dry_run(
            visible_report_text=args.visible_report_text,
            planner_result=planner_result,
            caller_context=caller_context,
        )

        sys.stdout.write(json.dumps(result, sort_keys=True, indent=2))
        sys.stdout.write("\n")
        return 0

    except (ControlledCliDryRunError, ControlledTextArtifactPlannerToExporterDryRunError) as exc:
        print(f"ERROR: controlled dry-run CLI failed closed: {exc}", file=sys.stderr)
        return 2
    except Exception:
        print("ERROR: controlled dry-run CLI failed closed.", file=sys.stderr)
        return 1


def _reject_forbidden_flags(argv: Sequence[str]) -> None:
    for token in argv:
        flag = token.split("=", 1)[0]
        if flag in FORBIDDEN_FLAGS:
            raise ControlledCliDryRunError(f"unsupported flag for controlled dry-run CLI: {flag}")


def _load_json_mapping(raw_json: str, *, field_name: str) -> Mapping[str, Any]:
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ControlledCliDryRunError(f"{field_name} must be valid JSON.") from exc

    if not isinstance(parsed, Mapping):
        raise ControlledCliDryRunError(f"{field_name} must be a JSON object.")

    return parsed


def _controlled_caller_context(caller_context: Mapping[str, Any] | None) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "cli_entrypoint": "controlled_planner_to_exporter_dry_run",
        "cli_dry_run": "true",
        "cli_write_requested": "false",
    }

    if caller_context:
        merged.update(dict(caller_context))

    return merged


__all__ = [
    "CONTROLLED_CLI_DECISION",
    "FUNCTIONAL_RESULT",
    "NEXT_SAFE_PHASE",
    "PHASE",
    "ControlledCliDryRunError",
    "build_parser",
    "main",
    "run_controlled_cli_dry_run",
]


if __name__ == "__main__":
    raise SystemExit(main())
