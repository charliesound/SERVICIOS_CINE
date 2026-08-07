"""Lazy local runtime composition for the editorial Semantic Index."""

from __future__ import annotations

import os

from scripts.editorial_intelligence.semantic_index.embedding_backend import (
    DIMENSION,
    MODEL,
    LocalEmbeddingConfig,
    OllamaEmbeddingAdapter,
)
from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticIndex
from scripts.editorial_intelligence.semantic_index.vector_store import (
    COLLECTION_NAME,
    QdrantVectorStore,
)


def build_local_semantic_index(
    *,
    ollama_url: str | None = None,
    qdrant_url: str | None = None,
    collection: str = COLLECTION_NAME,
    timeout_seconds: float = 30.0,
) -> SemanticIndex:
    """Build the real local stack without contacting either service."""
    configured_model = os.getenv("EMBEDDING_MODEL", MODEL)
    if configured_model != MODEL:
        raise ValueError("embedding model must be nomic-embed-text:v1.5")
    embedding = OllamaEmbeddingAdapter(
        config=LocalEmbeddingConfig(model=MODEL, dimension=DIMENSION, timeout_seconds=timeout_seconds),
        endpoint_url=ollama_url or os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"),
    )
    store = QdrantVectorStore(
        endpoint_url=qdrant_url or os.getenv("QDRANT_URL", "http://127.0.0.1:6333"),
        collection=collection,
        timeout_seconds=min(timeout_seconds, 10.0),
    )
    return SemanticIndex(embedding, store)
