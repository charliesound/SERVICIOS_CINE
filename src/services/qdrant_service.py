from __future__ import annotations

import os
from typing import Any

import httpx

from services.logging_service import logger


class QdrantService:
    def __init__(self) -> None:
        host = os.getenv("QDRANT_HOST", "127.0.0.1")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        scheme = os.getenv("QDRANT_SCHEME", "http")
        self.base_url = os.getenv("QDRANT_URL", f"{scheme}://{host}:{port}").rstrip("/")
        self.api_key = (os.getenv("QDRANT_API_KEY") or "").strip() or None
        self.timeout_seconds = float(os.getenv("QDRANT_TIMEOUT_SECONDS", "10"))

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            return {}
        return {"api-key": self.api_key}

    async def create_collection(self, *, name: str, vector_size: int, distance: str = "Cosine") -> bool:
        payload = {
            "vectors": {
                "size": int(vector_size),
                "distance": distance,
            }
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.put(
                    f"{self.base_url}/collections/{name}",
                    headers=self._headers(),
                    json=payload,
                )
            if response.status_code in (200, 201):
                return True
            logger.warning("Qdrant create_collection failed status=%s body=%s", response.status_code, response.text[:400])
            return False
        except Exception as exc:
            logger.warning("Qdrant create_collection exception name=%s error=%s", name, exc)
            return False

    async def upsert_points(self, *, collection: str, points: list[dict[str, Any]]) -> bool:
        if not points:
            return True
        payload = {"points": points}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.put(
                    f"{self.base_url}/collections/{collection}/points",
                    headers=self._headers(),
                    json=payload,
                )
            if response.status_code in (200, 201):
                return True
            logger.warning("Qdrant upsert_points failed status=%s body=%s", response.status_code, response.text[:400])
            return False
        except Exception as exc:
            logger.warning("Qdrant upsert_points exception collection=%s error=%s", collection, exc)
            return False

    async def semantic_search(
        self,
        *,
        collection: str,
        query_vector: list[float],
        limit: int = 5,
        filter_payload: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {
            "vector": query_vector,
            "limit": int(limit),
            "with_payload": True,
        }
        if filter_payload:
            payload["filter"] = filter_payload
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/collections/{collection}/points/search",
                    headers=self._headers(),
                    json=payload,
                )
            if response.status_code != 200:
                logger.warning("Qdrant semantic_search failed status=%s body=%s", response.status_code, response.text[:400])
                return []
            body = response.json()
            result = body.get("result")
            return result if isinstance(result, list) else []
        except Exception as exc:
            logger.warning("Qdrant semantic_search exception collection=%s error=%s", collection, exc)
            return []


qdrant_service = QdrantService()
