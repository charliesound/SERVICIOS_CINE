import logging
from pathlib import Path
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class DirectiveLoader:
    def load(self, name: str) -> Optional[str]:
        settings = get_settings()
        filepath = settings.DIRECTIVAS_DIR / f"{name}.md"

        if not filepath.exists():
            logger.warning("Directive not found: %s", filepath)
            return None

        try:
            content = filepath.read_text(encoding="utf-8")
            logger.info("Loaded directive: %s", name)
            return content
        except Exception as e:
            logger.error("Error reading directive %s: %s", name, e)
            return None

    def load_all(self) -> dict[str, Optional[str]]:
        settings = get_settings()
        directives = {}
        if settings.DIRECTIVAS_DIR.exists():
            for md_file in settings.DIRECTIVAS_DIR.glob("*.md"):
                directives[md_file.stem] = self.load(md_file.stem)
        return directives
