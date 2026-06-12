from __future__ import annotations

from ailink_tools.sync_dialogue.matching import suggest_matches
from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMatchSuggestion,
    SyncDialogueMediaFile,
    SyncDialogueScanResult,
)


def _media(
    relative_path: str,
    *,
    kind: str,
    duration: float | None = None,
    timecode: str | None = None,
) -> SyncDialogueMediaFile:
    filename = relative_path.rsplit("/", 1)[-1]
    extension = "." + filename.rsplit(".", 1)[-1]
    return SyncDialogueMediaFile(
        path=f"/project/{relative_path}",
        relative_path=relative_path,
        filename=filename,
        extension=extension,
        kind=kind,  # type: ignore[arg-type]
        size_bytes=1,
        probe_status="ok",
        duration_seconds=duration,
        timecode=timecode,
    )


def _result(media_files: list[SyncDialogueMediaFile]) -> SyncDialogueScanResult:
    return SyncDialogueScanResult(
        root_path="/project",
        total_files=len(media_files),
        video_count=sum(1 for media_file in media_files if media_file.kind == "video"),
        audio_count=sum(1 for media_file in media_files if media_file.kind == "audio"),
        unsupported_count=0,
        media_files=media_files,
    )


def test_no_media_returns_no_matches() -> None:
    assert suggest_matches(_result([])) == []


def test_only_videos_returns_no_matches() -> None:
    result = _result([_media("scene01/clip.mov", kind="video")])
    assert suggest_matches(result) == []


def test_only_audios_returns_no_matches() -> None:
    result = _result([_media("scene01/sound.wav", kind="audio")])
    assert suggest_matches(result) == []


def test_same_timecode_creates_high_confidence_timecode_match() -> None:
    result = _result(
        [
            _media("scene01/A001.mov", kind="video", duration=10, timecode="01:00:00:00"),
            _media("scene01/A001.wav", kind="audio", duration=10.2, timecode="01:00:00:00"),
        ]
    )

    matches = suggest_matches(result)

    assert len(matches) == 1
    assert matches[0].confidence == "high"
    assert matches[0].strategy == "timecode"
    assert matches[0].score >= 0.90
    assert "matching_timecode" in matches[0].reasons


def test_different_timecode_does_not_create_timecode_match() -> None:
    result = _result(
        [
            _media("scene01/A001.mov", kind="video", duration=10, timecode="01:00:00:00"),
            _media("scene01/B001.wav", kind="audio", duration=40, timecode="02:00:00:00"),
        ]
    )

    matches = suggest_matches(result)

    assert not any(match.strategy == "timecode" for match in matches)


def test_duration_within_one_second_and_shared_token_matches_high() -> None:
    result = _result(
        [
            _media("day01/scene42_take03.mov", kind="video", duration=20.0),
            _media("audio/scene42_take03.wav", kind="audio", duration=20.8),
        ]
    )

    match = suggest_matches(result)[0]

    assert match.confidence == "high"
    assert match.strategy == "duration_name"
    assert "duration_delta_lte_1s" in match.reasons
    assert "shared_name_tokens" in match.reasons
    assert match.duration_delta_seconds == 0.8


def test_duration_within_three_seconds_and_related_folder_matches_medium() -> None:
    result = _result(
        [
            _media("day01/cam/shot07.mov", kind="video", duration=30.0),
            _media("day01/audio/sound07.wav", kind="audio", duration=32.5),
        ]
    )

    match = suggest_matches(result)[0]

    assert match.confidence == "medium"
    assert match.strategy == "metadata"
    assert "duration_delta_lte_3s" in match.reasons
    assert "related_folder" in match.reasons


def test_very_different_duration_without_secondary_signal_returns_no_match() -> None:
    result = _result(
        [
            _media("video/alpha.mov", kind="video", duration=10.0),
            _media("audio/beta.wav", kind="audio", duration=90.0),
        ]
    )

    assert suggest_matches(result) == []


def test_max_three_suggestions_per_video() -> None:
    result = _result(
        [
            _media("scene01/shot01.mov", kind="video", duration=10.0),
            _media("scene01/shot01_a.wav", kind="audio", duration=10.0),
            _media("scene01/shot01_b.wav", kind="audio", duration=10.1),
            _media("scene01/shot01_c.wav", kind="audio", duration=10.2),
            _media("scene01/shot01_d.wav", kind="audio", duration=10.3),
        ]
    )

    matches = suggest_matches(result)

    assert len(matches) == 3


def test_order_is_stable_by_video_score_and_audio_path() -> None:
    result = _result(
        [
            _media("b/shot.mov", kind="video", duration=10),
            _media("a/shot.mov", kind="video", duration=10),
            _media("a/shot_b.wav", kind="audio", duration=10),
            _media("a/shot_a.wav", kind="audio", duration=10),
        ]
    )

    matches = suggest_matches(result)

    assert [match.video_relative_path for match in matches][:2] == ["a/shot.mov", "a/shot.mov"]
    assert [match.audio_relative_path for match in matches][:2] == ["a/shot_a.wav", "a/shot_b.wav"]


def test_to_dict_includes_match_suggestions() -> None:
    suggestion = SyncDialogueMatchSuggestion(
        video_relative_path="clip.mov",
        audio_relative_path="clip.wav",
        confidence="high",
        score=0.95,
        strategy="timecode",
        reasons=["matching_timecode"],
    )
    result = _result([])
    result = SyncDialogueScanResult(
        root_path=result.root_path,
        total_files=result.total_files,
        video_count=result.video_count,
        audio_count=result.audio_count,
        unsupported_count=result.unsupported_count,
        media_files=result.media_files,
        match_suggestions=[suggestion],
    )

    payload = result.to_dict()

    assert payload["match_suggestions"] == [suggestion.to_dict()]


def test_matching_does_not_modify_media_files_originals() -> None:
    media_files = [
        _media("scene/shot.mov", kind="video", duration=10),
        _media("scene/shot.wav", kind="audio", duration=10),
    ]
    before = [media_file.to_dict() for media_file in media_files]

    suggest_matches(_result(media_files))

    assert [media_file.to_dict() for media_file in media_files] == before
