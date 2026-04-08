from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.schemas.context_semantic import ContextSemanticSearchRequest
from src.services.embeddings_service import EmbeddingsService, EmbeddingsServiceError
from src.services.qdrant_context_service import QdrantContextService, QdrantContextServiceError


class SequenceSemanticContextService:
    _DEFAULT_USEFUL_ENTITY_TYPES = (
        "project_note",
        "sequence_note",
        "scene_note",
        "shot_note",
        "style_reference",
        "continuity_rule",
    )

    def __init__(
        self,
        embeddings_service: EmbeddingsService,
        qdrant_context_service: QdrantContextService,
        default_limit: int = 5,
    ) -> None:
        self.embeddings_service = embeddings_service
        self.qdrant_context_service = qdrant_context_service
        self.default_limit = max(1, min(int(default_limit), 10))

    def retrieve_relevant_context(
        self,
        *,
        project_id: Optional[str],
        query_text: Optional[str],
        sequence_id: Optional[str] = None,
        scene_id: Optional[str] = None,
        shot_id: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        normalized_project_id = self._safe_optional_text(project_id)
        normalized_query_text = self._safe_optional_text(query_text)
        normalized_sequence_id = self._safe_optional_text(sequence_id)
        normalized_scene_id = self._safe_optional_text(scene_id)
        normalized_shot_id = self._safe_optional_text(shot_id)
        normalized_limit = max(1, min(int(limit or self.default_limit), 10))

        if not normalized_project_id or not normalized_query_text:
            return self._empty_context(
                query_text=normalized_query_text,
                project_id=normalized_project_id,
                sequence_id=normalized_sequence_id,
                scene_id=normalized_scene_id,
                shot_id=normalized_shot_id,
                limit=normalized_limit,
                enabled=False,
            )

        try:
            embedding = self.embeddings_service.embed_text(
                text=normalized_query_text,
                metadata={
                    "project_id": normalized_project_id,
                    "sequence_id": normalized_sequence_id,
                    "scene_id": normalized_scene_id,
                    "shot_id": normalized_shot_id,
                    "source": "sequence_planner",
                    "limit": normalized_limit,
                },
            )
            search_response = self.qdrant_context_service.search_context(
                payload=ContextSemanticSearchRequest(
                    text=normalized_query_text,
                    project_id=normalized_project_id,
                    sequence_id=normalized_sequence_id,
                    scene_id=normalized_scene_id,
                    shot_id=normalized_shot_id,
                    limit=max(normalized_limit * 2, normalized_limit),
                ),
                vector=embedding["vector"],
                embedding_model=embedding["model"],
                dimensions=embedding["dimensions"],
            )
        except (ValueError, EmbeddingsServiceError, QdrantContextServiceError) as error:
            return self._empty_context(
                query_text=normalized_query_text,
                project_id=normalized_project_id,
                sequence_id=normalized_sequence_id,
                scene_id=normalized_scene_id,
                shot_id=normalized_shot_id,
                limit=normalized_limit,
                enabled=True,
                error=self._build_error_payload(error),
            )

        filtered_results = []
        for item in search_response.get("results", []):
            if not isinstance(item, dict):
                continue
            entity_type = self._safe_optional_text(item.get("entity_type"))
            if entity_type not in self._DEFAULT_USEFUL_ENTITY_TYPES:
                continue
            filtered_results.append(item)

        limited_results = filtered_results[:normalized_limit]
        items = [self._normalize_item(item) for item in limited_results]

        return {
            "enabled": True,
            "query": {
                "text": normalized_query_text,
                "project_id": normalized_project_id,
                "sequence_id": normalized_sequence_id,
                "scene_id": normalized_scene_id,
                "shot_id": normalized_shot_id,
                "limit": normalized_limit,
            },
            "count": len(items),
            "entity_types": sorted({item["entity_type"] for item in items if item.get("entity_type")}),
            "summary_text": self._build_summary_text(items),
            "continuity_hints": self._build_continuity_hints(items),
            "items": items,
            "error": None,
        }

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "point_id": self._safe_optional_text(item.get("point_id")),
            "score": float(item.get("score")) if item.get("score") is not None else None,
            "project_id": self._safe_optional_text(item.get("project_id")),
            "sequence_id": self._safe_optional_text(item.get("sequence_id")),
            "scene_id": self._safe_optional_text(item.get("scene_id")),
            "shot_id": self._safe_optional_text(item.get("shot_id")),
            "entity_type": self._safe_optional_text(item.get("entity_type")),
            "title": self._safe_optional_text(item.get("title")) or "Untitled context",
            "content": self._safe_optional_text(item.get("content")) or "",
            "content_excerpt": self._build_excerpt(self._safe_optional_text(item.get("content")) or ""),
            "tags": [str(tag).strip() for tag in item.get("tags", []) if isinstance(tag, str) and str(tag).strip()],
            "source": self._safe_optional_text(item.get("source")),
            "created_at": self._safe_optional_text(item.get("created_at")),
        }

    def _build_summary_text(self, items: List[Dict[str, Any]]) -> str:
        parts: List[str] = []
        for item in items[:3]:
            entity_type = item.get("entity_type") or "context"
            title = item.get("title") or "Untitled context"
            excerpt = item.get("content_excerpt") or ""
            parts.append(f"{entity_type}: {title}. {excerpt}".strip())
        return " | ".join(parts)

    def _build_continuity_hints(self, items: List[Dict[str, Any]]) -> List[str]:
        hints: List[str] = []
        for item in items[:4]:
            entity_type = item.get("entity_type") or "context"
            title = item.get("title") or "Untitled context"
            excerpt = item.get("content_excerpt") or ""
            hints.append(f"Semantic {entity_type}: {title}. {excerpt}".strip())
        return hints

    def _build_excerpt(self, content: str, max_chars: int = 180) -> str:
        normalized = " ".join(content.split()).strip()
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."

    def _build_error_payload(self, error: Exception) -> Dict[str, Any]:
        if hasattr(error, "code") and hasattr(error, "message"):
            return {
                "code": getattr(error, "code"),
                "message": getattr(error, "message"),
                "details": getattr(error, "details", None),
            }
        return {
            "code": error.__class__.__name__,
            "message": str(error),
            "details": None,
        }

    def _empty_context(
        self,
        *,
        query_text: Optional[str],
        project_id: Optional[str],
        sequence_id: Optional[str],
        scene_id: Optional[str],
        shot_id: Optional[str],
        limit: int,
        enabled: bool,
        error: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "enabled": enabled,
            "query": {
                "text": query_text,
                "project_id": project_id,
                "sequence_id": sequence_id,
                "scene_id": scene_id,
                "shot_id": shot_id,
                "limit": limit,
            },
            "count": 0,
            "entity_types": [],
            "summary_text": "",
            "continuity_hints": [],
            "items": [],
            "error": error,
        }

    def _safe_optional_text(self, value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None
