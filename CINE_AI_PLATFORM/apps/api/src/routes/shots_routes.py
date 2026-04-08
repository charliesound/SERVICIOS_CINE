from fastapi import APIRouter, Depends

from src.auth.dependencies import require_roles
from src.controllers.shots_controller import ShotsController
from src.models.shots import ShotIn, ShotUpdate


def create_shots_router(controller: ShotsController) -> APIRouter:
    router = APIRouter(prefix="/api/shots", tags=["shots"])

    @router.get("")
    def list_shots():
        return controller.list_shots()

    @router.get("/{shot_id}")
    def get_shot(shot_id: str):
        return controller.get_shot(shot_id)

    @router.post("", status_code=201, dependencies=[Depends(require_roles("admin", "editor"))])
    def create_shot(payload: ShotIn):
        return controller.create_shot(payload)

    @router.put("/{shot_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def replace_shot(shot_id: str, payload: ShotIn):
        return controller.replace_shot(shot_id, payload)

    @router.patch("/{shot_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def patch_shot(shot_id: str, payload: ShotUpdate):
        return controller.patch_shot(shot_id, payload)

    @router.delete("/{shot_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def delete_shot(shot_id: str):
        return controller.delete_shot(shot_id)

    return router
