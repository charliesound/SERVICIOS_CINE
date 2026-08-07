"""Local embedding adapter contracts; no service call occurs on import."""

from __future__ import annotations

import math
from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

import httpx


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
    """Lazy, loopback-only adapter for the CID ``/api/embed`` contract."""

    def __init__(
        self,
        embed_callable: Callable[[str], Sequence[float]] | None = None,
        config: LocalEmbeddingConfig | None = None,
        endpoint_url: str = "http://127.0.0.1:11434",
        client: httpx.Client | None = None,
    ) -> None:
        self.config = config or LocalEmbeddingConfig()
        self.provider = self.config.provider
        self.model = self.config.model
        self.dimension = self.config.dimension
        self._embed_callable = embed_callable
        self.endpoint_url = validate_loopback_url(endpoint_url)
        self._client = client

    def embed(self, text: str) -> list[float]:
        if self._embed_callable is not None:
            return self._validate_vector(self._embed_callable(text))
        try:
            response = self._http_client().post(
                f"{self.endpoint_url}/api/embed",
                json={"model": self.model, "input": text},
            )
            response.raise_for_status()
            body = response.json()
            raw = body.get("embeddings") if isinstance(body, dict) else None
            if isinstance(raw, list) and raw and isinstance(raw[0], list):
                return self._validate_vector(raw[0])
            raw_single = body.get("embedding") if isinstance(body, dict) else None
            if isinstance(raw_single, list):
                return self._validate_vector(raw_single)
            raise EmbeddingBackendError("embedding response invalid")
        except EmbeddingBackendError:
            raise
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            raise EmbeddingBackendError("embedding unavailable") from exc
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as exc:
            raise EmbeddingBackendError("embedding failed") from exc

    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self.config.timeout_seconds)
        return self._client

    def _validate_vector(self, values: Sequence[float]) -> list[float]:
        try:
            vector = [float(value) for value in values]
        except (TypeError, ValueError) as exc:
            raise EmbeddingBackendError("embedding response invalid") from exc
        if len(vector) != self.dimension:
            raise EmbeddingBackendError("embedding dimension mismatch")
        if not all(math.isfinite(value) for value in vector):
            raise EmbeddingBackendError("embedding response invalid")
        return vector


def validate_loopback_url(value: str) -> str:
    """Return a normalized URL only when its host is an approved loopback name."""
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
        raise ValueError("backend endpoint must be a loopback HTTP URL")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("backend endpoint must be loopback")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("backend endpoint must not contain a path or query")
    return value.rstrip("/")
