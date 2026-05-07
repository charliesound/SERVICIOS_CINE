from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StoryboardShotCreate(BaseModel):
    sequence_id: Optional[str] = None
    sequence_order: Optional[int] = None
    narrative_text: Optional[str] = None
    asset_id: Optional[str] = None
    shot_type: Optional[str] = None
    visual_mode: Optional[str] = None


class StoryboardShotUpdate(BaseModel):
    sequence_id: Optional[str] = None
    sequence_order: Optional[int] = None
    narrative_text: Optional[str] = None
    asset_id: Optional[str] = None
    shot_type: Optional[str] = None
    visual_mode: Optional[str] = None


class StoryboardShotReorderItem(BaseModel):
    shot_id: str
    sequence_order: int
    sequence_id: Optional[str] = None


class StoryboardShotBulkReorderRequest(BaseModel):
    shots: list[StoryboardShotReorderItem] = Field(default_factory=list)


class StoryboardShotResponse(BaseModel):
    id: str
    project_id: str
    organization_id: str
    sequence_id: Optional[str] = None
    sequence_order: int
    scene_number: Optional[int] = None
    scene_heading: Optional[str] = None
    narrative_text: Optional[str] = None
    asset_id: Optional[str] = None
    shot_type: Optional[str] = None
    visual_mode: Optional[str] = None
    generation_mode: Optional[str] = None
    generation_job_id: Optional[str] = None
    version: int = 1
    is_active: bool = True
    asset_file_name: Optional[str] = None
    asset_mime_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class StoryboardShotListResponse(BaseModel):
    shots: list[StoryboardShotResponse] = Field(default_factory=list)
