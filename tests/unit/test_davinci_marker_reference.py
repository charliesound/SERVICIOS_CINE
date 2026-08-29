from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction
from xml.etree import ElementTree as ET

from scripts.local_media_agent.davinci_marker_reference import (
    DAVINCI_REFERENCE_FORMAT,
    DAVINCI_REFERENCE_REASON_AUDIO_ONLY,
    DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER,
    build_davinci_reference,
    decimal_seconds_to_fcpxml_time,
    frame_duration_to_fps,
    media_path_to_uri,
    ndf_timecode_to_seconds,
)
from services.fcpxml_validation_service import fcpxml_validation_service

MEDIA_PATH = "F:/CINE/SIRUELA/A7IV_SL31277.MP4"
FRAME_DURATION = "1/25s"
FPS = 25
SOURCE_TIMECODE_START = "21:42:10:23"
SOURCE_DURATION = "3209.76"
SOURCE_ASSET_START = Fraction(1953273, 25)
SOURCE_ASSET_DURATION = Fraction(80244, 25)
REL_IN = Fraction(4433, 8)
REL_OUT = Fraction(22409, 40)
ABS_START = Fraction(15737009, 200)
ABS_END = Fraction(15738229, 200)
RANGE = Fraction(61, 10)


def _mapped_package(
    candidate_id: str = "SIRUELA-CTX-045",
    video_clip: str = "A7IV_SL31277.MP4",
    source_in: float = 554.125,
    source_out: float = 560.225,
) -> dict:
    return {
        "format": "CID_PRODUCER_EDITORIAL_MARKER_PACKAGE",
        "version": 1,
        "candidate_id": candidate_id,
        "editor_handoff_available": True,
        "editor_handoff_reason": None,
        "video_clip": video_clip,
        "source_media_mutation": False,
        "davinci_project_mutation": False,
        "markers": [
            {
                "candidate_id": candidate_id,
                "video_clip": video_clip,
                "source_in_seconds": source_in,
                "source_out_seconds": source_out,
                "marker_name": f"CID | problemas/dificultades | Pruden | {candidate_id}",
                "topic": "problemas/dificultades",
                "interview_subject": "Pruden",
                "excerpt": "en las vacas si no son capaces de echar la cría",
                "speaker_attribution": "UNKNOWN",
            }
        ],
    }


def _audio_only_package(candidate_id: str = "SIRUELA-CTX-022") -> dict:
    return {
        "format": "CID_PRODUCER_EDITORIAL_MARKER_PACKAGE",
        "version": 1,
        "candidate_id": candidate_id,
        "editor_handoff_available": False,
        "editor_handoff_reason": "AUDIO_ONLY_VIDEO_UNMAPPED",
        "video_clip": None,
        "markers": [],
    }


def _ref(
    package: dict | None = None,
    **kwargs,
) -> dict:
    pkg = package if package is not None else _mapped_package()
    return build_davinci_reference(
        pkg,
        media_path=kwargs.pop("media_path", MEDIA_PATH),
        frame_duration=kwargs.pop("frame_duration", FRAME_DURATION),
        source_timecode_start=kwargs.pop(
            "source_timecode_start", SOURCE_TIMECODE_START
        ),
        source_duration=kwargs.pop("source_duration", SOURCE_DURATION),
        **kwargs,
    )


# ---------------- NDF timecode / frame duration helpers ----------------

def test_ndf_timecode_start_yields_exact_rational() -> None:
    # 21:42:10:23 @ 25fps -> 1953273/25s
    assert ndf_timecode_to_seconds("21:42:10:23", 25) == SOURCE_ASSET_START


def test_frame_duration_to_fps() -> None:
    assert frame_duration_to_fps("1/25s") == 25
    assert frame_duration_to_fps("1/50s") == 50


# ---------------- Source domain conversions ----------------

def test_source_duration_exact_rational() -> None:
    # 3209.76s -> 80244/25s
    assert decimal_seconds_to_fcpxml_time("3209.76") == "80244/25s"


def test_relative_in_exact_rational() -> None:
    # 554.125 -> 4433/8s (unchanged relative editorial authority)
    assert decimal_seconds_to_fcpxml_time("554.125") == "4433/8s"


def test_absolute_selected_start_exact_rational() -> None:
    # SOURCE_ASSET_START + RELATIVE_SOURCE_IN -> 15737009/200s
    assert SOURCE_ASSET_START + REL_IN == ABS_START
    assert decimal_seconds_to_fcpxml_time(ABS_START) == "15737009/200s"


def test_absolute_selected_end_exact_rational() -> None:
    # SOURCE_ASSET_START + RELATIVE_SOURCE_OUT -> 15738229/200s
    assert SOURCE_ASSET_START + REL_OUT == ABS_END
    assert decimal_seconds_to_fcpxml_time(ABS_END) == "15738229/200s"


def test_selected_duration_exact_rational() -> None:
    assert ABS_END - ABS_START == RANGE
    assert decimal_seconds_to_fcpxml_time(RANGE) == "61/10s"


# ---------------- Asset representation ----------------

def test_asset_start_not_zero_and_is_source_domain() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    asset = root.find("resources/asset")
    assert asset.get("start") == "1953273/25s"
    assert asset.get("start") != "0s"


def test_asset_duration_is_full_physical_clip_duration() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    asset = root.find("resources/asset")
    assert asset.get("duration") == "80244/25s"


def test_exact_arithmetic_no_float_noise() -> None:
    # The three independent exact fractions sum correctly.
    assert Fraction(1953273, 25) + Fraction(4433, 8) == Fraction(15737009, 200)
    assert Fraction(15738229, 200) - Fraction(15737009, 200) == Fraction(61, 10)


# ---------------- Asset-clip / marker (absolute source domain) ----------------

def test_asset_clip_start_uses_absolute_source_domain() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    clip = root.find(".//asset-clip")
    assert clip.get("start") == "15737009/200s"
    assert clip.get("duration") == "61/10s"
    assert clip.get("offset") == "0s"


def test_marker_start_same_absolute_source_domain() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    marker = root.find(".//asset-clip/marker")
    assert marker.get("start") == "15737009/200s"
    assert marker.get("duration") == "1/25s"


def test_relative_editorial_values_unchanged_in_manifest() -> None:
    ref = _ref()
    assert Decimal(str(ref["source_in_seconds"])) == Decimal("554.125")
    assert Decimal(str(ref["source_out_seconds"])) == Decimal("560.225")
    assert ref["selected_start"] == str(ABS_START)
    assert ref["selected_end"] == str(ABS_END)


# ---------------- Preserved FCPXML 1.10 contract ----------------

def test_fcpxml_version_is_1_10() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    assert root.get("version") == "1.10"


def test_no_src_attribute_on_asset() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    asset = root.find("resources/asset")
    assert asset is not None
    assert asset.get("src") is None


def test_asset_has_original_media_rep() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    asset = root.find("resources/asset")
    media_rep = asset.find("media-rep")
    assert media_rep is not None
    assert media_rep.get("kind") == "original-media"
    assert media_rep.get("src") is not None


def test_media_path_becomes_expected_file_uri() -> None:
    assert media_path_to_uri(MEDIA_PATH) == "file:///F:/CINE/SIRUELA/A7IV_SL31277.MP4"


def test_no_hardcoded_resolution_or_fps() -> None:
    ref = _ref()
    text = ref["fcpxml_text"]
    assert "1920" not in text and "1080" not in text
    fmt = ET.fromstring(ref["fcpxml"]).find("resources/format")
    assert fmt.get("width") is None
    assert fmt.get("height") is None
    assert fmt.get("name") is None
    assert fmt.get("frameDuration") == "1/25s"


def test_note_metadata_preserved_with_absolute_domain() -> None:
    ref = _ref()
    note = ET.fromstring(ref["fcpxml"]).find(".//note")
    assert "source_in=4433/8s" in note.text
    assert "source_out=22409/40s" in note.text
    assert "absolute_start=15737009/200s" in note.text
    assert "absolute_end=15738229/200s" in note.text
    assert "speaker_attribution=UNKNOWN" in note.text
    assert "problemas/dificultades" in note.text
    assert "Pruden" in note.text


def test_audio_only_produces_no_fcpxml() -> None:
    ref = _ref(package=_audio_only_package())
    assert ref["davinci_reference_available"] is False
    assert ref["davinci_reference_reason"] == DAVINCI_REFERENCE_REASON_AUDIO_ONLY
    assert "fcpxml" not in ref


def test_output_is_deterministic() -> None:
    a = _ref()
    b = _ref()
    assert a["fcpxml"] == b["fcpxml"]
    assert a["fcpxml_text"] == b["fcpxml_text"]


def test_format_constant_no_mutation_flags() -> None:
    ref = _ref()
    assert ref["format"] == DAVINCI_REFERENCE_FORMAT
    assert ref["source_media_mutation"] is False
    assert ref["davinci_project_mutation"] is False


def test_internal_validator_not_applicable_to_1_10_media_rep() -> None:
    """CID's legacy FCPXML validator expects <asset src>, which FCPXML 1.10
    replaces with <media-rep>; an expected false negative, not conformance.
    """
    ref = _ref()
    validation = fcpxml_validation_service.validate(ref["fcpxml"])
    assert "asset_missing_src:r2" in validation["errors"]


def test_json_round_trip_of_reference_manifest() -> None:
    ref = _ref()
    manifested = {k: v for k, v in ref.items() if k not in ("fcpxml",)}
    json.dumps(manifested, ensure_ascii=False)
