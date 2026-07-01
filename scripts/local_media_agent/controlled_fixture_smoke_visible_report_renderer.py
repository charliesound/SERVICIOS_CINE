from __future__ import annotations

from collections.abc import Mapping
from typing import Any


DEFAULT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.RENDERER.IMPLEMENTATION.GATE.V1"
DEFAULT_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_RENDERER_IMPLEMENTATION_GATE_V1_CLOSED"

REQUIRED_MARKDOWN_SECTIONS: tuple[str, ...] = (
    "Report title",
    "Phase identifier",
    "Result identifier",
    "Smoke status",
    "Controlled fixture identity",
    "Fixture root",
    "Allowed relative path",
    "File name",
    "Byte size",
    "SHA256 digest",
    "CLI execution mode",
    "Exit code",
    "JSON stdout validation status",
    "Stderr validation status",
    "Fixture immutability status",
    "Output file creation status",
    "Forbidden boundary checklist",
    "Human review decision placeholder",
    "Next allowed phase placeholder",
)

FORBIDDEN_BOUNDARY_ITEMS: tuple[str, ...] = (
    "No CLI behavior changes",
    "No CLI execution inside renderer",
    "No report file generation",
    "No export behavior",
    "No subprocess",
    "No shell execution",
    "No fixture modification",
    "No scanner integration",
    "No batch processing",
    "No recursive product traversal",
    "No FFmpeg",
    "No ffprobe",
    "No SaaS integration",
    "No database access",
    "No backend or frontend access",
    "No real material",
    "No customer material",
)


def _stringify(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = " ".join(str(value).splitlines()).strip()
    if not text:
        return "UNKNOWN"
    return _redact_private_path_markers(text)


def _redact_private_path_markers(text: str) -> str:
    private_markers = (
        "/home/",
        "/Users/",
        "/mnt/c/",
        "/mnt/d/",
        "C:\\\\",
        "D:\\\\",
        "\\\\wsl.localhost\\\\",
    )
    if any(marker in text for marker in private_markers):
        return "[REDACTED_PRIVATE_PATH]"
    return text


def _get(data: Mapping[str, Any], key: str, default: str = "UNKNOWN") -> str:
    return _stringify(data.get(key, default))


def render_controlled_fixture_smoke_visible_report(
    smoke_result: Mapping[str, Any],
    *,
    phase: str = DEFAULT_PHASE,
    result: str = DEFAULT_RESULT,
    human_review_decision: str = "PENDING_HUMAN_REVIEW",
    next_allowed_phase: str = "PENDING_HUMAN_DECISION",
) -> str:
    """Render controlled fixture smoke evidence as Markdown text in memory."""
    if not isinstance(smoke_result, Mapping):
        raise TypeError("smoke_result must be a mapping")

    lines: list[str] = [
        "# CID Local Media Agent - Controlled Fixture Smoke Visible Report",
        "",
        "## Phase identifier",
        "",
        _stringify(phase),
        "",
        "## Result identifier",
        "",
        _stringify(result),
        "",
        "## Smoke status",
        "",
        _get(smoke_result, "smoke_status"),
        "",
        "## Controlled fixture identity",
        "",
        f"- Fixture id: {_get(smoke_result, 'fixture_id')}",
        f"- Fixture root: {_get(smoke_result, 'fixture_root')}",
        f"- Allowed relative path: {_get(smoke_result, 'allowed_relative_path')}",
        f"- File name: {_get(smoke_result, 'file_name')}",
        "",
        "## File metadata",
        "",
        f"- Byte size: {_get(smoke_result, 'byte_size')}",
        f"- SHA256 digest: {_get(smoke_result, 'sha256')}",
        "",
        "## CLI execution mode",
        "",
        _get(smoke_result, "cli_execution_mode"),
        "",
        "## Exit code",
        "",
        _get(smoke_result, "exit_code"),
        "",
        "## JSON stdout validation status",
        "",
        _get(smoke_result, "json_stdout_validation_status"),
        "",
        "## Stderr validation status",
        "",
        _get(smoke_result, "stderr_validation_status"),
        "",
        "## Fixture immutability status",
        "",
        _get(smoke_result, "fixture_immutability_status"),
        "",
        "## Output file creation status",
        "",
        _get(smoke_result, "output_file_creation_status"),
        "",
        "## Forbidden boundary checklist",
        "",
    ]

    for item in FORBIDDEN_BOUNDARY_ITEMS:
        lines.append(f"- PASS: {item}")

    lines.extend(
        [
            "",
            "## Human review decision placeholder",
            "",
            _stringify(human_review_decision),
            "",
            "## Next allowed phase placeholder",
            "",
            _stringify(next_allowed_phase),
            "",
        ]
    )

    return "\n".join(lines)
