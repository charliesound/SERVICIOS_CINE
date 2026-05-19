from __future__ import annotations

import os
from typing import Any

from services.project_document_rag_service import project_document_rag_service
from services.qdrant_service import qdrant_service


class CIDScreenwritingTheoryService:
    THEORY_COLLECTION = "cid_screenwriting_theory"
    DEFAULT_TOP_K = 6
    THEORY_TOPICS = (
        "three_act_structure",
        "plot_points",
        "midpoint",
        "conflict_matrix",
        "character_arc",
        "dramatic_action",
        "scene_value_shift",
        "crisis_climax_resolution",
        "sequence_design",
        "subtext",
        "pacing",
    )

    async def fetch_theory_context(self, *, topics: list[str] | None = None) -> dict[str, Any]:
        selected_topics = topics or list(self.THEORY_TOPICS)
        selected_topics = [topic for topic in selected_topics if topic]
        if not selected_topics:
            selected_topics = list(self.THEORY_TOPICS)

        query = " ".join(selected_topics)
        vectors, _provider = await project_document_rag_service._embed_texts([query])
        if not vectors:
            return {"summary": "", "sources": [], "fallback_used": True}

        vector = vectors[0]
        top_k = int(os.getenv("CID_THEORY_TOP_K", str(self.DEFAULT_TOP_K)))
        hits = await qdrant_service.semantic_search(
            collection=self.THEORY_COLLECTION,
            query_vector=vector,
            limit=top_k,
            filter_payload={
                "must": [
                    {"key": "topic", "match": {"value": "screenwriting_theory"}},
                ]
            },
        )
        if not hits:
            return {"summary": "", "sources": [], "fallback_used": True}

        snippets: list[str] = []
        sources: list[dict[str, Any]] = []
        for hit in hits:
            payload = hit.get("payload") if isinstance(hit, dict) else {}
            if not isinstance(payload, dict):
                continue
            chunk_text = str(payload.get("chunk_text") or "").strip()
            if chunk_text:
                snippets.append(chunk_text)
            sources.append(
                {
                    "author": payload.get("author"),
                    "title": payload.get("title"),
                    "chapter": payload.get("chapter"),
                    "topic": payload.get("topic"),
                    "source_file": payload.get("source_file"),
                    "chunk_index": payload.get("chunk_index"),
                    "score": hit.get("score") if isinstance(hit, dict) else None,
                }
            )

        summary = " ".join(snippets[:4])[:2200]
        return {
            "summary": summary,
            "sources": sources,
            "fallback_used": False,
        }


cid_screenwriting_theory_service = CIDScreenwritingTheoryService()
