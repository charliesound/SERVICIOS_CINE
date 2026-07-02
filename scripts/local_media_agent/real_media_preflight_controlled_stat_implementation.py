"""Non-executing controlled stat implementation wrapper for CID Local Media Agent.

This module deliberately avoids filesystem, media, scanner, subprocess, and SaaS
runtime execution. It wraps the validated controlled stat skeleton and exposes
only pure planning, redaction, and boundary helpers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from scripts.local_media_agent.real_media_preflight_controlled_stat_code_skeleton import (
    ControlledStatSkeletonInput,
    build_non_executing_controlled_stat_plan,
    describe_safety_boundary,
)


CONTROLLED_STAT_IMPLEMENTATION_HANDLE = "CONTROLLED_STAT_IMPLEMENTATION_HANDLE_001"
CONTROLLED_STAT_IMPLEMENTATION_RECORD_ID = "controlled_stat_implementation_001"
SANITIZED_SELECTION_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
NOT_EXECUTED = "not_executed"
NOT_ACCESSED = "not_accessed"
NOT_OPENED = "not_opened"
NOT_READ = "not_read"
NOT_RECORDED = "not_recorded"


@dataclass(frozen=True)
class ControlledStatImplementationRequest:
    """Sanitized request for a later controlled stat implementation."""

    input_record_id: str
    sanitized_selection_token: str
    manual_confirmation_handle: str
    isolated_boundary_handle: str
    skeleton_handle: str
    generic_file_category: str = "generic_video_file"
    single_file_status: str = "single_file_claimed"


@dataclass(frozen=True)
class ControlledStatImplementationResult:
    """Non-executing controlled implementation result shape."""

    implementation_record_id: str
    implementation_handle: str
    skeleton_handle: str
    input_record_id: str
    sanitized_selection_token: str
    generic_file_category: str
    single_file_status: str
    filesystem_stat_status: str
    file_access_status: str
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


def build_controlled_stat_implementation_result(
    request: ControlledStatImplementationRequest,
) -> ControlledStatImplementationResult:
    """Build a non-executing controlled stat implementation result."""

    skeleton_input = ControlledStatSkeletonInput(
        input_record_id=request.input_record_id,
        sanitized_selection_token=request.sanitized_selection_token,
        manual_confirmation_handle=request.manual_confirmation_handle,
        isolated_boundary_handle=request.isolated_boundary_handle,
        generic_file_category=request.generic_file_category,
        single_file_status=request.single_file_status,
    )
    skeleton_plan = build_non_executing_controlled_stat_plan(skeleton_input)

    return ControlledStatImplementationResult(
        implementation_record_id=CONTROLLED_STAT_IMPLEMENTATION_RECORD_ID,
        implementation_handle=CONTROLLED_STAT_IMPLEMENTATION_HANDLE,
        skeleton_handle=request.skeleton_handle,
        input_record_id=skeleton_plan.input_record_id,
        sanitized_selection_token=skeleton_plan.sanitized_selection_token,
        generic_file_category=skeleton_plan.generic_file_category,
        single_file_status=skeleton_plan.single_file_status,
        filesystem_stat_status=skeleton_plan.stat_status,
        file_access_status=skeleton_plan.access_status,
        file_open_status=skeleton_plan.file_open_status,
        file_bytes_status=skeleton_plan.file_bytes_status,
        filesystem_metadata_status=skeleton_plan.filesystem_metadata_status,
        file_size_status=skeleton_plan.file_size_status,
        timestamp_status=skeleton_plan.timestamp_status,
        hash_status=skeleton_plan.hash_status,
        ffmpeg_status=skeleton_plan.ffmpeg_status,
        ffprobe_status=skeleton_plan.ffprobe_status,
        scanner_status=skeleton_plan.scanner_status,
        saas_status=skeleton_plan.saas_status,
        verdict="controlled_stat_implementation_result_without_stat_open_or_metadata_read",
    )


def redact_controlled_stat_implementation_result(
    result: ControlledStatImplementationResult,
) -> dict[str, str]:
    """Return a sanitized dictionary representation of the implementation result."""

    redacted = asdict(result)
    redacted["sanitized_selection_token"] = SANITIZED_SELECTION_TOKEN
    return redacted


def describe_controlled_stat_implementation_boundary() -> Mapping[str, str]:
    """Describe the static non-execution boundary for this implementation wrapper."""

    skeleton_boundary = describe_safety_boundary()
    return {
        "filesystem_stat": skeleton_boundary["filesystem_stat"],
        "file_access": skeleton_boundary["file_access"],
        "file_open": skeleton_boundary["file_open"],
        "file_bytes": skeleton_boundary["file_bytes"],
        "filesystem_metadata": skeleton_boundary["filesystem_metadata"],
        "file_size": skeleton_boundary["file_size"],
        "timestamps": skeleton_boundary["timestamps"],
        "hashes": skeleton_boundary["hashes"],
        "ffmpeg": skeleton_boundary["ffmpeg"],
        "ffprobe": skeleton_boundary["ffprobe"],
        "scanner": skeleton_boundary["scanner"],
        "saas": skeleton_boundary["saas"],
        "implementation": "non_executing_wrapper",
    }
