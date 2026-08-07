from __future__ import annotations

import pytest

from scripts.editorial_intelligence.semantic_index.embedding_backend import OllamaEmbeddingAdapter
from scripts.editorial_intelligence.semantic_index.runtime import build_local_semantic_index
from scripts.editorial_intelligence.semantic_index.vector_store import QdrantVectorStore


def test_factory_builds_concrete_local_stack_without_contacting_services() -> None:
    index = build_local_semantic_index()
    assert isinstance(index.embedding_backend, OllamaEmbeddingAdapter)
    assert isinstance(index.vector_store, QdrantVectorStore)
    assert index.embedding_backend.model == "nomic-embed-text:v1.5"
    assert index.embedding_backend.dimension == 768
    assert index.vector_store.collection != "cid_memory"


def test_factory_accepts_only_loopback_endpoints() -> None:
    with pytest.raises(ValueError, match="loopback"):
        build_local_semantic_index(ollama_url="http://remote.example:11434")
    with pytest.raises(ValueError, match="loopback"):
        build_local_semantic_index(qdrant_url="http://10.0.0.2:6333")


def test_factory_rejects_model_substitution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMBEDDING_MODEL", "latest")
    with pytest.raises(ValueError, match="nomic-embed-text:v1.5"):
        build_local_semantic_index()


def test_factory_preserves_fake_dependency_injection_contract() -> None:
    from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticIndex

    embedding = OllamaEmbeddingAdapter(embed_callable=lambda text: [0.0] * 768)
    assert isinstance(SemanticIndex(embedding, object()), SemanticIndex)
