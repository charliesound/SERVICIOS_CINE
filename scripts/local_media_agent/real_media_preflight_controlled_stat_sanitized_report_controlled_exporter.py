from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import os
from pathlib import Path
from typing import Any, Mapping


PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.IMPLEMENTATION.GATE.V1"
)
IMPLEMENTATION_VERSION = "v1"
EXPORTER_RECORD_ID = "controlled_stat_sanitized_report_controlled_exporter_001"
EXPORTER_HANDLE = "CONTROLLED_STAT_SANITIZED_REPORT_CONTROLLED_EXPORTER_HANDLE_001"
FIXED_SANITIZED_SELECTION_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
EXPECTED_TITLE = "# CID Local Media Agent — Controlled Stat Implementation Sanitized Report"
ARTIFACT_TYPE = "controlled_sanitized_markdown_report"
ARTIFACT_FORMAT = "markdown_utf8"
ALLOWED_SUFFIX = ".md"


@dataclass(frozen=True)
class ControlledSanitizedReportExportResult:
    phase: str
    implementation_version: str
    exporter_record_id: str
    exporter_handle: str
    artifact_type: str
    artifact_format: str
    output_path: str
    output_filename: str
    export_opt_in: bool
    export_requested: bool
    export_performed: bool
    artifact_created_on_disk: bool
    bytes_intended: int
    bytes_written: int
    content_sha256_before_write: str
    content_sha256_after_write: str
    path_boundary: str
    overwrite_policy: str
    verification_status: str
    safety_flags: Mapping[str, bool]
    errors: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safety_flags(*, file_write_performed: bool = False, artifact_created: bool = False, path_violation: bool = False) -> dict[str, bool]:
    return {
        "real_media_access_performed": False,
        "scanner_execution_performed": False,
        "ffprobe_execution_performed": False,
        "ffmpeg_execution_performed": False,
        "external_process_execution_performed": False,
        "network_access_performed": False,
        "saas_or_database_access_performed": False,
        "directory_creation_performed": False,
        "file_write_performed": file_write_performed,
        "artifact_created_on_disk": artifact_created,
        "overwrite_performed": False,
        "path_boundary_violation_detected": path_violation,
    }


def _result(
    *,
    output_path: str,
    output_filename: str = "",
    export_opt_in: bool,
    export_requested: bool = True,
    export_performed: bool = False,
    artifact_created_on_disk: bool = False,
    bytes_intended: int = 0,
    bytes_written: int = 0,
    content_sha256_before_write: str = "",
    content_sha256_after_write: str = "",
    path_boundary: str = "NOT_VERIFIED",
    verification_status: str = "FAILED_CLOSED",
    errors: tuple[str, ...] = (),
) -> ControlledSanitizedReportExportResult:
    return ControlledSanitizedReportExportResult(
        phase=PHASE_ID,
        implementation_version=IMPLEMENTATION_VERSION,
        exporter_record_id=EXPORTER_RECORD_ID,
        exporter_handle=EXPORTER_HANDLE,
        artifact_type=ARTIFACT_TYPE,
        artifact_format=ARTIFACT_FORMAT,
        output_path=output_path,
        output_filename=output_filename,
        export_opt_in=export_opt_in,
        export_requested=export_requested,
        export_performed=export_performed,
        artifact_created_on_disk=artifact_created_on_disk,
        bytes_intended=bytes_intended,
        bytes_written=bytes_written,
        content_sha256_before_write=content_sha256_before_write,
        content_sha256_after_write=content_sha256_after_write,
        path_boundary=path_boundary,
        overwrite_policy="NO_OVERWRITE",
        verification_status=verification_status,
        safety_flags=_safety_flags(
            file_write_performed=export_performed,
            artifact_created=artifact_created_on_disk,
            path_violation=path_boundary == "VIOLATION",
        ),
        errors=errors,
    )


def _fail(output_path: str, export_opt_in: bool, error: str, *, path_violation: bool = False) -> ControlledSanitizedReportExportResult:
    return _result(
        output_path=output_path,
        export_opt_in=export_opt_in,
        path_boundary="VIOLATION" if path_violation else "NOT_VERIFIED",
        errors=(error,),
    )


def _validate_markdown(markdown_text: object) -> tuple[bytes | None, str | None]:
    if not isinstance(markdown_text, str):
        return None, "markdown text must be a string"
    if not markdown_text.strip():
        return None, "markdown text must not be empty"
    if EXPECTED_TITLE not in markdown_text:
        return None, "markdown text is not the validated sanitized report"
    if FIXED_SANITIZED_SELECTION_TOKEN not in markdown_text:
        return None, "fixed sanitized selection token is missing"
    if "LOCAL_OPERATOR_TOKEN" in markdown_text:
        return None, "markdown text contains an unsanitized operator token marker"

    try:
        return markdown_text.encode("utf-8"), None
    except UnicodeEncodeError:
        return None, "markdown text cannot be encoded as UTF-8"


def _validate_output_path(output_path: object) -> tuple[Path | None, str | None, bool]:
    if not isinstance(output_path, (str, Path)):
        return None, "output path must be text or Path", False

    path_text = str(output_path).strip()
    if not path_text:
        return None, "output path must not be empty", False
    if path_text.startswith("~"):
        return None, "output path must not be home-relative", True
    if path_text.startswith("\\\\"):
        return None, "output path must not be UNC-like", True
    if ":" in path_text:
        return None, "output path must not be drive-like", True
    if path_text.startswith("/" + "mnt" + "/"):
        return None, "output path must not be mount-like", True

    candidate = Path(path_text)
    if any(part in {".", ".."} for part in candidate.parts):
        return None, "output path must not contain traversal or dot segments", True
    if any(part.startswith("$") for part in candidate.parts):
        return None, "output path must not be environment-like", True
    if candidate.suffix != ALLOWED_SUFFIX:
        return None, "output path must target a Markdown file", False

    parent = candidate.parent
    if not parent.exists():
        return None, "output parent directory does not exist", False
    if not parent.is_dir():
        return None, "output parent is not a directory", False
    if candidate.exists():
        if candidate.is_dir():
            return None, "output path targets a directory", False
        return None, "output file already exists", False

    resolved_parent = parent.resolve()
    resolved_candidate = candidate.resolve(strict=False)
    try:
        resolved_candidate.relative_to(resolved_parent)
    except ValueError:
        return None, "output path escapes parent directory", True

    return resolved_candidate, None, False


def export_controlled_sanitized_markdown_report(
    markdown_text: object,
    output_path: object,
    export_opt_in: bool,
) -> ControlledSanitizedReportExportResult:
    output_text = "" if output_path is None else str(output_path)

    if export_opt_in is not True:
        return _fail(output_text, bool(export_opt_in), "explicit export opt-in is required")

    payload, markdown_error = _validate_markdown(markdown_text)
    if markdown_error is not None or payload is None:
        return _fail(output_text, export_opt_in, markdown_error or "markdown text is invalid")

    target_path, path_error, path_violation = _validate_output_path(output_path)
    if path_error is not None or target_path is None:
        return _fail(output_text, export_opt_in, path_error or "output path is invalid", path_violation=path_violation)

    before_hash = hashlib.sha256(payload).hexdigest()
    descriptor = getattr(os, "open")(
        str(target_path),
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        getattr(os, "write")(descriptor, payload)
    finally:
        os.close(descriptor)

    written_payload = target_path.read_bytes()
    after_hash = hashlib.sha256(written_payload).hexdigest()

    if len(written_payload) != len(payload):
        return _result(
            output_path=str(target_path),
            output_filename=target_path.name,
            export_opt_in=export_opt_in,
            bytes_intended=len(payload),
            bytes_written=len(written_payload),
            content_sha256_before_write=before_hash,
            content_sha256_after_write=after_hash,
            errors=("bytes written differ from bytes intended",),
        )
    if after_hash != before_hash:
        return _result(
            output_path=str(target_path),
            output_filename=target_path.name,
            export_opt_in=export_opt_in,
            bytes_intended=len(payload),
            bytes_written=len(written_payload),
            content_sha256_before_write=before_hash,
            content_sha256_after_write=after_hash,
            errors=("content hash after write differs from content hash before write",),
        )

    return _result(
        output_path=str(target_path),
        output_filename=target_path.name,
        export_opt_in=export_opt_in,
        export_performed=True,
        artifact_created_on_disk=True,
        bytes_intended=len(payload),
        bytes_written=len(written_payload),
        content_sha256_before_write=before_hash,
        content_sha256_after_write=after_hash,
        path_boundary="INSIDE_EXISTING_PARENT_DIRECTORY",
        verification_status="VERIFIED",
    )


def describe_controlled_sanitized_report_export_boundary() -> Mapping[str, str]:
    return {
        "record_id": EXPORTER_RECORD_ID,
        "handle": EXPORTER_HANDLE,
        "phase": PHASE_ID,
        "input_mode": "validated_sanitized_markdown_text_only",
        "output_mode": "controlled_markdown_utf8_file_only",
        "export_opt_in": "required",
        "directory_creation": "not_performed",
        "overwrite": "not_performed",
        "renderer_modification": "not_performed",
        "cli_integration": "not_performed",
        "real_media_access": "not_performed",
        "scanner_execution": "not_performed",
        "ffprobe_execution": "not_performed",
        "ffmpeg_execution": "not_performed",
        "external_process_execution": "not_performed",
        "network_access": "not_performed",
        "saas_access": "not_performed",
        "database_access": "not_performed",
        "docker_access": "not_performed",
        "alembic_access": "not_performed",
        "stripe_access": "not_performed",
        "ai_jobs_access": "not_performed",
        "credits_ledger_access": "not_performed",
    }


__all__ = [
    "ALLOWED_SUFFIX",
    "ARTIFACT_FORMAT",
    "ARTIFACT_TYPE",
    "ControlledSanitizedReportExportResult",
    "EXPORTER_HANDLE",
    "EXPORTER_RECORD_ID",
    "FIXED_SANITIZED_SELECTION_TOKEN",
    "PHASE_ID",
    "describe_controlled_sanitized_report_export_boundary",
    "export_controlled_sanitized_markdown_report",
]
