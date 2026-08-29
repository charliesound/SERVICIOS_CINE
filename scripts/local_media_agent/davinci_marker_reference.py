"""CID DaVinci Resolve FCPXML reference generator (read-only consumer).

Converts an existing CID_PRODUCER_EDITORIAL_MARKER_PACKAGE (version 1) into a
minimal, deterministic FCPXML 1.10 sidecar that a producer/editor can manually
import into DaVinci Resolve to locate the referenced source moment.

This module never controls Resolve directly: no import, no scripting, no
project or timeline mutation, no media relink, no source-media reads/writes.

FCPXML 1.10 media representation:
  * <asset> carries NO ``src`` attribute; the media is referenced through a
    child <media-rep kind="original-media" src="..."/> element.
  * <format> uses only ``id`` + the authoritative ``frameDuration`` supplied by
    the caller. No hardcoded resolution or fps.

Timing contract (source-media domain): the physical source file has its own
embedded start timecode. The converter takes the authoritative source timing
explicitly (`source_timecode_start` as NDF HH:MM:SS:FF and `source_duration`
in seconds), converting both to exact reduced fractional seconds via integer
frame arithmetic and Decimal/Fraction (no binary-float subtraction and no
decimal-string rounding). The asset thus begins at the real source timecode, not
at 0s.

The CID editorial values `source_in_seconds` / `source_out_seconds` remain
relative-to-clip authority (e.g. 554.125 -> 4433/8s and 560.225 -> 22409/40s)
and are NOT modified. The asset-clip/marker start is the absolute source-domain
moment: `source_asset_start + relative_source_in`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

FCPXML_VERSION = "1.10"

DAVINCI_REFERENCE_FORMAT = "CID_PRODUCER_EDITORIAL_DAVINCI_FCPXML_REFERENCE"
DAVINCI_REFERENCE_VERSION = 1

DAVINCI_REFERENCE_REASON_AUDIO_ONLY = "AUDIO_ONLY_VIDEO_UNMAPPED"
DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER = "NO_MAPPED_MARKER"

_WIN_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_RATIONAL_RE = re.compile(r"^\d+/\d+s$")
_NDF_TC_RE = re.compile(r"^(\d+):(\d+):(\d+):(\d+)$")


def frame_duration_to_fps(frame_duration: str) -> int:
    """Derive integer frames-per-second from a frameDuration string.

    Accepts inputs such as "1/25s" or "1/25" and returns the integer fps (25).
    """
    bare = frame_duration.removesuffix("s")
    numerator_s, _, denominator_s = bare.partition("/")
    numerator = int(numerator_s)
    denominator = int(denominator_s or "1")
    if numerator <= 0 or denominator <= 0:
        raise ValueError("invalid_frame_duration")
    fps = Fraction(denominator, numerator)
    if fps.denominator != 1:
        raise ValueError("non_integer_fps_from_frame_duration")
    return fps.numerator


def ndf_timecode_to_seconds(timecode: str, fps: int) -> Fraction:
    """Convert an NDF timecode HH:MM:SS:FF to exact fractional seconds.

    Uses integer frame arithmetic only (no floats): total frames =
    ((HH*60 + MM)*60 + SS)*fps + FF, then seconds = frames / fps.
    """
    match = _NDF_TC_RE.match(timecode)
    if not match:
        raise ValueError(f"invalid_ndf_timecode:{timecode}")
    hours, minutes, seconds, frames = (int(g) for g in match.groups())
    if minutes >= 60 or seconds >= 60 or frames >= fps:
        raise ValueError(f"invalid_ndf_timecode:{timecode}")
    total_frames = ((hours * 60 + minutes) * 60 + seconds) * fps + frames
    return Fraction(total_frames, fps)


def decimal_seconds_to_fcpxml_time(value: Any) -> str:
    """Convert exact seconds to a reduced fractional FCPXML time string.

    Accepts int/float/Decimal/str/Fraction and returns e.g. "4433/8s". The
    conversion goes through Decimal(str(...)) + Fraction so floating-point noise
    and lossy rounding are never introduced.
    """
    if isinstance(value, Decimal):
        dec = value
    elif isinstance(value, Fraction):
        return f"{value}s"
    elif isinstance(value, float):
        dec = Decimal(str(value))
    elif isinstance(value, str):
        dec = Decimal(value)
    else:
        dec = Decimal(value)
    return f"{Fraction(dec)}s"


def seconds_to_fraction(value: Any) -> Fraction:
    """Coerce a seconds value to an exact Fraction."""
    if isinstance(value, Fraction):
        return value
    return Fraction(Decimal(str(value)))


def decimal_seconds_to_fcpxml_time(value: Any) -> str:
    """Convert exact seconds to a reduced fractional FCPXML time string.

    Accepts int/float/Decimal/str and returns e.g. "4433/8s". The conversion
    goes through Decimal(str(...)) + Fraction so floating-point noise and
    lossy rounding are never introduced.
    """
    if isinstance(value, Decimal):
        dec = value
    elif isinstance(value, Fraction):
        return f"{value}s"
    elif isinstance(value, float):
        dec = Decimal(str(value))
    elif isinstance(value, str):
        dec = Decimal(value)
    else:
        dec = Decimal(value)
    return f"{Fraction(dec)}s"


def media_path_to_uri(media_path: str) -> str:
    """Convert an explicit editor-visible source path to a file URI.

    Reuses CID's proven path-to-URI transformation for POSIX and Windows drive
    paths; never reads or validates the source file.
    """
    normalized = media_path.replace("\\", "/")
    if _WIN_DRIVE_RE.match(media_path):
        return "file:///" + normalized
    if normalized.startswith("/"):
        return Path(normalized).as_uri()
    return Path(media_path).resolve().as_uri()


def build_davinci_reference(
    package: dict[str, Any],
    *,
    media_path: str,
    frame_duration: str,
    source_timecode_start: str,
    source_duration: str | float,
    event_name: str = "CID Editorial Reference",
) -> dict[str, Any]:
    """Build a DaVinci FCPXML 1.10 reference from one marker package.

    MAPPED packages yield FCPXML bytes; non-MAPPED (audio-only or unknown)
    packages yield a controlled refusal with no invented clip or timing.
    ``media_path``, ``frame_duration``, ``source_timecode_start`` and
    ``source_duration`` are explicit MAPPED-only inputs. Source timing is
    treated as authoritative string-only metadata; no source file is read.
    """
    if not package.get("editor_handoff_available"):
        return {
            "format": DAVINCI_REFERENCE_FORMAT,
            "version": DAVINCI_REFERENCE_VERSION,
            "candidate_id": package.get("candidate_id"),
            "davinci_reference_available": False,
            "davinci_reference_reason": (
                package.get("editor_handoff_reason")
                or DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER
            ),
            "video_clip": None,
            "source_in_seconds": None,
            "source_out_seconds": None,
        }

    markers = package.get("markers") or []
    if not markers:
        return {
            "format": DAVINCI_REFERENCE_FORMAT,
            "version": DAVINCI_REFERENCE_VERSION,
            "candidate_id": package.get("candidate_id"),
            "davinci_reference_available": False,
            "davinci_reference_reason": DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER,
            "video_clip": None,
            "source_in_seconds": None,
            "source_out_seconds": None,
        }

    if not media_path or not frame_duration or not source_timecode_start:
        raise ValueError(
            "davinci_reference_requires_media_path_frame_duration_and_source_timing"
        )

    fps = frame_duration_to_fps(frame_duration)
    source_asset_start = ndf_timecode_to_seconds(source_timecode_start, fps)
    source_asset_duration = seconds_to_fraction(source_duration)

    marker = markers[0]
    source_in = Decimal(str(marker["source_in_seconds"]))
    source_out = Decimal(str(marker["source_out_seconds"]))
    rel_in = Fraction(source_in)
    rel_out = Fraction(source_out)
    duration = rel_out - rel_in
    abs_start = source_asset_start + rel_in
    abs_end = source_asset_start + rel_out

    xml_bytes = _build_fcpxml(
        marker,
        media_path=media_path,
        frame_duration=frame_duration,
        source_asset_start=source_asset_start,
        source_asset_duration=source_asset_duration,
        abs_start=abs_start,
        abs_end=abs_end,
        duration=duration,
        rel_in=rel_in,
        rel_out=rel_out,
        event_name=event_name,
    )
    return {
        "format": DAVINCI_REFERENCE_FORMAT,
        "version": DAVINCI_REFERENCE_VERSION,
        "candidate_id": package.get("candidate_id"),
        "davinci_reference_available": True,
        "video_clip": marker["video_clip"],
        "source_in_seconds": str(source_in),
        "source_out_seconds": str(source_out),
        "source_asset_start": str(source_asset_start),
        "source_asset_duration": str(source_asset_duration),
        "selected_start": str(abs_start),
        "selected_end": str(abs_end),
        "marker_name": marker["marker_name"],
        "speaker_attribution": marker["speaker_attribution"],
        "source_media_mutation": False,
        "davinci_project_mutation": False,
        "media_uri": media_path_to_uri(media_path),
        "fcpxml": xml_bytes,
        "fcpxml_text": xml_bytes.decode("utf-8"),
    }


def _build_fcpxml(
    marker: dict[str, Any],
    *,
    media_path: str,
    frame_duration: str,
    source_asset_start: Fraction,
    source_asset_duration: Fraction,
    abs_start: Fraction,
    abs_end: Fraction,
    duration: Fraction,
    rel_in: Fraction,
    rel_out: Fraction,
    event_name: str,
) -> bytes:
    video_clip = marker["video_clip"]
    marker_name = marker["marker_name"]
    topic = marker.get("topic") or ""
    interview_subject = marker.get("interview_subject") or ""
    excerpt = marker.get("excerpt") or ""
    speaker_attribution = marker.get("speaker_attribution") or "UNKNOWN"
    media_uri = media_path_to_uri(media_path)

    asset_start_t = decimal_seconds_to_fcpxml_time(source_asset_start)
    asset_duration_t = decimal_seconds_to_fcpxml_time(source_asset_duration)
    abs_start_t = decimal_seconds_to_fcpxml_time(abs_start)
    abs_end_t = decimal_seconds_to_fcpxml_time(abs_end)
    duration_t = decimal_seconds_to_fcpxml_time(duration)
    rel_in_t = decimal_seconds_to_fcpxml_time(rel_in)
    rel_out_t = decimal_seconds_to_fcpxml_time(rel_out)

    for t in (asset_start_t, asset_duration_t, abs_start_t, abs_end_t, duration_t):
        if not _RATIONAL_RE.match(t):
            raise ValueError(f"invalid_rational_time:{t}")

    fcpxml = ET.Element("fcpxml", version=FCPXML_VERSION)
    resources = ET.SubElement(fcpxml, "resources")
    ET.SubElement(resources, "format", id="r1", frameDuration=frame_duration)
    asset = ET.SubElement(
        resources,
        "asset",
        id="r2",
        name=video_clip,
        start=asset_start_t,
        duration=asset_duration_t,
        hasVideo="1",
        hasAudio="1",
        format="r1",
    )
    ET.SubElement(
        asset,
        "media-rep",
        kind="original-media",
        src=media_uri,
    )

    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", name=event_name)
    project = ET.SubElement(event, "project", name="CID Producer Editorial Reference")
    sequence = ET.SubElement(
        project,
        "sequence",
        format="r1",
        duration=duration_t,
        tcStart="0s",
        tcFormat="NDF",
        audioLayout="stereo",
        audioRate="48k",
    )
    spine = ET.SubElement(sequence, "spine")
    clip = ET.SubElement(
        spine,
        "asset-clip",
        name=marker_name,
        ref="r2",
        start=abs_start_t,
        duration=duration_t,
        offset="0s",
        tcFormat="NDF",
    )
    ET.SubElement(
        clip,
        "marker",
        start=abs_start_t,
        duration=frame_duration,
        value=marker_name,
    )
    note = ET.SubElement(clip, "note")
    note.text = (
        f"CID reference | {marker_name} | source_in={rel_in_t} | "
        f"source_out={rel_out_t} | absolute_start={abs_start_t} | "
        f"absolute_end={abs_end_t} | topic={topic} | interview_subject="
        f"{interview_subject} | speaker_attribution={speaker_attribution} | "
        f"excerpt={excerpt}"
    )
    return ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
