from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.experimental_assembler import assembler

router = APIRouter(prefix="/api/workflows/experimental", tags=["experimental"])


class AssembleRequest(BaseModel):
    base_workflow: str
    modules: List[str]
    options: Optional[Dict[str, Any]] = None


class ModuleInfo(BaseModel):
    module_id: str
    name: str
    category: str
    dependencies: List[str]


@router.get("/modules")
async def list_modules():
    """List available experimental modules."""
    return {
        "modules": assembler.get_available_modules(),
        "warning": "EXPERIMENTAL - Alpha testing only"
    }


@router.get("/modules/{module_id}")
async def get_module_info(module_id: str):
    """Get info about a specific module."""
    info = assembler.get_module_info(module_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
    return {
        **info,
        "warning": "EXPERIMENTAL - Alpha testing only"
    }


@router.post("/assemble")
async def assemble_workflow(
    request: AssembleRequest,
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    x_experimental_enabled: Optional[str] = Header(None, alias="X-Experimental-Enabled")
):
    """
    Assemble a workflow with optional modules.
    
    ALPHA - Requires admin key or experimental flag.
    """
    ADMIN_KEY = "admin-secret-key-change-me"
    
    if x_admin_key != ADMIN_KEY and x_experimental_enabled != "true":
        raise HTTPException(
            status_code=403,
            detail="Experimental feature requires X-Admin-Key header or X-Experimental-Enabled: true"
        )
    
    result = assembler.assemble(
        base_workflow_key=request.base_workflow,
        modules=request.modules,
        options=request.options
    )
    
    return {
        "success": result.success,
        "workflow": result.workflow,
        "warnings": result.warnings,
        "errors": result.errors,
        "stats": {
            "node_count": result.node_count,
            "total_inputs": result.total_inputs
        }
    }


@router.get("/status")
async def get_experimental_status():
    """Get status of experimental features."""
    return {
        "enabled": True,
        "alpha": True,
        "production_ready": False,
        "available_modules": len(assembler.get_available_modules()),
        "max_modules": 5,
        "max_nodes": 50,
        "warning": "This is experimental software. Use at your own risk."
    }
