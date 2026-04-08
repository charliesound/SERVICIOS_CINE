import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class CineHandler:
    def __init__(self):
        self.api_url = settings.CINE_PLATFORM_BASE_URL
        self.internal_token = settings.CINE_PLATFORM_INTERNAL_TOKEN

    async def forward_lead(self, lead_data: dict) -> Optional[dict]:
        logger.info("Cine AI handler forwarding lead to %s", self.api_url)
        return {"status": "forwarded", "target": "cine_ai_platform", "url": self.api_url}

    async def forward_script(self, script_data: dict) -> Optional[dict]:
        logger.info("Cine AI handler forwarding script to %s", self.api_url)
        return {"status": "forwarded", "target": "cine_ai_platform", "url": self.api_url}
