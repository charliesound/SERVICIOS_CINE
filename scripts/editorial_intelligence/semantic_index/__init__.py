"""Editorial semantic indexing contracts for TranscriptSegment V1."""

from scripts.editorial_intelligence.semantic_index.semantic_index import (
    IndexDocument,
    IndexOperationResult,
    SemanticIndex,
    SemanticIndexError,
    SemanticSearchQuery,
    SemanticSearchResult,
)

__all__ = [
    "IndexDocument",
    "IndexOperationResult",
    "SemanticIndex",
    "SemanticIndexError",
    "SemanticSearchQuery",
    "SemanticSearchResult",
]
