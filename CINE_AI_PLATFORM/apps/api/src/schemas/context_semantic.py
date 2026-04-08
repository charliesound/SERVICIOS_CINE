from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContextSemanticPayload(BaseModel):
    project_id: str = Field(min_length=1)
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    entity_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    created_at: str = Field(min_length=1)


class ContextSemanticIngestRequest(BaseModel):
    project_id: str = Field(min_length=1)
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    entity_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    tags: List[str] = Field(default_factory=list)
    source: str = Field(min_length=1)
    created_at: Optional[str] = None
    point_id: Optional[str] = None
    text: Optional[str] = None


class ContextSemanticIngestResponse(BaseModel):
    ok: bool = True
    collection: str
    point_id: str
    embedding_model: str
    dimensions: int
    payload: ContextSemanticPayload
    qdrant: Dict[str, Any] = Field(default_factory=dict)


class ContextSemanticSearchRequest(BaseModel):
    text: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    entity_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)


class ContextSemanticSearchResult(BaseModel):
    point_id: Optional[str] = None
    score: Optional[float] = None
    project_id: Optional[str] = None
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    entity_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    created_at: Optional[str] = None


class ContextSemanticSearchQuery(BaseModel):
    text: str
    project_id: str
    sequence_id: Optional[str] = None
    scene_id: Optional[str] = None
    shot_id: Optional[str] = None
    entity_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    limit: int


class ContextSemanticSearchResponse(BaseModel):
    ok: bool = True
    collection: str
    embedding_model: str
    dimensions: int
    query: ContextSemanticSearchQuery
    count: int = 0
    results: List[ContextSemanticSearchResult] = Field(default_factory=list)


class ContextSemanticError(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ContextSemanticErrorResponse(BaseModel):
    ok: bool = False
    error: ContextSemanticError
