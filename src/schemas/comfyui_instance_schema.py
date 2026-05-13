from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ComfyUIInstance(BaseModel):
    key: str = Field(..., description="Instance key identifier")
    name: str
    base_url: str
    port: int
    enabled: bool
    task_types: list[str]
    health_endpoint: str
    status: str = "unknown"


class InstanceHealth(BaseModel):
    instance_key: str
    instance_name: str
    base_url: str
    status: str
    healthy: bool
    detail: dict[str, Any] = Field(default_factory=dict)


class ResolveResult(BaseModel):
    task_type: str
    instance_key: str
    instance_name: str
    base_url: str
    port: int


class ResolveError(BaseModel):
    task_type: str
    error: str
    detail: str


class InstancesHealthSummary(BaseModel):
    total: int
    online: int
    offline: int
    instances: list[InstanceHealth]
