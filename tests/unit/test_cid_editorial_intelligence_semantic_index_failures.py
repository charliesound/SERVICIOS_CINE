from __future__ import annotations

from dataclasses import dataclass

from scripts.editorial_intelligence.semantic_index.embedding_backend import DIMENSION, EmbeddingBackendError
from scripts.editorial_intelligence.semantic_index.semantic_index import SemanticIndex, SemanticIndexError, SemanticSearchQuery
from scripts.editorial_intelligence.semantic_index.vector_store import VectorStoreError
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1"


def segment():
    return TranscriptSegment(PHASE, "asset", 0, 0, "text", 0.0, 1.0, 5.0, 6.0, {"available": False}, {"internal_source_reference": "/secret.wav"}, None, [])


@dataclass
class Embedding:
    dimension: int = DIMENSION
    provider: str = "ollama"
    model: str = "nomic-embed-text:v1.5"
    mode: str = "ok"

    def embed(self, text):
        if self.mode == "unavailable":
            raise EmbeddingBackendError("embedding backend unavailable")
        if self.mode == "failure":
            raise EmbeddingBackendError("embedding failed")
        return [0.0] * self.dimension


class FailingStore:
    def __init__(self, mode="write"):
        self.mode = mode

    def replace_corpus(self, corpus_id, points):
        if self.mode == "write":
            raise VectorStoreError("write failed")

    def delete_corpus(self, corpus_id):
        raise VectorStoreError("store unavailable")

    def search(self, *, corpus_id, vector, limit, filters):
        raise VectorStoreError("search failed")


def test_dimension_mismatch_is_rejected_before_index():
    try:
        SemanticIndex(Embedding(dimension=1), FailingStore())
    except SemanticIndexError as exc:
        assert exc.error_code == "EMBEDDING_DIMENSION_MISMATCH"
    else:
        raise AssertionError("dimension mismatch accepted")


def test_embedding_unavailable_and_failure_are_explicit_partial_results():
    for mode, code in (("unavailable", "EMBEDDING_FAILED"), ("failure", "EMBEDDING_FAILED")):
        result = SemanticIndex(Embedding(mode=mode), FailingStore()).index_segments("corpus", [segment()])
        assert result.status == "INDEX_PARTIAL"
        assert result.failures[0]["error_code"] == code
        assert "/secret" not in result.failures[0]["message"]


def test_vector_store_write_and_search_failures_are_structured():
    result = SemanticIndex(Embedding(), FailingStore("write")).index_segments("corpus", [segment()])
    assert result.status == "INDEX_PARTIAL"
    assert result.failures[0]["error_code"] == "INDEX_WRITE_FAILED"
    index = SemanticIndex(Embedding(), FailingStore("search"))
    try:
        index.search(SemanticSearchQuery("query", corpus_id="corpus"))
    except SemanticIndexError as exc:
        assert exc.error_code == "SEARCH_FAILED"
    else:
        raise AssertionError("search failure swallowed")


def test_delete_failure_is_sanitized():
    try:
        SemanticIndex(Embedding(), FailingStore()).delete_corpus("corpus")
    except SemanticIndexError as exc:
        assert exc.error_code == "VECTOR_STORE_UNAVAILABLE"
    else:
        raise AssertionError("delete failure swallowed")


def test_failure_payload_never_contains_raw_source_path():
    result = SemanticIndex(Embedding(mode="failure"), FailingStore()).index_segments("corpus", [segment()])
    assert "/secret.wav" not in str(result.to_dict())


def test_dedicated_schema_mismatch_rejects_incompatible_vector_before_write():
    class RecordingStore(FailingStore):
        def __init__(self):
            super().__init__("write")
            self.write_attempted = False

        def replace_corpus(self, corpus_id, points):
            self.write_attempted = True
            super().replace_corpus(corpus_id, points)

    store = RecordingStore()
    try:
        SemanticIndex(Embedding(dimension=DIMENSION - 1), store)
    except SemanticIndexError as exc:
        assert exc.error_code == "EMBEDDING_DIMENSION_MISMATCH"
        assert store.write_attempted is False
        return
    raise AssertionError("schema-incompatible vector accepted")
