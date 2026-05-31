from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from routes.memory_routes import AnswerRequest, memory_answer
from schemas.auth_schema import TenantContext
from services.cid_rag_answer_service import (
    NO_CONTEXT_ANSWER,
    SYSTEM_PROMPT,
    CIDRAGAnswerService,
    build_answer_prompt,
)
from services.ollama_llm_service import OllamaLLMConnectionError
from services.ollama_llm_service import OllamaLLMService


def test_build_answer_prompt_includes_context_and_question() -> None:
    prompt = build_answer_prompt(
        "Que ocurre?",
        [
            {
                "source_type": "script_text",
                "title": "Guion",
                "source_id": "src-1",
                "score": 0.9,
                "text": "Una casa abandonada aparece en la noche.",
            }
        ],
        max_chars_per_chunk=1200,
    )
    assert "Contexto:" in prompt
    assert "Fuente 1 script_text" in prompt
    assert "Una casa abandonada" in prompt
    assert "Que ocurre?" in prompt


@pytest.mark.asyncio
async def test_answer_question_truncates_long_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()
    service.max_context_chunks = 5
    service.max_chars_per_chunk = 20
    service.max_prompt_chars = 120
    captured: dict[str, str] = {}

    async def fake_embed_query(question: str) -> list[float]:
        return [0.1] * 768

    async def fake_search(**kwargs):
        return [
            {
                "id": "1",
                "score": 0.91,
                "source_type": "storyboard_shot",
                "source_id": "shot-1",
                "source_table": "storyboard_shots",
                "title": "Plano 1",
                "text": "x" * 200,
                "chunk_index": 0,
                "chunk_count": 1,
                "tags": [],
            }
        ]

    async def fake_generate(*, prompt: str, system_prompt: str, model: str | None = None, temperature: float | None = None) -> str:
        captured["prompt"] = prompt
        captured["system_prompt"] = system_prompt
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="Pregunta",
        limit=5,
        include_sources=True,
    )
    assert result["answer"] == "Respuesta"
    assert result["usage"]["prompt_chars"] <= service.max_prompt_chars
    assert len(captured["prompt"]) <= service.max_prompt_chars
    assert SYSTEM_PROMPT.startswith("Eres CID")


@pytest.mark.asyncio
async def test_answer_question_filters_by_source_types(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()
    captured: dict[str, object] = {}

    async def fake_embed_query(question: str) -> list[float]:
        return [0.2] * 768

    async def fake_search(**kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="Pregunta",
        limit=5,
        source_types=["script_text", "storyboard_shot"],
    )
    assert result["answer"] == NO_CONTEXT_ANSWER
    assert captured["organization_id"] == "org-1"
    assert captured["project_id"] == "proj-1"
    assert captured["source_types"] == ["script_text", "storyboard_shot"]


@pytest.mark.asyncio
async def test_answer_question_without_results(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()

    async def fake_embed_query(question: str) -> list[float]:
        return [0.3] * 768

    async def fake_search(**kwargs):
        return []

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="Pregunta",
        limit=5,
    )
    assert result["answer"] == NO_CONTEXT_ANSWER
    assert result["sources"] == []
    assert result["usage"]["context_chunks"] == 0


@pytest.mark.asyncio
async def test_answer_question_ollama_error(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()

    async def fake_embed_query(question: str) -> list[float]:
        return [0.4] * 768

    async def fake_search(**kwargs):
        return [
            {
                "id": "1",
                "score": 0.9,
                "source_type": "script_text",
                "source_id": "src-1",
                "source_table": "projects",
                "title": "Guion",
                "text": "Texto",
                "chunk_index": 0,
                "chunk_count": 1,
                "tags": [],
            }
        ]

    async def fake_generate(**kwargs):
        raise OllamaLLMConnectionError("Ollama is unavailable")

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    with pytest.raises(OllamaLLMConnectionError):
        await service.answer_question(
            organization_id="org-1",
            project_id="proj-1",
            question="Pregunta",
            limit=5,
        )


@pytest.mark.asyncio
async def test_answer_question_limit_validation() -> None:
    service = CIDRAGAnswerService()
    with pytest.raises(ValueError, match="limit"):
        await service.answer_question(
            organization_id="org-1",
            project_id="proj-1",
            question="Pregunta",
            limit=11,
        )


@pytest.mark.asyncio
async def test_answer_question_hides_sources_when_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()

    async def fake_embed_query(question: str) -> list[float]:
        return [0.5] * 768

    async def fake_search(**kwargs):
        return [
            {
                "id": "1",
                "score": 0.88,
                "source_type": "production_breakdown",
                "source_id": "bd-1",
                "source_table": "production_breakdowns",
                "title": "Breakdown",
                "text": "Texto",
                "chunk_index": 0,
                "chunk_count": 1,
                "tags": [],
            }
        ]

    async def fake_generate(**kwargs):
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="Pregunta",
        limit=5,
        include_sources=False,
    )
    assert result["answer"] == "Respuesta"
    assert result["sources"] == []


@pytest.mark.asyncio
async def test_memory_answer_uses_tenant_organization(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = TenantContext(user_id="user-1", organization_id="org-tenant", role="admin")
    captured: dict[str, object] = {}

    async def fake_answer_question(**kwargs):
        captured.update(kwargs)
        return {
            "answer": "Respuesta",
            "project_id": "proj-1",
            "organization_id": kwargs["organization_id"],
            "model": "qwen2.5:14B",
            "sources": [],
            "usage": {"context_chunks": 0, "prompt_chars": 10},
        }

    monkeypatch.setattr("routes.memory_routes.cid_rag_answer_service.answer_question", fake_answer_question)

    response = await memory_answer(
        project_id="proj-1",
        req=AnswerRequest(question="Pregunta", limit=5, include_sources=True),
        tenant=tenant,
        db=None,
    )
    assert response.organization_id == "org-tenant"
    assert captured["organization_id"] == "org-tenant"
    assert captured["project_id"] == "proj-1"


@pytest.mark.asyncio
async def test_ollama_generate_payload_includes_num_predict_and_stream_false(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        @staticmethod
        def raise_for_status() -> None:
            return None

        @staticmethod
        def json() -> dict[str, str]:
            return {"response": "Respuesta completa"}

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

        async def post(self, url: str, json: dict[str, object]):
            captured["url"] = url
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("services.ollama_llm_service.httpx.AsyncClient", lambda timeout: FakeClient())

    service = OllamaLLMService()
    result = await service.generate(prompt="Pregunta", system_prompt="Sistema")

    assert result == "Respuesta completa"
    assert captured["url"] == f"{service.base_url}/api/generate"
    payload = captured["json"]
    assert payload["stream"] is False
    assert payload["options"]["num_predict"] == 512
