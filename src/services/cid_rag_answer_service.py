from __future__ import annotations

from typing import Any

from core.config import get_settings
from services.logging_service import logger
from services.ollama_llm_service import ollama_llm_service
from services.qdrant_memory_service import qdrant_memory_service
from services.rag_embedding_service import rag_embedding_service


SYSTEM_PROMPT = """Eres CID.
Usa solo el contexto.
No inventes.
Si falta contexto, dilo.
Responde en espanol, claro y breve."""

NO_CONTEXT_ANSWER = (
    "No hay suficiente informacion en la memoria recuperada del proyecto para responder "
    "con seguridad a esta pregunta."
)


def _truncate_text(text: str, max_chars: int) -> str:
    value = text.strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 3].rstrip() + "..."


def _format_source(index: int, source: dict[str, Any], max_chars_per_chunk: int) -> str:
    source_type = str(source.get("source_type", "unknown")).strip() or "unknown"
    text = _truncate_text(_sanitize_context_text(str(source.get("text", ""))), max_chars_per_chunk)
    return f"Fuente {index} {source_type}: {text}"


def _sanitize_context_text(text: str) -> str:
    value = " ".join(text.split())
    for marker in (
        " exact location:",
        " time and atmosphere:",
        " camera:",
        " lighting:",
        " lens/look:",
        " background:",
    ):
        if marker in value:
            value = value.split(marker, 1)[0]
    value = value.replace("cinematic storyboard frame.", "")
    if "model family:" in value:
        prefix, suffix = value.split("model family:", 1)
        if "." in suffix:
            suffix = suffix.split(".", 1)[1]
        value = f"{prefix} {suffix}".strip()
    if "; script-faithful detail:" in value:
        main_text, _detail_text = value.split("; script-faithful detail:", 1)
        value = main_text.strip()
    return " ".join(value.split())


def build_answer_prompt(question: str, sources: list[dict[str, Any]], *, max_chars_per_chunk: int) -> str:
    formatted_sources = [
        _format_source(index, source, max_chars_per_chunk)
        for index, source in enumerate(sources, start=1)
    ]
    context = "\n".join(formatted_sources) if formatted_sources else "Sin contexto recuperado."
    return f"Contexto:\n{context}\n\nPregunta: {question.strip()}\nResponde solo con el contexto y se breve."


class CIDRAGAnswerService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.rag_llm_model
        self.default_temperature = settings.rag_llm_temperature
        self.max_context_chunks = settings.rag_max_context_chunks
        self.max_chars_per_chunk = settings.rag_max_chars_per_chunk
        self.max_prompt_chars = settings.rag_max_prompt_chars

    async def answer_question(
        self,
        *,
        organization_id: str,
        project_id: str,
        question: str,
        limit: int = 5,
        source_types: list[str] | None = None,
        temperature: float | None = None,
        include_sources: bool = True,
    ) -> dict[str, Any]:
        question = question.strip()
        if not question or len(question) > 2000:
            raise ValueError("question must be between 1 and 2000 characters")
        if limit < 1 or limit > 10:
            raise ValueError("limit must be between 1 and 10")

        selected_temperature = self.default_temperature if temperature is None else temperature
        if selected_temperature < 0.0 or selected_temperature > 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

        query_vector = await rag_embedding_service.embed_query(question)
        results = await qdrant_memory_service.search(
            organization_id=organization_id,
            project_id=project_id,
            query_vector=query_vector,
            limit=min(limit, self.max_context_chunks),
            source_types=source_types,
        )

        if not results:
            return self._build_empty_response(
                organization_id=organization_id,
                project_id=project_id,
                include_sources=include_sources,
            )

        limited_results = self._select_context_sources(question=question, results=results)
        prompt = build_answer_prompt(
            question,
            limited_results,
            max_chars_per_chunk=min(self.max_chars_per_chunk, 350),
        )
        if len(prompt) > self.max_prompt_chars:
            prompt = _truncate_text(prompt, self.max_prompt_chars)

        answer = await ollama_llm_service.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            model=self.model,
            temperature=selected_temperature,
        )
        logger.info(
            "RAG answer generated project=%s org=%s sources=%d",
            project_id,
            organization_id,
            len(limited_results),
        )
        return {
            "answer": answer,
            "project_id": project_id,
            "organization_id": organization_id,
            "model": self.model,
            "sources": limited_results if include_sources else [],
            "usage": {
                "context_chunks": len(limited_results),
                "prompt_chars": len(prompt),
            },
        }

    def _select_context_sources(self, *, question: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        prompt_budget = min(self.max_prompt_chars, 1800)
        per_chunk_chars = min(self.max_chars_per_chunk, 220)
        max_selected_sources = min(self.max_context_chunks, 1)

        for source in results[:max_selected_sources]:
            candidate = [*selected, source]
            prompt = build_answer_prompt(question, candidate, max_chars_per_chunk=per_chunk_chars)
            if len(prompt) > prompt_budget and selected:
                break
            if len(prompt) > self.max_prompt_chars:
                break
            selected = candidate

        return selected or results[:1]

    def _build_empty_response(
        self,
        *,
        organization_id: str,
        project_id: str,
        include_sources: bool,
    ) -> dict[str, Any]:
        return {
            "answer": NO_CONTEXT_ANSWER,
            "project_id": project_id,
            "organization_id": organization_id,
            "model": self.model,
            "sources": [] if include_sources else [],
            "usage": {
                "context_chunks": 0,
                "prompt_chars": 0,
            },
        }


cid_rag_answer_service = CIDRAGAnswerService()
