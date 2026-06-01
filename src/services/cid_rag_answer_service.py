from __future__ import annotations

import re
from typing import Any

from core.config import get_settings
from core.i18n import get_no_context_answer, get_system_prompt, normalize_language
from services.logging_service import logger
from services.ollama_llm_service import ollama_llm_service
from services.qdrant_memory_service import qdrant_memory_service
from services.rag_embedding_service import rag_embedding_service


SYSTEM_PROMPT = """Eres CID.
Usa solo el contexto.
No inventes.
Si falta contexto, dilo.
Si hay varias fuentes, integralas.
Si detectas contradicciones o rarezas, indicalas sin bloquear la respuesta.
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
    title = str(source.get("title", "")).strip()
    text = _truncate_text(_sanitize_context_text(str(source.get("text", ""))), max_chars_per_chunk)
    prefix = f"Fuente {index}" if not title else f"Fuente {index} ({title})"
    return f"- {prefix}: {text}"


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


def _normalize_question(text: str) -> str:
    value = text.lower()
    value = value.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return value


def _section_title(source_type: str) -> str:
    mapping = {
        "script_text": "Guion",
        "storyboard_shot": "Storyboard",
        "production_breakdown": "Breakdown",
        "client_feedback": "Feedback de clientes",
    }
    return mapping.get(source_type, source_type)


def build_answer_prompt(question: str, sources: list[dict[str, Any]], *, max_chars_per_chunk: int) -> str:
    grouped: dict[str, list[str]] = {}
    for index, source in enumerate(sources, start=1):
        source_type = str(source.get("source_type", "unknown")).strip() or "unknown"
        grouped.setdefault(source_type, []).append(_format_source(index, source, max_chars_per_chunk))

    sections: list[str] = []
    for source_type in ("script_text", "storyboard_shot", "production_breakdown", "client_feedback"):
        items = grouped.get(source_type)
        if items:
            sections.append(f"{_section_title(source_type)}:\n" + "\n".join(items))

    for source_type, items in grouped.items():
        if source_type not in {"script_text", "storyboard_shot", "production_breakdown", "client_feedback"}:
            sections.append(f"{_section_title(source_type)}:\n" + "\n".join(items))

    context = "\n\n".join(sections) if sections else "Sin contexto recuperado."
    return (
        f"Contexto recuperado del proyecto:\n{context}\n\n"
        f"Pregunta: {question.strip()}\n\n"
        "Instrucciones:\n"
        "- Usa varias fuentes si estan disponibles.\n"
        "- Si la pregunta pide que ocurre, integra Guion o Breakdown si aparecen.\n"
        "- Si la pregunta pide planos, prioriza Storyboard.\n"
        "- No inventes.\n"
        "- Si ves rarezas o contradicciones, indicalas.\n"
        "- Si hay feedback de clientes, la respuesta corregida tiene prioridad sobre fuentes originales.\n\n"
        "Responde con este formato:\n"
        "Resumen de la escena:\n"
        "Planos de storyboard relacionados:\n"
        "Observaciones de continuidad/raccord:\n"
        "Fuentes usadas:\n"
    )


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
        language: str | None = None,
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
        requested_limit = min(limit, self.max_context_chunks)
        candidate_limit = min(max(requested_limit * 3, self.max_context_chunks), 15)
        results = await qdrant_memory_service.search(
            organization_id=organization_id,
            project_id=project_id,
            query_vector=query_vector,
            limit=candidate_limit,
            source_types=source_types,
        )

        if not results:
            return self._build_empty_response(
                organization_id=organization_id,
                project_id=project_id,
                include_sources=include_sources,
            )

        limited_results = self._select_context_sources(
            question=question,
            results=results,
            requested_limit=requested_limit,
        )
        prompt = build_answer_prompt(
            question,
            limited_results,
            max_chars_per_chunk=min(self.max_chars_per_chunk, 180),
        )
        if len(prompt) > self.max_prompt_chars:
            prompt = _truncate_text(prompt, self.max_prompt_chars)

        answer = await ollama_llm_service.generate(
            prompt=prompt,
            system_prompt=get_system_prompt(language),
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

    def _select_context_sources(
        self,
        *,
        question: str,
        results: list[dict[str, Any]],
        requested_limit: int,
    ) -> list[dict[str, Any]]:
        prompt_budget = min(self.max_prompt_chars, 3200)
        per_chunk_chars = min(self.max_chars_per_chunk, 180)
        normalized_question = _normalize_question(question)

        prioritized_types: list[str] = []
        if re.search(r"\b(plano|planos|storyboard)\b", normalized_question):
            prioritized_types.append("storyboard_shot")
        if re.search(r"\b(que ocurre|que pasa|escena|ocurre|pasa)\b", normalized_question):
            prioritized_types.extend(["script_text", "production_breakdown"])
        if re.search(r"\b(que es|que significa|explica|diferencia|como se llama|definicion)\b", normalized_question):
            prioritized_types.append("client_feedback")

        prioritized_types = list(dict.fromkeys(prioritized_types))
        selected_ids: set[str] = set()
        selected: list[dict[str, Any]] = []

        for source_type in prioritized_types:
            match = next((item for item in results if item.get("source_type") == source_type), None)
            if match and match.get("id") not in selected_ids:
                selected.append(match)
                selected_ids.add(str(match.get("id", "")))
            if len(selected) >= requested_limit:
                break

        for source in results:
            source_id = str(source.get("id", ""))
            if source_id in selected_ids:
                continue
            selected.append(source)
            selected_ids.add(source_id)
            if len(selected) >= requested_limit:
                break

        selected.sort(key=lambda item: float(item.get("score", 0.0)), reverse=True)

        fitted: list[dict[str, Any]] = []
        for source in selected:
            candidate = [*fitted, source]
            prompt = build_answer_prompt(question, candidate, max_chars_per_chunk=per_chunk_chars)
            if len(prompt) > prompt_budget and fitted:
                break
            if len(prompt) > self.max_prompt_chars:
                break
            fitted = candidate

        return fitted or selected[:1] or results[:1]

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
