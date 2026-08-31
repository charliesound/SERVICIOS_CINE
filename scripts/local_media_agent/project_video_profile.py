"""CID PROJECT_VIDEO_PROFILE V1 exact local authority."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from scripts.local_media_agent.local_project import (
    atomic_write_json,
    load_project,
    project_video_profile_path,
    validate_project_id,
)

PROFILE_FORMAT = "CID_PROJECT_VIDEO_PROFILE"
PROFILE_VERSION = 1
NOT_CONFIRMED = "NOT_CONFIRMED"
CONFIRMED = "CONFIRMED"
USER_CONFIRMED = "USER_CONFIRMED"
CID_RECOMMENDED_CONFIRMED = "CID_RECOMMENDED_CONFIRMED"

CID_PROJECT_VIDEO_PROFILE_REQUIRED = "CID_PROJECT_VIDEO_PROFILE_REQUIRED"
CID_PROJECT_VIDEO_PROFILE_NOT_CONFIRMED = "CID_PROJECT_VIDEO_PROFILE_NOT_CONFIRMED"
CID_PROJECT_VIDEO_PROFILE_PROJECT_MISMATCH = "CID_PROJECT_VIDEO_PROFILE_PROJECT_MISMATCH"
CID_PROJECT_VIDEO_PROFILE_INVALID = "CID_PROJECT_VIDEO_PROFILE_INVALID"

SUPPORTED_FRAME_RATES = (
    Fraction(24000, 1001), Fraction(24), Fraction(25), Fraction(30000, 1001),
    Fraction(30), Fraction(50), Fraction(60000, 1001), Fraction(60),
)


class ProjectVideoProfileError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def parse_supported_frame_rate(value: object) -> Fraction:
    if isinstance(value, bool) or isinstance(value, float):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    try:
        rate = value if isinstance(value, Fraction) else Fraction(str(value))
    except (ValueError, ZeroDivisionError, TypeError) as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc
    if rate not in SUPPORTED_FRAME_RATES:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    return rate


def frame_duration_for_rate(value: object) -> Fraction:
    rate = parse_supported_frame_rate(value)
    return Fraction(rate.denominator, rate.numerator)


def fcpxml_frame_duration(value: object) -> str:
    return f"{frame_duration_for_rate(value)}s"


def analyze_source_video_metadata(
    metadata: dict[str, Any] | Iterable[dict[str, Any]],
) -> dict[str, Any]:
    results = metadata.get("results", []) if isinstance(metadata, dict) else metadata
    rates: Counter[str] = Counter()
    resolutions: Counter[str] = Counter()
    considered = vfr = unknown_rate = unknown_resolution = 0
    for item in results if isinstance(results, Iterable) else []:
        if not isinstance(item, dict) or not isinstance(item.get("video"), dict):
            continue
        considered += 1
        video = item["video"]
        rate_info = video.get("frame_rate")
        if isinstance(rate_info, dict) and rate_info.get("variable") is True:
            vfr += 1
        rate = _metadata_rate(rate_info)
        if rate is None:
            unknown_rate += 1
        else:
            rates[_rate_text(rate)] += 1
        width, height = video.get("width"), video.get("height")
        if _positive_int(width) and _positive_int(height):
            resolutions[f"{width}x{height}"] += 1
        else:
            unknown_resolution += 1
    return {
        "video_clips_considered": considered,
        "vfr_clip_count": vfr,
        "unknown_rate_count": unknown_rate,
        "unknown_resolution_count": unknown_resolution,
        "frame_rate_distribution": dict(sorted(rates.items())),
        "resolution_distribution": dict(sorted(resolutions.items())),
    }


def build_recommendation(summary: dict[str, Any]) -> dict[str, Any]:
    unavailable = {"available": False, "timeline_frame_rate": None, "resolution": None}
    total = summary.get("video_clips_considered")
    if not isinstance(total, int) or total <= 0 or summary.get("vfr_clip_count", 0) > 0:
        return unavailable
    distribution = summary.get("frame_rate_distribution")
    if not isinstance(distribution, dict) or not distribution:
        return unavailable
    ranked = sorted(distribution.items(), key=lambda item: (-item[1], item[0]))
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return unavailable
    dominant_text, dominant_count = ranked[0]
    try:
        dominant = parse_supported_frame_rate(dominant_text)
    except ProjectVideoProfileError:
        return unavailable
    if dominant_count * 100 < total * 70:
        return unavailable
    incompatible = 0
    for rate_text, count in ranked[1:]:
        try:
            secondary = parse_supported_frame_rate(rate_text)
        except ProjectVideoProfileError:
            incompatible += count
            continue
        if secondary / dominant not in (Fraction(2),):
            incompatible += count
    if incompatible * 100 > total * 10:
        return unavailable
    if summary.get("unknown_rate_count", 0) > 0:
        return unavailable
    resolution = None
    resolution_distribution = summary.get("resolution_distribution")
    if isinstance(resolution_distribution, dict) and resolution_distribution:
        resolution_text, count = sorted(
            resolution_distribution.items(), key=lambda item: (-item[1], item[0])
        )[0]
        if count * 100 >= total * 80:
            width, height = resolution_text.split("x", 1)
            resolution = {"width": int(width), "height": int(height)}
    return {
        "available": True,
        "timeline_frame_rate": _rational_object(dominant),
        "resolution": resolution,
    }


def create_project_video_profile(
    project_id: str,
    source_analysis_summary: dict[str, Any],
    *,
    local_appdata: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    load_project(project_id, local_appdata=local_appdata)
    timestamp = _timestamp(now)
    profile = {
        "format": PROFILE_FORMAT,
        "version": PROFILE_VERSION,
        "project_id": project_id,
        "profile_revision": 1,
        "confirmation_status": NOT_CONFIRMED,
        "timeline_frame_rate": {"numerator": None, "denominator": None},
        "frame_duration": {"numerator": None, "denominator": None},
        "resolution": {"width": None, "height": None},
        "decision_authority": None,
        "confirmed_by_role": None,
        "confirmed_at": None,
        "recommendation": build_recommendation(source_analysis_summary),
        "source_analysis_summary": source_analysis_summary,
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    save_project_video_profile(profile, local_appdata=local_appdata)
    return profile


def refresh_project_video_analysis(
    project_id: str,
    source_analysis_summary: dict[str, Any],
    *,
    local_appdata: str | Path | None = None,
) -> dict[str, Any]:
    """Refresh detected-source facts without changing confirmed project choices."""
    try:
        profile = load_project_video_profile(project_id, local_appdata=local_appdata)
    except ProjectVideoProfileError as exc:
        if exc.code != CID_PROJECT_VIDEO_PROFILE_REQUIRED:
            raise
        return create_project_video_profile(
            project_id, source_analysis_summary, local_appdata=local_appdata
        )
    profile["source_analysis_summary"] = source_analysis_summary
    profile["recommendation"] = build_recommendation(source_analysis_summary)
    profile["updated_at"] = _timestamp()
    save_project_video_profile(profile, local_appdata=local_appdata)
    return profile


def update_project_video_configuration(
    project_id: str,
    timeline_frame_rate: object,
    resolution: tuple[int, int] | dict[str, int],
    *,
    local_appdata: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    profile = load_project_video_profile(project_id, local_appdata=local_appdata)
    rate = parse_supported_frame_rate(timeline_frame_rate)
    width, height = _resolution_values(resolution)
    changed = (
        profile["timeline_frame_rate"] != _rational_object(rate)
        or profile["resolution"] != {"width": width, "height": height}
    )
    if not changed:
        return profile
    if changed and profile["confirmation_status"] == CONFIRMED:
        profile["profile_revision"] += 1
    profile["timeline_frame_rate"] = _rational_object(rate)
    profile["frame_duration"] = _rational_object(Fraction(rate.denominator, rate.numerator))
    profile["resolution"] = {"width": width, "height": height}
    profile["confirmation_status"] = NOT_CONFIRMED
    profile["decision_authority"] = None
    profile["confirmed_by_role"] = None
    profile["confirmed_at"] = None
    profile["updated_at"] = _timestamp(now)
    save_project_video_profile(profile, local_appdata=local_appdata)
    return profile


def confirm_project_video_profile(
    project_id: str,
    *,
    decision_authority: str,
    confirmed_by_role: str,
    local_appdata: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    profile = load_project_video_profile(project_id, local_appdata=local_appdata)
    if decision_authority not in (USER_CONFIRMED, CID_RECOMMENDED_CONFIRMED):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    if not isinstance(confirmed_by_role, str) or not confirmed_by_role.strip():
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    _profile_rate(profile)
    _resolution_values(profile["resolution"])
    if decision_authority == CID_RECOMMENDED_CONFIRMED:
        recommendation = profile.get("recommendation")
        if (
            not isinstance(recommendation, dict)
            or recommendation.get("available") is not True
            or recommendation.get("timeline_frame_rate") != profile["timeline_frame_rate"]
            or recommendation.get("resolution") != profile["resolution"]
        ):
            raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    timestamp = _timestamp(now)
    profile["confirmation_status"] = CONFIRMED
    profile["decision_authority"] = decision_authority
    profile["confirmed_by_role"] = confirmed_by_role.strip()
    profile["confirmed_at"] = timestamp
    profile["updated_at"] = timestamp
    save_project_video_profile(profile, local_appdata=local_appdata)
    return profile


def postpone_project_video_profile(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    profile = load_project_video_profile(project_id, local_appdata=local_appdata)
    if profile["confirmation_status"] == CONFIRMED:
        profile["profile_revision"] += 1
    profile.update(
        confirmation_status=NOT_CONFIRMED,
        decision_authority=None,
        confirmed_by_role=None,
        confirmed_at=None,
        updated_at=_timestamp(),
    )
    save_project_video_profile(profile, local_appdata=local_appdata)
    return profile


def save_project_video_profile(
    profile: dict[str, Any], *, local_appdata: str | Path | None = None
) -> None:
    _validate_profile(profile)
    load_project(profile["project_id"], local_appdata=local_appdata)
    atomic_write_json(project_video_profile_path(profile["project_id"], local_appdata), profile)


def load_project_video_profile(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    validate_project_id(project_id)
    path = project_video_profile_path(project_id, local_appdata)
    if not path.is_file():
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_REQUIRED)
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc
    _validate_profile(profile, expected_project_id=project_id)
    return profile


def require_confirmed_project_video_profile(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    profile = load_project_video_profile(project_id, local_appdata=local_appdata)
    if profile["confirmation_status"] != CONFIRMED:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_NOT_CONFIRMED)
    return profile


def profile_frame_duration_text(profile: dict[str, Any]) -> str:
    duration = profile.get("frame_duration")
    if not isinstance(duration, dict):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    try:
        value = Fraction(duration["numerator"], duration["denominator"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc
    return f"{value}s"


def _validate_profile(profile: object, expected_project_id: str | None = None) -> None:
    if not isinstance(profile, dict):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    required = {
        "format", "version", "project_id", "profile_revision", "confirmation_status",
        "timeline_frame_rate", "frame_duration", "resolution", "decision_authority",
        "confirmed_by_role", "confirmed_at", "recommendation", "source_analysis_summary",
        "created_at", "updated_at",
    }
    if set(profile) != required or "project_name" in profile:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    if profile.get("format") != PROFILE_FORMAT or profile.get("version") != PROFILE_VERSION:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    try:
        identifier = validate_project_id(profile.get("project_id"))
    except ValueError as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc
    if expected_project_id is not None and identifier != expected_project_id:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_PROJECT_MISMATCH)
    revision = profile.get("profile_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    status = profile.get("confirmation_status")
    if status not in (NOT_CONFIRMED, CONFIRMED):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    resolution = profile.get("resolution")
    if not isinstance(resolution, dict) or set(resolution) != {"width", "height"}:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    if resolution != {"width": None, "height": None}:
        _resolution_values(resolution)
    if not isinstance(profile.get("recommendation"), dict) or not isinstance(
        profile.get("source_analysis_summary"), dict
    ):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    timeline_rate = profile.get("timeline_frame_rate")
    if not isinstance(timeline_rate, dict) or set(timeline_rate) != {
        "numerator", "denominator"
    }:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    configured = timeline_rate.get("numerator") is not None
    if configured:
        rate = _profile_rate(profile)
        if profile.get("frame_duration") != _rational_object(Fraction(rate.denominator, rate.numerator)):
            raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    elif profile.get("frame_duration") != {"numerator": None, "denominator": None}:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    if status == CONFIRMED:
        if profile.get("decision_authority") not in (USER_CONFIRMED, CID_RECOMMENDED_CONFIRMED):
            raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
        if (
            not configured
            or resolution == {"width": None, "height": None}
            or not profile.get("confirmed_by_role")
            or not profile.get("confirmed_at")
        ):
            raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    elif any(profile.get(key) is not None for key in ("decision_authority", "confirmed_by_role", "confirmed_at")):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    for key in ("created_at", "updated_at"):
        if not isinstance(profile.get(key), str) or not profile[key].endswith("Z"):
            raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)


def _profile_rate(profile: dict[str, Any]) -> Fraction:
    value = profile.get("timeline_frame_rate")
    try:
        return parse_supported_frame_rate(Fraction(value["numerator"], value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc


def _metadata_rate(value: object) -> Fraction | None:
    if not isinstance(value, dict) or value.get("variable") is True:
        return None
    valid: list[Fraction] = []
    for key in ("raw_avg", "raw_frame"):
        try:
            rate = Fraction(str(value.get(key)))
        except (ValueError, ZeroDivisionError):
            continue
        if rate > 0:
            valid.append(rate)
    if not valid or any(rate != valid[0] for rate in valid):
        return None
    return valid[0] if valid[0] in SUPPORTED_FRAME_RATES else None


def _rational_object(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _rate_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _resolution_values(value: tuple[int, int] | dict[str, int]) -> tuple[int, int]:
    try:
        width, height = (value["width"], value["height"]) if isinstance(value, dict) else value
    except (KeyError, TypeError, ValueError) as exc:
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID) from exc
    if not _positive_int(width) or not _positive_int(height):
        raise ProjectVideoProfileError(CID_PROJECT_VIDEO_PROFILE_INVALID)
    return width, height


def _timestamp(value: datetime | None = None) -> str:
    current = value or datetime.now(timezone.utc)
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
