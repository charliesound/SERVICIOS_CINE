from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Protocol

from scripts.editorial_intelligence.semantic_index.semantic_index import (
    MAX_TOP_K,
    SemanticSearchQuery,
    SemanticSearchResult,
)
from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    build_editorial_citation,
)
from services.llm.editorial_qa import (
    EditorialQAContext,
    EditorialQAGenerationProvider,
    EditorialQAGenerationRequest,
    GenerationError,
    GenerationUsage,
)


DEFAULT_TOP_K = 5


class EditorialQAOrchestrationError(RuntimeError):
    """Base class for sanitized orchestration failures."""


class EditorialQARequestError(EditorialQAOrchestrationError):
    pass


class EditorialQARetrievalError(EditorialQAOrchestrationError):
    pass


class EditorialQAProvenanceError(EditorialQAOrchestrationError):
    pass


class EditorialQARetriever(Protocol):
    def search(self, query: SemanticSearchQuery) -> list[SemanticSearchResult]:
        ...


@dataclass(frozen=True, slots=True)
class EditorialQARequest:
    question: str
    corpus_id: str
    top_k: int = DEFAULT_TOP_K


@dataclass(frozen=True, slots=True)
class EditorialQAResult:
    answer: str
    citations: tuple[dict[str, object], ...]
    insufficient_evidence: bool


@dataclass(frozen=True, slots=True)
class EditorialQAInternalResult:
    public_result: EditorialQAResult
    usage: GenerationUsage


class EditorialQAOrchestrator:
    def __init__(
        self,
        retriever: EditorialQARetriever,
        generation_provider: EditorialQAGenerationProvider,
    ) -> None:
        self._retriever = retriever
        self._generation_provider = generation_provider

    async def answer_question(self, request: EditorialQARequest) -> EditorialQAResult:
        result, _ = await self._answer_question(request)
        return result

    async def answer_question_internal(
        self, request: EditorialQARequest
    ) -> EditorialQAInternalResult:
        result, usage = await self._answer_question(request)
        return EditorialQAInternalResult(result, usage)

    async def _answer_question(
        self, request: EditorialQARequest
    ) -> tuple[EditorialQAResult, GenerationUsage]:
        _validate_request(request)
        try:
            results = self._retriever.search(
                SemanticSearchQuery(
                    query_text=request.question,
                    corpus_id=request.corpus_id,
                    top_k=request.top_k,
                )
            )
        except Exception as exc:
            if isinstance(exc, EditorialQAOrchestrationError):
                raise
            raise EditorialQARetrievalError("editorial retrieval failed") from exc

        selected = tuple(results)
        if not selected:
            return (
                EditorialQAResult(answer="", citations=(), insufficient_evidence=True),
                GenerationUsage(),
            )

        contexts, evidence_by_id = _build_context(selected)
        generation_request = EditorialQAGenerationRequest(
            question=request.question,
            contexts=contexts,
            allowed_citation_ids=tuple(evidence_by_id),
        )
        try:
            generated = await self._generation_provider.generate_editorial_qa(
                generation_request
            )
        except GenerationError:
            raise

        citations: list[dict[str, object]] = []
        try:
            for citation_id in generated.citation_ids:
                evidence = evidence_by_id[citation_id]
                citations.append(build_editorial_citation(_citation_segment(evidence)))
        except (KeyError, TypeError, ValueError) as exc:
            raise EditorialQAProvenanceError("editorial citation resolution failed") from exc

        return (
            EditorialQAResult(
                answer=generated.answer,
                citations=tuple(citations),
                insufficient_evidence=generated.insufficient_evidence,
            ),
            generated.usage,
        )


def _validate_request(request: EditorialQARequest) -> None:
    if not isinstance(request, EditorialQARequest):
        raise EditorialQARequestError("invalid editorial QA request")
    if not request.question.strip() or not request.corpus_id.strip():
        raise EditorialQARequestError("question and corpus_id are required")
    if request.top_k < 1 or request.top_k > MAX_TOP_K:
        raise EditorialQARequestError("top_k is outside the allowed range")


def _build_context(
    results: tuple[SemanticSearchResult, ...],
) -> tuple[tuple[EditorialQAContext, ...], dict[str, SemanticSearchResult]]:
    contexts: list[EditorialQAContext] = []
    evidence_by_id: dict[str, SemanticSearchResult] = {}
    for position, result in enumerate(results, 1):
        citation_id = f"CIT-{position:04d}"
        evidence_by_id[citation_id] = result
        contexts.append(
            EditorialQAContext(
                citation_id=citation_id,
                text=f"<source_data citation_id={citation_id}>\n{result.text}\n</source_data>",
            )
        )
    return tuple(contexts), evidence_by_id


def _citation_segment(result: SemanticSearchResult):
    return SimpleNamespace(
        asset_id=result.asset_id,
        segment_ref=result.segment_ref,
        text=result.text,
        source_start_seconds=result.source_start_seconds,
        source_end_seconds=result.source_end_seconds,
        source_timecode={
            "source_start_timecode": result.source_start_timecode,
            "source_end_timecode": result.source_end_timecode,
        },
    )
