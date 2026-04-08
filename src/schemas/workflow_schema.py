from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class WorkflowPlanRequest(BaseModel):
    intent: str
    context: Dict[str, Any]


class WorkflowBuildRequest(BaseModel):
    workflow_key: str
    inputs: Dict[str, Any]
    overrides: Optional[Dict[str, Any]] = None


class WorkflowValidateRequest(BaseModel):
    workflow: Dict[str, Any]
    strict: bool = True


class WorkflowCatalogItem(BaseModel):
    key: str
    name: str
    category: str
    backend: str
    description: str
    required_inputs: List[str]
    optional_inputs: List[str]
    tags: List[str]


class PresetCreate(BaseModel):
    name: str
    workflow_key: str
    inputs: Dict[str, Any]
    description: Optional[str] = ""
    tags: Optional[List[str]] = None
    is_public: bool = False


class PresetResponse(BaseModel):
    id: str
    name: str
    workflow_key: str
    description: str
    category: str
    backend: str
    tags: List[str]
    is_public: bool
    created_by: str
    created_at: str
