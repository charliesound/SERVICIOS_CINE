import json
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.model = settings.OPENAI_MODEL
        self.dry_run = settings.DRY_RUN

    async def classify_lead(self, directive: str, lead_text: str) -> Optional[dict]:
        if self.dry_run or not self.api_key:
            logger.info("LLM classify skipped (dry_run=%s, has_key=%s)", self.dry_run, bool(self.api_key))
            return None

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url or None)

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": directive},
                    {"role": "user", "content": lead_text},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("LLM classification returned: %s", result)
            return result
        except Exception as e:
            logger.error("LLM classify error: %s", e)
            return None

    async def analyze_script(self, directive: str, script_text: str) -> Optional[dict]:
        if self.dry_run or not self.api_key:
            logger.info("LLM script analysis skipped (dry_run=%s, has_key=%s)", self.dry_run, bool(self.api_key))
            return None

        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url or None)

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": directive},
                    {"role": "user", "content": script_text},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            result = json.loads(response.choices[0].message.content)
            logger.info("LLM script analysis returned: %s", result)
            return result
        except Exception as e:
            logger.error("LLM script analysis error: %s", e)
            return None
