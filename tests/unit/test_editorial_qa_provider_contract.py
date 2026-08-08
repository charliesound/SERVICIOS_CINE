from __future__ import annotations

import pytest

from services.llm.editorial_qa import (
    EditorialQAContext,
    EditorialQAGenerationRequest,
    EditorialQAGenerationResult,
    GenerationCitationValidationError,
    GenerationUsage,
    validate_generation_payload,
)


def test_request_accepts_prepared_text_only() -> None:
    request = EditorialQAGenerationRequest(
        question="What happened?",
        contexts=(EditorialQAContext("REAL-CIT-0001", "A factual excerpt."),),
        allowed_citation_ids=("REAL-CIT-0001",),
    )
    assert request.contexts[0].text == "A factual excerpt."
    assert not hasattr(request, "media")
    assert not hasattr(request, "qdrant")


def test_valid_result_has_provider_neutral_logical_fields() -> None:
    result = EditorialQAGenerationResult(
        answer="The archive opened.",
        citation_ids=("REAL-CIT-0001",),
        insufficient_evidence=False,
        provider="openai",
        model="gpt-5.6-luna",
        usage=GenerationUsage(input_tokens=10),
    )
    assert result.answer == "The archive opened."
    assert result.citation_ids == ("REAL-CIT-0001",)
    assert result.usage.input_tokens == 10
    assert not hasattr(result, "asset_id")
    assert not hasattr(result, "source_path")


def test_allowed_citation_is_accepted() -> None:
    answer, citations, insufficient = validate_generation_payload(
        {
            "answer": "Supported.",
            "citation_ids": ["REAL-CIT-0001"],
            "insufficient_evidence": False,
        },
        ["REAL-CIT-0001"],
    )
    assert (answer, citations, insufficient) == ("Supported.", ("REAL-CIT-0001",), False)


def test_unknown_citation_is_rejected_deterministically() -> None:
    with pytest.raises(GenerationCitationValidationError):
        validate_generation_payload(
            {"answer": "x", "citation_ids": ["REAL-CIT-9999"], "insufficient_evidence": False},
            ["REAL-CIT-0001"],
        )


def test_duplicate_citation_is_rejected_deterministically() -> None:
    with pytest.raises(GenerationCitationValidationError):
        validate_generation_payload(
            {"answer": "x", "citation_ids": ["REAL-CIT-0001", "REAL-CIT-0001"], "insufficient_evidence": False},
            ["REAL-CIT-0001"],
        )


def test_unexpected_provenance_field_is_rejected() -> None:
    with pytest.raises(Exception):
        validate_generation_payload(
            {"answer": "x", "citation_ids": [], "insufficient_evidence": True, "timecode": "00:01"},
            [],
        )
