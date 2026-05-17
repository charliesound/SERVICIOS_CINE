"""
Ollama client service for local LLM inference.
Supports Qwen3:30b, Gemma4:26b/31b, and automatic fallback.
"""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx

from config import get_llm_settings

logger = logging.getLogger(__name__)


_TASK_MODEL_SETTINGS_MAP = {
    "script_analysis": (
        "script_analysis_model",
        "analysis_model",
        "ollama_model",
    ),
    "storyboard_prompt": (
        "storyboard_prompt_model",
        "ollama_model",
    ),
    "pipeline_builder": (
        "pipeline_builder_model",
        "ollama_model",
    ),
    "quick": (
        "quick_model",
        "ollama_model",
    ),
    "visual": (
        "visual_model",
        "ollama_model",
    ),
    "fallback": (
        "fallback_model",
        "ollama_model",
    ),
    "smoke": (
        "smoke_model",
        "ollama_model",
    ),
}

_TASK_MODEL_ENV_MAP = {
    "script_analysis_model": "OLLAMA_SCRIPT_ANALYSIS_MODEL",
    "analysis_model": "OLLAMA_ANALYSIS_MODEL",
    "storyboard_prompt_model": "OLLAMA_STORYBOARD_PROMPT_MODEL",
    "pipeline_builder_model": "OLLAMA_PIPELINE_BUILDER_MODEL",
    "quick_model": "OLLAMA_QUICK_MODEL",
    "visual_model": "OLLAMA_VISUAL_MODEL",
    "fallback_model": "OLLAMA_FALLBACK_MODEL",
    "smoke_model": "OLLAMA_SMOKE_MODEL",
    "ollama_model": "OLLAMA_MODEL",
}


class OllamaClientService:
    """Client for Ollama API at OLLAMA_BASE_URL."""

    def __init__(self):
        self._base_url = None
        self._client = None
        self._status_cache: Dict[str, Any] = {}

    def _ensure_client(self):
        if self._client is None:
            settings = get_llm_settings()
            self._base_url = settings.get("ollama_base_url", "http://127.0.0.1:11434")
            self._client = httpx.AsyncClient(base_url=self._base_url, timeout=300.0)

    @staticmethod
    def get_model_for_task(task: str, settings: dict | None = None) -> str:
        """
        Resolve the best Ollama model for a CID task.

        Resolution order:
        1. Task-specific setting/env.
        2. Compatible alias setting/env.
        3. OLLAMA_MODEL.
        4. Hardcoded safe default: qwen2.5:14b.
        """
        safe_default = "qwen2.5:14b"
        if settings is None:
            settings = get_llm_settings()

        setting_keys = _TASK_MODEL_SETTINGS_MAP.get(task, ("ollama_model",))
        for setting_key in setting_keys:
            setting_value = settings.get(setting_key)
            if isinstance(setting_value, str) and setting_value.strip():
                return setting_value.strip()

            env_var = _TASK_MODEL_ENV_MAP.get(setting_key)
            if env_var:
                env_value = os.getenv(env_var)
                if isinstance(env_value, str) and env_value.strip():
                    return env_value.strip()

        global_model = settings.get("ollama_model")
        if isinstance(global_model, str) and global_model.strip():
            return global_model.strip()

        env_global = os.getenv("OLLAMA_MODEL")
        if isinstance(env_global, str) and env_global.strip():
            return env_global.strip()

        return safe_default

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
        # Normalize: model:tag matches model:latest if exact tag is missing
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
