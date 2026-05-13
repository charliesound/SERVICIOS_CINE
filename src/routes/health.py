from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core.config import get_settings

router = APIRouter(tags=["health"])


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


@router.get("/health/live")
async def health_live(request: Request):
    """Liveness probe: process is alive and responding."""
    return {
        "status": "ok",
        "service": get_settings().app_name,
        "env": get_settings().app_env,
        "request_id": _request_id(request),
    }


@router.get("/health/ready")
async def health_ready(request: Request):
    """Readiness probe: dependencies are reachable."""
    settings = get_settings()
    checks: dict[str, dict] = {}

    # DB check
    if settings.healthcheck_db_enabled:
        try:
            from database import engine
            from sqlalchemy import text

            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = {"status": "ok"}
        except Exception as exc:
            checks["database"] = {"status": "fail", "error": str(exc)}
    else:
        checks["database"] = {"status": "skipped"}

    # Redis check
    if settings.healthcheck_redis_enabled and settings.redis_url:
        try:
            import asyncio

            _, writer = await asyncio.wait_for(
                asyncio.open_connection(settings.redis_url, 6379),
                timeout=3.0,
            )
            writer.close()
            await writer.wait_closed()
            checks["redis"] = {"status": "ok"}
        except Exception as exc:
            checks["redis"] = {"status": "fail", "error": str(exc)}
    else:
        checks["redis"] = {"status": "skipped"}

    any_fail = any(chk.get("status") == "fail" for chk in checks.values())

    if any_fail:
        status = "degraded"
        code = 503
    else:
        status = "ok"
        code = 200

    return JSONResponse(
        status_code=code,
        content={
            "status": status,
            "service": settings.app_name,
            "env": settings.app_env,
            "checks": checks,
            "request_id": _request_id(request),
        },
    )


@router.get("/health/startup")
async def health_startup(request: Request):
    """Startup probe: reports initialisation status."""
    settings = get_settings()
    startup_ok = getattr(request.app.state, "startup_ok", True)
    router_count = len(request.app.routes) if hasattr(request.app, "routes") else 0

    return {
        "status": "ok" if startup_ok else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "env": settings.app_env,
        "startup_ok": startup_ok,
        "registered_routers": router_count,
        "db_check_configured": settings.healthcheck_db_enabled,
        "request_id": _request_id(request),
    }
