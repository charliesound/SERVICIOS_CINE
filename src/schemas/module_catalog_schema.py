from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ModuleInfo(BaseModel):
    key: str
    name: str
    short_description: str
    category: str
    status: str
    commercial_status: str
    requires_gpu: bool
    requires_local_gpu_node: bool
    default_enabled: bool
    visible_in_catalog: bool
    dependencies: list[str]
    recommended_pack: Optional[str] = None
    route_prefixes: list[str]
    feature_flag_key: Optional[str] = None


class ModuleCatalogResponse(BaseModel):
    modules: list[ModuleInfo]
    total: int


class ModuleAccessInfo(ModuleInfo):
    enabled: bool
    locked_reason: Optional[str] = None


class UserModulesResponse(BaseModel):
    plan: str
    organization_id: Optional[str] = None
    available_modules: list[ModuleAccessInfo]
    locked_modules: list[ModuleAccessInfo]
    total_available: int
    total_locked: int
