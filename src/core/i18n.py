"""Minimal i18n helpers for CID backend.

Supported languages:
- es: Spanish / castellano
- en: English

Spanish is the safe fallback.
"""

from __future__ import annotations

from typing import Optional


SUPPORTED_LANGUAGES = {"es", "en"}

_LANGUAGE_ALIASES = {
    "es": "es",
    "es-es": "es",
    "es_es": "es",
    "spanish": "es",
    "español": "es",
    "espanol": "es",
    "castellano": "es",
    "spa": "es",
    "en": "en",
    "en-us": "en",
    "en_us": "en",
    "en-gb": "en",
    "en_gb": "en",
    "english": "en",
    "eng": "en",
}


def normalize_language(language: Optional[str]) -> str:
    """Normalize a user/request language value to a supported CID language.

    Spanish is the safe fallback.
    """
    if not language:
        return "es"

    value = str(language).strip().lower()
    if not value:
        return "es"

    value = value.replace("_", "-")
    return _LANGUAGE_ALIASES.get(value, "es")


def get_system_prompt(language: Optional[str] = "es") -> str:
    """Return the language instruction for RAG answer generation."""
    lang = normalize_language(language)

    if lang == "en":
        return (
            "Respond in professional English. "
            "Use a clear, practical and production-oriented tone for film, "
            "screenwriting, audiovisual production and cinematic AI workflows."
        )

    return (
        "Responde en español/castellano profesional. "
        "Usa un tono claro, práctico y orientado a producción cinematográfica, "
        "guion, audiovisual e inteligencia artificial aplicada al cine."
    )


def get_no_context_answer(language: Optional[str] = "es") -> str:
    """Return a localized fallback answer when no RAG context is available."""
    lang = normalize_language(language)

    if lang == "en":
        return (
            "I do not have enough project context to answer reliably. "
            "Add or index more project material, such as script text, storyboard, "
            "production breakdown, or approved client feedback."
        )

    return (
        "No tengo suficiente contexto del proyecto para responder con fiabilidad. "
        "Añade o indexa más material del proyecto, como guion, storyboard, "
        "desglose de producción o feedback aprobado del cliente."
    )
