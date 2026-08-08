from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


class GenerationError(RuntimeError):
    """Base class for provider-neutral generation failures."""


class GenerationAuthenticationError(GenerationError):
    pass


class GenerationAuthorizationError(GenerationError):
    pass


class GenerationRateLimitError(GenerationError):
    pass


class GenerationTimeoutError(GenerationError):
    pass


class GenerationTransportError(GenerationError):
    pass


class GenerationStructuredOutputError(GenerationError):
    pass


class GenerationRefusalError(GenerationError):
    pass


class GenerationIncompleteResponseError(GenerationError):
    pass


class GenerationCitationValidationError(GenerationError):
    pass


@dataclass(frozen=True, slots=True)
class EditorialQAContext:
    citation_id: str
    text: str


@dataclass(frozen=True, slots=True)
class EditorialQAGenerationRequest:
    question: str
    contexts: tuple[EditorialQAContext, ...]
    allowed_citation_ids: tuple[str, ...]
    model: str | None = None
    timeout_seconds: float | None = None
    max_output_tokens: int | None = None
    reasoning_effort: str | None = None


@dataclass(frozen=True, slots=True)
class GenerationUsage:
    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    latency_seconds: float | None = None
    provider_request_id: str | None = None


@dataclass(frozen=True, slots=True)
class EditorialQAGenerationResult:
    answer: str
    citation_ids: tuple[str, ...]
    insufficient_evidence: bool
    provider: str
    model: str
    usage: GenerationUsage = field(default_factory=GenerationUsage)


class EditorialQAGenerationProvider(Protocol):
    async def generate_editorial_qa(
        self, request: EditorialQAGenerationRequest
    ) -> EditorialQAGenerationResult:
        ...


def validate_citation_ids(
    citation_ids: list[str] | tuple[str, ...],
    allowed_citation_ids: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    if not isinstance(citation_ids, (list, tuple)):
        raise GenerationCitationValidationError("citation_ids must be a list")
    if any(not isinstance(value, str) for value in citation_ids):
        raise GenerationCitationValidationError("citation_ids must contain strings")
    if len(set(citation_ids)) != len(citation_ids):
        raise GenerationCitationValidationError("duplicate citation IDs are not allowed")
    allowed = set(allowed_citation_ids)
    unknown = [value for value in citation_ids if value not in allowed]
    if unknown:
        raise GenerationCitationValidationError("unknown citation ID")
    return tuple(citation_ids)


def validate_generation_payload(
    payload: Any,
    allowed_citation_ids: tuple[str, ...] | list[str],
) -> tuple[str, tuple[str, ...], bool]:
    if not isinstance(payload, dict):
        raise GenerationStructuredOutputError("structured output must be an object")
    if set(payload) != {"answer", "citation_ids", "insufficient_evidence"}:
        raise GenerationStructuredOutputError("structured output fields are invalid")
    answer = payload.get("answer")
    insufficient_evidence = payload.get("insufficient_evidence")
    if not isinstance(answer, str):
        raise GenerationStructuredOutputError("answer must be a string")
    if not isinstance(insufficient_evidence, bool):
        raise GenerationStructuredOutputError("insufficient_evidence must be a boolean")
    citations = validate_citation_ids(payload.get("citation_ids"), allowed_citation_ids)
    return answer, citations, insufficient_evidence
