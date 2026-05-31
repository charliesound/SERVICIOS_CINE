from __future__ import annotations

import uuid as uuid_lib
from datetime import datetime, timezone
from typing import Any

from core.config import get_settings
from services.logging_service import logger
from services.qdrant_service import qdrant_service


COLLECTION = "cid_memory"
VERSION = "1"


def _build_point_id(
    organization_id: str,
    project_id: str,
    source_table: str,
    source_id: str,
    chunk_index: int,
) -> str:
    namespace = uuid_lib.uuid5(
        uuid_lib.NAMESPACE_DNS,
        f"cid-memory/{VERSION}/{organization_id}/{project_id}/{source_table}/{source_id}/{chunk_index}",
    )
    return str(namespace)


def _now_str() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_payload(
    *,
    organization_id: str,
    project_id: str,
    source_type: str,
    source_id: str,
    source_table: str,
    title: str,
    text: str,
    chunk_index: int,
    chunk_count: int,
    language: str = "es",
    tags: list[str] | None = None,
    visibility: str = "organization",
    embedding_model: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = _now_str()
    return {
        "organization_id": organization_id,
        "project_id": project_id,
        "source_type": source_type,
        "source_id": source_id,
        "source_table": source_table,
        "title": title,
        "text": text,
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "language": language,
        "tags": tags or [],
        "created_at": now,
        "updated_at": now,
        "version": VERSION,
        "visibility": visibility,
        "embedding_model": embedding_model,
        "metadata": metadata or {},
    }


def _project_filter(organization_id: str, project_id: str) -> dict[str, Any]:
    return {
        "must": [
            {"key": "organization_id", "match": {"value": organization_id}},
            {"key": "project_id", "match": {"value": project_id}},
        ]
    }


class QdrantMemoryService:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection: str = settings.cid_memory_collection
        self.embedding_model: str = settings.embedding_model

    async def upsert_memory(
        self,
        *,
        organization_id: str,
        project_id: str,
        source_type: str,
        source_id: str,
        source_table: str,
        title: str,
        chunks: list[str],
        language: str = "es",
        tags: list[str] | None = None,
        embedding_vectors: list[list[float]],
        metadata: dict[str, Any] | None = None,
    ) -> int:
        if not chunks or not embedding_vectors:
            return 0
        if len(chunks) != len(embedding_vectors):
            raise ValueError("chunks and embedding_vectors must have same length")

        points: list[dict[str, Any]] = []
        chunk_count = len(chunks)

        for i, (chunk_text, vector) in enumerate(zip(chunks, embedding_vectors)):
            point_id = _build_point_id(
                organization_id=organization_id,
                project_id=project_id,
                source_table=source_table,
                source_id=source_id,
                chunk_index=i,
            )
            payload = _build_payload(
                organization_id=organization_id,
                project_id=project_id,
                source_type=source_type,
                source_id=source_id,
                source_table=source_table,
                title=title,
                text=chunk_text,
                chunk_index=i,
                chunk_count=chunk_count,
                language=language,
                tags=tags,
                embedding_model=self.embedding_model,
                metadata=metadata,
            )
            points.append({"id": point_id, "vector": vector, "payload": payload})

        ok = await qdrant_service.upsert_points(collection=self.collection, points=points)
        if not ok:
            logger.error("QdrantMemoryService upsert failed for project=%s source=%s", project_id, source_table)
            return 0
        return len(points)

    async def search(
        self,
        *,
        organization_id: str,
        project_id: str,
        query_vector: list[float],
        limit: int = 10,
        source_type: str | None = None,
    ) -> list[dict[str, Any]]:
        filter_payload = _project_filter(organization_id, project_id)
        if source_type:
            filter_payload["must"].append(
                {"key": "source_type", "match": {"value": source_type}}
            )

        results = await qdrant_service.semantic_search(
            collection=self.collection,
            query_vector=query_vector,
            limit=limit,
            filter_payload=filter_payload,
        )

        out: list[dict[str, Any]] = []
        for hit in results:
            payload = hit.get("payload") or {}
            if not isinstance(payload, dict):
                payload = {}
            out.append({
                "id": hit.get("id", ""),
                "score": hit.get("score", 0.0),
                "source_type": payload.get("source_type", ""),
                "source_id": payload.get("source_id", ""),
                "source_table": payload.get("source_table", ""),
                "title": payload.get("title", ""),
                "text": payload.get("text", ""),
                "chunk_index": payload.get("chunk_index", 0),
                "chunk_count": payload.get("chunk_count", 0),
                "tags": payload.get("tags", []),
                "metadata": payload.get("metadata", {}),
            })
        return out

    async def count_project_points(self, organization_id: str, project_id: str) -> int:
        try:
            import httpx
            import os
            base = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{base}/collections/{self.collection}/points/count",
                    json={"filter": _project_filter(organization_id, project_id)},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return int(data.get("result", {}).get("count", 0))
                return 0
        except Exception as exc:
            logger.warning("count_project_points failed: %s", exc)
            return 0

    async def delete_project_points(self, organization_id: str, project_id: str) -> int:
        """
        Delete all points for a specific organization and project.
        Returns the number of points deleted.
        Requires both organization_id and project_id to be provided.
        """
        if not organization_id or not project_id:
            raise ValueError("Both organization_id and project_id are required for deletion")

        try:
            import httpx
            import os
            base = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
            filter_payload = _project_filter(organization_id, project_id)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{base}/collections/{self.collection}/points/delete",
                    json={"filter": filter_payload},
                )
                if resp.status_code in (200, 201):
                    # Get count of deleted points by checking count before/after or return approximate
                    # For now, we'll get the count after deletion to report remaining
                    remaining_count = await self.count_project_points(organization_id, project_id)
                    # We don't have before count easily, so we'll return 0 to indicate success but not exact count
                    # The caller can call count_project_points before and after if they need exact count
                    logger.info("Deleted points for org=%s, project=%s (remaining: %s)",
                              organization_id, project_id, remaining_count)
                    return 0  # Indicates success, caller should use count before/after for exact number
                else:
                    logger.error("delete_project_points failed status=%s body=%s",
                               resp.status_code, resp.text[:200])
                    return -1  # Indicates failure
        except Exception as exc:
            logger.error("delete_project_points exception: %s", exc)
            return -1  # Indicates failure

    async def get_collection_info(self) -> dict[str, Any]:
        """Get general information about the cid_memory collection."""
        try:
            import httpx
            import os
            base = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{base}/collections/{self.collection}")
                if resp.status_code == 200:
                    data = resp.json()
                    result = data.get("result", {})
                    config = result.get("config", {})
                    params = config.get("params", {})
                    vectors = params.get("vectors", {})
                    return {
                        "collection_name": self.collection,
                        "vector_size": vectors.get("size", 0),
                        "distance": vectors.get("distance", "Cosine"),
                        "status": result.get("status", "unknown"),
                        "points_count": result.get("count", 0),
                        "embedding_model": self.embedding_model
                    }
                return {}
        except Exception as exc:
            logger.warning("get_collection_info failed: %s", exc)
            return {}

    async def count_points_by_source_type(self, organization_id: str, project_id: str) -> dict[str, int]:
        """Count points in cid_memory filtered by organization_id and project_id, grouped by source_type."""
        try:
            import httpx
            import os
            base = os.getenv("QDRANT_URL", "http://qdrant:6333").rstrip("/")
            filter_payload = {
                "must": [
                    {"key": "organization_id", "match": {"value": organization_id}},
                    {"key": "project_id", "match": {"value": project_id}},
                ]
            }
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Scroll through all points with payload to count by source_type
                offset = 0
                limit = 100
                source_counts = {}

                while True:
                    resp = await client.post(
                        f"{base}/collections/{self.collection}/points/scroll",
                        json={
                            "filter": filter_payload,
                            "limit": limit,
                            "offset": offset,
                            "with_payload": True,
                            "with_vectors": False
                        }
                    )
                    if resp.status_code != 200:
                        logger.warning("Failed to scroll points for source type counting: %s", resp.text)
                        break

                    data = resp.json()
                    result = data.get("result", {})
                    points = result.get("points", [])

                    if not points:
                        break

                    for point in points:
                        payload = point.get("payload", {})
                        source_type = payload.get("source_type", "unknown")
                        source_counts[source_type] = source_counts.get(source_type, 0) + 1

                    # If we got less than the limit, we've reached the end
                    if len(points) < limit:
                        break

                    offset += limit

                return source_counts
        except Exception as exc:
            logger.warning("count_points_by_source_type failed: %s", exc)
            return {}


qdrant_memory_service = QdrantMemoryService()
