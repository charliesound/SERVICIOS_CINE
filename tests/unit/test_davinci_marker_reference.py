from __future__ import annotations

import json
from decimal import Decimal
from xml.etree import ElementTree as ET

from scripts.local_media_agent.davinci_marker_reference import (
    DAVINCI_REFERENCE_FORMAT,
    DAVINCI_REFERENCE_REASON_AUDIO_ONLY,
    DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER,
    build_davinci_reference,
    decimal_seconds_to_fcpxml_time,
    media_path_to_uri,
)
from services.fcpxml_validation_service import fcpxml_validation_service

MEDIA_PATH = "F:/CINE/SIRUELA/A7IV_SL31277.MP4"
FRAME_DURATION = "1/25s"


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
        **kwargs,
    )


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


def test_media_path_becomes_expected_windows_file_uri() -> None:
    assert media_path_to_uri("F:/CINE/SIRUELA/A7IV_SL31277.MP4") == (
        "file:///F:/CINE/SIRUELA/A7IV_SL31277.MP4"
    )
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    media_rep = root.find("resources/asset/media-rep")
    assert media_rep.get("src") == "file:///F:/CINE/SIRUELA/A7IV_SL31277.MP4"


def test_source_in_exact_rational_conversion() -> None:
    assert decimal_seconds_to_fcpxml_time("554.125") == "4433/8s"
    assert decimal_seconds_to_fcpxml_time(554.125) == "4433/8s"


def test_source_out_preserved_in_cid_reference_data() -> None:
    ref = _ref()
    assert Decimal(str(ref["source_out_seconds"])) == Decimal("560.225")
    assert decimal_seconds_to_fcpxml_time(ref["source_out_seconds"]) == "22409/40s"


def test_range_duration_exact_rational() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    clip = root.find(".//asset-clip")
    assert clip.get("start") == "4433/8s"
    assert clip.get("duration") == "61/10s"


def test_no_hardcoded_resolution() -> None:
    ref = _ref()
    text = ref["fcpxml_text"]
    assert "1920" not in text and "1080" not in text
    root = ET.fromstring(ref["fcpxml"])
    fmt = root.find("resources/format")
    assert fmt.get("width") is None and fmt.get("height") is None


def test_no_hardcoded_fps_inside_converter() -> None:
    ref = _ref(frame_duration="1/50s")
    root = ET.fromstring(ref["fcpxml"])
    fmt = root.find("resources/format")
    assert fmt.get("name") is None
    assert fmt.get("frameDuration") == "1/50s"


def test_frame_duration_comes_from_explicit_input() -> None:
    ref_default = _ref(frame_duration="1/25s")
    root_default = ET.fromstring(ref_default["fcpxml"])
    assert root_default.find("resources/format").get("frameDuration") == "1/25s"
    ref_other = _ref(frame_duration="1/24s")
    root_other = ET.fromstring(ref_other["fcpxml"])
    assert root_other.find("resources/format").get("frameDuration") == "1/24s"


def test_marker_start_and_duration_and_value() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    clip = root.find(".//asset-clip")
    marker = clip.find("marker")
    assert marker is not None
    assert marker.get("start") == "4433/8s"
    assert marker.get("duration") == "1/25s"
    assert marker.get("value") == "CID | problemas/dificultades | Pruden | SIRUELA-CTX-045"


def test_speaker_attribution_remains_unknown() -> None:
    ref = _ref()
    assert ref["speaker_attribution"] == "UNKNOWN"
    root = ET.fromstring(ref["fcpxml"])
    note = root.find(".//note")
    assert "speaker_attribution=UNKNOWN" in note.text


def test_note_metadata_preserved() -> None:
    ref = _ref()
    root = ET.fromstring(ref["fcpxml"])
    note = root.find(".//note")
    assert "problemas/dificultades" in note.text
    assert "Pruden" in note.text
    assert "en las vacas" in note.text
    assert "source_in=4433/8s" in note.text
    assert "source_out=22409/40s" in note.text


def test_audio_only_produces_no_fcpxml() -> None:
    ref = _ref(package=_audio_only_package())
    assert ref["davinci_reference_available"] is False
    assert ref["davinci_reference_reason"] == DAVINCI_REFERENCE_REASON_AUDIO_ONLY
    assert "fcpxml" not in ref


def test_no_mapped_marker_safely_refuses() -> None:
    pkg = _mapped_package()
    pkg["markers"] = []
    ref = _ref(package=pkg)
    assert ref["davinci_reference_available"] is False
    assert ref["davinci_reference_reason"] == DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER


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
    replaces with <media-rep>. The corrected reference intentionally omits the
    asset 'src' attribute, so the internal validator reports asset_missing_src.
    That is an expected false negative, not a conformance failure; the
    FCPXML 1.10 structure contract is asserted by the dedicated tests above.
    """
    ref = _ref()
    validation = fcpxml_validation_service.validate(ref["fcpxml"])
    assert "asset_missing_src:r2" in validation["errors"]


def test_json_round_trip_of_reference_manifest() -> None:
    ref = _ref()
    manifested = {k: v for k, v in ref.items() if k not in ("fcpxml",)}
    manifested["source_in_seconds"] = str(manifested["source_in_seconds"])
    manifested["source_out_seconds"] = str(manifested["source_out_seconds"])
    json.dumps(manifested, ensure_ascii=False)
