from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import httpx

from core.config import get_settings
from services.logging_service import logger


class RagEmbeddingService:
    def __init__(self) -> None:
        settings = get_settings()
        self.provider: str = settings.embedding_provider
        self.model: str = settings.embedding_model
        self.vector_size: int = settings.embedding_vector_size
        self.ollama_url: str = settings.ollama_url.rstrip("/")
        self.timeout_seconds: float = float(os.getenv("OLLAMA_EMBED_TIMEOUT_SECONDS", "30"))
        self._validate_config()

    def _validate_config(self) -> None:
        if self.provider != "ollama":
            logger.warning("Embedding provider '%s' not fully implemented, using ollama", self.provider)

    async def embed(self, text: str) -> list[float]:
        vectors = await self.embed_batch([text])
        return vectors[0] if vectors else []

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors: list[list[float]] = []
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            for text in texts:
                vector = await self._embed_one(client, text)
                vectors.append(vector)
        return vectors

    async def _embed_one(self, client: httpx.AsyncClient, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self.vector_size
        try:
            response = await client.post(
                f"{self.ollama_url}/api/embed",
                json={"model": self.model, "input": text},
            )
            response.raise_for_status()
            body: dict[str, Any] = response.json()
            raw = body.get("embeddings")
            if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], list):
                vector = [float(v) for v in raw[0]]
            else:
                raw_single = body.get("embedding")
                if isinstance(raw_single, list):
                    vector = [float(v) for v in raw_single]
                else:
                    raise RuntimeError(f"Unexpected Ollama embed response structure: {list(body.keys())}")
            if len(vector) != self.vector_size:
                logger.warning(
                    "Embedding dimension mismatch: got %d, expected %d",
                    len(vector), self.vector_size,
                )
            return vector
        except Exception as exc:
            logger.error("Embedding failed for text (len=%d): %s", len(text), exc)
            raise

    async def embed_query(self, query: str) -> list[float]:
        return await self.embed(query)


rag_embedding_service = RagEmbeddingService()
