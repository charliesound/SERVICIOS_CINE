"""
Ollama client service for local LLM inference.
Supports Qwen3:30b, Gemma4:26b/31b, and automatic fallback.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from config import get_llm_settings

logger = logging.getLogger(__name__)


class OllamaClientService:
    """Client for Ollama API at OLLAMA_BASE_URL."""

    def __init__(self):
        self._base_url = None
        self._client = None
        self._status_cache: Dict[str, Any] = {}

    def _ensure_client(self):
        if self._client is None:
            settings = get_llm_settings()
            self._base_url = settings.get("base_url", "http://127.0.0.1:11434")
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=300.0)

    async def healthcheck(self) -> Dict[str, Any]:
        """Check if Ollama is running."""
        self._ensure_client()
        try:
            resp = await self._client.get("/api/tags", timeout=5.0)
            return {"ollama_available": resp.status_code == 200, "base_url": self._base_url}
        except Exception as exc:
            logger.warning(f"Ollama health check failed: {exc}")
            return {"ollama_available": False, "base_url": self._base_url, "error": str(exc)}

    async def list_models(self) -> List[str]:
        """List available models."""
        self._ensure_client()
        try:
            resp = await self._client.get("/api/tags", timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception as exc:
            logger.error(f"Failed to list models: {exc}")
        return []

    async def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        models = await self.list_models()
        # Normalize: qwen3:30b matches qwen3:latest if qwen3:30b not found
        normalized = [m.split(":")[0] for m in models]
        target = model_name.split(":")[0]
        return model_name in models or target in normalized

    async def generate_json(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.25,
        num_ctx: int = 32768,
        timeout: int = 240,
    ) -> str:
        """Generate JSON response from Ollama."""
        self._ensure_client()
        settings = get_llm_settings()
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
            },
        }
        try:
            resp = await self._client.post(
                "/api/generate",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama returned {resp.status_code}: {resp.text[:200]}")
            
            data = resp.json()
            text = data.get("response", "")
            return self._clean_json_response(text)
            
        except Exception as exc:
            logger.error(f"Ollama generate failed: {exc}")
            raise

    async def generate_text(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.25,
        num_ctx: int = 32768,
        timeout: int = 240,
    ) -> str:
        """Generate text response from Ollama."""
        self._ensure_client()
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
            },
        }
        try:
            resp = await self._client.post(
                "/api/generate",
                json=payload,
                timeout=timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama returned {resp.status_code}: {resp.text[:200]}")
            data = resp.json()
            return data.get("response", "")
        except Exception as exc:
            logger.error(f"Ollama generate_text failed: {exc}")
            raise

    def _clean_json_response(self, text: str) -> str:
        """Clean Ollama response: remove markdown, extract first valid JSON."""
        # Remove ```json ... ``` blocks
        text = re.sub(r'```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```\s*', '', text)
        
        # Find first { ... } block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text.strip()


ollama_client = OllamaClientService()
