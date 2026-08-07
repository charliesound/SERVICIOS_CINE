"""Local embedding adapter contracts; no service call occurs on import."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence


PROVIDER = "ollama"
MODEL = "nomic-embed-text:v1.5"
DIMENSION = 768


class EmbeddingBackendError(RuntimeError):
    """Sanitized embedding backend failure."""


class EmbeddingBackend(Protocol):
    provider: str
    model: str
    dimension: int

    def embed(self, text: str) -> list[float]: ...


@dataclass(frozen=True)
class LocalEmbeddingConfig:
    provider: str = PROVIDER
    model: str = MODEL
    dimension: int = DIMENSION
    timeout_seconds: float = 30.0


class OllamaEmbeddingAdapter:
    """Adapter shell for the existing local Ollama contract.

    A callable is injected by implementation tests or a future runtime wiring layer. This
    keeps importing the semantic index side-effect free and prevents accidental network calls.
    """

    def __init__(
        self,
        embed_callable: Callable[[str], Sequence[float]] | None = None,
        config: LocalEmbeddingConfig | None = None,
    ) -> None:
        self.config = config or LocalEmbeddingConfig()
        self.provider = self.config.provider
        self.model = self.config.model
        self.dimension = self.config.dimension
        self._embed_callable = embed_callable

    def embed(self, text: str) -> list[float]:
        if self._embed_callable is None:
            raise EmbeddingBackendError("embedding backend unavailable")
        try:
            vector = [float(value) for value in self._embed_callable(text)]
        except Exception as exc:
            raise EmbeddingBackendError("embedding failed") from exc
        if len(vector) != self.dimension:
            raise EmbeddingBackendError("embedding dimension mismatch")
        return vector
