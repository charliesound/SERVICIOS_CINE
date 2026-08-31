from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from scripts.local_media_agent.local_project import create_project, project_video_profile_path
from scripts.local_media_agent.project_video_profile import (
    CID_RECOMMENDED_CONFIRMED,
    CONFIRMED,
    NOT_CONFIRMED,
    USER_CONFIRMED,
    ProjectVideoProfileError,
    analyze_source_video_metadata,
    confirm_project_video_profile,
    create_project_video_profile,
    fcpxml_frame_duration,
    postpone_project_video_profile,
    load_project_video_profile,
    update_project_video_configuration,
)

PROJECT_ID = "PRJ-123e4567-e89b-42d3-a456-426614174000"
RATES = {
    "24000/1001": "1001/24000s", "24/1": "1/24s", "25/1": "1/25s",
    "30000/1001": "1001/30000s", "30/1": "1/30s", "50/1": "1/50s",
    "60000/1001": "1001/60000s", "60/1": "1/60s",
}


def item(rate: str, *, vfr: bool = False, width: int = 1920, height: int = 1080) -> dict:
    return {
        "category": "video",
        "video": {
            "width": width, "height": height,
            "frame_rate": {"raw_avg": rate, "raw_frame": rate, "variable": vfr},
        },
    }


@pytest.mark.parametrize(("rate", "duration"), RATES.items())
def test_supported_rates_have_exact_reciprocals(rate: str, duration: str) -> None:
    assert fcpxml_frame_duration(rate) == duration
    with pytest.raises(ProjectVideoProfileError):
        fcpxml_frame_duration(float(Fraction(rate)))


def test_25_50_acquisition_mix_recommends_25_but_never_confirms(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    summary = analyze_source_video_metadata([item("25/1") for _ in range(8)] + [item("50/1") for _ in range(2)])
    profile = create_project_video_profile(PROJECT_ID, summary, local_appdata=tmp_path)
    assert profile["recommendation"]["timeline_frame_rate"] == {"numerator": 25, "denominator": 1}
    assert profile["confirmation_status"] == NOT_CONFIRMED
    assert profile["decision_authority"] is None
    assert "project_name" not in profile
    configured = update_project_video_configuration(
        PROJECT_ID, "25/1", (1920, 1080), local_appdata=tmp_path
    )
    confirmed = confirm_project_video_profile(
        PROJECT_ID,
        decision_authority=CID_RECOMMENDED_CONFIRMED,
        confirmed_by_role="PRODUCER",
        local_appdata=tmp_path,
    )
    assert configured["confirmation_status"] == NOT_CONFIRMED
    assert confirmed["confirmation_status"] == CONFIRMED


@pytest.mark.parametrize(
    "metadata",
    [[item("25/1", vfr=True)], [item("25/1") for _ in range(5)] + [item("24/1") for _ in range(5)]],
)
def test_vfr_and_ambiguous_distributions_have_no_recommendation(tmp_path: Path, metadata: list[dict]) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    profile = create_project_video_profile(
        PROJECT_ID, analyze_source_video_metadata(metadata), local_appdata=tmp_path
    )
    assert profile["recommendation"]["available"] is False
    assert profile["confirmation_status"] == NOT_CONFIRMED


def test_explicit_manual_confirmation_postpone_and_revision_invalidation(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    create_project_video_profile(
        PROJECT_ID, analyze_source_video_metadata([item("25/1")]), local_appdata=tmp_path
    )
    configured = update_project_video_configuration(
        PROJECT_ID, "25/1", (1920, 1080), local_appdata=tmp_path
    )
    assert configured["confirmation_status"] == NOT_CONFIRMED
    confirmed = confirm_project_video_profile(
        PROJECT_ID,
        decision_authority=USER_CONFIRMED,
        confirmed_by_role="EDITOR",
        local_appdata=tmp_path,
    )
    assert confirmed["confirmation_status"] == CONFIRMED
    changed = update_project_video_configuration(
        PROJECT_ID, "50/1", (3840, 2160), local_appdata=tmp_path
    )
    assert changed["profile_revision"] == confirmed["profile_revision"] + 1
    assert changed["confirmation_status"] == NOT_CONFIRMED
    assert changed["decision_authority"] is None
    reconfirmed = confirm_project_video_profile(
        PROJECT_ID,
        decision_authority=USER_CONFIRMED,
        confirmed_by_role="PRODUCER",
        local_appdata=tmp_path,
    )
    postponed = postpone_project_video_profile(PROJECT_ID, local_appdata=tmp_path)
    assert reconfirmed["confirmation_status"] == CONFIRMED
    assert postponed["confirmation_status"] == NOT_CONFIRMED


def test_malformed_nested_profile_fails_with_controlled_error(tmp_path: Path) -> None:
    create_project("P", local_appdata=tmp_path, project_id=PROJECT_ID)
    profile = create_project_video_profile(
        PROJECT_ID, analyze_source_video_metadata([item("25/1")]), local_appdata=tmp_path
    )
    profile["timeline_frame_rate"] = None
    project_video_profile_path(PROJECT_ID, tmp_path).write_text(
        json.dumps(profile), encoding="utf-8"
    )
    with pytest.raises(ProjectVideoProfileError, match="CID_PROJECT_VIDEO_PROFILE_INVALID"):
        load_project_video_profile(PROJECT_ID, local_appdata=tmp_path)
