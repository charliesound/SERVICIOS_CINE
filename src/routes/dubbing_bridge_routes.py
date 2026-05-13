"""
CID Dubbing Bridge — Integra AI Dubbing Legal Studio en CID.

Proxy que permite a CID enviar jobs de doblaje y consultar
contratos desde el ecosistema CID, manteniendo la app
standalone con su propia base de datos.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import httpx

DUBBING_API_URL = os.getenv("DUBBING_API_URL", "http://127.0.0.1:8000")

router = APIRouter(prefix="/api/dubbing", tags=["dubbing-bridge"])


class BridgeJobCreate(BaseModel):
    project_id: int
    mode: str = "doblaje_humano_asistido"
    source_language: str = "es"
    target_language: str = "en"
    contract_id: Optional[int] = None
    actor_id: Optional[int] = None


@router.post("/projects/{project_id}/jobs")
async def create_dubbing_job(project_id: int, data: BridgeJobCreate):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DUBBING_API_URL}/api/dubbing-jobs/project/{project_id}",
            json=data.model_dump(),
            timeout=10,
        )
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


@router.get("/projects/{project_id}/jobs")
async def list_dubbing_jobs(project_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{DUBBING_API_URL}/api/dubbing-jobs/project/{project_id}",
            timeout=10,
        )
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


@router.post("/contracts/{contract_id}/validate")
async def validate_contract(contract_id: int, mode: str = "voz_original_ia_autorizada",
                            language: str = "es", territory: str = None, usage_type: str = None):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DUBBING_API_URL}/api/contracts/{contract_id}/validate",
            json={"mode": mode, "language": language, "territory": territory, "usage_type": usage_type},
            timeout=10,
        )
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


@router.get("/jobs/{job_id}")
async def get_job(job_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DUBBING_API_URL}/api/dubbing-jobs/{job_id}", timeout=10)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()


@router.get("/audit/job/{job_id}")
async def get_job_audit(job_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DUBBING_API_URL}/api/audit/job/{job_id}", timeout=10)
        if resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json()
