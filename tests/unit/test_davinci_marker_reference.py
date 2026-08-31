from __future__ import annotations

import io
import json
from decimal import Decimal
from fractions import Fraction
from xml.etree import ElementTree as ET

import pytest

import scripts.local_media_agent.editorial_selection_cli as editorial_selection_cli
from scripts.local_media_agent.davinci_marker_reference import (
    DAVINCI_REFERENCE_FORMAT,
    DAVINCI_REFERENCE_REASON_AUDIO_ONLY,
    DAVINCI_REFERENCE_REASON_NO_MAPPED_MARKER,
    build_davinci_reference,
    decimal_seconds_to_fcpxml_time,
    frame_duration_to_fps,
    media_path_to_uri,
    ndf_timecode_to_seconds,
    parse_source_frame_rate,
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


def test_fractional_ndf_timecode_uses_nominal_base_without_float_math() -> None:
    assert ndf_timecode_to_seconds(
        "00:00:01:00", Fraction(30000, 1001)
    ) == Fraction(1001, 1000)


def test_ndf_accepts_ff_37_at_50_source_rate() -> None:
    assert ndf_timecode_to_seconds("00:00:00:37", 50) == Fraction(37, 50)


def test_ndf_rejects_semicolon_drop_frame_notation() -> None:
    with pytest.raises(ValueError, match="invalid_ndf_timecode"):
        ndf_timecode_to_seconds("00:00:00;12", Fraction(30000, 1001))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("25/1", Fraction(25, 1)),
        ("50/1", Fraction(50, 1)),
        ("24000/1001", Fraction(24000, 1001)),
        (Fraction(60000, 1001), Fraction(60000, 1001)),
    ],
)
def test_approved_source_frame_rates_are_exact(raw, expected) -> None:
    assert parse_source_frame_rate(raw) == expected


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


def test_explicit_50_source_rate_separates_project_and_source_formats() -> None:
    ref = _ref(source_frame_rate="50/1", source_timecode_start="00:00:00:37")
    root = ET.fromstring(ref["fcpxml"])
    formats = root.findall("resources/format")
    asset = root.find("resources/asset")
    sequence = root.find(".//sequence")
    clip = root.find(".//asset-clip")
    marker = root.find(".//asset-clip/marker")

    assert [(item.get("id"), item.get("frameDuration")) for item in formats] == [
        ("r1", "1/25s"),
        ("r2", "1/50s"),
    ]
    assert asset.get("id") == "r3"
    assert asset.get("format") == "r2"
    assert asset.get("start") == "37/50s"
    assert clip.get("ref") == "r3"
    assert sequence.get("format") == "r1"
    assert marker.get("duration") == "1/25s"


def test_fractional_source_rate_emits_exact_reduced_reciprocal() -> None:
    ref = _ref(
        frame_duration="1/25s",
        source_frame_rate=Fraction(24000, 1001),
        source_timecode_start="00:00:00:23",
    )
    root = ET.fromstring(ref["fcpxml"])

    source_format = root.find("resources/format[@id='r2']")
    assert source_format.get("frameDuration") == "1001/24000s"
    assert root.find("resources/asset").get("start") == "23023/24000s"


@pytest.mark.parametrize(
    ("source_rate", "project_duration", "source_duration"),
    [
        ("25/1", "1/25s", "1/25s"),
        ("25/1", "1/50s", "1/25s"),
        ("24000/1001", "1/24s", "1001/24000s"),
        ("30000/1001", "1/25s", "1001/30000s"),
    ],
)
def test_normal_mode_keeps_source_and_project_formats_independent(
    source_rate, project_duration, source_duration
) -> None:
    root = ET.fromstring(
        _ref(
            source_frame_rate=source_rate,
            frame_duration=project_duration,
            source_timecode_start="00:00:01:00",
        )["fcpxml"]
    )
    assert root.find("resources/format[@id='r1']").get("frameDuration") == project_duration
    assert root.find("resources/format[@id='r2']").get("frameDuration") == source_duration
    assert root.find("resources/asset").get("format") == "r2"
    assert root.find(".//sequence").get("format") == "r1"


def test_30000_over_1001_ndf_source_start_is_exact_in_25_project() -> None:
    root = ET.fromstring(
        _ref(
            source_frame_rate="30000/1001",
            frame_duration="1/25s",
            source_timecode_start="00:00:01:00",
        )["fcpxml"]
    )
    assert root.find("resources/asset").get("start") == "1001/1000s"


def test_legacy_omission_keeps_single_shared_format_and_ids() -> None:
    root = ET.fromstring(_ref()["fcpxml"])

    formats = root.findall("resources/format")
    assert [(item.get("id"), item.get("frameDuration")) for item in formats] == [
        ("r1", "1/25s"),
    ]
    assert root.find("resources/asset").get("id") == "r2"
    assert root.find("resources/asset").get("format") == "r1"
    assert root.find(".//asset-clip").get("ref") == "r2"


@pytest.mark.parametrize(
    ("source_in", "source_out", "source_duration"),
    [(-1, 1, "10"), (2, 1, "10"), (1, 11, "10")],
)
def test_invalid_source_interval_refuses(source_in, source_out, source_duration) -> None:
    with pytest.raises(ValueError, match="invalid_source_interval"):
        _ref(
            package=_mapped_package(source_in=source_in, source_out=source_out),
            source_duration=source_duration,
        )


def test_cli_source_frame_rate_reaches_generator(monkeypatch) -> None:
    generated: dict[str, bytes] = {}

    def _prepare(**kwargs):
        assert kwargs["source_frame_rate"] == "50/1"
        generated["fcpxml"] = _ref(
            source_frame_rate=kwargs["source_frame_rate"]
        )["fcpxml"]
        return {
            "subject": "Subject",
            "topic": "Topic",
            "editorial_note": None,
            "video_clip": "clip.mov",
            "source_in_seconds": "0",
            "source_out_seconds": "1",
            "davinci_reference_path": kwargs["output_path"],
            "status": "READY_FOR_EDITOR",
        }

    monkeypatch.setattr(
        editorial_selection_cli,
        "prepare_davinci_reference_for_selection",
        _prepare,
    )
    code = editorial_selection_cli.run_cli(
        [
            "prepare-davinci",
            "--store", "store",
            "--selection", "selection",
            "--evidence-path", "evidence.json",
            "--media-path", MEDIA_PATH,
            "--frame-duration", "1/25s",
            "--source-timecode-start", SOURCE_TIMECODE_START,
            "--source-duration", SOURCE_DURATION,
            "--source-frame-rate", "50/1",
            "--output", "reference.fcpxml",
        ],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    )

    assert code == 0
    root = ET.fromstring(generated["fcpxml"])
    assert root.find("resources/format[@id='r2']").get("frameDuration") == "1/50s"


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
