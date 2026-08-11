from __future__ import annotations

import hashlib

from services.llm.editorial_qa import EditorialQAContext, EditorialQAGenerationRequest
from services.llm.editorial_qa_pilot_provider import (
    V3_BYTES,
    V3_INSTRUCTIONS,
    V3_SHA256,
    SeptemberPilotV3EditorialQAGenerationProvider,
)
from services.llm.openai_editorial_qa_provider import (
    EDITORIAL_QA_SCHEMA,
    EDITORIAL_QA_SYSTEM_INSTRUCTIONS,
)


def request() -> EditorialQAGenerationRequest:
    return EditorialQAGenerationRequest(
        question="What happened?",
        contexts=(EditorialQAContext("CIT-0001", "Evidence."),),
        allowed_citation_ids=("CIT-0001",),
    )


def test_v3_runtime_payload_identity_is_exact() -> None:
    encoded = V3_INSTRUCTIONS.encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == V3_SHA256
    assert len(encoded) == V3_BYTES == 1387
    assert V3_INSTRUCTIONS.endswith("\n")


def test_pilot_adapter_selects_v3_without_mutating_global_instruction() -> None:
    payload = SeptemberPilotV3EditorialQAGenerationProvider().build_request_payload(request())
    assert payload["input"][0]["content"][0]["text"] == V3_INSTRUCTIONS
    assert EDITORIAL_QA_SYSTEM_INSTRUCTIONS != V3_INSTRUCTIONS


def test_pilot_adapter_preserves_provider_invariants() -> None:
    payload = SeptemberPilotV3EditorialQAGenerationProvider().build_request_payload(request())
    assert payload["store"] is False
    assert "tools" not in payload
    assert payload["text"]["format"]["schema"] == EDITORIAL_QA_SCHEMA
    assert payload["text"]["format"]["strict"] is True
    assert payload["model"] == "gpt-5.6-luna"
