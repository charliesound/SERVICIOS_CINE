import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class CIDHandler:
    def __init__(self):
        self.api_url = settings.CID_BASE_URL
        self.internal_token = settings.CID_INTERNAL_TOKEN

    async def forward_lead(self, lead_data: dict) -> Optional[dict]:
        logger.info("CID handler forwarding lead to %s", self.api_url)
        return {"status": "forwarded", "target": "cid", "url": self.api_url}

    async def forward_script(self, script_data: dict) -> Optional[dict]:
        logger.info("CID handler forwarding script to %s", self.api_url)
        return {"status": "forwarded", "target": "cid", "url": self.api_url}
