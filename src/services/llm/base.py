from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class LLMRequest:
    system_prompt: str
    user_prompt: str
    temperature: float = 0.2
    timeout_seconds: int = 120
    json_mode: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMResponse:
    provider: str
    model: str
    content: str
    raw: dict[str, Any] | None = None
    json_mode: bool = False


@dataclass(slots=True)
class LLMStatus:
    provider: str
    model: str
    base_url: str
    available: bool
    error_message: Optional[str] = None


class BaseLLMProvider(ABC):
    provider_name: str = "base"

    @abstractmethod
    async def chat(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    async def get_status(self) -> LLMStatus:
        raise NotImplementedError
