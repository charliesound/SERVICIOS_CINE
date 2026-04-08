from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ShotIn(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    raw_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    camera_preset: Optional[str] = None
    nominal_ratio: Optional[str] = None
    scene_id: Optional[str] = None
    sequence_id: Optional[str] = None
    status: Optional[str] = None
    tags: List[Any] = Field(default_factory=list)
    references: List[Any] = Field(default_factory=list)
    layers: List[Any] = Field(default_factory=list)
    render_inputs: Dict[str, Any] = Field(default_factory=dict)
    structured_prompt: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ShotUpdate(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    raw_prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    camera_preset: Optional[str] = None
    nominal_ratio: Optional[str] = None
    scene_id: Optional[str] = None
    sequence_id: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[Any]] = None
    references: Optional[List[Any]] = None
    layers: Optional[List[Any]] = None
    render_inputs: Optional[Dict[str, Any]] = None
    structured_prompt: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None