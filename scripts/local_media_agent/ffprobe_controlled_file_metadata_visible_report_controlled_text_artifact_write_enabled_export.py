from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping


PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI."
    "VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CONTROLLED."
    "IMPLEMENTATION.V1"
)

IMPLEMENTATION_VERSION = "v1"

ARTIFACT_TYPE = "controlled_visible_report_text"
ARTIFACT_FORMAT = "utf-8 text"
DEFAULT_FILENAME = "controlled_visible_report.controlled.txt"
ALLOWED_EXTENSION = ".controlled.txt"
WRITE_AUTHORIZATION = "CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY"

_ALLOWED_FILENAME_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")


def _empty_safety_flags() -> dict[str, bool]:
    return {
        "real_media_access_performed": False,
        "scanner_execution_performed": False,
        "ffprobe_execution_performed": False,
        "ffmpeg_execution_performed": False,
        "external_process_execution_performed": False,
        "network_access_performed": False,
        "saas_or_database_access_performed": False,
        "directory_creation_performed": False,
        "file_write_performed": False,
        "artifact_created_on_disk": False,
        "overwrite_performed": False,
        "path_boundary_violation_detected": False,
    }


def _base_result(
    *,
    controlled_output_root: str,
    artifact_path: str,
    filename: str,
    extension: str,
    write_authorization: str | None,
    write_requested: bool,
) -> dict[str, Any]:
    return {
        "phase": PHASE_ID,
        "implementation_version": IMPLEMENTATION_VERSION,
        "artifact_type": ARTIFACT_TYPE,
        "artifact_format": ARTIFACT_FORMAT,
        "controlled_output_root": controlled_output_root,
        "artifact_path": artifact_path,
        "filename": filename,
        "extension": extension,
        "write_authorization": write_authorization,
        "write_requested": write_requested,
        "write_performed": False,
        "artifact_created_on_disk": False,
        "bytes_intended": 0,
        "bytes_written": 0,
        "content_sha256_before_write": "",
        "content_sha256_after_write": "",
        "path_boundary": "NOT_VERIFIED",
        "overwrite_policy": "NO_OVERWRITE",
        "verification_status": "NOT_VERIFIED",
        "cleanup_expectation": "FIXTURE_OWNED_OUTPUT_CLEANUP_BY_TEST_OWNER",
        "safety_flags": _empty_safety_flags(),
        "warnings": [],
        "errors": [],
    }


def _fail(
    result: dict[str, Any],
    error: str,
    *,
    path_boundary_violation: bool = False,
) -> dict[str, Any]:
    result["errors"].append(error)
    result["verification_status"] = "FAILED_CLOSED"
    if path_boundary_violation:
        result["path_boundary"] = "VIOLATION"
        result["safety_flags"]["path_boundary_violation_detected"] = True
    return result


def _is_fixture_owned_output_root(path: Path) -> bool:
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        path.relative_to(temp_root)
    except ValueError:
        return False

    parts = set(path.parts)
    return any(part.startswith("pytest-") for part in parts) or "pytest-of-harliesound" in parts


def _validate_filename(filename: str) -> str | None:
    if not filename:
        return "filename is missing"
    if "/" in filename or "\\" in filename:
        return "filename contains separators"
    if ".." in filename:
        return "filename contains parent traversal"
    if filename.startswith("."):
        return "filename begins with a dot"
    if any(char not in _ALLOWED_FILENAME_CHARS for char in filename):
        return "filename contains unsafe characters"
    if not filename.endswith(ALLOWED_EXTENSION):
        return "extension is unsupported"
    if filename != DEFAULT_FILENAME:
        return "filename is unsupported"
    return None


def _encode_visible_report_text(visible_report_text: str) -> bytes:
    return visible_report_text.encode("utf-8")


def export_controlled_visible_report_text_artifact(
    *,
    visible_report_text: str,
    controlled_output_root: str | Path | None,
    filename: str = DEFAULT_FILENAME,
    caller_context: Mapping[str, Any] | None = None,
    write_authorization: str | None = None,
) -> dict[str, Any]:
    del caller_context

    write_requested = write_authorization is not None
    root_display = "" if controlled_output_root is None else str(controlled_output_root)

    result = _base_result(
        controlled_output_root=root_display,
        artifact_path="",
        filename=filename,
        extension=ALLOWED_EXTENSION if filename.endswith(ALLOWED_EXTENSION) else Path(filename).suffix,
        write_authorization=write_authorization,
        write_requested=write_requested,
    )

    if write_authorization is None:
        return _fail(result, "write authorization is missing")
    if write_authorization != WRITE_AUTHORIZATION:
        if write_authorization == "DRY_RUN" or write_authorization == "CONTROLLED_DRY_RUN_ACCEPTED":
            return _fail(result, "write authorization is dry-run-only")
        return _fail(result, "write authorization is unknown")

    if controlled_output_root is None:
        return _fail(result, "controlled output root is missing")

    root = Path(controlled_output_root)

    if str(root).startswith("~"):
        return _fail(result, "candidate path is home-relative", path_boundary_violation=True)

    if any(part.startswith("$") for part in root.parts):
        return _fail(result, "candidate path is environment-derived", path_boundary_violation=True)

    if not root.exists():
        return _fail(result, "controlled output root does not exist")

    if not root.is_dir():
        return _fail(result, "controlled output root is not a directory")

    resolved_root = root.resolve()
    result["controlled_output_root"] = str(resolved_root)

    if not _is_fixture_owned_output_root(resolved_root):
        return _fail(result, "controlled output root is not controlled")

    filename_error = _validate_filename(filename)
    if filename_error:
        return _fail(result, filename_error)

    candidate_path = (resolved_root / filename).resolve()
    result["artifact_path"] = str(candidate_path)

    try:
        candidate_path.relative_to(resolved_root)
    except ValueError:
        return _fail(result, "candidate path escapes controlled output root", path_boundary_violation=True)

    result["path_boundary"] = "INSIDE_CONTROLLED_OUTPUT_ROOT"

    if candidate_path.exists():
        return _fail(result, "target artifact already exists")

    if not isinstance(visible_report_text, str):
        return _fail(result, "content cannot be encoded as UTF-8")

    if visible_report_text == "":
        return _fail(result, "content is empty")

    try:
        payload = _encode_visible_report_text(visible_report_text)
    except UnicodeEncodeError:
        return _fail(result, "content cannot be encoded as UTF-8")

    if not payload:
        return _fail(result, "content is empty")

    before_hash = hashlib.sha256(payload).hexdigest()
    intended_byte_count = len(payload)

    result["bytes_intended"] = intended_byte_count
    result["content_sha256_before_write"] = before_hash

    descriptor = os.open(str(candidate_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, payload)
    finally:
        os.close(descriptor)

    result["write_performed"] = True
    result["artifact_created_on_disk"] = True
    result["safety_flags"]["file_write_performed"] = True
    result["safety_flags"]["artifact_created_on_disk"] = True

    written_payload = candidate_path.read_bytes()
    after_hash = hashlib.sha256(written_payload).hexdigest()

    result["content_sha256_after_write"] = after_hash
    result["bytes_written"] = len(written_payload)

    if result["bytes_written"] != result["bytes_intended"]:
        return _fail(result, "bytes written differ from bytes intended")

    if after_hash != before_hash:
        return _fail(result, "content hash after write differs from content hash before write")

    result["verification_status"] = "VERIFIED"
    return result
