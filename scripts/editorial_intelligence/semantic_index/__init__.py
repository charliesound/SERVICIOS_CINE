"""Editorial semantic indexing contracts for TranscriptSegment V1."""

from scripts.editorial_intelligence.semantic_index.semantic_index import (
    IndexDocument,
    IndexOperationResult,
    SemanticIndex,
    SemanticIndexError,
    SemanticSearchQuery,
    SemanticSearchResult,
)
from scripts.editorial_intelligence.semantic_index.runtime import build_local_semantic_index

__all__ = [
    "IndexDocument",
    "IndexOperationResult",
    "SemanticIndex",
    "SemanticIndexError",
    "SemanticSearchQuery",
    "SemanticSearchResult",
    "build_local_semantic_index",
]
