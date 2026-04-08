from typing import Optional

from pydantic import BaseModel, field_validator


class RenderContextFlags(BaseModel):
    character_id: Optional[str] = None
    scene_id: Optional[str] = None
    use_ipadapter: Optional[bool] = None

    @field_validator("character_id", "scene_id", mode="before")
    @classmethod
    def _normalize_optional_text(cls, value: object) -> Optional[str]:
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return None
