"""Pure controlled text artifact export path planner.

This module is intentionally side-effect free.

It validates a controlled export root and a controlled visible report text
artifact descriptor, then returns a planned path descriptor.

It performs planning only. It has no filesystem, process, network, SaaS,
database, installer, or client-facing side effects.
"""

from __future__ import annotations

from pathlib import PurePath, PurePosixPath, PureWindowsPath
from typing import Any, Mapping

CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX = ".controlled_visible_report.txt"
CONTROLLED_PATH_BOUNDARY = "controlled_export_root"


class ControlledTextArtifactExportPathPlannerError(ValueError):
    """Raised when controlled export path planning input is unsafe."""


def _as_non_empty_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ControlledTextArtifactExportPathPlannerError(f"{field_name} must be text")

    stripped = value.strip()
    if not stripped:
        raise ControlledTextArtifactExportPathPlannerError(f"{field_name} must not be empty")

    return stripped


def _reject_path_separators(value: str, *, field_name: str) -> None:
    if "/" in value or "\\" in value:
        raise ControlledTextArtifactExportPathPlannerError(
            f"{field_name} must be a filename, not a path"
        )


def _reject_drive_or_unc(value: str, *, field_name: str) -> None:
    windows_path = PureWindowsPath(value)

    if windows_path.drive:
        raise ControlledTextArtifactExportPathPlannerError(
            f"{field_name} must not contain a drive prefix"
        )

    if value.startswith("\\\\"):
        raise ControlledTextArtifactExportPathPlannerError(
            f"{field_name} must not be a UNC path"
        )


def _validate_controlled_export_root(controlled_export_root: object) -> PurePath:
    root_text = _as_non_empty_text(
        controlled_export_root,
        field_name="controlled_export_root",
    )

    _reject_drive_or_unc(root_text, field_name="controlled_export_root")

    root_path = PurePosixPath(root_text)

    if any(part in {"..", "."} for part in root_path.parts):
        raise ControlledTextArtifactExportPathPlannerError(
            "controlled_export_root must not contain traversal or dot segments"
        )

    if root_path.name.startswith("."):
        raise ControlledTextArtifactExportPathPlannerError(
            "controlled_export_root must not target a hidden path"
        )

    return root_path


def _validate_suggested_filename(suggested_filename: object) -> str:
    filename = _as_non_empty_text(
        suggested_filename,
        field_name="suggested_filename",
    )

    _reject_path_separators(filename, field_name="suggested_filename")
    _reject_drive_or_unc(filename, field_name="suggested_filename")

    if filename in {".", ".."}:
        raise ControlledTextArtifactExportPathPlannerError(
            "suggested_filename must not be a traversal segment"
        )

    if ".." in filename:
        raise ControlledTextArtifactExportPathPlannerError(
            "suggested_filename must not contain traversal"
        )

    if filename.startswith("."):
        raise ControlledTextArtifactExportPathPlannerError(
            "suggested_filename must not be a hidden dotfile"
        )

    if not filename.endswith(CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX):
        raise ControlledTextArtifactExportPathPlannerError(
            "suggested_filename must end with .controlled_visible_report.txt"
        )

    return filename


def _validate_descriptor(descriptor: object) -> Mapping[str, Any]:
    if not isinstance(descriptor, Mapping):
        raise ControlledTextArtifactExportPathPlannerError(
            "controlled descriptor must be a mapping"
        )

    if "suggested_filename" not in descriptor:
        raise ControlledTextArtifactExportPathPlannerError(
            "controlled descriptor must include suggested_filename"
        )

    return descriptor


def plan_controlled_text_artifact_export_path(
    *,
    controlled_export_root: str,
    controlled_descriptor: Mapping[str, Any],
) -> dict[str, Any]:
    """Return a controlled planned path descriptor without filesystem effects."""

    root_path = _validate_controlled_export_root(controlled_export_root)
    descriptor = _validate_descriptor(controlled_descriptor)
    filename = _validate_suggested_filename(descriptor["suggested_filename"])

    planned_path = root_path / filename

    try:
        planned_path.relative_to(root_path)
    except ValueError as exc:
        raise ControlledTextArtifactExportPathPlannerError(
            "planned_artifact_path must stay inside controlled_export_root"
        ) from exc

    return {
        "controlled_export_root": str(root_path),
        "suggested_filename": filename,
        "planned_artifact_path": str(planned_path),
        "artifact_format": "controlled_visible_report_text",
        "content_sha256": descriptor.get("content_sha256"),
        "write_performed": False,
        "artifact_created_on_disk": False,
        "path_boundary": CONTROLLED_PATH_BOUNDARY,
        "safety_flags": {
            "real_media_access_performed": False,
            "scanner_execution_performed": False,
            "ffprobe_execution_performed": False,
            "ffmpeg_execution_performed": False,
            "subprocess_execution_performed": False,
            "network_access_performed": False,
            "saas_or_database_access_performed": False,
            "file_write_performed": False,
            "directory_creation_performed": False,
            "artifact_created_on_disk": False,
        },
    }


__all__ = [
    "CONTROLLED_PATH_BOUNDARY",
    "CONTROLLED_VISIBLE_REPORT_TEXT_SUFFIX",
    "ControlledTextArtifactExportPathPlannerError",
    "plan_controlled_text_artifact_export_path",
]
