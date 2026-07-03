from __future__ import annotations

import io
import json
from typing import Any

from scripts.local_media_agent.real_media_preflight_controlled_stat_sanitized_report_controlled_export_cli import (
    run_controlled_sanitized_report_export_cli,
)


REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN = (
    "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
)

_CONTROLLED_SMOKE_FIXTURE_MARKDOWN = (
    "# CID Local Media Agent \u2014 Controlled Stat Implementation Sanitized Report\n"
    "\n"
    "## Sanitized selection\n"
    "\n"
    "- `sanitized_selection_token`:" +
    " `REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN`\n"
    "\n"
    "## Report record\n"
    "\n"
    "- `report_mode`: `markdown_report`\n"
    "\n"
    "## Controlled stat status map\n"
    "\n"
    "- `filesystem_stat_status`: `not_executed`\n"
    "\n"
    "## Human-readable verdict\n"
    "\n"
    "Controlled smoke fixture.\n"
    "\n"
    "## Renderer closure criteria\n"
    "\n"
    "- `markdown_text_only`: `controlled`\n"
    "- `file_write`: `not_executed`\n"
    "- `media_execution`: `not_executed`\n"
    "- `saas_integration`: `no_saas_integration`\n"
)


def run_controlled_sanitized_report_export_cli_controlled_smoke(
    output_path: str,
    export_opt_in: bool,
) -> dict[str, Any]:
    argv: list[str] = [
        "--markdown-text",
        _CONTROLLED_SMOKE_FIXTURE_MARKDOWN,
        "--output-path",
        output_path,
    ]
    if export_opt_in:
        argv.append("--export-opt-in")

    stdout = io.StringIO()
    cli_exit_code = run_controlled_sanitized_report_export_cli(argv, stdout=stdout)

    stdout_value = stdout.getvalue()
    try:
        payload = json.loads(stdout_value)
    except json.JSONDecodeError:
        return {
            "status": "error",
            "cli_exit_code": cli_exit_code,
            "output_path": output_path,
            "created": False,
            "errors": ["CLI output is not valid JSON"],
            "verification_status": "JSON_PARSE_ERROR",
        }

    return {
        "status": "ok" if cli_exit_code == 0 else "error",
        "cli_exit_code": cli_exit_code,
        "output_path": output_path,
        "created": payload.get("artifact_created_on_disk", False),
        "errors": list(payload.get("errors", [])),
        "verification_status": payload.get("verification_status", "UNKNOWN"),
    }


def main() -> int:
    import sys

    export_opt_in = "--export-opt-in" in sys.argv[1:]
    output_path = "output.md"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output-path" and i + 1 < len(sys.argv[1:]):
            output_path = sys.argv[1:][i + 1]

    result = run_controlled_sanitized_report_export_cli_controlled_smoke(
        output_path, export_opt_in
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
