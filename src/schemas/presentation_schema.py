from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PresentationProjectSummary(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    status: str


class PresentationSummary(BaseModel):
    sequences_count: int = 0
    shots_count: int = 0
    orphan_assets_count: int = 0
    comments_count: int = 0
    source_assets_count: int = 0


class PresentationCommentItem(BaseModel):
    id: str
    review_id: str
    author_name: Optional[str] = None
    body: str
    created_at: Optional[datetime] = None


class PresentationShotItem(BaseModel):
    asset_id: str
    job_id: Optional[str] = None
    file_name: str
    asset_type: str
    asset_source: Optional[str] = None
    content_ref: Optional[str] = None
    shot_order: int = 0
    shot_type: Optional[str] = None
    visual_mode: Optional[str] = None
    prompt_summary: Optional[str] = None
    canonical_path_present: bool = False
    thumbnail_url: Optional[str] = None
    created_at: Optional[datetime] = None


class PresentationSequenceItem(BaseModel):
    sequence_id: str
    title: str
    visual_modes: list[str] = Field(default_factory=list)
    shots: list[PresentationShotItem] = Field(default_factory=list)


class PresentationFilmstripResponse(BaseModel):
    project: PresentationProjectSummary
    summary: PresentationSummary
    sequences: list[PresentationSequenceItem] = Field(default_factory=list)
    orphan_assets: list[PresentationShotItem] = Field(default_factory=list)
    review_comments: list[PresentationCommentItem] = Field(default_factory=list)
    generated_at: datetime


class PresentationPdfExportResponse(BaseModel):
    status: str
    detail: str
