from __future__ import annotations

import math

import httpx
import pytest

from scripts.editorial_intelligence.semantic_index.embedding_backend import (
    EmbeddingBackendError,
    LocalEmbeddingConfig,
    OllamaEmbeddingAdapter,
    validate_loopback_url,
)
from scripts.editorial_intelligence.semantic_index.vector_store import (
    COLLECTION_NAME,
    QdrantVectorStore,
    VectorPoint,
    VectorStoreError,
)


def mock_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_loopback_urls_are_accepted_and_remote_urls_rejected() -> None:
    assert validate_loopback_url("http://127.0.0.1:11434") == "http://127.0.0.1:11434"
    assert validate_loopback_url("http://localhost:6333") == "http://localhost:6333"
    assert validate_loopback_url("http://[::1]:6333") == "http://[::1]:6333"
    for value in ("http://example.test:11434", "http://192.168.1.20:6333"):
        with pytest.raises(ValueError, match="loopback"):
            validate_loopback_url(value)


def test_ollama_posts_exact_embed_contract_and_accepts_768_vector() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["json"] = request.read()
        return httpx.Response(200, json={"embeddings": [[0.25] * 768]})

    adapter = OllamaEmbeddingAdapter(client=mock_client(handler))
    vector = adapter.embed("migration")
    assert len(vector) == 768
    assert seen["method"] == "POST"
    assert seen["url"] == "http://127.0.0.1:11434/api/embed"
    assert b'"model":"nomic-embed-text:v1.5"' in seen["json"]
    assert b'"input":"migration"' in seen["json"]


@pytest.mark.parametrize(
    "body, expected",
    [
        ({"embedding": [0.0] * 767}, "dimension mismatch"),
        ({"embedding": [math.nan] * 768}, "embedding failed"),
        ({"embedding": [math.inf] * 768}, "embedding failed"),
        ({"result": []}, "embedding response invalid"),
    ],
)
def test_ollama_rejects_invalid_vectors(body, expected: str) -> None:
    adapter = OllamaEmbeddingAdapter(client=mock_client(lambda request: httpx.Response(200, json=body)))
    with pytest.raises(EmbeddingBackendError, match=expected):
        adapter.embed("test")


def test_ollama_unavailable_and_timeout_are_sanitized() -> None:
    unavailable = OllamaEmbeddingAdapter(client=mock_client(lambda request: (_ for _ in ()).throw(httpx.ConnectError("secret"))))
    with pytest.raises(EmbeddingBackendError, match="unavailable"):
        unavailable.embed("test")
    timeout = OllamaEmbeddingAdapter(client=mock_client(lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("secret"))))
    with pytest.raises(EmbeddingBackendError, match="unavailable"):
        timeout.embed("test")


def test_ollama_injected_callable_remains_supported() -> None:
    adapter = OllamaEmbeddingAdapter(embed_callable=lambda text: [1.0] * 768)
    assert len(adapter.embed("test")) == 768


def test_qdrant_rejects_cid_memory_and_invalid_collection_names() -> None:
    with pytest.raises(ValueError):
        QdrantVectorStore(collection="cid_memory")
    with pytest.raises(ValueError):
        QdrantVectorStore(collection="/tmp/private")
    assert QdrantVectorStore(collection=COLLECTION_NAME).collection == COLLECTION_NAME


def test_qdrant_creates_schema_and_maps_upsert_delete() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path, request.read()))
        if request.method == "GET":
            return httpx.Response(404, json={"status": "error"})
        return httpx.Response(200, json={"result": True})

    store = QdrantVectorStore(client=mock_client(handler))
    point = VectorPoint("uuid5-point", (0.1,) * 768, {"corpus_id": "test", "asset_id": "asset"})
    store.replace_corpus("test", [point])
    assert calls[0][0:2] == ("GET", f"/collections/{COLLECTION_NAME}")
    assert any(path.endswith("/points/delete") for _, path, _ in calls)
    upsert = next(body for method, path, body in calls if method == "PUT" and path.endswith("/points"))
    assert b'"id":"uuid5-point"' in upsert
    assert b'"vector"' in upsert


def test_qdrant_validates_compatible_schema_and_maps_search_hits() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(200, json={"result": {"config": {"params": {"vectors": {"size": 768, "distance": "Cosine"}}}}})
        return httpx.Response(200, json={"result": [{"id": "p1", "score": 0.9, "payload": {"asset_id": "a"}}]})

    store = QdrantVectorStore(client=mock_client(handler))
    hits = store.search(corpus_id="test", vector=[0.1] * 768, limit=3, filters={"asset_id": "a"})
    assert hits[0].point_id == "p1"
    assert hits[0].score == 0.9


def test_qdrant_rejects_schema_mismatch_and_sanitizes_failures() -> None:
    mismatch = QdrantVectorStore(client=mock_client(lambda request: httpx.Response(200, json={"result": {"config": {"params": {"vectors": {"size": 96, "distance": "Cosine"}}}}})))
    with pytest.raises(VectorStoreError, match="schema mismatch"):
        mismatch.delete_corpus("test")
    failure = QdrantVectorStore(client=mock_client(lambda request: httpx.Response(500, text="private backend detail")))
    with pytest.raises(VectorStoreError, match="unavailable"):
        failure.delete_corpus("test")
