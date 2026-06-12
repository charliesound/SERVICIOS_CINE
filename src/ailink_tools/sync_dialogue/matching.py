from __future__ import annotations

import re
from pathlib import PurePosixPath

from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMatchSuggestion,
    SyncDialogueMediaFile,
    SyncDialogueScanResult,
)

GENERIC_TOKENS = frozenset(
    {
        "cam",
        "camera",
        "audio",
        "sound",
        "wav",
        "mov",
        "mp4",
        "mxf",
        "clip",
        "video",
        "take",
    }
)
MAX_SUGGESTIONS_PER_VIDEO = 3


def suggest_matches(result: SyncDialogueScanResult) -> list[SyncDialogueMatchSuggestion]:
    videos = [media_file for media_file in result.media_files if media_file.kind == "video"]
    audios = [media_file for media_file in result.media_files if media_file.kind == "audio"]
    suggestions: list[SyncDialogueMatchSuggestion] = []

    for video in videos:
        per_video: list[SyncDialogueMatchSuggestion] = []
        for audio in audios:
            suggestion = _suggest_match(video, audio)
            if suggestion is not None:
                per_video.append(suggestion)
        per_video.sort(key=lambda item: (-item.score, item.audio_relative_path))
        suggestions.extend(per_video[:MAX_SUGGESTIONS_PER_VIDEO])

    return sorted(
        suggestions,
        key=lambda item: (item.video_relative_path, -item.score, item.audio_relative_path),
    )


def _suggest_match(
    video: SyncDialogueMediaFile, audio: SyncDialogueMediaFile
) -> SyncDialogueMatchSuggestion | None:
    duration_delta = _duration_delta(video, audio)
    if video.timecode and audio.timecode and video.timecode == audio.timecode:
        return _build_suggestion(
            video,
            audio,
            score=0.95,
            strategy="timecode",
            reasons=["matching_timecode"],
            duration_delta_seconds=duration_delta,
        )

    score = 0.0
    reasons: list[str] = []
    if duration_delta is not None:
        if duration_delta <= 1.0:
            score += 0.55
            reasons.append("duration_delta_lte_1s")
        elif duration_delta <= 3.0:
            score += 0.45
            reasons.append("duration_delta_lte_3s")

    if _shared_name_tokens(video, audio):
        score += 0.30
        reasons.append("shared_name_tokens")

    if _related_folder(video, audio):
        score += 0.15
        reasons.append("related_folder")

    if score < 0.40:
        return None

    strategy = "duration_name" if "shared_name_tokens" in reasons else "metadata"
    return _build_suggestion(
        video,
        audio,
        score=min(score, 0.89),
        strategy=strategy,
        reasons=reasons or ["fallback_metadata"],
        duration_delta_seconds=duration_delta,
    )


def _build_suggestion(
    video: SyncDialogueMediaFile,
    audio: SyncDialogueMediaFile,
    *,
    score: float,
    strategy: str,
    reasons: list[str],
    duration_delta_seconds: float | None,
) -> SyncDialogueMatchSuggestion:
    score = round(score, 3)
    return SyncDialogueMatchSuggestion(
        video_relative_path=video.relative_path,
        audio_relative_path=audio.relative_path,
        confidence=_confidence_for_score(score),
        score=score,
        strategy=strategy,
        reasons=reasons,
        video_timecode=video.timecode,
        audio_timecode=audio.timecode,
        video_duration_seconds=video.duration_seconds,
        audio_duration_seconds=audio.duration_seconds,
        duration_delta_seconds=duration_delta_seconds,
    )


def _duration_delta(
    video: SyncDialogueMediaFile, audio: SyncDialogueMediaFile
) -> float | None:
    if video.duration_seconds is None or audio.duration_seconds is None:
        return None
    return round(abs(video.duration_seconds - audio.duration_seconds), 3)


def _confidence_for_score(score: float) -> str:
    if score >= 0.85:
        return "high"
    if score >= 0.55:
        return "medium"
    return "low"


def _shared_name_tokens(video: SyncDialogueMediaFile, audio: SyncDialogueMediaFile) -> bool:
    return bool(_tokens_from_stem(video.filename) & _tokens_from_stem(audio.filename))


def _related_folder(video: SyncDialogueMediaFile, audio: SyncDialogueMediaFile) -> bool:
    video_parent = PurePosixPath(video.relative_path).parent
    audio_parent = PurePosixPath(audio.relative_path).parent
    if str(video_parent) != "." and video_parent == audio_parent:
        return True
    video_tokens = _tokens_from_text(str(video_parent))
    audio_tokens = _tokens_from_text(str(audio_parent))
    return bool(video_tokens & audio_tokens)


def _tokens_from_stem(filename: str) -> set[str]:
    return _tokens_from_text(PurePosixPath(filename).stem)


def _tokens_from_text(value: str) -> set[str]:
    tokens = re.split(r"[\s_\-.\\/]+", value.lower())
    return {
        token
        for token in tokens
        if len(token) >= 2 and token not in GENERIC_TOKENS
    }
