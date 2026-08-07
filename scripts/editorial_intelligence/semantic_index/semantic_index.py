"""Source-cited semantic indexing for published TranscriptSegment objects."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Sequence

from scripts.editorial_intelligence.semantic_index.embedding_backend import (
    DIMENSION,
    MODEL,
    PROVIDER,
    EmbeddingBackend,
    EmbeddingBackendError,
)
from scripts.editorial_intelligence.semantic_index.vector_store import (
    COLLECTION_NAME,
    DISTANCE_METRIC,
    VectorPoint,
    VectorStore,
    VectorStoreError,
)
from scripts.editorial_intelligence.transcript_provenance import TranscriptSegment


INDEX_DOCUMENT_VERSION = "CID.SEMANTIC_INDEX_DOCUMENT.V1"
PAYLOAD_SCHEMA_VERSION = "1"
POINT_ID_NAMESPACE = uuid.NAMESPACE_URL
DEFAULT_TOP_K = 5
MAX_TOP_K = 20


class SemanticIndexError(ValueError):
    def __init__(self, error_code: str, message_sanitized: str) -> None:
        super().__init__(message_sanitized)
        self.error_code = error_code
        self.message_sanitized = message_sanitized


@dataclass(frozen=True)
class IndexDocument:
    index_document_version: str
    corpus_id: str
    point_id: str
    asset_id: str
    segment_ref: str
    source_audio_stream_index: int | None
    segment_index: int
    text: str
    source_start_seconds: float
    source_end_seconds: float
    source_start_timecode: str | None
    source_end_timecode: str | None
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int
    payload_schema_version: str = PAYLOAD_SCHEMA_VERSION

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SemanticSearchQuery:
    query_text: str
    top_k: int = DEFAULT_TOP_K
    corpus_id: str = ""
    asset_id: str | None = None
    source_audio_stream_index: int | None = None


@dataclass(frozen=True)
class SemanticSearchResult:
    rank: int
    score: float
    asset_id: str
    segment_ref: str
    text: str
    source_start_seconds: float
    source_end_seconds: float
    source_start_timecode: str | None
    source_end_timecode: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IndexOperationResult:
    status: str
    corpus_id: str
    indexed_count: int
    skipped_count: int
    failures: tuple[dict[str, str], ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["failures"] = list(self.failures)
        value["warnings"] = list(self.warnings)
        return value


def point_id_for_segment(corpus_id: str, segment: TranscriptSegment) -> str:
    corpus = _required_text(corpus_id, "corpus_id")
    if not isinstance(segment, TranscriptSegment):
        raise SemanticIndexError("INVALID_INPUT", "input must contain TranscriptSegment objects")
    identity = "/".join(
        (
            INDEX_DOCUMENT_VERSION,
            corpus,
            _required_text(segment.asset_id, "asset_id"),
            str(segment.source_audio_stream_index),
            str(segment.segment_index),
        )
    )
    return str(uuid.uuid5(POINT_ID_NAMESPACE, identity))


def document_from_segment(
    corpus_id: str,
    segment: TranscriptSegment,
    *,
    embedding_provider: str = PROVIDER,
    embedding_model: str = MODEL,
    embedding_dimension: int = DIMENSION,
) -> IndexDocument:
    corpus = _required_text(corpus_id, "corpus_id")
    if not isinstance(segment, TranscriptSegment):
        raise SemanticIndexError("INVALID_INPUT", "input must contain TranscriptSegment objects")
    text = segment.text if isinstance(segment.text, str) else ""
    if not text.strip():
        raise SemanticIndexError("INVALID_INPUT", "segment text is empty")
    if embedding_dimension <= 0:
        raise SemanticIndexError("INVALID_INPUT", "embedding dimension is invalid")
    source_timecode = segment.source_timecode or {}
    return IndexDocument(
        index_document_version=INDEX_DOCUMENT_VERSION,
        corpus_id=corpus,
        point_id=point_id_for_segment(corpus, segment),
        asset_id=segment.asset_id,
        segment_ref=segment.segment_ref,
        source_audio_stream_index=segment.source_audio_stream_index,
        segment_index=segment.segment_index,
        text=text,
        source_start_seconds=segment.source_start_seconds,
        source_end_seconds=segment.source_end_seconds,
        source_start_timecode=source_timecode.get("source_start_timecode"),
        source_end_timecode=source_timecode.get("source_end_timecode"),
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        embedding_dimension=embedding_dimension,
    )


class SemanticIndex:
    def __init__(self, embedding_backend: EmbeddingBackend, vector_store: VectorStore) -> None:
        self.embedding_backend = embedding_backend
        self.vector_store = vector_store
        if embedding_backend.dimension != DIMENSION:
            raise SemanticIndexError("EMBEDDING_DIMENSION_MISMATCH", "embedding dimension mismatch")

    def index_segments(
        self,
        corpus_id: str,
        segments: Iterable[TranscriptSegment],
    ) -> IndexOperationResult:
        corpus = _required_text(corpus_id, "corpus_id")
        documents: list[IndexDocument] = []
        points: list[VectorPoint] = []
        failures: list[dict[str, str]] = []
        warnings: list[str] = []
        skipped = 0
        for segment in segments:
            if not isinstance(segment, TranscriptSegment):
                failures.append({"error_code": "INVALID_INPUT", "message": "invalid transcript segment"})
                continue
            if not segment.text.strip():
                skipped += 1
                warnings.append(f"segment {segment.segment_index}: empty text skipped")
                continue
            try:
                document = document_from_segment(
                    corpus,
                    segment,
                    embedding_provider=self.embedding_backend.provider,
                    embedding_model=self.embedding_backend.model,
                    embedding_dimension=self.embedding_backend.dimension,
                )
                vector = tuple(self.embedding_backend.embed(document.text))
                if len(vector) != DIMENSION:
                    raise SemanticIndexError("EMBEDDING_DIMENSION_MISMATCH", "embedding dimension mismatch")
                documents.append(document)
                points.append(VectorPoint(document.point_id, vector, document.to_payload()))
            except SemanticIndexError as exc:
                failures.append({"error_code": exc.error_code, "message": exc.message_sanitized})
            except EmbeddingBackendError as exc:
                code = "EMBEDDING_DIMENSION_MISMATCH" if "dimension" in str(exc) else "EMBEDDING_FAILED"
                failures.append({"error_code": code, "message": str(exc)})
            except Exception:
                failures.append({"error_code": "EMBEDDING_FAILED", "message": "embedding failed"})

        if failures and not points:
            return IndexOperationResult("INDEX_PARTIAL", corpus, 0, skipped, tuple(failures), tuple(warnings))
        if failures:
            return IndexOperationResult("INDEX_PARTIAL", corpus, 0, skipped, tuple(failures), tuple(warnings))
        try:
            self.vector_store.replace_corpus(corpus, points)
        except VectorStoreError:
            return IndexOperationResult(
                "INDEX_PARTIAL", corpus, 0, skipped,
                ({"error_code": "INDEX_WRITE_FAILED", "message": "index write failed"},), tuple(warnings),
            )
        return IndexOperationResult("INDEX_COMPLETED", corpus, len(documents), skipped, (), tuple(warnings))

    def rebuild_current_corpus(self, corpus_id: str, segments: Iterable[TranscriptSegment]) -> IndexOperationResult:
        return self.index_segments(corpus_id, segments)

    def delete_corpus(self, corpus_id: str) -> None:
        try:
            self.vector_store.delete_corpus(_required_text(corpus_id, "corpus_id"))
        except VectorStoreError as exc:
            raise SemanticIndexError("VECTOR_STORE_UNAVAILABLE", "vector store unavailable") from exc

    def search(self, query: SemanticSearchQuery) -> list[SemanticSearchResult]:
        if not isinstance(query, SemanticSearchQuery):
            raise SemanticIndexError("SEARCH_INVALID_QUERY", "invalid search query")
        if not query.query_text.strip() or not query.corpus_id.strip():
            raise SemanticIndexError("SEARCH_INVALID_QUERY", "query text and corpus_id are required")
        if query.top_k < 1 or query.top_k > MAX_TOP_K:
            raise SemanticIndexError("SEARCH_INVALID_QUERY", "top_k is outside allowed range")
        try:
            vector = self.embedding_backend.embed(query.query_text)
            hits = self.vector_store.search(
                corpus_id=query.corpus_id,
                vector=vector,
                limit=query.top_k,
                filters={
                    key: value for key, value in {
                        "corpus_id": query.corpus_id,
                        "asset_id": query.asset_id,
                        "source_audio_stream_index": query.source_audio_stream_index,
                    }.items() if value is not None
                },
            )
        except EmbeddingBackendError as exc:
            raise SemanticIndexError("EMBEDDING_FAILED", "embedding failed") from exc
        except VectorStoreError as exc:
            raise SemanticIndexError("SEARCH_FAILED", "search failed") from exc
        ordered = sorted(hits, key=lambda hit: (-float(hit.score), hit.point_id))
        results: list[SemanticSearchResult] = []
        for rank, hit in enumerate(ordered[: query.top_k], 1):
            payload = hit.payload
            try:
                results.append(SemanticSearchResult(
                    rank=rank, score=float(hit.score), asset_id=payload["asset_id"],
                    segment_ref=payload["segment_ref"], text=payload["text"],
                    source_start_seconds=payload["source_start_seconds"],
                    source_end_seconds=payload["source_end_seconds"],
                    source_start_timecode=payload.get("source_start_timecode"),
                    source_end_timecode=payload.get("source_end_timecode"),
                ))
            except (KeyError, TypeError):
                raise SemanticIndexError("SEARCH_FAILED", "invalid vector payload") from None
        return results


def serialize_result(result: SemanticSearchResult) -> str:
    return json.dumps(result.to_dict(), sort_keys=True, separators=(",", ":"))


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SemanticIndexError("INVALID_INPUT", f"{field} is required")
    return value.strip()
