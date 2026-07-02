"""Non-executing controlled stat code skeleton for CID Local Media Agent.

This module deliberately contains no filesystem, media, scanner, subprocess,
or SaaS runtime execution. It only defines pure data shapes and planning helpers
for a later controlled implementation gate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping


BOUNDARY_HANDLE = "CODE_SKELETON_HANDLE_001"
READINESS_RECORD_ID = "code_skeleton_readiness_001"
SKELETON_RECORD_ID = "code_skeleton_001"
SANITIZED_SELECTION_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
NOT_EXECUTED = "not_executed"
NOT_ACCESSED = "not_accessed"
NOT_OPENED = "not_opened"
NOT_READ = "not_read"
NOT_RECORDED = "not_recorded"


@dataclass(frozen=True)
class ControlledStatSkeletonInput:
    """Sanitized control input for a later controlled stat implementation."""

    input_record_id: str
    sanitized_selection_token: str
    manual_confirmation_handle: str
    isolated_boundary_handle: str
    generic_file_category: str = "generic_video_file"
    single_file_status: str = "single_file_claimed"


@dataclass(frozen=True)
class ControlledStatSkeletonPlan:
    """Non-executing plan shape returned by the skeleton."""

    skeleton_record_id: str
    boundary_handle: str
    input_record_id: str
    sanitized_selection_token: str
    generic_file_category: str
    single_file_status: str
    stat_status: str
    access_status: str
    file_open_status: str
    file_bytes_status: str
    filesystem_metadata_status: str
    file_size_status: str
    timestamp_status: str
    hash_status: str
    ffmpeg_status: str
    ffprobe_status: str
    scanner_status: str
    saas_status: str
    verdict: str


def build_non_executing_controlled_stat_plan(
    control_input: ControlledStatSkeletonInput,
) -> ControlledStatSkeletonPlan:
    """Build a sanitized non-executing controlled stat plan.

    The function performs no I/O and intentionally returns only conservative
    status fields for a future implementation gate.
    """

    return ControlledStatSkeletonPlan(
        skeleton_record_id=SKELETON_RECORD_ID,
        boundary_handle=BOUNDARY_HANDLE,
        input_record_id=control_input.input_record_id,
        sanitized_selection_token=control_input.sanitized_selection_token,
        generic_file_category=control_input.generic_file_category,
        single_file_status=control_input.single_file_status,
        stat_status=NOT_EXECUTED,
        access_status=NOT_ACCESSED,
        file_open_status=NOT_OPENED,
        file_bytes_status=NOT_READ,
        filesystem_metadata_status=NOT_READ,
        file_size_status=NOT_RECORDED,
        timestamp_status=NOT_RECORDED,
        hash_status=NOT_RECORDED,
        ffmpeg_status=NOT_EXECUTED,
        ffprobe_status=NOT_EXECUTED,
        scanner_status=NOT_EXECUTED,
        saas_status="no_saas_integration",
        verdict="code_skeleton_plan_without_runtime_stat_open_or_metadata_read",
    )


def redact_controlled_stat_plan(plan: ControlledStatSkeletonPlan) -> dict[str, str]:
    """Return a sanitized dictionary representation of the plan."""

    redacted = asdict(plan)
    redacted["sanitized_selection_token"] = SANITIZED_SELECTION_TOKEN
    return redacted


def describe_safety_boundary() -> Mapping[str, str]:
    """Describe the static non-execution boundary for tests and docs."""

    return {
        "filesystem_stat": NOT_EXECUTED,
        "file_access": NOT_ACCESSED,
        "file_open": NOT_OPENED,
        "file_bytes": NOT_READ,
        "filesystem_metadata": NOT_READ,
        "file_size": NOT_RECORDED,
        "timestamps": NOT_RECORDED,
        "hashes": NOT_RECORDED,
        "ffmpeg": NOT_EXECUTED,
        "ffprobe": NOT_EXECUTED,
        "scanner": NOT_EXECUTED,
        "saas": "no_saas_integration",
    }
