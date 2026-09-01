from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import create_project
from scripts.local_media_agent.sony_sidecar_parser import (
    SOURCE_COLOR_PROFILE_UNAVAILABLE,
)
from scripts.local_media_agent.source_video_profile import (
    CID_ACTIVE_MEDIA_ROOT_REQUIRED,
    CID_SOURCE_MEDIA_PATH_INVALID,
    CID_SOURCE_VIDEO_CATALOG_INVALID,
    CID_SOURCE_VIDEO_DURATION_UNAVAILABLE,
    CID_SOURCE_VIDEO_RATE_AMBIGUOUS,
    CID_SOURCE_VIDEO_RATE_UNAVAILABLE,
    CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED,
    SourceVideoProfileError,
    build_source_video_profiles,
    load_source_video_profiles,
    normalize_source_media_ref,
    resolve_source_media_path,
    resolve_source_video_profile,
    save_source_video_profiles,
)

PROJECT_ID = "PRJ-123e4567-e89b-42d3-a456-426614174000"


def item(
    reference: str,
    *,
    avg: str | None = "50/1",
    raw: str | None = "50/1",
    vfr: bool = False,
    duration: str | None = "12.340000",
) -> dict:
    return {
        "category": "video", "relative_path": reference,
        "duration_raw": duration, "duration_origin": "format",
        "timecode": "10:24:12:37",
        "video": {
            "width": 3840, "height": 2160,
            "frame_rate": {"raw_avg": avg, "raw_frame": raw, "variable": vfr},
        },
    }


def test_catalog_is_sanitized_exact_and_independent_of_project_rate(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll\\clip.mov")])
    entry = catalog["entries"][0]
    assert entry["source_media_ref"] == "roll/clip.mov"
    assert entry["source_filename"] == "clip.mov"
    assert entry["source_frame_rate"] == "50/1"
    assert entry["source_duration_raw"] == "12.340000"
    assert "duration_seconds" not in entry
    assert "project" not in str(entry).lower()
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


@pytest.mark.parametrize("reference", ["/clip.mov", "../clip.mov", "a/../clip.mov", "C:/clip.mov"])
def test_absolute_and_traversal_identity_rejected(reference: str) -> None:
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_MEDIA_PATH_INVALID):
        normalize_source_media_ref(reference)


def test_exact_lookup_then_unique_basename_and_duplicate_refusal() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("a/clip.mov"), item("b/clip.mov"), item("c/unique.mov")]
    )
    assert resolve_source_video_profile(catalog, "a/clip.mov")["source_media_ref"] == "a/clip.mov"
    assert resolve_source_video_profile(catalog, "unique.mov")["source_media_ref"] == "c/unique.mov"
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_RATE_AMBIGUOUS):
        resolve_source_video_profile(catalog, "clip.mov")


@pytest.mark.parametrize(
    ("source", "code"),
    [
        (item("vfr.mov", vfr=True), CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED),
        (item("missing.mov", avg=None, raw=None), CID_SOURCE_VIDEO_RATE_UNAVAILABLE),
        (item("conflict.mov", avg="25/1", raw="50/1"), CID_SOURCE_VIDEO_RATE_AMBIGUOUS),
        (item("duration.mov", duration=None), CID_SOURCE_VIDEO_DURATION_UNAVAILABLE),
    ],
)
def test_invalid_source_authorities_refuse_at_resolution(source: dict, code: str) -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [source])
    with pytest.raises(SourceVideoProfileError, match=code):
        resolve_source_video_profile(catalog, source["relative_path"])


def test_active_media_root_resolution_and_escape_refusal(tmp_path: Path) -> None:
    with pytest.raises(SourceVideoProfileError, match=CID_ACTIVE_MEDIA_ROOT_REQUIRED):
        resolve_source_media_path(None, "clip.mov")
    root = tmp_path / "media"
    clip = root / "roll" / "clip.mov"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"synthetic")
    assert resolve_source_media_path(root, "roll/clip.mov") == clip.resolve()
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_MEDIA_PATH_INVALID):
        resolve_source_media_path(root, "../outside.mov")


def test_source_sar_dar_and_rotation_persisted_exactly(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    media = {
        "category": "video", "relative_path": "roll/anamorphic.mov",
        "duration_raw": "12.340000", "duration_origin": "format",
        "timecode": "10:24:12:37",
        "video": {
            "width": 1920, "height": 1080,
            "frame_rate": {"raw_avg": "50/1", "raw_frame": "50/1", "variable": False},
            "sample_aspect_ratio": {"numerator": 2, "denominator": 1},
            "display_aspect_ratio": {"numerator": 4, "denominator": 3},
            "rotation": 90,
        },
    }
    catalog = build_source_video_profiles(PROJECT_ID, [media])
    entry = catalog["entries"][0]
    assert entry["source_sample_aspect_ratio"] == {"numerator": 2, "denominator": 1}
    assert entry["source_display_aspect_ratio"] == {"numerator": 4, "denominator": 3}
    assert entry["source_rotation"] == 90
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


def test_missing_sar_dar_rotation_are_null_not_invented(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("plain.mov", avg="25/1", raw="25/1")]
    )
    entry = catalog["entries"][0]
    assert entry["source_sample_aspect_ratio"] is None
    assert entry["source_display_aspect_ratio"] is None
    assert entry["source_rotation"] is None


def test_invalid_sar_dar_or_rotation_catalog_is_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("ok.mov", avg="25/1", raw="25/1")])
    catalog["entries"][0]["source_sample_aspect_ratio"] = {"numerator": 0, "denominator": 1}
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


COLOR_PROFILE_CONFIRMED = {
    "capture_gamma_raw": "s-log3-cine",
    "capture_color_primaries_raw": "s-gamut3-cine",
    "coding_equations_raw": "rec709",
    "capture_gamma_display": "S-Log3",
    "capture_gamut_display": "S-Gamut3.Cine",
    "monitoring_lut_status": "NOT_RECORDED",
    "monitoring_lut_identity": None,
    "metadata_source": "SONY_XML_SIDECAR",
    "metadata_confidence": "CONFIRMED",
    "sidecar_path": "CARD/A7IV_SL31404M01.XML",
}


def test_source_color_profile_persisted_roundtrip(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    media = item("CARD/A7IV_SL31404.MP4")
    media["source_color_profile"] = dict(COLOR_PROFILE_CONFIRMED)
    catalog = build_source_video_profiles(PROJECT_ID, [media])
    entry = catalog["entries"][0]
    assert entry["source_color_profile"] == COLOR_PROFILE_CONFIRMED
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


def test_media_without_sidecar_gets_stable_unavailable_color_profile(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    assert catalog["entries"][0]["source_color_profile"] == SOURCE_COLOR_PROFILE_UNAVAILABLE
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


def test_legacy_catalog_without_color_profile_still_validates(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/legacy.mov")])
    for entry in catalog["entries"]:
        del entry["source_color_profile"]
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


def test_invalid_source_color_profile_catalog_is_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("ok.mov")])
    catalog["entries"][0]["source_color_profile"] = {"capture_gamma_raw": "s-log3-cine"}
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)
