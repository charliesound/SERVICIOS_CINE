from fastapi import HTTPException

from src.models.shots import ShotIn, ShotUpdate
from src.services.shots_service import ShotsService


class ShotsController:
    def __init__(self, service: ShotsService):
        self.service = service

    def list_shots(self):
        return {"ok": True, "shots": self.service.list_shots()}

    def get_shot(self, shot_id: str):
        shot = self.service.get_shot(shot_id)
        if not shot:
            raise HTTPException(status_code=404, detail="Shot no encontrado")
        return {"ok": True, "shot": shot}

    def create_shot(self, payload: ShotIn):
        shot = self.service.create_shot(payload.model_dump())
        return {"ok": True, "shot": shot}

    def replace_shot(self, shot_id: str, payload: ShotIn):
        shot = self.service.replace_shot(shot_id, payload.model_dump())
        if not shot:
            raise HTTPException(status_code=404, detail="Shot no encontrado")
        return {"ok": True, "shot": shot}

    def patch_shot(self, shot_id: str, payload: ShotUpdate):
        shot = self.service.patch_shot(shot_id, payload.model_dump(exclude_unset=True))
        if not shot:
            raise HTTPException(status_code=404, detail="Shot no encontrado")
        return {"ok": True, "shot": shot}

    def delete_shot(self, shot_id: str):
        deleted = self.service.delete_shot(shot_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Shot no encontrado")
        return {"ok": True}