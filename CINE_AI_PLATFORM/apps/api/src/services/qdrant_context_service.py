import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from src.schemas.context_semantic import ContextSemanticIngestRequest, ContextSemanticSearchRequest


class QdrantContextServiceError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or None
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code,
        }


class QdrantContextService:
    def __init__(self, base_url: str, collection: str, timeout_seconds: float, vector_size: int = 384) -> None:
        self.base_url = str(base_url or "").strip().rstrip("/")
        self.collection = str(collection or "").strip() or "cine_project_context"
        self.timeout_seconds = max(float(timeout_seconds), 0.1)
        self.vector_size = max(int(vector_size), 1)

    def upsert_context(
        self,
        payload: ContextSemanticIngestRequest,
        vector: List[float],
        embedding_model: str,
        dimensions: int,
    ) -> Dict[str, Any]:
        self._validate_vector(vector=vector, dimensions=dimensions)

        normalized_payload = self._normalize_payload(payload)
        point_id = str(payload.point_id or self._build_point_id(normalized_payload)).strip()

        request_body = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": normalized_payload,
                }
            ]
        }
        response = self._request_json(
            method="PUT",
            path=f"collections/{self.collection}/points?wait=true",
            payload=request_body,
        )
        body = response["body"] if isinstance(response["body"], dict) else {}

        return {
            "ok": True,
            "collection": self.collection,
            "point_id": point_id,
            "embedding_model": embedding_model,
            "dimensions": dimensions,
            "payload": normalized_payload,
            "qdrant": body,
        }

    def search_context(
        self,
        payload: ContextSemanticSearchRequest,
        vector: List[float],
        embedding_model: str,
        dimensions: int,
    ) -> Dict[str, Any]:
        self._validate_vector(vector=vector, dimensions=dimensions)

        request_body = {
            "vector": vector,
            "limit": int(payload.limit),
            "with_payload": True,
            "with_vector": False,
            "filter": {"must": self._build_search_filters(payload)},
        }
        response = self._request_json(
            method="POST",
            path=f"collections/{self.collection}/points/search",
            payload=request_body,
        )
        body = response["body"] if isinstance(response["body"], dict) else {}
        raw_results = body.get("result") if isinstance(body.get("result"), list) else []

        results = []
        for item in raw_results:
            if not isinstance(item, dict):
                continue
            item_payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
            results.append(
                {
                    "point_id": str(item.get("id")) if item.get("id") is not None else None,
                    "score": float(item.get("score")) if item.get("score") is not None else None,
                    "project_id": item_payload.get("project_id"),
                    "sequence_id": item_payload.get("sequence_id"),
                    "scene_id": item_payload.get("scene_id"),
                    "shot_id": item_payload.get("shot_id"),
                    "entity_type": item_payload.get("entity_type"),
                    "title": item_payload.get("title"),
                    "content": item_payload.get("content"),
                    "tags": item_payload.get("tags") if isinstance(item_payload.get("tags"), list) else [],
                    "source": item_payload.get("source"),
                    "created_at": item_payload.get("created_at"),
                }
            )

        return {
            "ok": True,
            "collection": self.collection,
            "embedding_model": embedding_model,
            "dimensions": dimensions,
            "query": {
                "text": payload.text.strip(),
                "project_id": payload.project_id.strip(),
                "sequence_id": self._normalize_optional(payload.sequence_id),
                "scene_id": self._normalize_optional(payload.scene_id),
                "shot_id": self._normalize_optional(payload.shot_id),
                "entity_type": self._normalize_optional(payload.entity_type),
                "tags": self._normalize_tags(payload.tags),
                "source": self._normalize_optional(payload.source),
                "limit": int(payload.limit),
            },
            "count": len(results),
            "results": results,
        }

    def _normalize_payload(self, payload: ContextSemanticIngestRequest) -> Dict[str, Any]:
        normalized = {
            "project_id": payload.project_id.strip(),
            "sequence_id": self._normalize_optional(payload.sequence_id),
            "scene_id": self._normalize_optional(payload.scene_id),
            "shot_id": self._normalize_optional(payload.shot_id),
            "entity_type": payload.entity_type.strip(),
            "title": payload.title.strip(),
            "content": payload.content.strip(),
            "tags": self._normalize_tags(payload.tags),
            "source": payload.source.strip(),
            "created_at": self._normalize_optional(payload.created_at) or self._utc_now_iso(),
        }

        if not normalized["project_id"] or not normalized["entity_type"] or not normalized["title"] or not normalized["content"] or not normalized["source"]:
            raise ValueError("Semantic context payload is missing required fields")

        return normalized

    def _build_search_filters(self, payload: ContextSemanticSearchRequest) -> List[Dict[str, Any]]:
        must: List[Dict[str, Any]] = [{"key": "project_id", "match": {"value": payload.project_id.strip()}}]

        sequence_id = self._normalize_optional(payload.sequence_id)
        scene_id = self._normalize_optional(payload.scene_id)
        shot_id = self._normalize_optional(payload.shot_id)
        entity_type = self._normalize_optional(payload.entity_type)
        source = self._normalize_optional(payload.source)
        tags = self._normalize_tags(payload.tags)

        if sequence_id:
            must.append({"key": "sequence_id", "match": {"value": sequence_id}})
        if scene_id:
            must.append({"key": "scene_id", "match": {"value": scene_id}})
        if shot_id:
            must.append({"key": "shot_id", "match": {"value": shot_id}})
        if entity_type:
            must.append({"key": "entity_type", "match": {"value": entity_type}})
        if source:
            must.append({"key": "source", "match": {"value": source}})
        if tags:
            must.append({"key": "tags", "match": {"any": tags}})

        return must

    def _build_point_id(self, normalized_payload: Dict[str, Any]) -> str:
        timestamp = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
        return ":".join(
            [
                normalized_payload["project_id"],
                normalized_payload.get("sequence_id") or "root",
                normalized_payload.get("scene_id") or "root",
                normalized_payload.get("shot_id") or "root",
                normalized_payload["entity_type"],
                str(timestamp),
            ]
        )

    def _validate_vector(self, vector: List[float], dimensions: int) -> None:
        if dimensions != self.vector_size or len(vector) != self.vector_size:
            raise QdrantContextServiceError(
                code="QDRANT_INVALID_VECTOR_DIMENSIONS",
                message=f"Vector dimensions must be {self.vector_size}",
                details={"dimensions": dimensions, "vector_length": len(vector)},
            )

    def _normalize_tags(self, tags: Optional[List[str]]) -> List[str]:
        normalized_tags: List[str] = []
        for tag in tags or []:
            normalized = str(tag or "").strip()
            if normalized:
                normalized_tags.append(normalized)
        return normalized_tags

    def _normalize_optional(self, value: Optional[str]) -> Optional[str]:
        normalized = str(value or "").strip()
        return normalized or None

    def _utc_now_iso(self) -> str:
        return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _request_json(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.base_url:
            raise QdrantContextServiceError(
                code="QDRANT_BASE_URL_NOT_CONFIGURED",
                message="Qdrant base URL is not configured",
            )

        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=data, headers=headers, method=method.upper())

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                parsed_body = json.loads(raw_body) if raw_body else {}
                return {"status_code": int(response.status), "body": parsed_body}
        except HTTPError as error:
            details: Dict[str, Any] = {}
            try:
                raw_body = error.read().decode("utf-8")
                details["body"] = json.loads(raw_body) if raw_body else None
            except Exception:
                details["body"] = None
            raise QdrantContextServiceError(
                code="QDRANT_HTTP_ERROR",
                message=f"Qdrant returned HTTP {error.code}",
                details=details or None,
                status_code=int(error.code),
            ) from error
        except URLError as error:
            raise QdrantContextServiceError(
                code="QDRANT_UNREACHABLE",
                message="Qdrant is unreachable",
                details={"reason": str(getattr(error, "reason", error))},
            ) from error
        except Exception as error:
            raise QdrantContextServiceError(
                code="QDRANT_REQUEST_FAILED",
                message="Qdrant request failed",
                details={"reason": str(error)},
            ) from error
