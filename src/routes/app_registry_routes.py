from fastapi import APIRouter, HTTPException
from src.services.app_registry import (
    get_all_apps, get_app, get_integrated_apps,
    get_standalone_apps, get_apps_by_category, get_app_categories,
    load_all,
)

router = APIRouter(prefix="/api/apps", tags=["app-registry"])


@router.get("")
async def list_apps():
    apps = await get_all_apps()
    return {"apps": apps, "total": len(apps)}


@router.get("/integrated")
async def list_integrated():
    apps = await get_integrated_apps()
    return {"apps": apps, "total": len(apps)}


@router.get("/standalone")
async def list_standalone():
    apps = await get_standalone_apps()
    return {"apps": apps, "total": len(apps)}


@router.get("/categories")
async def list_categories():
    cats = await get_app_categories()
    return {"categories": cats}


@router.get("/category/{category}")
async def by_category(category: str):
    apps = await get_apps_by_category(category)
    return {"category": category, "apps": apps}


@router.post("/refresh")
async def refresh_registry():
    count = await load_all()
    return {"status": "ok", "apps_count": len(count), "apps": list(count.keys())}


@router.get("/{app_id}")
async def app_detail(app_id: str):
    manifest = await get_app(app_id)
    if not manifest:
        raise HTTPException(status_code=404, detail="App no encontrada")
    return manifest
