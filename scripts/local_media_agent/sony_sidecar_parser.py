"""Read-only Sony XML sidecar source color profile extraction (V1).

Extracts a minimal SOURCE_COLOR_PROFILE from Sony ``.XML`` sidecars
(sibling ``<clip_base>M01.XML`` next to ``<clip_base>.MP4``). Purely
read-only: the XML is parsed, never modified, no sidecars are written,
and no LUT / CST / color transform is applied.

The profile is explicitly separated from PROJECT_COLOR_PIPELINE: it only
describes what the camera recorded, it never decides how a project should
grade or output its media.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SOURCE_COLOR_PROFILE_SOURCE = "SONY_XML_SIDECAR"
SOURCE_COLOR_PROFILE_SOURCE_UNKNOWN = "UNKNOWN"

CONFIDENCE_CONFIRMED = "CONFIRMED"
CONFIDENCE_PARTIAL = "PARTIAL"
CONFIDENCE_UNAVAILABLE = "UNAVAILABLE"

MONITORING_LUT_NOT_RECORDED = "NOT_RECORDED"
MONITORING_LUT_RECORDED = "RECORDED"

SONY_CAPTURE_GAMMA_ITEM = "CaptureGammaEquation"
SONY_CAPTURE_COLOR_PRIMARIES_ITEM = "CaptureColorPrimaries"
SONY_CODING_EQUATIONS_ITEM = "CodingEquations"
SONY_LUT_NAME_TOKENS = ("LUT", "MLUT", "Look")

SONY_SIDECAR_MARKER = "M01"
SONY_SIDECAR_SUFFIX = ".XML"

SONY_SIDECAR_ERROR_MALFORMED = "SONY_SIDECAR_MALFORMED"

SOURCE_COLOR_PROFILE_FIELDS = frozenset({
    "capture_gamma_raw",
    "capture_color_primaries_raw",
    "coding_equations_raw",
    "capture_gamma_display",
    "capture_gamut_display",
    "monitoring_lut_status",
    "monitoring_lut_identity",
    "metadata_source",
    "metadata_confidence",
    "sidecar_path",
})

# Explicit deterministic raw->display mappings (V1, demonstrated real values).
# Values not present here are preserved raw and NEVER guessed for display.
CAPTURE_GAMMA_DISPLAY_MAP = {
    "s-log3-cine": "S-Log3",
    "s-cinetone": "S-Cinetone",
    "ex-cine1": "Ex-Cine1",
    "rec709": "Rec.709",
}
CAPTURE_GAMUT_DISPLAY_MAP = {
    "s-gamut3-cine": "S-Gamut3.Cine",
    "rec709": "Rec.709",
}

SOURCE_COLOR_PROFILE_UNAVAILABLE: dict[str, Any] = {
    "capture_gamma_raw": None,
    "capture_color_primaries_raw": None,
    "coding_equations_raw": None,
    "capture_gamma_display": None,
    "capture_gamut_display": None,
    "monitoring_lut_status": MONITORING_LUT_NOT_RECORDED,
    "monitoring_lut_identity": None,
    "metadata_source": SOURCE_COLOR_PROFILE_SOURCE_UNKNOWN,
    "metadata_confidence": CONFIDENCE_UNAVAILABLE,
    "sidecar_path": None,
}


class SonySidecarError(ValueError):
    """Raised when a Sony sidecar cannot be read or parsed."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def resolve_sony_sidecar(media_path: str | Path) -> Path | None:
    """Resolve the exact sibling Sony M01.XML sidecar for a media file (V1).

    Only the V1 pattern is supported:

      media:   <dir>/<clip_base>.MP4
      sidecar: <dir>/<clip_base>M01.XML

    The sidecar must be an exact sibling of the media file. No recursive
    search, no nearby-subdirectory search, no ambiguous glob, no
    first-match global, no basename association outside the media
    directory, no support for other manufacturers.

    Returns the sidecar ``Path`` when it exists and is a file, else None.
    """
    media = Path(media_path)
    if media.suffix.lower() != ".mp4":
        return None
    sidecar = media.parent / f"{media.stem}{SONY_SIDECAR_MARKER}{SONY_SIDECAR_SUFFIX}"
    if sidecar.is_file():
        return sidecar
    return None


def extract_sony_sidecar_color_metadata(sidecar_path: str | Path) -> dict[str, Any]:
    """Parse a Sony sidecar and return only explicit Item color metadata.

    Raises :class:`SonySidecarError` when the sidecar is malformed or
    unreadable. No value is invented and no field is inferred.
    """
    path = Path(sidecar_path)
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError, UnicodeError) as exc:
        raise SonySidecarError(SONY_SIDECAR_ERROR_MALFORMED) from exc

    root = tree.getroot()
    items = _collect_named_items(root)

    return {
        "capture_gamma_raw": items.get(SONY_CAPTURE_GAMMA_ITEM),
        "capture_color_primaries_raw": items.get(SONY_CAPTURE_COLOR_PRIMARIES_ITEM),
        "coding_equations_raw": items.get(SONY_CODING_EQUATIONS_ITEM),
        "lut_metadata": _collect_lut_metadata(items),
    }


def build_source_color_profile(
    sidecar_path: str | Path,
    *,
    relative_sidecar_path: str | None = None,
) -> dict[str, Any]:
    """Build a SOURCE_COLOR_PROFILE dict from a Sony XML sidecar.

    Never raises for media/XML problems: malformed or unreadable sidecars
    produce the UNAVAILABLE contract representation. The sidecar path is
    stored normalized and relative (POSIX) when ``relative_sidecar_path``
    is provided; absolute sidecar paths are never exposed.
    """
    stored_sidecar_path = _normalize_sidecar_path(relative_sidecar_path)
    try:
        parsed = extract_sony_sidecar_color_metadata(sidecar_path)
    except SonySidecarError:
        return dict(SOURCE_COLOR_PROFILE_UNAVAILABLE)

    gamma_raw = parsed.get("capture_gamma_raw")
    primaries_raw = parsed.get("capture_color_primaries_raw")
    coding_raw = parsed.get("coding_equations_raw")
    lut_metadata = parsed.get("lut_metadata") or []
    lut_identity = lut_metadata[0]["value"] if lut_metadata else None

    has_core_fields = any(
        value is not None and str(value) != ""
        for value in (gamma_raw, primaries_raw, coding_raw)
    )
    has_lut = bool(lut_metadata)
    if not has_core_fields and not has_lut:
        return dict(SOURCE_COLOR_PROFILE_UNAVAILABLE)

    confidence = CONFIDENCE_CONFIRMED if has_core_fields else CONFIDENCE_PARTIAL

    return {
        "capture_gamma_raw": gamma_raw if gamma_raw is not None and str(gamma_raw) != "" else None,
        "capture_color_primaries_raw": (
            primaries_raw if primaries_raw is not None and str(primaries_raw) != "" else None
        ),
        "coding_equations_raw": (
            coding_raw if coding_raw is not None and str(coding_raw) != "" else None
        ),
        "capture_gamma_display": CAPTURE_GAMMA_DISPLAY_MAP.get(gamma_raw),
        "capture_gamut_display": CAPTURE_GAMUT_DISPLAY_MAP.get(primaries_raw),
        "monitoring_lut_status": (
            MONITORING_LUT_RECORDED if has_lut else MONITORING_LUT_NOT_RECORDED
        ),
        "monitoring_lut_identity": lut_identity,
        "metadata_source": SOURCE_COLOR_PROFILE_SOURCE,
        "metadata_confidence": confidence,
        "sidecar_path": stored_sidecar_path,
    }


def _collect_named_items(root: ET.Element) -> dict[str, str]:
    """Return name -> value for every ``Item`` element with an explicit name.

    Only elements whose local-name is exactly ``Item`` are considered, so
    other elements that happen to carry a ``name`` attribute can never
    contaminate metadata. The value is taken in precedence:

    * explicit ``value`` attribute (real Sony structure), then
    * ``Value`` attribute (legacy), then
    * the first non-empty text node under the item (legacy text-node).

    Raw values are preserved exactly: no case folding, no trimming of the
    returned string, no substitution, no canonicalization. Display
    normalization stays a separate, later step.
    """
    result: dict[str, str] = {}
    for _element in root.iter():
        if _local_name(_element.tag) != "Item":
            continue
        name = _element.attrib.get("name") or _element.attrib.get("Name")
        if not isinstance(name, str) or not name.strip():
            continue
        value = _first_item_value(_element)
        if value is not None:
            result[name] = value
    return result


def _local_name(tag: Any) -> str:
    """Return the XML local-name of an ElementTree tag, namespace-safe."""
    if not isinstance(tag, str):
        return ""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _first_item_value(element: ET.Element) -> str | None:
    """Return an Item value: ``value``/``Value`` attribute then text fallback.

    The attribute is used only when non-empty; the raw attribute string is
    returned untouched. When no attribute carries the value, fall back to the
    first non-empty text node for legacy text-node compatibility.
    """
    for attr in ("value", "Value"):
        raw = element.attrib.get(attr)
        if isinstance(raw, str) and raw.strip():
            return raw
    return _first_text(element)


def _first_text(element: ET.Element) -> str | None:
    """Return the first non-empty ``.text`` in document order."""
    for descendant in _iter_element_texts(element):
        if descendant is not None and str(descendant).strip():
            return str(descendant)
    text = element.text
    if text is not None and str(text).strip():
        return str(text)
    return None


def _iter_element_texts(element: ET.Element):
    for descendant in element.iter():
        text = descendant.text
        if isinstance(text, str) and text.strip():
            yield text


def _collect_lut_metadata(items: dict[str, str]) -> list[dict[str, Any]]:
    """Collect explicit LUT/MLUT/Look fields without inferring anything."""
    found: list[dict[str, Any]] = []
    for name, value in items.items():
        lowered = name.lower()
        if any(token.lower() in lowered for token in SONY_LUT_NAME_TOKENS):
            found.append({"name": name, "value": value})
    found.sort(key=lambda item: item["name"])
    return found


def _normalize_sidecar_path(value: str | None) -> str | None:
    """Normalize a relative sidecar path to POSIX form; never absolute."""
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("\\", "/")
    if normalized.startswith("/") or (len(normalized) > 1 and normalized[1] == ":"):
        return None
    return normalized