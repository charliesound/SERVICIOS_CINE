from fastapi import APIRouter

from src.settings import settings
from src.services.health_service import HealthService


def create_health_router(store_backend: str, health_service: HealthService) -> APIRouter:
    router = APIRouter(tags=["health"])

    @router.get("/api/health")
    def health():
        return {
            "ok": True,
            "app_name": settings.app_name,
            "store_backend": store_backend,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "integrations": {
                "comfyui": {
                    "optional": True,
                    "configured": bool(settings.comfyui_base_url.strip()),
                }
            },
        }

    @router.get("/api/health/details")
    def health_details():
        return health_service.get_details()

    @router.get("/api/ops/status")
    def ops_status():
        details = health_service.get_details()
        integrations = details.get("health", {}).get("integrations", {})
        comfyui = integrations.get("comfyui", {})

        return {
            "ok": bool(details.get("ok")),
            "mode": settings.app_env,
            "storage_backend": store_backend,
            "legacy_routes_enabled": settings.enable_legacy_routes,
            "comfyui": {
                "optional": True,
                "configured": bool(comfyui.get("configured")),
                "reachable": bool(comfyui.get("reachable")),
                "latency_ms": comfyui.get("latency_ms"),
                "error": comfyui.get("error"),
            },
            "checks": details.get("health", {}).get("checks", {}),
        }

    return router
