from __future__ import annotations

import asyncio
import httpx
import pytest

from services.llm.editorial_qa import (
    EditorialQAContext,
    EditorialQAGenerationRequest,
    GenerationAuthenticationError,
    GenerationAuthorizationError,
    GenerationIncompleteResponseError,
    GenerationRateLimitError,
    GenerationRefusalError,
    GenerationStructuredOutputError,
    GenerationTimeoutError,
    GenerationTransportError,
)
from services.llm.openai_editorial_qa_provider import (
    EDITORIAL_QA_SCHEMA,
    OpenAIEditorialQAGenerationProvider,
)


def request() -> EditorialQAGenerationRequest:
    return EditorialQAGenerationRequest(
        question="What happened?",
        contexts=(EditorialQAContext("REAL-CIT-0001", "The station became an archive."),),
        allowed_citation_ids=("REAL-CIT-0001",),
    )


class FakeAsyncClient:
    def __init__(self, response: httpx.Response | None = None, error: Exception | None = None):
        self.response = response
        self.error = error
        self.request = None

    async def post(self, url, **kwargs):
        self.request = (url, kwargs)
        if self.error:
            raise self.error
        return self.response

    async def aclose(self):
        return None


def response(payload, status_code=200, headers=None):
    return httpx.Response(status_code, json=payload, headers=headers or {})


def completed_payload(result=None):
    return {
        "id": "resp_test",
        "model": "gpt-5.6-luna",
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": __import__('json').dumps(result or {"answer": "Supported.", "citation_ids": ["REAL-CIT-0001"], "insufficient_evidence": False})}]}],
        "usage": {"input_tokens": 12, "output_tokens": 7, "input_token_details": {"cached_tokens": 3}, "output_token_details": {"reasoning_tokens": 2}},
    }


def test_request_uses_responses_contract_and_parses_usage():
    client = FakeAsyncClient(response(completed_payload(), headers={"x-request-id": "req_test"}))
    provider = OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=client)
    result = asyncio.run(provider.generate_editorial_qa(request()))
    url, kwargs = client.request
    payload = kwargs["json"]
    assert url.endswith("/v1/responses")
    assert payload["model"] == "gpt-5.6-luna"
    assert payload["store"] is False
    assert payload["stream"] is False
    assert payload["reasoning"] == {"effort": "none"}
    assert "tools" not in payload
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["text"]["format"]["schema"] == EDITORIAL_QA_SCHEMA
    assert result.answer == "Supported."
    assert result.usage.input_tokens == 12
    assert result.usage.cached_input_tokens == 3
    assert result.usage.output_tokens == 7
    assert result.usage.reasoning_tokens == 2
    assert result.usage.provider_request_id == "req_test"


def test_insufficient_evidence_and_multiple_output_items_parse():
    payload = completed_payload({"answer": "", "citation_ids": [], "insufficient_evidence": True})
    payload["output"].insert(0, {"type": "reasoning", "summary": []})
    client = FakeAsyncClient(response(payload))
    result = asyncio.run(OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=client).generate_editorial_qa(request()))
    assert result.insufficient_evidence is True
    assert result.citation_ids == ()


def test_missing_key_is_sanitized(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(GenerationAuthenticationError, match="not configured") as exc_info:
        asyncio.run(OpenAIEditorialQAGenerationProvider().generate_editorial_qa(request()))
    assert "test-openai-key" not in str(exc_info.value)


@pytest.mark.parametrize("status,error", [(401, GenerationAuthenticationError), (403, GenerationAuthorizationError), (429, GenerationRateLimitError)])
def test_http_failures_normalize(status, error):
    client = FakeAsyncClient(response(payload={}, status_code=status))
    with pytest.raises(error):
        asyncio.run(OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=client).generate_editorial_qa(request()))


def response_payload():
    return {"error": {"message": "sanitized"}}


def test_timeout_and_transport_failures_normalize():
    timeout_client = FakeAsyncClient(error=httpx.ReadTimeout("timeout"))
    with pytest.raises(GenerationTimeoutError):
        asyncio.run(OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=timeout_client).generate_editorial_qa(request()))
    transport_client = FakeAsyncClient(error=httpx.ConnectError("connection"))
    with pytest.raises(GenerationTransportError):
        asyncio.run(OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=transport_client).generate_editorial_qa(request()))


@pytest.mark.parametrize("payload,error", [({"status": "incomplete", "incomplete_details": {}}, GenerationIncompleteResponseError), ({"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}]}, GenerationRefusalError), ({"status": "completed", "output": []}, GenerationStructuredOutputError), ({"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": "not-json"}]}]}, GenerationStructuredOutputError)])
def test_response_failures_normalize(payload, error):
    with pytest.raises(error):
        asyncio.run(OpenAIEditorialQAGenerationProvider(api_key="test-openai-key-not-real", client=FakeAsyncClient(response(payload))).generate_editorial_qa(request()))
