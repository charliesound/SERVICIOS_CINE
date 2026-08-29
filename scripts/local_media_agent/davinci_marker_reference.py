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

Timing contract: the authoritative CID values are ``source_in_seconds`` and
``source_out_seconds``. They are converted to exact reduced fractional seconds
via Decimal/Fraction (no binary-float subtraction and no decimal-string
rounding), e.g. 554.125 -> 4433/8s and 560.225 -> 22409/40s.
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
    event_name: str = "CID Editorial Reference",
) -> dict[str, Any]:
    """Build a DaVinci FCPXML 1.10 reference from one marker package.

    MAPPED packages yield FCPXML bytes; non-MAPPED (audio-only or unknown)
    packages yield a controlled refusal with no invented clip or timing.
    ``media_path`` and ``frame_duration`` are explicit MAPPED-only inputs.
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

    if not media_path or not frame_duration:
        raise ValueError("davinci_reference_requires_media_path_and_frame_duration")

    marker = markers[0]
    source_in = Decimal(str(marker["source_in_seconds"]))
    source_out = Decimal(str(marker["source_out_seconds"]))
    source_range = source_out - source_in

    xml_bytes = _build_fcpxml(
        marker,
        media_path=media_path,
        frame_duration=frame_duration,
        source_in=source_in,
        source_out=source_out,
        source_range=source_range,
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
    source_in: Decimal,
    source_out: Decimal,
    source_range: Decimal,
    event_name: str,
) -> bytes:
    video_clip = marker["video_clip"]
    marker_name = marker["marker_name"]
    topic = marker.get("topic") or ""
    interview_subject = marker.get("interview_subject") or ""
    excerpt = marker.get("excerpt") or ""
    speaker_attribution = marker.get("speaker_attribution") or "UNKNOWN"
    media_uri = media_path_to_uri(media_path)

    in_t = decimal_seconds_to_fcpxml_time(source_in)
    range_t = decimal_seconds_to_fcpxml_time(source_range)

    if not _RATIONAL_RE.match(in_t):
        raise ValueError(f"invalid_rational_time:{in_t}")
    if not _RATIONAL_RE.match(range_t):
        raise ValueError(f"invalid_rational_time:{range_t}")

    fcpxml = ET.Element("fcpxml", version=FCPXML_VERSION)
    resources = ET.SubElement(fcpxml, "resources")
    ET.SubElement(resources, "format", id="r1", frameDuration=frame_duration)
    asset = ET.SubElement(
        resources,
        "asset",
        id="r2",
        name=video_clip,
        start="0s",
        duration=decimal_seconds_to_fcpxml_time(source_out),
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
        duration=range_t,
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
        start=in_t,
        duration=range_t,
        offset="0s",
        tcFormat="NDF",
    )
    ET.SubElement(
        clip,
        "marker",
        start=in_t,
        duration=frame_duration,
        value=marker_name,
    )
    note = ET.SubElement(clip, "note")
    source_out_t = decimal_seconds_to_fcpxml_time(source_out)
    note.text = (
        f"CID reference | {marker_name} | source_in={in_t} | "
        f"source_out={source_out_t} | topic={topic} | interview_subject="
        f"{interview_subject} | speaker_attribution={speaker_attribution} | "
        f"excerpt={excerpt}"
    )
    return ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
