from fastapi import Depends, FastAPI

from src.auth.dependencies import require_authenticated
from src.routes.projects import router as legacy_projects_router
from src.routes.scenes import router as legacy_scenes_router
from src.routes.shots import router as legacy_shots_router
from src.routes.jobs import router as legacy_jobs_router


LEGACY_ROUTES_TAG = "LEGACY-DEPRECATED"


def include_legacy_routers(app: FastAPI) -> None:
    app.include_router(legacy_projects_router, tags=[LEGACY_ROUTES_TAG], dependencies=[Depends(require_authenticated)])
    app.include_router(legacy_scenes_router, tags=[LEGACY_ROUTES_TAG], dependencies=[Depends(require_authenticated)])
    app.include_router(legacy_shots_router, tags=[LEGACY_ROUTES_TAG], dependencies=[Depends(require_authenticated)])
    app.include_router(legacy_jobs_router, tags=[LEGACY_ROUTES_TAG], dependencies=[Depends(require_authenticated)])


def legacy_route_prefixes() -> list[str]:
    return ["/projects", "/scenes", "/shots", "/jobs"]
