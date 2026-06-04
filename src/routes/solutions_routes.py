from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.solutions_service import (
    register_solution, get_solution, list_solutions,
    deactivate_solution, record_execution, seed_defaults,
)
from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext

router = APIRouter(prefix="/api/solutions", tags=["solutions"])


class SolutionCreate(BaseModel):
    name: str
    workflow_id: str = ""
    backend: str = "still"
    workflow_path: str = ""
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    n8n_workflow_url: str = ""
    created_by: str = "user"


class SolutionOut(BaseModel):
    id: str
    name: str
    workflow_id: str = ""
    backend: str = "still"
    workflow_path: str = ""
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    n8n_workflow_url: str = ""
    is_active: bool = True
    created_by: str = "system"
    created_at: str
    updated_at: str
    execution_count: int = 0
    last_executed_at: Optional[str] = None


@router.get("", response_model=list[SolutionOut])
async def list_all(
    backend: str = None,
    tag: str = None,
    tenant: TenantContext = Depends(get_tenant_context),
):
    del tenant
    return list_solutions(backend=backend, tag=tag)


@router.post("", response_model=SolutionOut)
async def create(
    data: SolutionCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    del tenant
    del _write
    sol = register_solution(
        name=data.name,
        workflow_id=data.workflow_id,
        backend=data.backend,
        workflow_path=data.workflow_path,
        description=data.description,
        tags=data.tags,
        n8n_workflow_url=data.n8n_workflow_url,
        created_by=data.created_by,
    )
    return sol


@router.get("/{solution_id}", response_model=SolutionOut)
async def get(
    solution_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
):
    del tenant
    sol = get_solution(solution_id)
    if not sol:
        raise HTTPException(status_code=404, detail="Solución no encontrada")
    return sol


@router.delete("/{solution_id}")
async def delete(
    solution_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    del tenant
    del _write
    if not deactivate_solution(solution_id):
        raise HTTPException(status_code=404, detail="Solución no encontrada")
    return {"status": "deactivated"}


@router.post("/{solution_id}/execute")
async def execute(
    solution_id: str,
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    del tenant
    del _write
    sol = get_solution(solution_id)
    if not sol:
        raise HTTPException(status_code=404, detail="Solución no encontrada")
    record_execution(solution_id)
    return {
        "status": "queued",
        "solution_id": solution_id,
        "name": sol["name"],
        "backend": sol["backend"],
        "workflow_id": sol["workflow_id"],
    }


@router.post("/seed")
async def seed(
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
):
    del tenant
    del _write
    seed_defaults()
    return {"status": "ok", "seeded": len(list_solutions())}
