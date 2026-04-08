from fastapi import APIRouter

from src.settings import settings
from src.routes.legacy_routes import legacy_route_prefixes


def create_config_router(store_backend: str) -> APIRouter:
    router = APIRouter(tags=["config"])

    @router.get("/api/config")
    def config():
        return {
            "ok": True,
            "config": {
                "app_name": settings.app_name,
                "app_env": settings.app_env,
                "api_host": settings.api_host,
                "api_port": settings.api_port,
                "cors_origins": [origin.strip() for origin in (settings.cors_origins.strip() or settings.frontend_origins).split(",") if origin.strip()],
                "frontend_origins": [origin.strip() for origin in settings.frontend_origins.split(",") if origin.strip()],
                "shots_store_backend": store_backend,
                "shots_json_file": settings.shots_json_file,
                "shots_sqlite_file": settings.shots_sqlite_file,
                "render_jobs_sqlite_file": settings.render_jobs_sqlite_file,
                "comfyui_base_url": settings.comfyui_base_url,
                "comfyui_timeout_seconds": settings.comfyui_timeout_seconds,
                "enable_legacy_routes": settings.enable_legacy_routes,
                "legacy_route_prefixes": legacy_route_prefixes(),
            },
        }

    return router
