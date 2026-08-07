"""Vector-store adapter contracts for the isolated editorial collection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence


COLLECTION_NAME = "cid_editorial_transcripts_v1"
VECTOR_DIMENSION = 768
DISTANCE_METRIC = "Cosine"


class VectorStoreError(RuntimeError):
    """Sanitized vector-store failure."""


@dataclass(frozen=True)
class VectorPoint:
    point_id: str
    vector: tuple[float, ...]
    payload: dict[str, Any]


@dataclass(frozen=True)
class VectorHit:
    point_id: str
    score: float
    payload: dict[str, Any]


class VectorStore(Protocol):
    def replace_corpus(self, corpus_id: str, points: Sequence[VectorPoint]) -> None: ...

    def delete_corpus(self, corpus_id: str) -> None: ...

    def search(
        self,
        *,
        corpus_id: str,
        vector: Sequence[float],
        limit: int,
        filters: dict[str, Any],
    ) -> list[VectorHit]: ...
