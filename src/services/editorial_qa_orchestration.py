from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Callable, Protocol

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
_DiagnosticSink = Callable[[dict[str, object]], None]


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
        diagnostic_sink: _DiagnosticSink | None = None,
    ) -> None:
        self._retriever = retriever
        self._generation_provider = generation_provider
        self._diagnostic_sink = diagnostic_sink

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
            public_result = EditorialQAResult(answer="", citations=(), insufficient_evidence=True)
            self._emit_diagnostic(
                request,
                results,
                selected,
                (),
                {},
                public_result,
                None,
            )
            return public_result, GenerationUsage()

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

        public_result = EditorialQAResult(
            answer=generated.answer,
            citations=tuple(citations),
            insufficient_evidence=generated.insufficient_evidence,
        )
        self._emit_diagnostic(
            request,
            results,
            selected,
            contexts,
            evidence_by_id,
            public_result,
            generated,
        )
        return public_result, generated.usage

    def _emit_diagnostic(
        self,
        request: EditorialQARequest,
        results: tuple[SemanticSearchResult, ...] | list[SemanticSearchResult],
        selected: tuple[SemanticSearchResult, ...],
        contexts: tuple[EditorialQAContext, ...],
        evidence_by_id: dict[str, SemanticSearchResult],
        public_result: EditorialQAResult,
        generated,
    ) -> None:
        if self._diagnostic_sink is None:
            return

        result_by_citation = {
            citation_id: citation
            for citation_id, citation in zip(
                generated.citation_ids if generated is not None else (),
                public_result.citations,
            )
        }
        context_bytes = _context_wire_text(contexts).encode("utf-8")
        self._diagnostic_sink(
            {
                "schema_version": "CID.EDITORIAL_QA.RUNTIME_DIAGNOSTIC_SNAPSHOT.V1",
                "question_sha256": hashlib.sha256(request.question.encode("utf-8")).hexdigest(),
                "corpus_id": request.corpus_id,
                "retrieved_result_count": len(results),
                "retrieved_results": [_retrieval_diagnostic(result) for result in results],
                "selected_evidence_count": len(selected),
                "selected_evidence": [
                    _selected_evidence_diagnostic(citation_id, evidence)
                    for citation_id, evidence in evidence_by_id.items()
                ],
                "selected_context_bytes": len(context_bytes),
                "selected_context_sha256": hashlib.sha256(context_bytes).hexdigest(),
                "citation_id_to_canonical_segment_map": {
                    citation_id: evidence.segment_ref
                    for citation_id, evidence in evidence_by_id.items()
                },
                "provider_boundary": _provider_boundary_diagnostic(
                    self._generation_provider,
                    contexts,
                    tuple(evidence_by_id),
                ),
                "logical_result": {
                    "answer": public_result.answer,
                    "citation_ids": list(generated.citation_ids) if generated is not None else [],
                    "insufficient_evidence": public_result.insufficient_evidence,
                },
                "resolved_returned_citations": [
                    {"citation_id": citation_id, "citation": citation}
                    for citation_id, citation in result_by_citation.items()
                ],
            }
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


def _context_wire_text(contexts: tuple[EditorialQAContext, ...]) -> str:
    return "\n\n".join(
        f"[{context.citation_id}]\n{context.text}" for context in contexts
    )


def _retrieval_diagnostic(result: SemanticSearchResult) -> dict[str, object]:
    return {
        "rank": result.rank,
        "canonical_segment_id": result.segment_ref,
        "asset_id": result.asset_id,
        "score": result.score,
        "source_start": result.source_start_seconds,
        "source_end": result.source_end_seconds,
        "text_sha256": hashlib.sha256(result.text.encode("utf-8")).hexdigest(),
    }


def _selected_evidence_diagnostic(
    citation_id: str,
    result: SemanticSearchResult,
) -> dict[str, object]:
    return {
        "citation_id": citation_id,
        "canonical_segment_id": result.segment_ref,
        "asset_id": result.asset_id,
        "source_start": result.source_start_seconds,
        "source_end": result.source_end_seconds,
        "score": result.score,
        "text_sha256": hashlib.sha256(result.text.encode("utf-8")).hexdigest(),
    }


def _provider_boundary_diagnostic(
    provider: EditorialQAGenerationProvider,
    contexts: tuple[EditorialQAContext, ...],
    allowed_citation_ids: tuple[str, ...],
) -> dict[str, object]:
    provider_module = sys.modules.get(provider.__class__.__module__)
    return {
        "provider_class": provider.__class__.__name__,
        "model": getattr(provider, "model", None),
        "instruction_identity": getattr(provider_module, "V3_SHA256", None),
        "allowed_citation_ids": list(allowed_citation_ids),
        "context_count": len(contexts),
        "context_bytes": len(_context_wire_text(contexts).encode("utf-8")),
        "context_sha256": hashlib.sha256(
            _context_wire_text(contexts).encode("utf-8")
        ).hexdigest(),
    }


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
