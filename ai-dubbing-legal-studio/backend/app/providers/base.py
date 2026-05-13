from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSInput:
    text: str
    language: str
    voice_id: Optional[str] = None
    speed: float = 1.0


@dataclass
class TTSOutput:
    audio_path: str
    duration_seconds: float
    provider: str
    model_used: str


class BaseTTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, input_data: TTSInput) -> TTSOutput:
        ...


@dataclass
class LipSyncInput:
    video_path: str
    audio_path: str
    face_id: Optional[str] = None


@dataclass
class LipSyncOutput:
    video_path: str
    duration_seconds: float
    provider: str
    model_used: str


class BaseLipSyncProvider(ABC):
    @abstractmethod
    async def process(self, input_data: LipSyncInput) -> LipSyncOutput:
        ...
