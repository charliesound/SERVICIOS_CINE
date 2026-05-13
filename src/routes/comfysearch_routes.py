from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from services.comfy_search_service import scan_workflows, index_all, get_embedder, get_store

router = APIRouter(prefix="/api/comfysearch", tags=["comfysearch"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 8


class ReindexResponse(BaseModel):
    status: str
    indexed: int


@router.post("/search")
async def search_workflows(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="query vacía")
    embedder = get_embedder()
    store = get_store()
    results = store.search(req.query, embedder, top_k=req.top_k)
    return {"query": req.query, "results": results, "total": len(results)}


@router.get("/scan")
async def scan():
    items = scan_workflows()
    return {"total": len(items), "workflows": items}


@router.post("/reindex", response_model=ReindexResponse)
async def reindex():
    count = index_all()
    return {"status": "ok", "indexed": count}


@router.get("/workflows/{wf_id}")
async def get_workflow(wf_id: str):
    items = scan_workflows()
    for item in items:
        if item["id"] == wf_id:
            return item
    raise HTTPException(status_code=404, detail="Workflow no encontrado")
