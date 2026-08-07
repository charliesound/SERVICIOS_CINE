from __future__ import annotations

from dataclasses import dataclass

from scripts.editorial_intelligence.semantic_index.embedding_backend import DIMENSION
from scripts.editorial_intelligence.semantic_index.semantic_index import (
    SemanticIndex,
    SemanticSearchQuery,
    document_from_segment,
    point_id_for_segment,
    serialize_result,
)
from scripts.editorial_intelligence.semantic_index.vector_store import (
    COLLECTION_NAME,
    DISTANCE_METRIC,
    VectorHit,
    VectorPoint,
)
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


PHASE = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.TRANSCRIPT_SEGMENT.V1"


def segment(index: int = 0, asset: str = "asset-a", text: str = "Camera battery") -> TranscriptSegment:
    return TranscriptSegment(
        phase=PHASE, asset_id=asset, source_audio_stream_index=0, segment_index=index,
        text=text, stt_start_seconds=1.0, stt_end_seconds=2.0,
        source_start_seconds=11.0, source_end_seconds=12.0,
        source_timecode={"available": False, "source_start_timecode": None, "source_end_timecode": None},
        provenance={"internal_source_reference": "/private/take.wav"}, error=None, warnings=[],
    )


@dataclass
class FakeEmbedding:
    provider: str = "ollama"
    model: str = "nomic-embed-text:v1.5"
    dimension: int = DIMENSION

    def __post_init__(self):
        self.calls: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        return [0.1] * self.dimension


class FakeStore:
    def __init__(self):
        self.points: dict[str, VectorPoint] = {}
        self.filters: list[dict] = []

    def replace_corpus(self, corpus_id, points):
        self.points = {point.point_id: point for point in points}

    def delete_corpus(self, corpus_id):
        self.points = {key: point for key, point in self.points.items() if point.payload["corpus_id"] != corpus_id}

    def search(self, *, corpus_id, vector, limit, filters):
        self.filters.append(filters)
        return [VectorHit(key, 0.8, point.payload) for key, point in self.points.items()
                if point.payload["corpus_id"] == corpus_id][:limit]


class MultiHitStore(FakeStore):
    def search(self, *, corpus_id, vector, limit, filters):
        self.filters.append(filters)
        scores = [0.91, 0.76, 0.42]
        return [
            VectorHit(key, scores[index], point.payload)
            for index, (key, point) in enumerate(self.points.items())
            if point.payload["corpus_id"] == corpus_id
        ][:limit]


def test_segment_maps_to_document_and_embedding_uses_text_only():
    embedding = FakeEmbedding()
    document = document_from_segment("corpus-a", segment())
    assert document.asset_id == "asset-a"
    assert document.segment_ref == "asset-a::0::0"
    assert document.text == "Camera battery"
    assert document.source_start_seconds == 11.0
    assert document.source_end_seconds == 12.0
    assert document.embedding_dimension == 768
    assert "/private" not in document.text
    index = SemanticIndex(embedding, FakeStore())
    result = index.index_segments("corpus-a", [segment()])
    assert result.indexed_count == 1
    assert embedding.calls == ["Camera battery"]


def test_one_vector_per_segment_and_payload_has_editorial_provenance():
    store = FakeStore()
    index = SemanticIndex(FakeEmbedding(), store)
    result = index.index_segments("corpus-a", [segment(0), segment(1, asset="asset-b")])
    assert result.indexed_count == 2
    assert len(store.points) == 2
    payload = next(iter(store.points.values())).payload
    assert {"asset_id", "segment_ref", "text", "source_start_seconds", "source_end_seconds"} <= payload.keys()
    assert "internal_source_reference" not in payload


def test_uuid5_is_deterministic_by_corpus_and_run_local_identity():
    first = point_id_for_segment("corpus-a", segment())
    assert first == point_id_for_segment("corpus-a", segment())
    assert first != point_id_for_segment("corpus-b", segment())
    assert first != point_id_for_segment("corpus-a", segment(asset="asset-b"))
    assert first != point_id_for_segment("corpus-a", segment(index=1))


def test_identical_text_with_different_provenance_is_not_deduplicated():
    store = FakeStore()
    index = SemanticIndex(FakeEmbedding(), store)
    result = index.index_segments("corpus-a", [segment(asset="asset-a", text="Sí, fue en 1998."), segment(asset="asset-b", text="Sí, fue en 1998.")])
    assert result.indexed_count == 2
    assert len(store.points) == 2


def test_search_returns_complete_future_qa_result_and_authorized_filters():
    store = FakeStore()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus-a", [segment()])
    results = index.search(SemanticSearchQuery("battery", corpus_id="corpus-a", asset_id="asset-a", source_audio_stream_index=0))
    assert len(results) == 1
    assert results[0].rank == 1
    assert results[0].asset_id == "asset-a"
    assert results[0].segment_ref == "asset-a::0::0"
    assert results[0].source_start_seconds == 11.0
    assert results[0].source_end_seconds == 12.0
    assert "internal_source_reference" not in results[0].to_dict()
    assert store.filters[-1] == {"corpus_id": "corpus-a", "asset_id": "asset-a", "source_audio_stream_index": 0}


def test_result_serialization_is_deterministic():
    store = FakeStore()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus-a", [segment()])
    result = index.search(SemanticSearchQuery("battery", corpus_id="corpus-a"))[0]
    assert serialize_result(result) == serialize_result(result)


def test_dedicated_cosine_distance_contract():
    assert COLLECTION_NAME == "cid_editorial_transcripts_v1"
    assert DISTANCE_METRIC == "Cosine"


def test_dedicated_multi_hit_ranking_preserves_rank_score_and_provenance():
    store = MultiHitStore()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus-a", [segment(0, "asset-a"), segment(1, "asset-b"), segment(2, "asset-c")])
    results = index.search(SemanticSearchQuery("query", top_k=3, corpus_id="corpus-a"))
    assert [result.rank for result in results] == [1, 2, 3]
    assert [result.score for result in results] == [0.91, 0.76, 0.42]
    assert [result.asset_id for result in results] == ["asset-a", "asset-b", "asset-c"]
    assert [result.source_start_seconds for result in results] == [11.0, 11.0, 11.0]


def test_dedicated_no_generative_behavior_returns_structured_retrieval_only():
    store = FakeStore()
    index = SemanticIndex(FakeEmbedding(), store)
    index.index_segments("corpus-a", [segment()])
    result = index.search(SemanticSearchQuery("query", corpus_id="corpus-a"))[0].to_dict()
    assert set(result) == {
        "rank", "score", "asset_id", "segment_ref", "text",
        "source_start_seconds", "source_end_seconds",
        "source_start_timecode", "source_end_timecode",
    }
    assert "answer" not in result
    assert "summary" not in result
    assert "llm_response" not in result
