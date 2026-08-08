"""Vector-store adapter contracts for the isolated editorial collection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

import httpx

from scripts.editorial_intelligence.semantic_index.embedding_backend import validate_loopback_url


COLLECTION_NAME = "cid_editorial_transcripts_v1"
VECTOR_DIMENSION = 768
DISTANCE_METRIC = "Cosine"


class VectorStoreError(RuntimeError):
    """Sanitized vector-store failure."""


@dataclass(frozen=True)
class VectorPoint:
    point_id: str
    vector: tuple[float, ...]
    payload: dict[str, Any]


@dataclass(frozen=True)
class VectorHit:
    point_id: str
    score: float
    payload: dict[str, Any]


@dataclass(frozen=True)
class ReadPoint:
    point_id: str
    payload: dict[str, Any]


class VectorStore(Protocol):
    def replace_corpus(self, corpus_id: str, points: Sequence[VectorPoint]) -> None: ...

    def delete_corpus(self, corpus_id: str) -> None: ...

    def search(
        self,
        *,
        corpus_id: str,
        vector: Sequence[float],
        limit: int,
        filters: dict[str, Any],
    ) -> list[VectorHit]: ...


class QdrantVectorStore:
    """Lazy loopback-only REST implementation of the editorial VectorStore contract."""

    def __init__(
        self,
        endpoint_url: str = "http://127.0.0.1:6333",
        collection: str = COLLECTION_NAME,
        timeout_seconds: float = 10.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.endpoint_url = validate_loopback_url(endpoint_url)
        self.collection = _validate_collection_name(collection)
        self.timeout_seconds = timeout_seconds
        self._client = client

    def replace_corpus(self, corpus_id: str, points: Sequence[VectorPoint]) -> None:
        self._ensure_collection()
        self.delete_corpus(corpus_id)
        if not points:
            return
        self._request(
            "PUT",
            f"/collections/{self.collection}/points",
            json={
                "points": [
                    {"id": point.point_id, "vector": list(point.vector), "payload": point.payload}
                    for point in points
                ],
                "wait": True,
            },
            error_code="index write failed",
        )

    def delete_corpus(self, corpus_id: str) -> None:
        self._ensure_collection()
        self._request(
            "POST",
            f"/collections/{self.collection}/points/delete",
            json={"filter": _filter_payload({"corpus_id": corpus_id}), "wait": True},
            error_code="vector store unavailable",
        )

    def search(
        self,
        *,
        corpus_id: str,
        vector: Sequence[float],
        limit: int,
        filters: dict[str, Any],
    ) -> list[VectorHit]:
        body = self._request(
            "POST",
            f"/collections/{self.collection}/points/search",
            json={
                "vector": list(vector),
                "limit": limit,
                "with_payload": True,
                "filter": _filter_payload(filters | {"corpus_id": corpus_id}),
            },
            error_code="search failed",
        )
        result = body.get("result") if isinstance(body, dict) else None
        if not isinstance(result, list):
            raise VectorStoreError("search failed")
        try:
            return [VectorHit(str(item["id"]), float(item["score"]), item.get("payload") or {}) for item in result]
        except (KeyError, TypeError, ValueError) as exc:
            raise VectorStoreError("search failed") from exc

    def count_points(self, *, filters: dict[str, Any]) -> int:
        response = self._request_raw(
            "POST",
            f"/collections/{self.collection}/points/count",
            json={"filter": _filter_payload(filters), "exact": True},
        )
        if response.status_code == 404:
            raise VectorStoreError("collection not found")
        if response.status_code < 200 or response.status_code >= 300:
            raise VectorStoreError("filtered count failed")
        try:
            body = response.json()
            count = body["result"]["count"]
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                raise TypeError
            return count
        except (KeyError, TypeError, ValueError) as exc:
            raise VectorStoreError("filtered count failed") from exc

    def scroll_points(
        self,
        *,
        filters: dict[str, Any],
        page_size: int = 256,
        max_pages: int = 3,
    ) -> tuple[ReadPoint, ...]:
        if page_size <= 0 or page_size > 256:
            raise VectorStoreError("invalid page size")
        if max_pages <= 0 or max_pages > 3:
            raise VectorStoreError("invalid max pages")

        points: list[ReadPoint] = []
        offset: Any | None = None
        for page_number in range(max_pages):
            body = {
                "filter": _filter_payload(filters),
                "limit": page_size,
                "with_payload": True,
                "with_vector": False,
            }
            if offset is not None:
                body["offset"] = offset
            response = self._request_raw(
                "POST",
                f"/collections/{self.collection}/points/scroll",
                json=body,
            )
            if response.status_code == 404:
                raise VectorStoreError("collection not found")
            if response.status_code < 200 or response.status_code >= 300:
                raise VectorStoreError("filtered read failed")
            try:
                result = response.json()["result"]
                page = result["points"]
                next_offset = result.get("next_page_offset")
                if not isinstance(page, list):
                    raise TypeError
                for item in page:
                    if not isinstance(item, dict) or "id" not in item or not isinstance(item.get("payload"), dict):
                        raise TypeError
                    points.append(ReadPoint(str(item["id"]), item["payload"]))
            except (KeyError, TypeError, ValueError) as exc:
                raise VectorStoreError("filtered read response invalid") from exc
            if next_offset is None:
                return tuple(points)
            offset = next_offset

        raise VectorStoreError("read verification limit exceeded")

    def _ensure_collection(self) -> None:
        response = self._request_raw("GET", f"/collections/{self.collection}")
        if response.status_code == 404:
            self._request(
                "PUT",
                f"/collections/{self.collection}",
                json={"vectors": {"size": VECTOR_DIMENSION, "distance": DISTANCE_METRIC}},
                error_code="vector store unavailable",
            )
            return
        if response.status_code != 200:
            raise VectorStoreError("vector store unavailable")
        try:
            vectors = response.json()["result"]["config"]["params"]["vectors"]
            size = vectors["size"]
            distance = vectors["distance"]
        except (KeyError, TypeError, ValueError) as exc:
            raise VectorStoreError("vector store schema mismatch") from exc
        if int(size) != VECTOR_DIMENSION or str(distance).lower() != DISTANCE_METRIC.lower():
            raise VectorStoreError("vector store schema mismatch")

    def _request_raw(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            return self._http_client().request(method, f"{self.endpoint_url}{path}", **kwargs)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            raise VectorStoreError("vector store unavailable") from exc
        except httpx.HTTPError as exc:
            raise VectorStoreError("vector store unavailable") from exc

    def _request(self, method: str, path: str, *, json: dict[str, Any], error_code: str) -> dict[str, Any]:
        response = self._request_raw(method, path, json=json)
        if response.status_code < 200 or response.status_code >= 300:
            raise VectorStoreError(error_code)
        try:
            body = response.json()
        except ValueError as exc:
            raise VectorStoreError(error_code) from exc
        return body if isinstance(body, dict) else {}

    def _http_client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout_seconds)
        return self._client


def _validate_collection_name(value: str) -> str:
    if not value or value == "cid_memory" or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for char in value):
        raise ValueError("invalid editorial collection name")
    if len(value) > 100 or not value.startswith("cid_editorial_transcripts_v1"):
        raise ValueError("invalid editorial collection name")
    return value


def _filter_payload(filters: dict[str, Any]) -> dict[str, Any]:
    allowed = {"corpus_id", "asset_id", "source_audio_stream_index"}
    return {"must": [{"key": key, "match": {"value": value}} for key, value in filters.items() if key in allowed and value is not None]}
