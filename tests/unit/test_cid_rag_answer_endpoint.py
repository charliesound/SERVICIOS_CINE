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
    assert "Contexto recuperado del proyecto:" in prompt
    assert "Guion:" in prompt
    assert "Fuente 1 (Guion)" in prompt
    assert "Una casa abandonada" in prompt
    assert "Que ocurre?" in prompt
    assert "Planos de storyboard relacionados:" in prompt


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
async def test_answer_question_prompt_includes_multiple_chunks(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()
    captured: dict[str, str] = {}

    async def fake_embed_query(question: str) -> list[float]:
        return [0.6] * 768

    async def fake_search(**kwargs):
        return [
            {"id": "1", "score": 0.99, "source_type": "storyboard_shot", "source_id": "s1", "source_table": "storyboard_shots", "title": "Plano 1", "text": "Plano general de la casa.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "2", "score": 0.98, "source_type": "script_text", "source_id": "g1", "source_table": "projects", "title": "Guion", "text": "Marta entra en la casa abandonada.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "3", "score": 0.97, "source_type": "production_breakdown", "source_id": "b1", "source_table": "production_breakdowns", "title": "Breakdown", "text": "Interior noche con linterna.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "4", "score": 0.96, "source_type": "storyboard_shot", "source_id": "s2", "source_table": "storyboard_shots", "title": "Plano 2", "text": "Primer plano de la linterna.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "5", "score": 0.95, "source_type": "storyboard_shot", "source_id": "s3", "source_table": "storyboard_shots", "title": "Plano 3", "text": "Pasillo oscuro.", "chunk_index": 0, "chunk_count": 1, "tags": []},
        ]

    async def fake_generate(*, prompt: str, system_prompt: str, model: str | None = None, temperature: float | None = None) -> str:
        captured["prompt"] = prompt
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="¿Qué ocurre en la escena y qué planos la representan?",
        limit=5,
        include_sources=True,
    )
    assert result["answer"] == "Respuesta"
    assert result["usage"]["context_chunks"] >= 3
    assert captured["prompt"].count("Fuente ") >= 3


def test_build_answer_prompt_preserves_type_sections() -> None:
    prompt = build_answer_prompt(
        "Pregunta",
        [
            {"source_type": "script_text", "title": "Guion", "text": "Accion de guion."},
            {"source_type": "storyboard_shot", "title": "Plano", "text": "Plano del pasillo."},
            {"source_type": "production_breakdown", "title": "Breakdown", "text": "Detalle tecnico."},
        ],
        max_chars_per_chunk=120,
    )
    assert "Guion:" in prompt
    assert "Storyboard:" in prompt
    assert "Breakdown:" in prompt


@pytest.mark.asyncio
async def test_answer_question_prioritizes_storyboard_for_planos(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()

    async def fake_embed_query(question: str) -> list[float]:
        return [0.7] * 768

    async def fake_search(**kwargs):
        return [
            {"id": "a", "score": 0.95, "source_type": "script_text", "source_id": "g1", "source_table": "projects", "title": "Guion", "text": "Marta entra.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "b", "score": 0.90, "source_type": "storyboard_shot", "source_id": "s1", "source_table": "storyboard_shots", "title": "Plano", "text": "MS de Marta con linterna.", "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "c", "score": 0.85, "source_type": "production_breakdown", "source_id": "bd1", "source_table": "production_breakdowns", "title": "Breakdown", "text": "Interior noche.", "chunk_index": 0, "chunk_count": 1, "tags": []},
        ]

    async def fake_generate(**kwargs):
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="¿Qué planos representan la escena?",
        limit=3,
    )
    source_types = [source["source_type"] for source in result["sources"]]
    assert "storyboard_shot" in source_types


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


# ── Feedback-aware Answering ─────────────────────────────────────────────────

def test_build_answer_prompt_includes_client_feedback_section() -> None:
    prompt = build_answer_prompt(
        "¿Qué es un dolly?",
        [
            {
                "source_type": "client_feedback",
                "title": "feedback-answer_helpful",
                "source_id": "fb-1",
                "score": 0.95,
                "text": "Pregunta: ¿Qué es un dolly shot?\nRespuesta corregida: Un dolly shot es un plano con travelling sobre ruedas.",
            }
        ],
        max_chars_per_chunk=1200,
    )
    assert "Feedback de clientes:" in prompt
    assert "Respuesta corregida:" in prompt
    assert "feedback de clientes" in prompt.lower()


def test_build_answer_prompt_orders_client_feedback_after_standard_sources() -> None:
    prompt = build_answer_prompt(
        "Pregunta",
        [
            {"source_type": "script_text", "title": "Guion", "text": "Accion."},
            {"source_type": "client_feedback", "title": "feedback", "text": "Feedback."},
        ],
        max_chars_per_chunk=120,
    )
    guion_pos = prompt.find("Guion:")
    feedback_pos = prompt.find("Feedback de clientes:")
    assert guion_pos >= 0
    assert feedback_pos >= 0
    assert guion_pos < feedback_pos


def test_build_answer_prompt_includes_feedback_priority_instruction() -> None:
    prompt = build_answer_prompt(
        "Pregunta",
        [{"source_type": "script_text", "title": "Guion", "text": "Texto."}],
        max_chars_per_chunk=120,
    )
    assert "feedback de clientes" in prompt.lower()
    assert "prioridad" in prompt.lower() or "prioritaria" in prompt.lower()


@pytest.mark.asyncio
async def test_answer_question_includes_feedback_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()
    captured_prompt: dict[str, str] = {}

    async def fake_embed_query(question: str) -> list[float]:
        return [0.5] * 768

    async def fake_search(**kwargs):
        return [
            {"id": "f1", "score": 0.95, "source_type": "client_feedback", "source_id": "fb-1",
             "source_table": "cid_client_feedback", "title": "feedback", "text": "Pregunta: ¿Qué es un dolly?",
             "chunk_index": 0, "chunk_count": 1, "tags": ["client_feedback"]},
            {"id": "s1", "score": 0.85, "source_type": "script_text", "source_id": "g1",
             "source_table": "projects", "title": "Guion", "text": "Texto.", "chunk_index": 0,
             "chunk_count": 1, "tags": []},
        ]

    async def fake_generate(*, prompt: str, system_prompt: str, model: str | None = None,
                            temperature: float | None = None) -> str:
        captured_prompt["prompt"] = prompt
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="¿Qué es un dolly?",
        limit=5,
    )
    source_types = [s["source_type"] for s in result["sources"]]
    assert "client_feedback" in source_types
    assert captured_prompt["prompt"].count("Feedback de clientes:") >= 1


@pytest.mark.asyncio
async def test_answer_question_prioritizes_feedback_when_relevant(monkeypatch: pytest.MonkeyPatch) -> None:
    service = CIDRAGAnswerService()

    async def fake_embed_query(question: str) -> list[float]:
        return [0.5] * 768

    async def fake_search(**kwargs):
        return [
            {"id": "s1", "score": 0.96, "source_type": "script_text", "source_id": "g1",
             "source_table": "projects", "title": "Guion", "text": "Entra en la casa. La puerta cruje.",
             "chunk_index": 0, "chunk_count": 1, "tags": []},
            {"id": "f1", "score": 0.91, "source_type": "client_feedback", "source_id": "fb-1",
             "source_table": "cid_client_feedback", "title": "feedback", "text": "Pregunta: ¿Qué es un travelling?\nRespuesta corregida: Movimiento de cámara sobre rieles.",
             "chunk_index": 0, "chunk_count": 1, "tags": ["client_feedback"]},
        ]

    async def fake_generate(**kwargs):
        return "Respuesta"

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)
    monkeypatch.setattr("services.cid_rag_answer_service.ollama_llm_service.generate", fake_generate)

    result = await service.answer_question(
        organization_id="org-1",
        project_id="proj-1",
        question="¿Qué es un travelling? Explícamelo.",
        limit=3,
    )
    source_types = [s["source_type"] for s in result["sources"]]
    assert "client_feedback" in source_types


@pytest.mark.asyncio
async def test_answer_question_feedback_isolates_by_org(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feedback from org-A must not appear when answering for org-B."""
    service = CIDRAGAnswerService()
    captured_org: list[str] = []

    async def fake_embed_query(question: str) -> list[float]:
        return [0.5] * 768

    async def fake_search(**kwargs):
        captured_org.append(kwargs.get("organization_id", ""))
        return []  # empty for isolation test

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)

    await service.answer_question(
        organization_id="org-client-a",
        project_id="proj-1",
        question="Pregunta",
        limit=3,
    )
    assert "org-client-a" in captured_org


@pytest.mark.asyncio
async def test_answer_question_feedback_isolates_by_project(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feedback from proj-A must not appear when answering for proj-B."""
    service = CIDRAGAnswerService()
    captured_project: list[str] = []

    async def fake_embed_query(question: str) -> list[float]:
        return [0.5] * 768

    async def fake_search(**kwargs):
        captured_project.append(kwargs.get("project_id", ""))
        return []

    monkeypatch.setattr("services.cid_rag_answer_service.rag_embedding_service.embed_query", fake_embed_query)
    monkeypatch.setattr("services.cid_rag_answer_service.qdrant_memory_service.search", fake_search)

    await service.answer_question(
        organization_id="org-1",
        project_id="proj-client-b",
        question="Pregunta",
        limit=3,
    )
    assert "proj-client-b" in captured_project
