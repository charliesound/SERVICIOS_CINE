"""Project-scoped sanitized SOURCE_VIDEO_PROFILE catalog."""

from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from scripts.local_media_agent.local_project import (
    atomic_write_json,
    load_project,
    source_video_profiles_path,
    validate_project_id,
)
from scripts.local_media_agent.project_video_profile import SUPPORTED_FRAME_RATES
from scripts.local_media_agent.sony_sidecar_parser import (
    CONFIDENCE_CONFIRMED,
    CONFIDENCE_PARTIAL,
    CONFIDENCE_UNAVAILABLE,
    MONITORING_LUT_NOT_RECORDED,
    MONITORING_LUT_RECORDED,
    SOURCE_COLOR_PROFILE_FIELDS,
    SOURCE_COLOR_PROFILE_UNAVAILABLE,
    SOURCE_COLOR_PROFILE_SOURCE,
    SOURCE_COLOR_PROFILE_SOURCE_UNKNOWN,
)

CATALOG_FORMAT = "CID_SOURCE_VIDEO_PROFILES"
CATALOG_VERSION = 1

CID_SOURCE_VIDEO_RATE_UNAVAILABLE = "CID_SOURCE_VIDEO_RATE_UNAVAILABLE"
CID_SOURCE_VIDEO_RATE_AMBIGUOUS = "CID_SOURCE_VIDEO_RATE_AMBIGUOUS"
CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED = "CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED"
CID_SOURCE_TIMECODE_RATE_UNSUPPORTED = "CID_SOURCE_TIMECODE_RATE_UNSUPPORTED"
CID_SOURCE_MEDIA_PATH_INVALID = "CID_SOURCE_MEDIA_PATH_INVALID"
CID_SOURCE_MEDIA_NOT_FOUND = "CID_SOURCE_MEDIA_NOT_FOUND"
CID_ACTIVE_MEDIA_ROOT_REQUIRED = "CID_ACTIVE_MEDIA_ROOT_REQUIRED"
CID_SOURCE_VIDEO_DURATION_UNAVAILABLE = "CID_SOURCE_VIDEO_DURATION_UNAVAILABLE"
CID_SOURCE_VIDEO_CATALOG_INVALID = "CID_SOURCE_VIDEO_CATALOG_INVALID"

_NDF_RE = re.compile(r"^\d+:\d{2}:\d{2}:\d{2}$")


class SourceVideoProfileError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def normalize_source_media_ref(value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip() or "\x00" in value:
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_PATH_INVALID)
    normalized = value.replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_PATH_INVALID)
    path = PurePosixPath(normalized)
    if any(part in ("", ".", "..") for part in path.parts):
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_PATH_INVALID)
    return path.as_posix()


def build_source_video_profiles(
    project_id: str,
    metadata: dict[str, Any] | Iterable[dict[str, Any]],
) -> dict[str, Any]:
    validate_project_id(project_id)
    results = metadata.get("results", []) if isinstance(metadata, dict) else metadata
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in results if isinstance(results, Iterable) else []:
        if not isinstance(item, dict) or not isinstance(item.get("video"), dict):
            continue
        reference = normalize_source_media_ref(item.get("relative_path"))
        if reference in seen:
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_RATE_AMBIGUOUS)
        seen.add(reference)
        entries.append(_project_entry(item, reference))
    entries.sort(key=lambda entry: entry["source_media_ref"])
    return {
        "format": CATALOG_FORMAT,
        "version": CATALOG_VERSION,
        "project_id": project_id,
        "entries": entries,
    }


def save_source_video_profiles(
    catalog: dict[str, Any], *, local_appdata: str | Path | None = None
) -> None:
    project_id = catalog.get("project_id") if isinstance(catalog, dict) else None
    try:
        validate_project_id(project_id)
        _validate_catalog(catalog, project_id)
        load_project(project_id, local_appdata=local_appdata)
    except ValueError as exc:
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID) from exc
    atomic_write_json(source_video_profiles_path(project_id, local_appdata), catalog)


def load_source_video_profiles(
    project_id: str, *, local_appdata: str | Path | None = None
) -> dict[str, Any]:
    validate_project_id(project_id)
    path = source_video_profiles_path(project_id, local_appdata)
    if not path.is_file():
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_NOT_FOUND)
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID) from exc
    _validate_catalog(catalog, project_id)
    return catalog


def resolve_source_video_profile(
    catalog: dict[str, Any], source_reference: str
) -> dict[str, Any]:
    _validate_catalog(catalog, catalog.get("project_id"))
    reference = normalize_source_media_ref(source_reference)
    entries = catalog["entries"]
    exact = [entry for entry in entries if entry["source_media_ref"] == reference]
    if len(exact) == 1:
        selected = exact[0]
    elif len(PurePosixPath(reference).parts) == 1:
        basename = PurePosixPath(reference).name
        matches = [entry for entry in entries if entry["source_filename"] == basename]
        if not matches:
            raise SourceVideoProfileError(CID_SOURCE_MEDIA_NOT_FOUND)
        if len(matches) > 1:
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_RATE_AMBIGUOUS)
        selected = matches[0]
    else:
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_NOT_FOUND)
    if selected["variable_frame_rate"]:
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED)
    if selected.get("rate_conflict"):
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_RATE_AMBIGUOUS)
    if selected["source_frame_rate"] is None:
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_RATE_UNAVAILABLE)
    if selected["source_duration_raw"] is None:
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_DURATION_UNAVAILABLE)
    timecode = selected.get("source_timecode_start")
    if not isinstance(timecode, str) or not _NDF_RE.fullmatch(timecode):
        raise SourceVideoProfileError(CID_SOURCE_TIMECODE_RATE_UNSUPPORTED)
    return selected


def resolve_source_media_path(
    active_media_root: str | Path | None, source_media_ref: str
) -> Path:
    if active_media_root is None or not str(active_media_root).strip():
        raise SourceVideoProfileError(CID_ACTIVE_MEDIA_ROOT_REQUIRED)
    reference = normalize_source_media_ref(source_media_ref)
    try:
        root = Path(active_media_root).resolve(strict=True)
    except OSError as exc:
        raise SourceVideoProfileError(CID_ACTIVE_MEDIA_ROOT_REQUIRED) from exc
    if not root.is_dir():
        raise SourceVideoProfileError(CID_ACTIVE_MEDIA_ROOT_REQUIRED)
    try:
        resolved = root.joinpath(*PurePosixPath(reference).parts).resolve(strict=True)
        resolved.relative_to(root)
    except FileNotFoundError as exc:
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_NOT_FOUND) from exc
    except (OSError, ValueError) as exc:
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_PATH_INVALID) from exc
    if not resolved.is_file():
        raise SourceVideoProfileError(CID_SOURCE_MEDIA_NOT_FOUND)
    return resolved


def _project_entry(item: dict[str, Any], reference: str) -> dict[str, Any]:
    video = item["video"]
    rate_info = video.get("frame_rate")
    variable = isinstance(rate_info, dict) and rate_info.get("variable") is True
    rates: list[Fraction] = []
    if isinstance(rate_info, dict):
        for key in ("raw_avg", "raw_frame"):
            try:
                rate = Fraction(str(rate_info.get(key)))
            except (ValueError, ZeroDivisionError):
                continue
            if rate > 0:
                rates.append(rate)
    conflict = bool(rates and any(rate != rates[0] for rate in rates[1:]))
    rate = rates[0] if rates and not conflict and rates[0] in SUPPORTED_FRAME_RATES else None
    duration_raw = _valid_duration(item.get("duration_raw"))
    origin = item.get("duration_origin") if duration_raw is not None else None
    return {
        "source_media_ref": reference,
        "source_filename": PurePosixPath(reference).name,
        "source_frame_rate": (
            f"{rate.numerator}/{rate.denominator}" if rate is not None else None
        ),
        "variable_frame_rate": variable,
        "rate_conflict": conflict,
        "source_width": _optional_positive_int(video.get("width")),
        "source_height": _optional_positive_int(video.get("height")),
        "source_sample_aspect_ratio": _rational_pair(video.get("sample_aspect_ratio")),
        "source_display_aspect_ratio": _rational_pair(video.get("display_aspect_ratio")),
        "source_rotation": _valid_rotation(video.get("rotation")),
        "source_timecode_start": item.get("timecode") if isinstance(item.get("timecode"), str) else None,
        "source_duration_raw": duration_raw,
        "source_duration_origin": origin if origin in ("format", "video_stream") else None,
        "source_color_profile": _normalize_color_profile(item.get("source_color_profile")),
    }


def _validate_catalog(catalog: object, project_id: object) -> None:
    if (
        not isinstance(catalog, dict)
        or set(catalog) != {"format", "version", "project_id", "entries"}
        or catalog.get("format") != CATALOG_FORMAT
        or catalog.get("version") != CATALOG_VERSION
        or catalog.get("project_id") != project_id
        or not isinstance(catalog.get("entries"), list)
    ):
        raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
    expected = {
        "source_media_ref", "source_filename", "source_frame_rate", "variable_frame_rate",
        "rate_conflict", "source_width", "source_height", "source_sample_aspect_ratio",
        "source_display_aspect_ratio", "source_rotation", "source_timecode_start",
        "source_duration_raw", "source_duration_origin", "source_color_profile",
    }
    expected_legacy = expected - {"source_color_profile"}
    seen: set[str] = set()
    for entry in catalog["entries"]:
        entry_keys = set(entry) if isinstance(entry, dict) else set()
        if entry_keys not in (expected, expected_legacy):
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        if "source_color_profile" in entry_keys and not _valid_color_profile(
            entry.get("source_color_profile")
        ):
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        reference = normalize_source_media_ref(entry.get("source_media_ref"))
        if reference in seen or entry.get("source_filename") != PurePosixPath(reference).name:
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        seen.add(reference)
        if not isinstance(entry.get("variable_frame_rate"), bool) or not isinstance(
            entry.get("rate_conflict"), bool
        ):
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        rate_text = entry.get("source_frame_rate")
        if rate_text is not None:
            try:
                rate = Fraction(rate_text)
            except (ValueError, ZeroDivisionError) as exc:
                raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID) from exc
            if (
                rate not in SUPPORTED_FRAME_RATES
                or rate_text != f"{rate.numerator}/{rate.denominator}"
            ):
                raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        duration = entry.get("source_duration_raw")
        if duration is not None and _valid_duration(duration) is None:
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        origin = entry.get("source_duration_origin")
        if (duration is None and origin is not None) or (
            duration is not None and origin not in ("format", "video_stream")
        ):
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        for key in ("source_width", "source_height"):
            if entry.get(key) is not None and _optional_positive_int(entry.get(key)) is None:
                raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        for key in ("source_sample_aspect_ratio", "source_display_aspect_ratio"):
            if entry.get(key) is not None and _rational_pair(entry.get(key)) is None:
                raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)
        if entry.get("source_rotation") is not None and _valid_rotation(
            entry.get("source_rotation")
        ) is None:
            raise SourceVideoProfileError(CID_SOURCE_VIDEO_CATALOG_INVALID)


def _valid_duration(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    return value if parsed.is_finite() and parsed > 0 else None


def _optional_positive_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def _rational_pair(value: object) -> dict[str, int] | None:
    """Normalize an exact positive rational from a dict or ``a/b``/``a:b`` string.

    Returns ``None`` for absent/invalid/non-positive values (no invention).
    """
    if value is None:
        return None
    if isinstance(value, dict):
        try:
            return _pair_from_dict(value)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            return None
    if isinstance(value, str):
        normalized = value.strip().replace("/", ":")
        parts = normalized.split(":")
        if len(parts) != 2 or any(not part.isdigit() or not part for part in parts):
            return None
        try:
            return _pair_from_int(int(parts[0]), int(parts[1]))
        except (ValueError, ZeroDivisionError):
            return None
    return None


def _pair_from_dict(value: dict[str, int]) -> dict[str, int]:
    return _pair_from_int(value["numerator"], value["denominator"])


def _pair_from_int(numerator: int, denominator: int) -> dict[str, int]:
    if isinstance(numerator, bool) or isinstance(denominator, bool):
        raise ValueError
    ratio = Fraction(numerator, denominator)
    if ratio <= 0:
        raise ValueError
    return {"numerator": ratio.numerator, "denominator": ratio.denominator}


def _valid_rotation(value: object) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 359:
        return None
    return value


def _normalize_color_profile(value: object) -> dict[str, Any]:
    """Return a color profile dict, or the stable UNAVAILABLE representation.

    Only a structurally valid profile is preserved; anything else defaults
    to the stable UNAVAILABLE/UNKNOWN representation so media without a Sony
    sidecar is never fabricated.
    """
    if not isinstance(value, dict):
        return dict(SOURCE_COLOR_PROFILE_UNAVAILABLE)
    if set(value) != SOURCE_COLOR_PROFILE_FIELDS:
        return dict(SOURCE_COLOR_PROFILE_UNAVAILABLE)
    return dict(value)


def _valid_color_profile(value: object) -> bool:
    if not isinstance(value, dict) or set(value) != SOURCE_COLOR_PROFILE_FIELDS:
        return False
    confidence = value.get("metadata_confidence")
    if confidence not in (CONFIDENCE_CONFIRMED, CONFIDENCE_PARTIAL, CONFIDENCE_UNAVAILABLE):
        return False
    lut_status = value.get("monitoring_lut_status")
    if lut_status not in (MONITORING_LUT_NOT_RECORDED, MONITORING_LUT_RECORDED):
        return False
    if lut_status == MONITORING_LUT_NOT_RECORDED and value.get("monitoring_lut_identity") is not None:
        return False
    for key in (
        "capture_gamma_raw",
        "capture_color_primaries_raw",
        "coding_equations_raw",
        "capture_gamma_display",
        "capture_gamut_display",
    ):
        if value.get(key) is not None and not isinstance(value.get(key), str):
            return False
    meta_source = value.get("metadata_source")
    if meta_source not in (SOURCE_COLOR_PROFILE_SOURCE, SOURCE_COLOR_PROFILE_SOURCE_UNKNOWN):
        return False
    identity = value.get("monitoring_lut_identity")
    if identity is not None and not isinstance(identity, str):
        return False
    sidecar_path = value.get("sidecar_path")
    if sidecar_path is not None and (
        not isinstance(sidecar_path, str) or sidecar_path.startswith(("/", "\\"))
    ):
        return False
    return True
