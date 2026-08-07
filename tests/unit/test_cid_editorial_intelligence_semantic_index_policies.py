from __future__ import annotations

from dataclasses import dataclass

from scripts.editorial_intelligence.semantic_index.embedding_backend import DIMENSION
from scripts.editorial_intelligence.semantic_index.semantic_index import (
    MAX_TOP_K,
    SemanticIndex,
    SemanticIndexError,
    SemanticSearchQuery,
)
from scripts.editorial_intelligence.semantic_index.vector_store import COLLECTION_NAME, VectorHit, VectorPoint
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1"


def segment(index=0, text="text", asset="asset"):
    return TranscriptSegment(PHASE, asset, 0, index, text, 0.0, 1.0, 5.0, 6.0,
                             {"available": False, "source_start_timecode": None, "source_end_timecode": None}, {}, None, [])


@dataclass
class FakeEmbedding:
    provider: str = "ollama"
    model: str = "nomic-embed-text:v1.5"
    dimension: int = DIMENSION

    def __post_init__(self):
        self.calls = []

    def embed(self, text):
        self.calls.append(text)
        return [0.0] * self.dimension


class Store:
    def __init__(self):
        self.points = {}
        self.deleted = []

    def replace_corpus(self, corpus_id, points):
        self.points = {point.point_id: point for point in points}

    def delete_corpus(self, corpus_id):
        self.deleted.append(corpus_id)
        self.points = {key: point for key, point in self.points.items() if point.payload["corpus_id"] != corpus_id}

    def search(self, *, corpus_id, vector, limit, filters):
        return [VectorHit(point.point_id, 0.5, point.payload) for point in self.points.values()
                if point.payload["corpus_id"] == corpus_id][:limit]


def test_empty_segment_is_skipped_without_embedding():
    embedding = FakeEmbedding()
    result = SemanticIndex(embedding, Store()).index_segments("corpus", [segment(text="  "), segment(index=1)])
    assert result.status == "INDEX_COMPLETED"
    assert result.skipped_count == 1
    assert result.warnings == ("segment 0: empty text skipped",)
    assert embedding.calls == ["text"]


def test_rebuild_is_repeatable_and_delete_is_corpus_scoped():
    store = Store()
    index = SemanticIndex(FakeEmbedding(), store)
    first = index.rebuild_current_corpus("corpus", [segment()])
    second = index.rebuild_current_corpus("corpus", [segment()])
    assert first.indexed_count == second.indexed_count == 1
    assert len(store.points) == 1
    index.delete_corpus("corpus")
    assert store.deleted == ["corpus"]
    assert store.points == {}


def test_empty_query_and_top_k_policy():
    index = SemanticIndex(FakeEmbedding(), Store())
    for query in ("", "  "):
        try:
            index.search(SemanticSearchQuery(query, corpus_id="corpus"))
        except SemanticIndexError as exc:
            assert exc.error_code == "SEARCH_INVALID_QUERY"
        else:
            raise AssertionError("empty query accepted")
    for value in (0, -1, MAX_TOP_K + 1):
        try:
            index.search(SemanticSearchQuery("query", top_k=value, corpus_id="corpus"))
        except SemanticIndexError as exc:
            assert exc.error_code == "SEARCH_INVALID_QUERY"
        else:
            raise AssertionError("invalid top_k accepted")


def test_default_and_explicit_top_k_are_forwarded():
    store = Store()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus", [segment(index=i) for i in range(3)])
    assert len(index.search(SemanticSearchQuery("query", corpus_id="corpus"))) == 3
    assert len(index.search(SemanticSearchQuery("query", top_k=1, corpus_id="corpus"))) == 1


def test_optional_safe_timecode_is_preserved():
    value = segment()
    value = TranscriptSegment(value.phase, value.asset_id, value.source_audio_stream_index, value.segment_index,
                              value.text, value.stt_start_seconds, value.stt_end_seconds, value.source_start_seconds,
                              value.source_end_seconds, {"available": True, "source_start_timecode": "00:00:05:00", "source_end_timecode": "00:00:06:00"}, {}, None, [])
    store = Store()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus", [value])
    result = index.search(SemanticSearchQuery("query", corpus_id="corpus"))[0]
    assert result.source_start_timecode == "00:00:05:00"
    assert result.source_end_timecode == "00:00:06:00"


def test_dedicated_cid_memory_isolation_uses_editorial_collection():
    store = Store()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus", [segment()])
    assert COLLECTION_NAME != "cid_memory"
    assert all(point.payload["corpus_id"] == "corpus" for point in store.points.values())
    assert store.deleted == []


def test_dedicated_model_change_requires_reindex_on_incompatible_dimension():
    try:
        SemanticIndex(
            FakeEmbedding(model="other-embedding-model", dimension=DIMENSION - 1),
            Store(),
        )
    except SemanticIndexError as exc:
        assert exc.error_code == "EMBEDDING_DIMENSION_MISMATCH"
        assert "other-embedding-model" not in str(exc)
        return
    raise AssertionError("incompatible model identity was accepted without reindex boundary")
