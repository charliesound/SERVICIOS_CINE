from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from scripts.local_media_agent.real_media_preflight_controlled_stat_implementation import (
    ControlledStatImplementationResult,
)


SANITIZED_REPORT_RENDERER_RECORD_ID = "controlled_stat_sanitized_report_renderer_001"
SANITIZED_REPORT_RENDERER_HANDLE = "CONTROLLED_STAT_SANITIZED_REPORT_RENDERER_HANDLE_001"
SANITIZED_REPORT_SCHEMA_VERSION = "controlled_stat_sanitized_report_v1"
SANITIZED_REPORT_TITLE = "CID Local Media Agent — Controlled Stat Implementation Sanitized Report"
FIXED_SANITIZED_SELECTION_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"

_HUMAN_READABLE_VERDICT = (
    "Sanitized report generated from a non-executing controlled stat implementation result. "
    "No filesystem stat, file access, file open, byte read, metadata read, media probing, "
    "scanner execution, or SaaS integration was performed."
)


@dataclass(frozen=True)
class SanitizedControlledStatReport:
    report_record_id: str
    report_schema_version: str
    source_implementation_record_id: str
    source_implementation_handle: str
    sanitized_selection_token: str
    report_scope: str
    report_mode: str
    status_map: Mapping[str, str]
    disclosure_boundary: Mapping[str, str]
    media_tooling_boundary: Mapping[str, str]
    saas_boundary: Mapping[str, str]
    report_verdict: str


def _text(value: object) -> str:
    return str(value)


def _result_value(result: ControlledStatImplementationResult, field_name: str, default: str) -> str:
    return _text(getattr(result, field_name, default))


def build_sanitized_status_map(
    result: ControlledStatImplementationResult,
) -> Mapping[str, str]:
    return {
        "filesystem_stat_status": _result_value(result, "filesystem_stat_status", "not_executed"),
        "file_access_status": _result_value(result, "file_access_status", "not_accessed"),
        "file_open_status": _result_value(result, "file_open_status", "not_opened"),
        "file_bytes_status": _result_value(result, "file_bytes_status", "not_read"),
        "filesystem_metadata_status": _result_value(result, "filesystem_metadata_status", "not_read"),
        "file_size_status": _result_value(result, "file_size_status", "not_recorded"),
        "timestamp_status": _result_value(result, "timestamp_status", "not_recorded"),
        "hash_status": _result_value(result, "hash_status", "not_recorded"),
        "ffmpeg_status": _result_value(result, "ffmpeg_status", "not_executed"),
        "ffprobe_status": _result_value(result, "ffprobe_status", "not_executed"),
        "scanner_status": _result_value(result, "scanner_status", "not_executed"),
        "saas_status": _result_value(result, "saas_status", "no_saas_integration"),
    }


def build_sanitized_disclosure_boundary() -> Mapping[str, str]:
    return {
        "absolute_local_path": "not_allowed",
        "relative_local_path": "not_allowed",
        "windows_path": "not_allowed",
        "mount_path": "not_allowed",
        "unc_path": "not_allowed",
        "sensitive_filename": "not_allowed",
        "parent_folder": "not_allowed",
        "real_file_size": "not_recorded",
        "real_timestamp": "not_recorded",
        "real_hash": "not_recorded",
        "operator_home_directory": "not_allowed",
        "customer_private_name": "not_allowed",
        "project_private_name": "not_allowed",
    }


def build_sanitized_media_tooling_boundary() -> Mapping[str, str]:
    return {
        "media_decode_status": "not_executed",
        "media_probe_status": "not_executed",
        "media_scan_status": "not_executed",
        "transcription_status": "not_executed",
        "thumbnail_status": "not_generated",
        "waveform_status": "not_generated",
        "ffmpeg_execution_status": "not_executed",
        "ffprobe_execution_status": "not_executed",
        "scanner_execution_status": "not_executed",
    }


def build_sanitized_saas_boundary() -> Mapping[str, str]:
    return {
        "saas_backend_status": "not_touched",
        "saas_frontend_status": "not_touched",
        "database_status": "not_touched",
        "docker_status": "not_touched",
        "alembic_status": "not_touched",
        "stripe_status": "not_touched",
        "ai_jobs_status": "not_touched",
        "credits_ledger_status": "not_touched",
    }


def build_controlled_stat_sanitized_report(
    result: ControlledStatImplementationResult,
) -> SanitizedControlledStatReport:
    return SanitizedControlledStatReport(
        report_record_id=SANITIZED_REPORT_RENDERER_RECORD_ID,
        report_schema_version=SANITIZED_REPORT_SCHEMA_VERSION,
        source_implementation_record_id="controlled_stat_implementation_001",
        source_implementation_handle="CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001",
        sanitized_selection_token=FIXED_SANITIZED_SELECTION_TOKEN,
        report_scope="controlled",
        report_mode="markdown_report",
        status_map=build_sanitized_status_map(result),
        disclosure_boundary=build_sanitized_disclosure_boundary(),
        media_tooling_boundary=build_sanitized_media_tooling_boundary(),
        saas_boundary=build_sanitized_saas_boundary(),
        report_verdict=_HUMAN_READABLE_VERDICT,
    )


def _mapping_lines(mapping: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(f"- `{key}`: `{value}`" for key, value in mapping.items())


def _machine_readable_lines(report: SanitizedControlledStatReport) -> tuple[str, ...]:
    status_map = report.status_map
    return (
        f"report_record_id={report.report_record_id}",
        f"report_schema_version={report.report_schema_version}",
        f"source_implementation_record_id={report.source_implementation_record_id}",
        f"source_implementation_handle={report.source_implementation_handle}",
        f"sanitized_selection_token={report.sanitized_selection_token}",
        f"filesystem_stat_status={status_map['filesystem_stat_status']}",
        f"file_access_status={status_map['file_access_status']}",
        f"file_open_status={status_map['file_open_status']}",
        f"file_bytes_status={status_map['file_bytes_status']}",
        f"filesystem_metadata_status={status_map['filesystem_metadata_status']}",
        f"file_size_status={status_map['file_size_status']}",
        f"timestamp_status={status_map['timestamp_status']}",
        f"hash_status={status_map['hash_status']}",
        f"ffmpeg_status={status_map['ffmpeg_status']}",
        f"ffprobe_status={status_map['ffprobe_status']}",
        f"scanner_status={status_map['scanner_status']}",
        f"saas_status={status_map['saas_status']}",
        "path_disclosure_status=not_allowed",
        "filename_disclosure_status=not_allowed",
        "parent_folder_disclosure_status=not_allowed",
        f"report_verdict={report.report_verdict}",
    )


def build_controlled_stat_sanitized_markdown_report(
    result: ControlledStatImplementationResult,
) -> str:
    report = build_controlled_stat_sanitized_report(result)

    lines = [
        f"# {SANITIZED_REPORT_TITLE}",
        "",
        "## Report record",
        "",
        f"- `report_record_id`: `{report.report_record_id}`",
        f"- `report_schema_version`: `{report.report_schema_version}`",
        f"- `report_scope`: `{report.report_scope}`",
        f"- `report_mode`: `{report.report_mode}`",
        f"- `report_verdict`: `{report.report_verdict}`",
        "",
        "## Source implementation",
        "",
        f"- `implementation_record_id`: `{report.source_implementation_record_id}`",
        f"- `implementation_handle`: `{report.source_implementation_handle}`",
        "- `implementation_verdict`: `controlled_stat_implementation_result_without_stat_open_or_metadata_read`",
        "- `implementation_boundary_status`: `non_executing`",
        "- `source_request_record_id`: `sanitized`",
        f"- `source_sanitized_selection_token`: `{report.sanitized_selection_token}`",
        "",
        "## Sanitized selection",
        "",
        f"- `sanitized_selection_token`: `{report.sanitized_selection_token}`",
        "",
        "## Controlled stat status map",
        "",
        *_mapping_lines(report.status_map),
        "",
        "## Non-execution boundary",
        "",
        "- `filesystem_stat`: `not_executed`",
        "- `file_access`: `not_accessed`",
        "- `file_open`: `not_opened`",
        "- `file_bytes`: `not_read`",
        "- `filesystem_metadata`: `not_read`",
        "- `file_size`: `not_recorded`",
        "- `timestamps`: `not_recorded`",
        "- `hashes`: `not_recorded`",
        "- `ffmpeg`: `not_executed`",
        "- `ffprobe`: `not_executed`",
        "- `scanner`: `not_executed`",
        "- `saas`: `no_saas_integration`",
        "",
        "## Disclosure boundary",
        "",
        *_mapping_lines(report.disclosure_boundary),
        "",
        "## Media tooling boundary",
        "",
        *_mapping_lines(report.media_tooling_boundary),
        "",
        "## SaaS boundary",
        "",
        *_mapping_lines(report.saas_boundary),
        "",
        "## Human-readable verdict",
        "",
        report.report_verdict,
        "",
        "## Machine-readable status map",
        "",
        "```text",
        *_machine_readable_lines(report),
        "```",
        "",
        "## Renderer closure criteria",
        "",
        "- `markdown_text_only`: `controlled`",
        "- `file_write`: `not_executed`",
        "- `media_execution`: `not_executed`",
        "- `saas_integration`: `no_saas_integration`",
        "",
    ]

    return "\n".join(lines)


def describe_sanitized_report_renderer_boundary() -> Mapping[str, str]:
    return {
        "record_id": SANITIZED_REPORT_RENDERER_RECORD_ID,
        "handle": SANITIZED_REPORT_RENDERER_HANDLE,
        "schema_version": SANITIZED_REPORT_SCHEMA_VERSION,
        "output_mode": "markdown_text_only",
        "input_mode": "controlled_stat_implementation_result_only",
        "filesystem_write": "not_performed",
        "existing_file_modification": "not_performed",
        "filesystem_stat": "not_executed",
        "file_access": "not_accessed",
        "file_open": "not_opened",
        "file_bytes": "not_read",
        "filesystem_metadata": "not_read",
        "file_size": "not_recorded",
        "timestamps": "not_recorded",
        "hashes": "not_recorded",
        "path_disclosure": "not_allowed",
        "filename_disclosure": "not_allowed",
        "parent_folder_disclosure": "not_allowed",
        "media_decode": "not_executed",
        "media_probe": "not_executed",
        "media_scan": "not_executed",
        "transcription": "not_executed",
        "thumbnail": "not_generated",
        "waveform": "not_generated",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
        "database": "not_touched",
        "docker": "not_touched",
        "alembic": "not_touched",
        "stripe": "not_touched",
        "ai_jobs": "not_touched",
        "credits_ledger": "not_touched",
    }
