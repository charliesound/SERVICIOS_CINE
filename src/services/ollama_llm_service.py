from __future__ import annotations

from typing import Any

import httpx

from core.config import get_settings
from services.logging_service import logger


class OllamaLLMError(RuntimeError):
    pass


class OllamaLLMConnectionError(OllamaLLMError):
    pass


class OllamaLLMTimeoutError(OllamaLLMError):
    pass


class OllamaLLMEmptyResponseError(OllamaLLMError):
    pass


class OllamaLLMService:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.ollama_url.rstrip("/")
        self.model = settings.rag_llm_model
        self.temperature = settings.rag_llm_temperature
        self.num_predict = settings.rag_llm_num_predict
        # qwen2.5:14B can exceed 60s on the current runtime for full answers.
        self.timeout_seconds = max(float(settings.rag_llm_timeout_seconds), 240.0)

    async def generate(
        self,
        *,
        prompt: str,
        system_prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model or self.model,
            "system": system_prompt,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature if temperature is None else temperature,
                "num_predict": self.num_predict,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.error("Ollama generation timeout model=%s: %s", payload["model"], exc)
            raise OllamaLLMTimeoutError("Ollama generation timed out") from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama generation failed model=%s: %s", payload["model"], exc)
            raise OllamaLLMConnectionError("Ollama is unavailable") from exc

        body = response.json()
        text = str(body.get("response", "")).strip()
        if not text:
            logger.error("Ollama returned empty response model=%s", payload["model"])
            raise OllamaLLMEmptyResponseError("Ollama returned an empty response")
        return text


ollama_llm_service = OllamaLLMService()
