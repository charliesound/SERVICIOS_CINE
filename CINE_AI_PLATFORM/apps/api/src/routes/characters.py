from typing import Any, Optional
from fastapi import APIRouter, Body, Depends
from fastapi.responses import JSONResponse
from src.auth.dependencies import require_roles
from src.schemas.character import Character
from src.services.storage_service import StorageService, StorageImportError

def create_characters_router(store_backend: str, storage_service: StorageService) -> APIRouter:
    router = APIRouter(prefix="/characters", tags=["characters"])

    @router.get("", response_model=list[Character])
    def list_characters():
        try:
            result = storage_service.get_active_storage_characters(store_backend)
            return result.get("characters", [])
        except Exception:
            return []

    @router.get("/{character_id}", response_model=Character)
    def get_character(character_id: str):
        try:
            character = storage_service.get_active_storage_character(store_backend, character_id)
            if character is None:
                return JSONResponse(
                    status_code=404,
                    content={"ok": False, "error": {"code": "CHARACTER_NOT_FOUND", "message": f"Character {character_id} not found"}},
                )
            return character
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "CHARACTER_GET_FAILED", "message": "Character retrieval failed"}},
            )

    @router.post("", response_model=Character, dependencies=[Depends(require_roles("admin", "editor"))])
    def create_character(payload: Any = Body(...)):
        try:
            result = storage_service.create_active_storage_character(store_backend, payload)
            return result.get("character")
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "CHARACTER_CREATE_FAILED", "message": "Character create failed"}},
            )

    @router.patch("/{character_id}", response_model=Character, dependencies=[Depends(require_roles("admin", "editor"))])
    def update_character(character_id: str, payload: Any = Body(...)):
        try:
            result = storage_service.update_active_storage_character(store_backend, character_id, payload)
            return result.get("character")
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "CHARACTER_UPDATE_FAILED", "message": "Character update failed"}},
            )

    @router.delete("/{character_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def delete_character(character_id: str):
        try:
            return storage_service.delete_active_storage_character(store_backend, character_id)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "CHARACTER_DELETE_FAILED", "message": "Character delete failed"}},
            )

    return router
