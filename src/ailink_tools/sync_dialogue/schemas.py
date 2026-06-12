from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

SyncDialogueMediaKind = Literal["video", "audio", "other"]


@dataclass(frozen=True)
class SyncDialogueMediaFile:
    path: str
    relative_path: str
    filename: str
    extension: str
    kind: SyncDialogueMediaKind
    size_bytes: int
    probe_status: str  # "not_run" | "ok" | "failed" | "ffprobe_missing"
    duration_seconds: float | None = None
    timecode: str | None = None
    fps: float | None = None
    audio_channels: int | None = None
    codec_name: str | None = None
    format_name: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SyncDialogueMatchSuggestion:
    video_relative_path: str
    audio_relative_path: str
    confidence: str  # "high" | "medium" | "low"
    score: float
    strategy: str  # "timecode" | "metadata" | "duration_name" | "fallback"
    reasons: list[str]
    video_timecode: str | None = None
    audio_timecode: str | None = None
    video_duration_seconds: float | None = None
    audio_duration_seconds: float | None = None
    duration_delta_seconds: float | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SyncDialogueScanResult:
    root_path: str
    total_files: int
    video_count: int
    audio_count: int
    unsupported_count: int
    media_files: list[SyncDialogueMediaFile]
    match_suggestions: list[SyncDialogueMatchSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "root_path": self.root_path,
            "summary": {
                "total_files": self.total_files,
                "video_count": self.video_count,
                "audio_count": self.audio_count,
                "unsupported_count": self.unsupported_count,
            },
            "media_files": [media_file.to_dict() for media_file in self.media_files],
            "match_suggestions": [
                match_suggestion.to_dict()
                for match_suggestion in self.match_suggestions
            ],
        }
