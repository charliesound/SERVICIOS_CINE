"""
qdrant_store.py — Almacén vectorial para workflows indexados.

Guarda vectores + payload en Qdrant y permite búsqueda semántica.
"""

from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue


class QdrantStore:
    def __init__(self, host: str = "localhost", port: int = 6333, collection: str = "comfy_workflows"):
        self.collection = collection
        self.client = QdrantClient(host=host, port=port)

    def ensure_collection(self, dim: int):
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def ingest(self, items: list[dict], embedder, batch_size: int = 64):
        self.ensure_collection(embedder.dim)
        points = []
        for i, item in enumerate(items):
            text = (
                f"{item['name']}. {item['summary']}. "
                f"Tags: {', '.join(item['tags'])}. "
                f"Nodos: {', '.join(item['nodes'][:20])}. "
                f"Uso: {item.get('cinema_use_case', '')}"
            )
            vec = embedder.encode(text)
            points.append(PointStruct(id=i, vector=vec, payload=item))

            if len(points) >= batch_size:
                self.client.upsert(collection_name=self.collection, points=points)
                points = []

        if points:
            self.client.upsert(collection_name=self.collection, points=points)

        return len(items)

    def search(self, query: str, embedder, top_k: int = 8, filters: dict = None) -> list[dict]:
        vector = embedder.encode(query)

        search_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            search_filter = Filter(must=conditions)

        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=search_filter,
        )

        results = []
        for h in hits:
            payload = h.payload or {}
            results.append({
                "id": payload.get("id"),
                "name": payload.get("name"),
                "path": payload.get("path"),
                "summary": payload.get("summary"),
                "tags": payload.get("tags", []),
                "nodes": payload.get("nodes", []),
                "models": payload.get("models", []),
                "backend": payload.get("backend", "still"),
                "phase": payload.get("phase", "general"),
                "cinema_use_case": payload.get("cinema_use_case", ""),
                "score": round(h.score, 4),
            })

        return results

    def get_by_id(self, workflow_id: str) -> Optional[dict]:
        from qdrant_client.models import Filter as QFilter, FieldCondition, MatchValue
        scroll_filter = QFilter(
            must=[FieldCondition(key="id", match=MatchValue(value=workflow_id))]
        )
        points = self.client.scroll(
            collection_name=self.collection,
            scroll_filter=scroll_filter,
            limit=1,
        )[0]
        if points:
            return points[0].payload
        return None

    def count(self) -> int:
        try:
            info = self.client.get_collection(self.collection)
            return info.points_count
        except Exception:
            return 0

    def delete_collection(self):
        if self.client.collection_exists(self.collection):
            self.client.delete_collection(self.collection)
