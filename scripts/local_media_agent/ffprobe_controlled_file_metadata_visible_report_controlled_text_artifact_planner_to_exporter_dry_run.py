"""Controlled dry-run planner-to-exporter bridge for visible report text artifacts.

This module is intentionally pure. It validates a planner result and returns an
exporter-facing dry-run decision without writing files, creating directories, or
creating artifacts on disk.
"""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
from typing import Any


CONTROLLED_VISIBLE_REPORT_SUFFIX = ".controlled_visible_report.txt"

_REQUIRED_PLANNER_RESULT_FIELDS = frozenset(
    {
        "controlled_export_root",
        "suggested_filename",
        "planned_artifact_path",
        "artifact_format",
        "content_sha256",
        "write_performed",
        "artifact_created_on_disk",
        "path_boundary",
        "safety_flags",
    }
)


class ControlledTextArtifactPlannerToExporterDryRunError(ValueError):
    """Raised when a planner result cannot be accepted by the dry-run bridge."""


def plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
    *,
    visible_report_text: str,
    planner_result: Mapping[str, Any],
    dry_run: bool = True,
    write_requested: bool = False,
    caller_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a planner result and return a controlled exporter-facing dry-run result.

    The function never writes files, never creates directories, and never creates
    artifacts on disk. It only validates input and returns structured metadata
    that a later exporter implementation can use as a safe dry-run decision.
    """

    if dry_run is not True:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "Only dry-run mode is supported by this controlled implementation."
        )

    if write_requested is not False:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "write_requested must remain false in controlled dry-run mode."
        )

    normalized_visible_report_text = _require_non_empty_text(
        visible_report_text,
        field_name="visible_report_text",
    )

    if not isinstance(planner_result, Mapping):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result must be a mapping."
        )

    missing_fields = sorted(_REQUIRED_PLANNER_RESULT_FIELDS.difference(planner_result))
    if missing_fields:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            f"planner_result missing required fields: {', '.join(missing_fields)}"
        )

    suggested_filename = _require_non_empty_text(
        planner_result["suggested_filename"],
        field_name="suggested_filename",
    )
    if not suggested_filename.endswith(CONTROLLED_VISIBLE_REPORT_SUFFIX):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "suggested_filename must use the controlled visible report suffix."
        )

    planned_artifact_path = _require_non_empty_text(
        planner_result["planned_artifact_path"],
        field_name="planned_artifact_path",
    )
    if suggested_filename not in planned_artifact_path:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planned_artifact_path must include the suggested filename."
        )

    artifact_format = _require_non_empty_text(
        planner_result["artifact_format"],
        field_name="artifact_format",
    )

    planner_content_sha256 = _require_non_empty_text(
        planner_result["content_sha256"],
        field_name="content_sha256",
    )
    expected_content_sha256 = _sha256_text(normalized_visible_report_text)
    if planner_content_sha256 != expected_content_sha256:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result content hash does not match visible_report_text."
        )

    if planner_result["write_performed"] is not False:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result must not claim prior write execution."
        )

    if planner_result["artifact_created_on_disk"] is not False:
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result must not claim prior artifact creation."
        )

    path_boundary = planner_result["path_boundary"]
    if not _is_safe_path_boundary(path_boundary):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result path_boundary is not accepted as safe."
        )

    safety_flags = planner_result["safety_flags"]
    if not _all_safety_flags_false(safety_flags):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "planner_result safety_flags must all be false."
        )

    sanitized_caller_context = _sanitize_caller_context(caller_context)

    return {
        "planned_artifact_path": planned_artifact_path,
        "suggested_filename": suggested_filename,
        "artifact_format": artifact_format,
        "content_sha256": expected_content_sha256,
        "dry_run": True,
        "write_requested": False,
        "write_performed": False,
        "artifact_created_on_disk": False,
        "path_boundary": path_boundary,
        "safety_flags": dict(safety_flags),
        "exporter_decision": "CONTROLLED_DRY_RUN_ACCEPTED",
        "human_visible_summary": (
            "Controlled dry-run accepted. Planned artifact path is available for "
            "human review. No file was written and no artifact was created on disk."
        ),
        "caller_context": sanitized_caller_context,
    }


def _require_non_empty_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            f"{field_name} must be a string."
        )

    if not value.strip():
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            f"{field_name} must not be empty."
        )

    return value


def _sha256_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _all_safety_flags_false(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    if not value:
        return False

    return all(flag_value is False for flag_value in value.values())


def _is_safe_path_boundary(value: Any) -> bool:
    accepted_safe_values = {
        "CONTROLLED_EXPORT_ROOT_BOUNDARY_OK",
        "controlled_export_root_boundary_ok",
        "safe",
    }

    if isinstance(value, str):
        return value in accepted_safe_values

    if isinstance(value, Mapping):
        if not value:
            return False

        return all(boundary_value in accepted_safe_values for boundary_value in value.values())

    return False


def _sanitize_caller_context(value: Mapping[str, Any] | None) -> dict[str, str]:
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise ControlledTextArtifactPlannerToExporterDryRunError(
            "caller_context must be a mapping when provided."
        )

    sanitized: dict[str, str] = {}
    for key, context_value in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ControlledTextArtifactPlannerToExporterDryRunError(
                "caller_context keys must be non-empty strings."
            )

        if context_value is None:
            continue

        if isinstance(context_value, str):
            sanitized[key] = context_value
        elif isinstance(context_value, bool | int | float):
            sanitized[key] = str(context_value)
        else:
            raise ControlledTextArtifactPlannerToExporterDryRunError(
                "caller_context values must be scalar and non-sensitive."
            )

    return sanitized
