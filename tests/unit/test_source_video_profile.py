from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import create_project
from scripts.local_media_agent.media_catalog import media_item_key
from scripts.local_media_agent.sony_sidecar_parser import (
    SOURCE_COLOR_PROFILE_UNAVAILABLE,
)
from scripts.local_media_agent.source_video_profile import (
    CATALOG_VERSION,
    CID_ACTIVE_MEDIA_ROOT_REQUIRED,
    CID_SOURCE_MEDIA_PATH_INVALID,
    CID_SOURCE_VIDEO_CATALOG_INVALID,
    CID_SOURCE_VIDEO_DURATION_UNAVAILABLE,
    CID_SOURCE_VIDEO_RATE_AMBIGUOUS,
    CID_SOURCE_VIDEO_RATE_UNAVAILABLE,
    CID_SOURCE_VIDEO_RATE_VARIABLE_UNSUPPORTED,
    LEGACY_CATALOG_VERSION,
    PROFILE_MIGRATION_AUTO_MIGRATABLE,
    PROFILE_MIGRATION_BLOCKED,
    PROFILE_MIGRATION_USER_CONFIRMATION_REQUIRED,
    SourceVideoProfileError,
    build_source_video_profiles,
    classify_legacy_profile_migration,
    load_source_video_profiles,
    migrate_legacy_profile_to_v2,
    normalize_source_media_ref,
    resolve_source_media_path,
    resolve_source_video_profile,
    resolve_source_video_profile_by_media_ref,
    save_source_video_profiles,
)

PROJECT_ID = "PRJ-123e4567-e89b-42d3-a456-426614174000"
SRC_A = "SRC-11111111-1111-4111-8111-111111111111"
SRC_B = "SRC-22222222-2222-4222-8222-222222222222"


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


def test_v1_builder_output_remains_legacy_version() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    assert catalog["version"] == LEGACY_CATALOG_VERSION
    entry = catalog["entries"][0]
    assert "source_id" not in entry
    assert "media_ref" not in entry


def test_v1_loader_still_loads_roundtrip(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    save_source_video_profiles(catalog, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == catalog


def test_explicit_source_id_produces_v2() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    assert catalog["version"] == CATALOG_VERSION
    entry = catalog["entries"][0]
    assert entry["source_id"] == SRC_A


def test_v2_source_media_ref_remains_bare_relative_path() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    assert catalog["entries"][0]["source_media_ref"] == "M4ROOT/CLIP/A001.MP4"


def test_v2_media_ref_equals_media_item_key() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    expected = media_item_key(SRC_A, "M4ROOT/CLIP/A001.MP4")
    assert catalog["entries"][0]["media_ref"] == expected
    assert catalog["entries"][0]["media_ref"] == f"{SRC_A}::M4ROOT/CLIP/A001.MP4"


def test_same_relative_path_distinct_sources_distinct_media_ref() -> None:
    a = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )["entries"][0]
    b = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_B
    )["entries"][0]
    assert a["source_media_ref"] == b["source_media_ref"]
    assert a["media_ref"] != b["media_ref"]


def test_v2_source_media_ref_may_repeat_across_sources() -> None:
    a = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    b = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_B
    )
    merged = {
        "format": a["format"],
        "version": CATALOG_VERSION,
        "project_id": PROJECT_ID,
        "entries": a["entries"] + b["entries"],
    }
    assert merged["entries"][0]["source_media_ref"] == merged["entries"][1]["source_media_ref"]
    assert merged["entries"][0]["media_ref"] != merged["entries"][1]["media_ref"]


def test_duplicate_media_ref_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    dup = dict(catalog["entries"][0])
    dup["source_media_ref"] = "OTHER/a.MP4"
    dup["source_filename"] = "a.MP4"
    dup["media_ref"] = catalog["entries"][0]["media_ref"]
    catalog["entries"].append(dup)
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_source_filename_derived_from_source_media_ref_v2() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    assert catalog["entries"][0]["source_filename"] == "A001.MP4"
    assert "::" not in catalog["entries"][0]["source_filename"]


def test_v2_missing_source_id_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    del catalog["entries"][0]["source_id"]
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_v2_missing_media_ref_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    del catalog["entries"][0]["media_ref"]
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_v2_invalid_source_id_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    catalog["entries"][0]["source_id"] = "not-a-source-id"
    catalog["entries"][0]["media_ref"] = media_item_key(
        "not-a-source-id", "M4ROOT/CLIP/A001.MP4"
    )
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_v2_media_ref_mismatch_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    catalog["entries"][0]["media_ref"] = "SRC-99999999-9999-4999-8999-999999999999::x"
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_unknown_catalog_version_rejected(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    catalog["version"] = 99
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)


def test_v1_namespaced_string_not_auto_interpreted_as_source_id(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    catalog["entries"][0]["source_media_ref"] = f"{SRC_A}::M4ROOT/CLIP/A001.MP4"
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        save_source_video_profiles(catalog, local_appdata=tmp_path)
    catalog2 = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    assert catalog2["version"] == LEGACY_CATALOG_VERSION


def test_legacy_single_source_classified_auto_migratable() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    assert classify_legacy_profile_migration(catalog, [SRC_A]) == PROFILE_MIGRATION_AUTO_MIGRATABLE


def test_legacy_multiple_source_classified_user_confirmation() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    assert (
        classify_legacy_profile_migration(catalog, [SRC_A, SRC_B])
        == PROFILE_MIGRATION_USER_CONFIRMATION_REQUIRED
    )


def test_malformed_legacy_catalog_classified_blocked() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("roll/clip.mov")])
    del catalog["project_id"]
    assert classify_legacy_profile_migration(catalog, [SRC_A]) == PROFILE_MIGRATION_BLOCKED


def test_invalid_source_id_classified_blocked() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    assert classify_legacy_profile_migration(catalog, ["BAD"]) == PROFILE_MIGRATION_BLOCKED


def test_clean_v1_to_v2_migration_preserves_entry_count() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4"), item("M4ROOT/CARD/A002.MP4")]
    )
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["version"] == CATALOG_VERSION
    assert len(migrated["entries"]) == len(catalog["entries"])


def test_migration_preserves_source_media_ref_exactly() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["entries"][0]["source_media_ref"] == "M4ROOT/CLIP/A001.MP4"


def test_migration_preserves_technical_profile_payload(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    media = item("M4ROOT/CLIP/A001.MP4")
    media["source_color_profile"] = dict(COLOR_PROFILE_CONFIRMED)
    catalog = build_source_video_profiles(PROJECT_ID, [media])
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    entry = migrated["entries"][0]
    assert entry["source_frame_rate"] == "50/1"
    assert entry["source_duration_raw"] == "12.340000"
    assert entry["source_color_profile"] == COLOR_PROFILE_CONFIRMED
    assert entry["source_id"] == SRC_A
    assert entry["media_ref"] == media_item_key(SRC_A, "M4ROOT/CLIP/A001.MP4")


def test_migration_zero_media_access(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["entries"][0]["source_media_ref"] == "M4ROOT/CLIP/A001.MP4"
    assert not (tmp_path / "media" / "M4ROOT").exists()


def test_migration_zero_ffprobe(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["entries"][0]["media_ref"] == media_item_key(SRC_A, "M4ROOT/CLIP/A001.MP4")


def test_migration_zero_sony_reparse(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    media = item("M4ROOT/CLIP/A001.MP4")
    media["source_color_profile"] = dict(COLOR_PROFILE_CONFIRMED)
    catalog = build_source_video_profiles(PROJECT_ID, [media])
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["entries"][0]["source_color_profile"] == COLOR_PROFILE_CONFIRMED


def test_migration_whole_file_output_validates_before_save(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4"), item("M4ROOT/CLIP/A002.MP4")]
    )
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    save_source_video_profiles(migrated, local_appdata=tmp_path)
    assert load_source_video_profiles(PROJECT_ID, local_appdata=tmp_path) == migrated
    assert all(e["source_id"] == SRC_A for e in migrated["entries"])


def test_migration_no_mixed_v1_v2_entries(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4"), item("M4ROOT/CLIP/A002.MP4")]
    )
    migrated = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert migrated["version"] == CATALOG_VERSION
    assert all("source_id" in e and "media_ref" in e for e in migrated["entries"])


def test_migration_rerun_idempotent() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")])
    first = migrate_legacy_profile_to_v2(catalog, SRC_A)
    second = migrate_legacy_profile_to_v2(first, SRC_A)
    assert second == first
    assert len(second["entries"]) == 1


def test_already_v2_same_source_converges() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A)
    result = migrate_legacy_profile_to_v2(catalog, SRC_A)
    assert result is catalog


def test_already_v2_conflicting_source_fails_closed() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A)
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_CATALOG_INVALID):
        migrate_legacy_profile_to_v2(catalog, SRC_B)


def test_no_absolute_path_in_v2() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A)
    entry = catalog["entries"][0]
    for key in ("current_location", "absolute_path", "root_path", "drive", "mount_path"):
        assert key not in entry


def test_no_online_offline_state_in_v2() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A)
    entry = catalog["entries"][0]
    for key in ("ONLINE", "OFFLINE", "DETACHED", "RECONNECTED", "state"):
        assert key not in entry


def test_legacy_resolve_behavior_unchanged() -> None:
    catalog = build_source_video_profiles(PROJECT_ID, [item("a/clip.mov")])
    assert resolve_source_video_profile(catalog, "a/clip.mov")["source_media_ref"] == "a/clip.mov"


def test_v2_canonical_media_ref_lookup() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    entry = resolve_source_video_profile_by_media_ref(
        catalog, media_item_key(SRC_A, "M4ROOT/CLIP/A001.MP4")
    )
    assert entry["source_id"] == SRC_A


def test_v2_bare_lookup_single_match_ok() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    entry = resolve_source_video_profile(catalog, "M4ROOT/CLIP/A001.MP4")
    assert entry["source_id"] == SRC_A


def test_v2_bare_lookup_two_sources_fails_ambiguous() -> None:
    a = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    b = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_B
    )
    both = dict(a)
    both["entries"] = a["entries"] + b["entries"]
    with pytest.raises(SourceVideoProfileError, match=CID_SOURCE_VIDEO_RATE_AMBIGUOUS):
        resolve_source_video_profile(both, "M4ROOT/CLIP/A001.MP4")


def test_resolve_source_media_path_receives_bare_relative_path(tmp_path: Path) -> None:
    root = tmp_path / "media"
    clip = root / "M4ROOT" / "CLIP" / "A001.MP4"
    clip.parent.mkdir(parents=True)
    clip.write_bytes(b"synthetic")
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    ref = catalog["entries"][0]["source_media_ref"]
    assert "::" not in ref
    assert resolve_source_media_path(root, ref) == clip.resolve()


def test_media_item_key_encoding_reused_no_duplicate_delimiter() -> None:
    catalog = build_source_video_profiles(
        PROJECT_ID, [item("M4ROOT/CLIP/A001.MP4")], source_id=SRC_A
    )
    expected = f"{SRC_A}::M4ROOT/CLIP/A001.MP4"
    assert catalog["entries"][0]["media_ref"] == expected == media_item_key(SRC_A, "M4ROOT/CLIP/A001.MP4")
