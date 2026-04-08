# apps/api/src/routes/storage_routes.py
from typing import Any, Optional
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from src.auth.dependencies import require_roles
from src.settings import settings
from src.services.storage_service import StorageImportError, StorageService

def create_storage_router(store_backend: str, storage_service: StorageService) -> APIRouter:
    router = APIRouter(tags=["storage"])

    @router.get("/api/storage/info")
    def storage_info():
        json_path = Path(settings.shots_json_file)
        sqlite_path = Path(settings.shots_sqlite_file)
        return {
            "ok": True,
            "storage": {
                "active_backend": store_backend,
                "json": {
                    "path": str(json_path),
                    "exists": json_path.exists(),
                    "is_file": json_path.is_file(),
                },
                "sqlite": {
                    "path": str(sqlite_path),
                    "exists": sqlite_path.exists(),
                    "is_file": sqlite_path.is_file(),
                },
            },
        }

    @router.get("/api/storage/summary")
    def storage_summary():
        try:
            return storage_service.get_active_storage_summary(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SUMMARY_FAILED",
                        "message": "Storage summary failed",
                    },
                },
            )

    @router.get("/api/storage/project")
    def storage_project():
        try:
            return storage_service.get_active_storage_project(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_PROJECT_FAILED",
                        "message": "Storage project retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/project/{project_id}/sequences")
    def storage_project_sequences(project_id: str):
        try:
            project_sequences = storage_service.get_active_storage_project_sequences(store_backend, project_id)
            if project_sequences is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "PROJECT_NOT_FOUND",
                            "message": f"Project not found: {project_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "project_id": project_sequences["project_id"],
                "sequences": project_sequences["sequences"],
                "count": project_sequences["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_PROJECT_SEQUENCES_FAILED",
                        "message": "Storage project sequences retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/project/{project_id}/scenes")
    def storage_project_scenes(project_id: str):
        try:
            project_scenes = storage_service.get_active_storage_project_scenes(store_backend, project_id)
            if project_scenes is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "PROJECT_NOT_FOUND",
                            "message": f"Project not found: {project_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "project_id": project_scenes["project_id"],
                "scenes": project_scenes["scenes"],
                "count": project_scenes["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_PROJECT_SCENES_FAILED",
                        "message": "Storage project scenes retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/project/{project_id}/shots")
    def storage_project_shots(project_id: str):
        try:
            project_shots = storage_service.get_active_storage_project_shots(store_backend, project_id)
            if project_shots is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "PROJECT_NOT_FOUND",
                            "message": f"Project not found: {project_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "project_id": project_shots["project_id"],
                "shots": project_shots["shots"],
                "count": project_shots["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_PROJECT_SHOTS_FAILED",
                        "message": "Storage project shots retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/characters")
    def storage_characters():
        try:
            return storage_service.get_active_storage_characters(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_CHARACTERS_FAILED",
                        "message": "Storage characters retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/character/{character_id}")
    def storage_character(character_id: str):
        try:
            character = storage_service.get_active_storage_character(store_backend, character_id)
            if character is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "CHARACTER_NOT_FOUND",
                            "message": f"Character not found: {character_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "character": character,
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_CHARACTER_FAILED",
                        "message": "Storage character retrieval failed",
                    },
                },
            )

    @router.post("/api/storage/character", dependencies=[Depends(require_roles("admin", "editor"))])
    def create_character(payload: Any = Body(...)):
        try:
            return storage_service.create_active_storage_character(store_backend, payload)
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

    @router.patch("/api/storage/character/{character_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def update_character(character_id: str, payload: Any = Body(...)):
        try:
            return storage_service.update_active_storage_character(store_backend, character_id, payload)
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

    @router.delete("/api/storage/character/{character_id}", dependencies=[Depends(require_roles("admin", "editor"))])
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

    @router.get("/api/storage/sequences")
    def storage_sequences():
        try:
            return storage_service.get_active_storage_sequences(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SEQUENCES_FAILED",
                        "message": "Storage sequences retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/sequence/{sequence_id}")
    def storage_sequence(sequence_id: str):
        try:
            sequence = storage_service.get_active_storage_sequence(store_backend, sequence_id)
            if sequence is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SEQUENCE_NOT_FOUND",
                            "message": f"Sequence not found: {sequence_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "sequence": sequence,
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SEQUENCE_FAILED",
                        "message": "Storage sequence retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/sequence/{sequence_id}/scenes")
    def storage_sequence_scenes(sequence_id: str):
        try:
            sequence_scenes = storage_service.get_active_storage_sequence_scenes(store_backend, sequence_id)
            if sequence_scenes is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SEQUENCE_NOT_FOUND",
                            "message": f"Sequence not found: {sequence_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "sequence_id": sequence_scenes["sequence_id"],
                "scenes": sequence_scenes["scenes"],
                "count": sequence_scenes["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SEQUENCE_SCENES_FAILED",
                        "message": "Storage sequence scenes retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/sequence/{sequence_id}/shots")
    def storage_sequence_shots(sequence_id: str):
        try:
            sequence_shots = storage_service.get_active_storage_sequence_shots(store_backend, sequence_id)
            if sequence_shots is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SEQUENCE_NOT_FOUND",
                            "message": f"Sequence not found: {sequence_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "sequence_id": sequence_shots["sequence_id"],
                "shots": sequence_shots["shots"],
                "count": sequence_shots["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SEQUENCE_SHOTS_FAILED",
                        "message": "Storage sequence shots retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/scenes")
    def storage_scenes():
        try:
            return storage_service.get_active_storage_scenes(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SCENES_FAILED",
                        "message": "Storage scenes retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/scene/{scene_id}")
    def storage_scene(scene_id: str):
        try:
            scene = storage_service.get_active_storage_scene(store_backend, scene_id)
            if scene is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SCENE_NOT_FOUND",
                            "message": f"Scene not found: {scene_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "scene": scene,
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SCENE_FAILED",
                        "message": "Storage scene retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/scene/{scene_id}/shots")
    def storage_scene_shots(scene_id: str):
        try:
            scene_shots = storage_service.get_active_storage_scene_shots(store_backend, scene_id)
            if scene_shots is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SCENE_NOT_FOUND",
                            "message": f"Scene not found: {scene_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "scene_id": scene_shots["scene_id"],
                "shots": scene_shots["shots"],
                "count": scene_shots["count"],
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SCENE_SHOTS_FAILED",
                        "message": "Storage scene shots retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/shots")
    def storage_shots():
        try:
            return storage_service.get_active_storage_shots(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SHOTS_FAILED",
                        "message": "Storage shots retrieval failed",
                    },
                },
            )

    @router.get("/api/storage/shot/{shot_id}")
    def storage_shot(shot_id: str):
        try:
            shot = storage_service.get_active_storage_shot(store_backend, shot_id)
            if shot is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "ok": False,
                        "error": {
                            "code": "SHOT_NOT_FOUND",
                            "message": f"Shot not found: {shot_id.strip()}",
                        },
                    },
                )
            return {
                "ok": True,
                "storage": {
                    "backend": store_backend,
                },
                "shot": shot,
            }
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_SHOT_FAILED",
                        "message": "Storage shot retrieval failed",
                    },
                },
            )

    @router.patch("/api/storage/project", dependencies=[Depends(require_roles("admin", "editor"))])
    def update_project(payload: Any = Body(...)):
        try:
            return storage_service.update_active_storage_project(store_backend, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "PROJECT_UPDATE_FAILED", "message": "Project update failed"}},
            )

    @router.post("/api/storage/sequence", dependencies=[Depends(require_roles("admin", "editor"))])
    def create_sequence(payload: Any = Body(...)):
        try:
            return storage_service.create_active_storage_sequence(store_backend, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SEQUENCE_CREATE_FAILED", "message": "Sequence create failed"}},
            )

    @router.patch("/api/storage/sequence/{sequence_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def update_sequence(sequence_id: str, payload: Any = Body(...)):
        try:
            return storage_service.update_active_storage_sequence(store_backend, sequence_id, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SEQUENCE_UPDATE_FAILED", "message": "Sequence update failed"}},
            )

    @router.delete("/api/storage/sequence/{sequence_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def delete_sequence(sequence_id: str):
        try:
            return storage_service.delete_active_storage_sequence(store_backend, sequence_id)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SEQUENCE_DELETE_FAILED", "message": "Sequence delete failed"}},
            )

    @router.post("/api/storage/scene", dependencies=[Depends(require_roles("admin", "editor"))])
    def create_scene(payload: Any = Body(...)):
        try:
            return storage_service.create_active_storage_scene(store_backend, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SCENE_CREATE_FAILED", "message": "Scene create failed"}},
            )

    @router.patch("/api/storage/scene/{scene_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def update_scene(scene_id: str, payload: Any = Body(...)):
        try:
            return storage_service.update_active_storage_scene(store_backend, scene_id, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SCENE_UPDATE_FAILED", "message": "Scene update failed"}},
            )

    @router.delete("/api/storage/scene/{scene_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def delete_scene(scene_id: str):
        try:
            return storage_service.delete_active_storage_scene(store_backend, scene_id)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SCENE_DELETE_FAILED", "message": "Scene delete failed"}},
            )

    @router.post("/api/storage/shot", dependencies=[Depends(require_roles("admin", "editor"))])
    def create_shot(payload: Any = Body(...)):
        try:
            return storage_service.create_active_storage_shot(store_backend, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SHOT_CREATE_FAILED", "message": "Shot create failed"}},
            )

    @router.patch("/api/storage/shot/{shot_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def update_shot(shot_id: str, payload: Any = Body(...)):
        try:
            return storage_service.update_active_storage_shot(store_backend, shot_id, payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SHOT_UPDATE_FAILED", "message": "Shot update failed"}},
            )

    @router.delete("/api/storage/shot/{shot_id}", dependencies=[Depends(require_roles("admin", "editor"))])
    def delete_shot(shot_id: str):
        try:
            return storage_service.delete_active_storage_shot(store_backend, shot_id)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={"ok": False, "error": {"code": error.code, "message": error.message}},
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": {"code": "SHOT_DELETE_FAILED", "message": "Shot delete failed"}},
            )

    @router.post("/api/storage/migrate-json-to-sqlite", dependencies=[Depends(require_roles("admin", "editor"))])
    def migrate_json_to_sqlite():
        return storage_service.migrate_json_to_sqlite()

    @router.post("/api/storage/seed-demo", dependencies=[Depends(require_roles("admin", "editor"))])
    def seed_demo(replace: bool = Query(False)):
        return storage_service.seed_demo(store_backend, replace=replace)

    @router.post("/api/storage/reset", dependencies=[Depends(require_roles("admin", "editor"))])
    def reset_storage():
        return storage_service.reset_backend(store_backend)

    @router.get("/api/storage/export-json")
    def export_json():
        try:
            return storage_service.export_active_backend_to_json(store_backend)
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_EXPORT_FAILED",
                        "message": "Storage export failed",
                    },
                },
            )

    @router.post("/api/storage/import-json", dependencies=[Depends(require_roles("admin", "editor"))])
    def import_json(payload: Any = Body(default=None), mode: Optional[str] = Query(default=None)):
        try:
            merged_payload = payload
            if isinstance(payload, dict) and mode is not None:
                merged_payload = {**payload, "mode": mode}
            return storage_service.import_json_into_active_backend(store_backend, merged_payload)
        except StorageImportError as error:
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "ok": False,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                    },
                },
            )
        except Exception:
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "code": "STORAGE_IMPORT_FAILED",
                        "message": "Storage import failed",
                    },
                },
            )

    return router
