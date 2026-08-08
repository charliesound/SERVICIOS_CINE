from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest

from scripts.editorial_intelligence.semantic_index.semantic_index import (
    SemanticSearchQuery,
    SemanticSearchResult,
)
from services.llm.editorial_qa import (
    EditorialQAGenerationResult,
    GenerationCitationValidationError,
    GenerationUsage,
    validate_citation_ids,
)
from services.editorial_qa_orchestration import (
    EditorialQAOrchestrationError,
    EditorialQAOrchestrator,
    EditorialQARequest,
    EditorialQARequestError,
    EditorialQARetrievalError,
)


def result(index: int, text: str = "Evidence", *, timecode: str | None = None):
    return SemanticSearchResult(
        rank=index + 1,
        score=0.9 - index / 10,
        asset_id="asset-a",
        segment_ref=f"asset-a::0::{index}",
        text=text,
        source_start_seconds=10.0 + index,
        source_end_seconds=11.0 + index,
        source_start_timecode=timecode,
        source_end_timecode=None,
    )


@dataclass
class FakeRetriever:
    results: list[SemanticSearchResult]
    query: SemanticSearchQuery | None = None
    calls: int = 0
    error: Exception | None = None

    def search(self, query: SemanticSearchQuery):
        self.calls += 1
        self.query = query
        if self.error:
            raise self.error
        return self.results


class FakeProvider:
    def __init__(self, citation_ids=("CIT-0001",), insufficient=False, error=None):
        self.request = None
        self.calls = 0
        self.citation_ids = tuple(citation_ids)
        self.insufficient = insufficient
        self.error = error

    async def generate_editorial_qa(self, request):
        self.calls += 1
        self.request = request
        if self.error:
            raise self.error
        validate_citation_ids(self.citation_ids, request.allowed_citation_ids)
        return EditorialQAGenerationResult(
            answer="Supported.",
            citation_ids=self.citation_ids,
            insufficient_evidence=self.insufficient,
            provider="fake",
            model="fake-model",
            usage=GenerationUsage(output_tokens=3),
        )


def run(orchestrator, request):
    return asyncio.run(orchestrator.answer_question(request))


def test_happy_path_propagates_query_and_builds_public_citation():
    retriever = FakeRetriever([result(0, "The station opened.")])
    provider = FakeProvider()
    answer = run(
        EditorialQAOrchestrator(retriever, provider),
        EditorialQARequest("What happened?", "corpus-a"),
    )
    assert retriever.query == SemanticSearchQuery("What happened?", corpus_id="corpus-a", top_k=5)
    assert provider.request.allowed_citation_ids == ("CIT-0001",)
    assert provider.request.contexts[0].text.startswith("<source_data")
    assert answer.answer == "Supported."
    assert answer.citations[0]["segment_ref"] == "asset-a::0::0"
    assert answer.citations[0]["source_start_seconds"] == 10.0
    assert "source_path" not in answer.citations[0]


def test_top_k_override_and_order_are_preserved():
    retriever = FakeRetriever([result(1), result(0)])
    provider = FakeProvider(("CIT-0001", "CIT-0002"))
    answer = run(
        EditorialQAOrchestrator(retriever, provider),
        EditorialQARequest("Question", "corpus-a", top_k=2),
    )
    assert retriever.query.top_k == 2
    assert [citation["segment_ref"] for citation in answer.citations] == [
        "asset-a::0::1",
        "asset-a::0::0",
    ]
    assert [context.citation_id for context in provider.request.contexts] == [
        "CIT-0001",
        "CIT-0002",
    ]


def test_same_order_assigns_same_ids_and_timecode_is_preserved():
    retriever = FakeRetriever([result(0, timecode="01:00:00:00")])
    provider = FakeProvider()
    answer = run(
        EditorialQAOrchestrator(retriever, provider),
        EditorialQARequest("Question", "corpus-a"),
    )
    assert provider.request.allowed_citation_ids == ("CIT-0001",)
    assert answer.citations[0]["source_start_timecode"] == "01:00:00:00"


def test_zero_evidence_skips_provider_and_returns_insufficient_evidence():
    retriever = FakeRetriever([])
    provider = FakeProvider()
    answer = run(
        EditorialQAOrchestrator(retriever, provider),
        EditorialQARequest("Question", "corpus-a"),
    )
    assert answer == type(answer)("", (), True)
    assert provider.calls == 0


def test_provider_insufficient_evidence_is_preserved():
    provider = FakeProvider((), insufficient=True)
    answer = run(
        EditorialQAOrchestrator(FakeRetriever([result(0)]), provider),
        EditorialQARequest("Question", "corpus-a"),
    )
    assert answer.insufficient_evidence is True
    assert answer.citations == ()


def test_unknown_and_duplicate_citations_fail_deterministically():
    with pytest.raises(GenerationCitationValidationError):
        run(
            EditorialQAOrchestrator(
                FakeRetriever([result(0)]), FakeProvider(("CIT-9999",))
            ),
            EditorialQARequest("Question", "corpus-a"),
        )
    with pytest.raises(GenerationCitationValidationError):
        run(
            EditorialQAOrchestrator(
                FakeRetriever([result(0), result(1)]),
                FakeProvider(("CIT-0001", "CIT-0001")),
            ),
            EditorialQARequest("Question", "corpus-a"),
        )


def test_invalid_request_and_retrieval_failure_are_not_swallowed():
    with pytest.raises(EditorialQARequestError):
        run(EditorialQAOrchestrator(FakeRetriever([]), FakeProvider()), EditorialQARequest("", "corpus-a"))
    with pytest.raises(EditorialQARetrievalError):
        run(
            EditorialQAOrchestrator(FakeRetriever([], error=RuntimeError("qdrant")), FakeProvider()),
            EditorialQARequest("Question", "corpus-a"),
        )


def test_provider_failure_propagates_without_network_or_fallback():
    provider_error = RuntimeError("provider failure")
    with pytest.raises(RuntimeError, match="provider failure"):
        run(
            EditorialQAOrchestrator(FakeRetriever([result(0)]), FakeProvider(error=provider_error)),
            EditorialQARequest("Question", "corpus-a"),
        )


def test_request_contract_has_no_clients_or_media_inputs():
    request = EditorialQARequest("Question", "corpus-a")
    assert not hasattr(request, "qdrant")
    assert not hasattr(request, "openai")
    assert not hasattr(request, "media_path")
    assert not hasattr(request, "raw_media")
