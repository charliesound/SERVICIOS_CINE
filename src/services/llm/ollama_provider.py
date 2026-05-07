from __future__ import annotations

from typing import Any

import httpx

from config import get_llm_settings
from services.llm.base import BaseLLMProvider, LLMRequest, LLMResponse, LLMStatus


class OllamaProvider(BaseLLMProvider):
    provider_name = "ollama"

    def __init__(self) -> None:
        settings = get_llm_settings()
        self.base_url = str(settings["ollama_base_url"]).rstrip("/")
        self.model = str(settings["ollama_model"])
        self.default_timeout = int(settings["timeout_seconds"])
        self.default_temperature = float(settings["temperature"])

    async def chat(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "options": {
                "temperature": request.temperature,
            },
        }
        if request.json_mode:
            payload["format"] = "json"

        timeout = httpx.Timeout(request.timeout_seconds or self.default_timeout)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise RuntimeError("Ollama request timed out") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected Ollama failure: {exc}") from exc

        content = ((data.get("message") or {}).get("content") or "").strip()
        if not content:
            raise RuntimeError("Ollama returned an empty response")

        return LLMResponse(
            provider=self.provider_name,
            model=self.model,
            content=content,
            raw=data,
            json_mode=request.json_mode,
        )

    async def get_status(self) -> LLMStatus:
        timeout = httpx.Timeout(min(self.default_timeout, 10))
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
            return LLMStatus(
                provider=self.provider_name,
                model=self.model,
                base_url=self.base_url,
                available=True,
            )
        except Exception as exc:
            return LLMStatus(
                provider=self.provider_name,
                model=self.model,
                base_url=self.base_url,
                available=False,
                error_message=str(exc),
            )
