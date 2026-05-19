from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.project_document_rag_service import ProjectDocumentRagService  # noqa: E402


@pytest.mark.asyncio
async def test_real_embedding_provider_uses_ollama_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PROJECT_DOCUMENT_EMBEDDING_PROVIDER", "ollama")
    service = ProjectDocumentRagService()

    async def fake_embed(texts):
        return [[0.1, 0.2, 0.3] for _ in texts]

    monkeypatch.setattr(service, "_embed_texts_with_ollama", fake_embed)
    vectors, provider = await service._embed_texts(["hola mundo"])
    assert provider == "ollama"
    assert vectors and len(vectors[0]) == 3


@pytest.mark.asyncio
async def test_fallback_without_qdrant_keeps_db_similarity_path() -> None:
    service = ProjectDocumentRagService()
    service.qdrant_enabled = False

    chunk = SimpleNamespace(
        id="chunk-1",
        metadata_json="{}",
        chunk_index=0,
        chunk_text="fragmento util",
        embedding_payload=service._serialize_embedding([1.0] + [0.0] * (service.embedding_dimensions - 1)),
    )
    document = SimpleNamespace(id="doc-1", file_name="doc.txt", document_type="script")

    class FakeResult:
        @staticmethod
        def all():
            return [(chunk, document)]

    class FakeDb:
        async def execute(self, *args, **kwargs):
            return FakeResult()

    result = await service.ask(
        FakeDb(),
        project_id="p1",
        organization_id="o1",
        query_text="fragmento",
        top_k=1,
    )
    assert result["retrieved_chunks"]
    assert result["retrieved_chunks"][0]["chunk_id"] == "chunk-1"
