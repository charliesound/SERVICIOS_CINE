import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class WebHandler:
    def __init__(self):
        self.api_url = settings.WEB_BASE_URL

    async def forward_lead(self, lead_data: dict) -> Optional[dict]:
        logger.info("Web handler forwarding lead to %s", self.api_url)
        return {"status": "forwarded", "target": "web_ailink_cinema", "url": self.api_url}

    async def forward_script(self, script_data: dict) -> Optional[dict]:
        logger.info("Web handler forwarding script to %s", self.api_url)
        return {"status": "forwarded", "target": "web_ailink_cinema", "url": self.api_url}
