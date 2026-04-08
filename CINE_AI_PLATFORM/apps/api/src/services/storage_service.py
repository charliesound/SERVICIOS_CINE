# apps/api/src/services/storage_service.py
from pathlib import Path
from typing import Any, Dict, List, Optional
from copy import deepcopy
import json
from uuid import uuid4
from datetime import datetime, timezone
import sqlite3
from src.storage.json_shots_store import JsonShotsStore
from src.storage.sqlite_shots_store import SQLiteShotsStore

class StorageImportError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

class StorageService:
    def __init__(self, json_file: Path, sqlite_file: Path):
        self.json_file = json_file
        self.sqlite_file = sqlite_file

    def migrate_json_to_sqlite(self) -> Dict[str, Any]:
        if not self.json_file.exists():
            return {
                "ok": False,
                "migration": {
                    "source_json_exists": False,
                    "migrated": 0,
                    "skipped": 0,
                    "error": "No existe shots.json",
                },
            }
        raw = self.json_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            return {
                "ok": False,
                "migration": {
                    "source_json_exists": True,
                    "migrated": 0,
                    "skipped": 0,
                    "error": "shots.json debe contener un array",
                },
            }
        sqlite_store = SQLiteShotsStore(self.sqlite_file)
        existing_ids = {shot["id"] for shot in sqlite_store.list_shots() if shot.get("id")}
        migrated = 0
        skipped = 0
        for shot in data:
            shot_id = shot.get("id")
            if not shot_id or shot_id in existing_ids:
                skipped += 1
                continue
            sqlite_store.create_shot(shot)
            migrated += 1
            existing_ids.add(shot_id)
        return {
            "ok": True,
            "migration": {
                "source_json_exists": True,
                "target_sqlite_exists": self.sqlite_file.exists(),
                "migrated": migrated,
                "skipped": skipped,
                "total_json_items": len(data),
                "sqlite_path": str(self.sqlite_file),
            },
        }

    def seed_demo(self, backend: str, replace: bool = False) -> Dict[str, Any]:
        backend = backend.strip().lower()
        store = self._get_store(backend)
        existing = store.list_shots()

        if existing and not replace:
            return {
                "ok": True,
                "seed": {
                    "backend": backend,
                    "inserted": 0,
                    "skipped": len(existing),
                    "replaced": False,
                    "message": "Ya existen shots; usa replace=true para sobrescribir",
                },
            }

        if replace:
            self._reset_backend_data(backend)
            store = self._get_store(backend)

        demo_project = {
            "id": "project_001",
            "name": "Proyecto Demo",
        }

        demo_sequences = [
            {
                "id": "seq_001",
                "project_id": "project_001",
                "name": "Secuencia 1",
            }
        ]

        demo_characters = [
            {
                "id": "char_001",
                "project_id": "project_001",
                "name": "Personaje 1",
                "seed_master": 123456,
                "reference_images": [],
            }
        ]

        demo_scenes = [
            {
                "id": "scene_001",
                "sequence_id": "seq_001",
                "name": "Escena 1",
            },
            {
                "id": "scene_002",
                "sequence_id": "seq_001",
                "name": "Escena 2",
            },
        ]

        self._save_storage_metadata(
            {
                "project": demo_project,
                "characters": demo_characters,
                "sequences": demo_sequences,
                "scenes": demo_scenes,
            }
        )

        demo_shots = self._build_demo_shots()
        inserted = 0
        for shot in demo_shots:
            store.create_shot(shot)
            inserted += 1

        return {
            "ok": True,
            "seed": {
                "backend": backend,
                "inserted": inserted,
                "skipped": 0,
                "replaced": replace,
            },
        }

    def reset_backend(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        store = self._get_store(backend)
        before = len(store.list_shots())
        self._reset_backend_data(backend)
        self._save_storage_metadata(
            {
                "project": None,
                "characters": [],
                "sequences": [],
                "scenes": [],
            }
        )
        after = len(self._get_store(backend).list_shots())
        return {
            "ok": True,
            "reset": {
                "backend": backend,
                "deleted": before,
                "remaining": after,
            },
        }

    def export_active_backend_to_json(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        characters_response = self.get_active_storage_characters(backend)
        characters = characters_response.get("characters", []) if isinstance(characters_response, dict) else []
        if not isinstance(characters, list):
            characters = []
        export_data = {
            "project": deepcopy(state.get("project")) if state.get("project") is not None else None,
            "characters": deepcopy(characters),
            "sequences": deepcopy(state.get("sequences", [])),
            "scenes": deepcopy(state.get("scenes", [])),
            "shots": deepcopy(state.get("shots", [])),
        }
        export_path = self.json_file.parent / f"shots_export_{backend}.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(
            json.dumps(export_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "data": export_data,
            "counts": {
                "project": 1 if export_data.get("project") is not None else 0,
                "characters": len(export_data.get("characters", [])),
                "sequences": len(export_data.get("sequences", [])),
                "scenes": len(export_data.get("scenes", [])),
                "shots": len(export_data.get("shots", [])),
            },
        }

    def get_active_storage_summary(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        metadata_file = self._storage_metadata_file()
        if backend == "sqlite":
            shots_store_path = self.sqlite_file
            shots_store_kind = "sqlite"
        else:
            shots_store_path = self.json_file
            shots_store_kind = "json"
        return {
            "ok": True,
            "storage": {
                "backend": backend,
                "metadata_file": {
                    "path": str(metadata_file),
                    "exists": metadata_file.exists(),
                },
                "shots_store": {
                    "path": str(shots_store_path),
                    "exists": shots_store_path.exists(),
                    "kind": shots_store_kind,
                },
            },
            "summary": {
                "project": 1 if state.get("project") is not None else 0,
                "sequences": len(state.get("sequences", [])),
                "scenes": len(state.get("scenes", [])),
                "shots": len(state.get("shots", [])),
            },
        }

    def get_active_storage_project(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "project": deepcopy(state.get("project")) if state.get("project") is not None else None,
        }

    def get_active_storage_project_sequences(self, backend: str, project_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_project_id = project_id.strip()
        state = self._load_active_storage_state(backend)

        project = state.get("project")
        if not self._is_object(project):
            return None
        if self._entity_id(project) != normalized_project_id:
            return None

        project_sequences = []
        for sequence in state.get("sequences", []):
            sequence_project_id = sequence.get("project_id")
            if isinstance(sequence_project_id, str):
                sequence_project_id = sequence_project_id.strip()
            else:
                sequence_project_id = None
            if sequence_project_id != normalized_project_id:
                continue
            project_sequences.append(deepcopy(sequence))

        return {
            "project_id": normalized_project_id,
            "sequences": project_sequences,
            "count": len(project_sequences),
        }

    def get_active_storage_project_scenes(self, backend: str, project_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_project_id = project_id.strip()
        state = self._load_active_storage_state(backend)

        project = state.get("project")
        if not self._is_object(project):
            return None
        if self._entity_id(project) != normalized_project_id:
            return None

        project_sequence_ids = set()
        for sequence in state.get("sequences", []):
            sequence_project_id = sequence.get("project_id")
            if isinstance(sequence_project_id, str):
                sequence_project_id = sequence_project_id.strip()
            else:
                sequence_project_id = None

            if sequence_project_id != normalized_project_id:
                continue

            sequence_id = self._entity_id(sequence)
            if sequence_id is not None:
                project_sequence_ids.add(sequence_id)

        project_scenes = []
        for scene in state.get("scenes", []):
            scene_sequence_id = scene.get("sequence_id")
            if isinstance(scene_sequence_id, str):
                scene_sequence_id = scene_sequence_id.strip()
            else:
                scene_sequence_id = None

            if scene_sequence_id not in project_sequence_ids:
                continue

            project_scenes.append(deepcopy(scene))

        return {
            "project_id": normalized_project_id,
            "scenes": project_scenes,
            "count": len(project_scenes),
        }

    def get_active_storage_project_shots(self, backend: str, project_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_project_id = project_id.strip()
        state = self._load_active_storage_state(backend)

        project = state.get("project")
        if not self._is_object(project):
            return None
        if self._entity_id(project) != normalized_project_id:
            return None

        project_sequence_ids = set()
        for sequence in state.get("sequences", []):
            sequence_project_id = sequence.get("project_id")
            if isinstance(sequence_project_id, str):
                sequence_project_id = sequence_project_id.strip()
            else:
                sequence_project_id = None

            if sequence_project_id != normalized_project_id:
                continue

            sequence_id = self._entity_id(sequence)
            if sequence_id is not None:
                project_sequence_ids.add(sequence_id)

        project_shots = []
        for shot in state.get("shots", []):
            if not self._is_active_shot(shot):
                continue

            shot_sequence_id = shot.get("sequence_id")
            if isinstance(shot_sequence_id, str):
                shot_sequence_id = shot_sequence_id.strip()
            else:
                shot_sequence_id = None

            if shot_sequence_id not in project_sequence_ids:
                continue

            project_shots.append(
                {
                    "id": shot.get("id"),
                    "title": shot.get("title"),
                    "scene_id": shot.get("scene_id"),
                    "sequence_id": shot.get("sequence_id"),
                }
            )

        return {
            "project_id": normalized_project_id,
            "shots": project_shots,
            "count": len(project_shots),
        }

    def get_active_storage_characters(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        characters: List[Dict[str, Any]] = []

        for raw_character in state.get("characters", []):
            if not self._is_object(raw_character):
                continue

            normalized_character = deepcopy(raw_character)
            self._normalize_entity_id(normalized_character)

            character_id = self._entity_id(normalized_character)
            if character_id is None:
                continue

            normalized_character["id"] = character_id

            project_id_value = normalized_character.get("project_id")
            if isinstance(project_id_value, str):
                normalized_character["project_id"] = project_id_value.strip()
            else:
                normalized_character["project_id"] = ""

            name_value = normalized_character.get("name")
            if isinstance(name_value, str) and name_value.strip():
                normalized_character["name"] = name_value.strip()
            else:
                normalized_character["name"] = character_id

            seed_value = self._coerce_int(normalized_character.get("seed_master"))
            normalized_character["seed_master"] = seed_value if seed_value is not None else 0

            reference_images = normalized_character.get("reference_images")
            if isinstance(reference_images, list):
                normalized_character["reference_images"] = self._normalize_string_list(reference_images)
            else:
                normalized_character["reference_images"] = []

            characters.append(normalized_character)

        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "characters": characters,
            "count": len(characters),
        }

    def get_active_storage_character(self, backend: str, character_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_character_id = character_id.strip()
        state = self._load_active_storage_state(backend)
        for character in state.get("characters", []):
            if self._entity_id(character) == normalized_character_id:
                return deepcopy(character)
        return None

    def create_active_storage_character(self, backend: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Character payload must be an object", 400)

        project_id = payload.get("project_id")
        if not isinstance(project_id, str) or not project_id.strip():
            raise StorageImportError("INVALID_PAYLOAD", "Character project_id is required", 400)

        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            raise StorageImportError("INVALID_PAYLOAD", "Character name is required", 400)

        state = self._load_active_storage_state(backend)
        character = deepcopy(payload)
        self._normalize_entity_id(character)

        if not character.get("id"):
            character["id"] = f"char_{str(uuid4())[:8]}"

        if any(self._entity_id(c) == character["id"] for c in state["characters"]):
            raise StorageImportError("ID_COLLISION", f"Character with id {character['id']} already exists", 409)

        character["project_id"] = project_id.strip()
        character["name"] = name.strip()

        seed_input = payload.get("seed_master")
        if seed_input is None or (isinstance(seed_input, str) and not seed_input.strip()):
            character["seed_master"] = 0
        else:
            seed_master = self._coerce_int(seed_input)
            if seed_master is None:
                raise StorageImportError("INVALID_PAYLOAD", "Character seed_master must be an integer", 400)
            character["seed_master"] = seed_master

        reference_images = payload.get("reference_images")
        if reference_images is None:
            character["reference_images"] = []
        elif isinstance(reference_images, list):
            character["reference_images"] = self._normalize_string_list(reference_images)
        else:
            raise StorageImportError("INVALID_PAYLOAD", "Character reference_images must be a list", 400)

        state["characters"].append(character)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "character": character}

    def update_active_storage_character(self, backend: str, character_id: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Character payload must be an object", 400)

        state = self._load_active_storage_state(backend)
        normalized_character_id = character_id.strip()

        found_index = None
        for i, character in enumerate(state["characters"]):
            if self._entity_id(character) == normalized_character_id:
                found_index = i
                break

        if found_index is None:
            raise StorageImportError("CHARACTER_NOT_FOUND", f"Character {normalized_character_id} not found", 404)

        current_character = state["characters"][found_index]
        updated_character = deepcopy(current_character)

        if "name" in payload:
            name_value = payload.get("name")
            if not isinstance(name_value, str) or not name_value.strip():
                raise StorageImportError("INVALID_PAYLOAD", "Character name must be a non-empty string", 400)
            updated_character["name"] = name_value.strip()

        if "seed_master" in payload:
            seed_input = payload.get("seed_master")
            if seed_input is None or (isinstance(seed_input, str) and not seed_input.strip()):
                updated_character["seed_master"] = 0
            else:
                seed_master = self._coerce_int(seed_input)
                if seed_master is None:
                    raise StorageImportError("INVALID_PAYLOAD", "Character seed_master must be an integer", 400)
                updated_character["seed_master"] = seed_master

        if "reference_images" in payload:
            reference_images = payload.get("reference_images")
            if reference_images is None:
                updated_character["reference_images"] = []
            elif not isinstance(reference_images, list):
                raise StorageImportError("INVALID_PAYLOAD", "Character reference_images must be a list", 400)
            else:
                updated_character["reference_images"] = self._normalize_string_list(reference_images)

        updated_character["id"] = current_character.get("id")
        updated_character["project_id"] = current_character.get("project_id")

        if not isinstance(updated_character.get("name"), str) or not updated_character.get("name").strip():
            raise StorageImportError("INVALID_PAYLOAD", "Character name must be a non-empty string", 400)

        normalized_existing_seed = self._coerce_int(updated_character.get("seed_master"))
        updated_character["seed_master"] = normalized_existing_seed if normalized_existing_seed is not None else 0

        reference_images = updated_character.get("reference_images")
        if isinstance(reference_images, list):
            updated_character["reference_images"] = self._normalize_string_list(reference_images)
        else:
            updated_character["reference_images"] = []

        state["characters"][found_index] = updated_character
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "character": updated_character}

    def delete_active_storage_character(self, backend: str, character_id: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        character_id = character_id.strip()
        before = len(state["characters"])
        state["characters"] = [c for c in state["characters"] if self._entity_id(c) != character_id]

        if len(state["characters"]) == before:
            raise StorageImportError("CHARACTER_NOT_FOUND", f"Character {character_id} not found", 404)

        self._persist_active_storage_state(backend, state)
        return {"ok": True, "deleted": character_id}

    def get_active_storage_sequences(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        sequences = deepcopy(state.get("sequences", []))
        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "sequences": sequences,
            "count": len(sequences),
        }

    def get_active_storage_sequence(self, backend: str, sequence_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_sequence_id = sequence_id.strip()
        state = self._load_active_storage_state(backend)
        for sequence in state.get("sequences", []):
            if self._entity_id(sequence) == normalized_sequence_id:
                return deepcopy(sequence)
        return None

    def get_active_storage_sequence_scenes(self, backend: str, sequence_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_sequence_id = sequence_id.strip()
        state = self._load_active_storage_state(backend)
        sequence_exists = False
        for sequence in state.get("sequences", []):
            if self._entity_id(sequence) == normalized_sequence_id:
                sequence_exists = True
                break
        if not sequence_exists:
            return None
        scenes = []
        for scene in state.get("scenes", []):
            scene_sequence_id = scene.get("sequence_id")
            if isinstance(scene_sequence_id, str):
                scene_sequence_id = scene_sequence_id.strip()
            else:
                scene_sequence_id = None
            if scene_sequence_id != normalized_sequence_id:
                continue
            scenes.append(deepcopy(scene))
        return {
            "sequence_id": normalized_sequence_id,
            "scenes": scenes,
            "count": len(scenes),
        }

    def get_active_storage_sequence_shots(self, backend: str, sequence_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_sequence_id = sequence_id.strip()
        state = self._load_active_storage_state(backend)
        sequence_exists = False
        for sequence in state.get("sequences", []):
            if self._entity_id(sequence) == normalized_sequence_id:
                sequence_exists = True
                break
        if not sequence_exists:
            return None
        sequence_shots = []
        for shot in state.get("shots", []):
            if not self._is_active_shot(shot):
                continue
            shot_sequence_id = shot.get("sequence_id")
            if isinstance(shot_sequence_id, str):
                shot_sequence_id = shot_sequence_id.strip()
            else:
                shot_sequence_id = None
            if shot_sequence_id != normalized_sequence_id:
                continue
            sequence_shots.append(
                {
                    "id": shot.get("id"),
                    "title": shot.get("title"),
                    "scene_id": shot.get("scene_id"),
                    "sequence_id": shot.get("sequence_id"),
                }
            )
        return {
            "sequence_id": normalized_sequence_id,
            "shots": sequence_shots,
            "count": len(sequence_shots),
        }

    def get_active_storage_scenes(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        scenes = deepcopy(state.get("scenes", []))
        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "scenes": scenes,
            "count": len(scenes),
        }

    def get_active_storage_scene(self, backend: str, scene_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_scene_id = scene_id.strip()
        state = self._load_active_storage_state(backend)
        for scene in state.get("scenes", []):
            if self._entity_id(scene) == normalized_scene_id:
                return deepcopy(scene)
        return None

    def get_active_storage_scene_shots(self, backend: str, scene_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_scene_id = scene_id.strip()
        state = self._load_active_storage_state(backend)
        scene_exists = False
        for scene in state.get("scenes", []):
            if self._entity_id(scene) == normalized_scene_id:
                scene_exists = True
                break
        if not scene_exists:
            return None
        scene_shots = []
        for shot in state.get("shots", []):
            if not self._is_active_shot(shot):
                continue
            shot_scene_id = shot.get("scene_id")
            if isinstance(shot_scene_id, str):
                shot_scene_id = shot_scene_id.strip()
            else:
                shot_scene_id = None
            if shot_scene_id != normalized_scene_id:
                continue
            scene_shots.append(
                {
                    "id": shot.get("id"),
                    "title": shot.get("title"),
                    "scene_id": shot.get("scene_id"),
                    "sequence_id": shot.get("sequence_id"),
                }
            )
        return {
            "scene_id": normalized_scene_id,
            "shots": scene_shots,
            "count": len(scene_shots),
        }

    def get_active_storage_shots(self, backend: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        active_shots = []
        for shot in state.get("shots", []):
            if not self._is_active_shot(shot):
                continue

            workflow_key = shot.get("workflow_key")
            if isinstance(workflow_key, str):
                workflow_key = workflow_key.strip() or None
            else:
                workflow_key = None

            refs_value = shot.get("refs")
            if not isinstance(refs_value, list):
                refs_value = shot.get("references")

            refs = self._normalize_string_list(refs_value) if isinstance(refs_value, list) else []

            seed_value = self._coerce_int(shot.get("seed"))
            cfg_value = self._coerce_float(shot.get("cfg"))
            steps_value = self._coerce_int(shot.get("steps"))

            active_shots.append(
                {
                    "id": shot.get("id"),
                    "title": shot.get("title"),
                    "prompt": shot.get("prompt"),
                    "negative_prompt": shot.get("negative_prompt"),
                    "status": shot.get("status"),
                    "scene_id": shot.get("scene_id"),
                    "sequence_id": shot.get("sequence_id"),
                    "seed": seed_value,
                    "cfg": cfg_value,
                    "steps": steps_value,
                    "workflow_key": workflow_key,
                    "refs": refs,
                }
            )
        return {
            "ok": True,
            "storage": {
                "backend": backend,
            },
            "shots": active_shots,
            "count": len(active_shots),
        }

    def get_active_storage_shot(self, backend: str, shot_id: str) -> Optional[Dict[str, Any]]:
        backend = backend.strip().lower()
        normalized_shot_id = shot_id.strip()
        state = self._load_active_storage_state(backend)
        for shot in state.get("shots", []):
            if self._entity_id(shot) != normalized_shot_id:
                continue
            if not self._is_active_shot(shot):
                continue

            return deepcopy(shot)

        return None

    def import_json_into_active_backend(self, backend: str, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        backend = backend.strip().lower()
        validated = self.validate_storage_import_payload(payload)
        normalized = self.normalize_import_payload(validated)
        current_state = self._load_active_storage_state(backend)
        if normalized["mode"] == "append":
            next_state = self.apply_append_import(current_state, normalized)
        else:
            next_state = self.apply_replace_import(current_state, normalized)
        self._persist_active_storage_state(backend, next_state)
        return self.build_import_summary(normalized["mode"], next_state, normalized)

    def validate_storage_import_payload(self, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not self._is_object(payload):
            raise StorageImportError("INVALID_IMPORT_PAYLOAD", "Body must be a JSON object", 400)
        mode = payload.get("mode", "replace")
        if not isinstance(mode, str):
            raise StorageImportError("INVALID_IMPORT_PAYLOAD", "mode must be a string", 400)
        mode = mode.strip().lower()
        if mode not in ("replace", "append"):
            raise StorageImportError("UNSUPPORTED_IMPORT_MODE", f'Unsupported import mode "{mode}"', 400)
        project = self._ensure_object_or_none(payload.get("project"), "project")
        characters = self._ensure_array_of_objects(payload.get("characters"), "characters")
        sequences = self._ensure_array_of_objects(payload.get("sequences"), "sequences")
        scenes = self._ensure_array_of_objects(payload.get("scenes"), "scenes")
        shots = self._ensure_array_of_objects(payload.get("shots"), "shots")
        self._assert_no_duplicate_ids(characters, "characters")
        self._assert_no_duplicate_ids(sequences, "sequences")
        self._assert_no_duplicate_ids(scenes, "scenes")
        self._assert_no_duplicate_ids(shots, "shots")
        return {
            "mode": mode,
            "project": project,
            "characters": characters,
            "sequences": sequences,
            "scenes": scenes,
            "shots": shots,
        }

    def normalize_import_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project = payload.get("project")
        characters = payload.get("characters")
        sequences = payload.get("sequences")
        scenes = payload.get("scenes")
        shots = payload.get("shots")
        normalized_project: Optional[Dict[str, Any]] = None
        if self._is_object(project):
            normalized_project = deepcopy(project)
            self._normalize_entity_id(normalized_project)

        normalized_characters: List[Dict[str, Any]] = []
        if isinstance(characters, list):
            for raw_character in characters:
                if not self._is_object(raw_character):
                    continue

                normalized_character = deepcopy(raw_character)
                self._normalize_entity_id(normalized_character)

                character_id = self._entity_id(normalized_character)
                if character_id is not None:
                    normalized_character["id"] = character_id

                name_value = normalized_character.get("name")
                if isinstance(name_value, str) and name_value.strip():
                    normalized_character["name"] = name_value.strip()
                elif character_id is not None:
                    normalized_character["name"] = character_id

                project_id_value = normalized_character.get("project_id")
                if isinstance(project_id_value, str):
                    normalized_character["project_id"] = project_id_value.strip()
                elif "project_id" in normalized_character:
                    normalized_character["project_id"] = ""

                seed_input = normalized_character.get("seed_master")
                if seed_input is None or (isinstance(seed_input, str) and not seed_input.strip()):
                    normalized_character["seed_master"] = 0
                else:
                    normalized_seed = self._coerce_int(seed_input)
                    if normalized_seed is None:
                        raise StorageImportError("INVALID_IMPORT_PAYLOAD", "characters contains invalid seed_master", 400)
                    normalized_character["seed_master"] = normalized_seed

                reference_images = normalized_character.get("reference_images")
                if reference_images is None:
                    normalized_character["reference_images"] = []
                elif isinstance(reference_images, list):
                    normalized_character["reference_images"] = self._normalize_string_list(reference_images)
                else:
                    raise StorageImportError("INVALID_IMPORT_PAYLOAD", "characters contains invalid reference_images", 400)

                normalized_characters.append(normalized_character)

        normalized_sequences = [self._normalize_entity(item) for item in sequences] if isinstance(sequences, list) else []
        normalized_scenes = [self._normalize_entity(item) for item in scenes] if isinstance(scenes, list) else []
        normalized_shots = self._normalize_shot_list(shots if isinstance(shots, list) else [])
        return {
            "mode": payload.get("mode", "replace"),
            "project": normalized_project,
            "characters": normalized_characters,
            "sequences": normalized_sequences,
            "scenes": normalized_scenes,
            "shots": normalized_shots,
        }

    def apply_replace_import(self, current_state: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "project": deepcopy(incoming.get("project")) if incoming.get("project") is not None else None,
            "characters": deepcopy(incoming.get("characters", [])),
            "sequences": deepcopy(incoming.get("sequences", [])),
            "scenes": deepcopy(incoming.get("scenes", [])),
            "shots": deepcopy(incoming.get("shots", [])),
        }

    def apply_append_import(self, current_state: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        self._assert_no_append_collisions(current_state.get("characters", []), incoming.get("characters", []), "characters")
        self._assert_no_append_collisions(current_state.get("sequences", []), incoming.get("sequences", []), "sequences")
        self._assert_no_append_collisions(current_state.get("scenes", []), incoming.get("scenes", []), "scenes")
        self._assert_no_append_collisions(current_state.get("shots", []), incoming.get("shots", []), "shots")
        current_project = current_state.get("project")
        incoming_project = incoming.get("project")
        if self._is_object(current_project) and self._is_object(incoming_project):
            current_project_id = self._entity_id(current_project)
            incoming_project_id = self._entity_id(incoming_project)
            if current_project_id and incoming_project_id and current_project_id == incoming_project_id:
                raise StorageImportError(
                    "ID_COLLISION_WITH_EXISTING_DATA",
                    f'Project id collision: "{incoming_project_id}" already exists',
                    409,
                )
            raise StorageImportError(
                "ID_COLLISION_WITH_EXISTING_DATA",
                "Project already exists in active storage",
                409,
            )
        return {
            "project": deepcopy(current_project) if current_project is not None else deepcopy(incoming_project),
            "characters": deepcopy(current_state.get("characters", [])) + deepcopy(incoming.get("characters", [])),
            "sequences": deepcopy(current_state.get("sequences", [])) + deepcopy(incoming.get("sequences", [])),
            "scenes": deepcopy(current_state.get("scenes", [])) + deepcopy(incoming.get("scenes", [])),
            "shots": deepcopy(current_state.get("shots", [])) + deepcopy(incoming.get("shots", [])),
        }

    def build_import_summary(self, mode: str, imported_state: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "ok": True,
            "mode": mode,
            "imported": {
                "project": 1 if incoming.get("project") is not None else 0,
                "characters": len(incoming.get("characters", [])),
                "sequences": len(incoming.get("sequences", [])),
                "scenes": len(incoming.get("scenes", [])),
                "shots": len(incoming.get("shots", [])),
            },
            "totals": {
                "project": 1 if imported_state.get("project") is not None else 0,
                "characters": len(imported_state.get("characters", [])),
                "sequences": len(imported_state.get("sequences", [])),
                "scenes": len(imported_state.get("scenes", [])),
                "shots": len(imported_state.get("shots", [])),
            },
        }

    def _load_active_storage_state(self, backend: str) -> Dict[str, Any]:
        store = self._get_store(backend)
        metadata = self._load_storage_metadata()
        shots = store.list_shots()
        return {
            "project": metadata.get("project") if self._is_object(metadata.get("project")) else None,
            "characters": self._safe_list_of_objects(metadata.get("characters")),
            "sequences": self._safe_list_of_objects(metadata.get("sequences")),
            "scenes": self._safe_list_of_objects(metadata.get("scenes")),
            "shots": self._normalize_shot_list(shots if isinstance(shots, list) else []),
        }

    def _persist_active_storage_state(self, backend: str, state: Dict[str, Any]) -> None:
        self._reset_backend_data(backend)
        store = self._get_store(backend)
        for shot in state.get("shots", []):
            store.create_shot(shot)
        self._save_storage_metadata(
            {
                "project": deepcopy(state.get("project")) if state.get("project") is not None else None,
                "characters": deepcopy(state.get("characters", [])),
                "sequences": deepcopy(state.get("sequences", [])),
                "scenes": deepcopy(state.get("scenes", [])),
            }
        )

    def _load_storage_metadata(self) -> Dict[str, Any]:
        path = self._storage_metadata_file()
        if not path.exists():
            return {
                "project": None,
                "characters": [],
                "sequences": [],
                "scenes": [],
            }
        try:
            raw = path.read_text(encoding="utf-8")
            parsed = json.loads(raw)
        except (OSError, json.JSONDecodeError):
            return {
                "project": None,
                "characters": [],
                "sequences": [],
                "scenes": [],
            }
        return {
            "project": parsed.get("project") if self._is_object(parsed.get("project")) else None,
            "characters": self._safe_list_of_objects(parsed.get("characters")),
            "sequences": self._safe_list_of_objects(parsed.get("sequences")),
            "scenes": self._safe_list_of_objects(parsed.get("scenes")),
        }

    def _save_storage_metadata(self, metadata: Dict[str, Any]) -> None:
        path = self._storage_metadata_file()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def _storage_metadata_file(self) -> Path:
        return self.json_file.parent / "active-storage.json"

    def _safe_list_of_objects(self, value: Any) -> List[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [deepcopy(item) for item in value if self._is_object(item)]

    def _normalize_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        normalized = deepcopy(entity)
        self._normalize_entity_id(normalized)
        return normalized

    def _normalize_entity_id(self, entity: Dict[str, Any]) -> None:
        entity_id = entity.get("id")
        if isinstance(entity_id, str):
            entity["id"] = entity_id.strip()

    def _normalize_shot_list(self, shots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self._normalize_shot(shot) for shot in shots if self._is_object(shot)]

    def _normalize_shot(self, shot: Dict[str, Any]) -> Dict[str, Any]:
        normalized = deepcopy(shot)
        self._normalize_entity_id(normalized)
        shot_id = normalized.get("id")
        if not isinstance(shot_id, str) or not shot_id.strip():
            normalized["id"] = str(uuid4())

        text_fields = (
            "title",
            "prompt",
            "raw_prompt",
            "negative_prompt",
            "camera_preset",
            "nominal_ratio",
            "scene_id",
            "sequence_id",
            "status",
        )
        for field in text_fields:
            if field not in normalized:
                normalized[field] = None
                continue
            value = normalized.get(field)
            if isinstance(value, str):
                trimmed = value.strip()
                normalized[field] = trimmed if trimmed else None

        workflow_key = normalized.get("workflow_key")
        if isinstance(workflow_key, str):
            trimmed_workflow_key = workflow_key.strip()
            normalized["workflow_key"] = trimmed_workflow_key if trimmed_workflow_key else None

        references_value = normalized.get("references")
        refs_value = normalized.get("refs")
        if isinstance(references_value, list):
            normalized_references = self._normalize_string_list(references_value)
        elif isinstance(refs_value, list):
            normalized_references = self._normalize_string_list(refs_value)
        else:
            normalized_references = []

        normalized["references"] = normalized_references
        normalized["refs"] = deepcopy(normalized_references)

        seed_value = self._coerce_int(normalized.get("seed"))
        cfg_value = self._coerce_float(normalized.get("cfg"))
        steps_value = self._coerce_int(normalized.get("steps"))

        if seed_value is not None:
            normalized["seed"] = seed_value
        if cfg_value is not None:
            normalized["cfg"] = cfg_value
        if steps_value is not None:
            normalized["steps"] = steps_value

        normalized["tags"] = normalized.get("tags") if isinstance(normalized.get("tags"), list) else []
        normalized["layers"] = normalized.get("layers") if isinstance(normalized.get("layers"), list) else []
        normalized["render_inputs"] = normalized.get("render_inputs") if isinstance(normalized.get("render_inputs"), dict) else {}
        normalized["structured_prompt"] = (
            normalized.get("structured_prompt") if isinstance(normalized.get("structured_prompt"), dict) else {}
        )
        normalized["metadata"] = normalized.get("metadata") if isinstance(normalized.get("metadata"), dict) else {}

        metadata = normalized["metadata"]

        if seed_value is None:
            seed_value = self._coerce_int(metadata.get("seed"))
            if seed_value is not None:
                normalized["seed"] = seed_value

        if cfg_value is None:
            cfg_value = self._coerce_float(metadata.get("cfg"))
            if cfg_value is not None:
                normalized["cfg"] = cfg_value

        if steps_value is None:
            steps_value = self._coerce_int(metadata.get("steps"))
            if steps_value is not None:
                normalized["steps"] = steps_value

        workflow_key_value = normalized.get("workflow_key")
        if workflow_key_value is None:
            metadata_workflow_key = metadata.get("workflow_key")
            if isinstance(metadata_workflow_key, str):
                trimmed_metadata_workflow_key = metadata_workflow_key.strip()
                if trimmed_metadata_workflow_key:
                    workflow_key_value = trimmed_metadata_workflow_key
                    normalized["workflow_key"] = trimmed_metadata_workflow_key

        if seed_value is not None:
            metadata["seed"] = seed_value
        if cfg_value is not None:
            metadata["cfg"] = cfg_value
        if steps_value is not None:
            metadata["steps"] = steps_value
        if isinstance(workflow_key_value, str) and workflow_key_value:
            metadata["workflow_key"] = workflow_key_value

        now = self._now_iso()
        updated_at = normalized.get("updated_at")
        created_at = normalized.get("created_at")
        if not isinstance(updated_at, str) or not updated_at.strip():
            updated_at = now
        if not isinstance(created_at, str) or not created_at.strip():
            created_at = updated_at
        normalized["updated_at"] = updated_at
        normalized["created_at"] = created_at
        return normalized

    def _normalize_shot_payload_aliases(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        normalized_payload = deepcopy(payload)

        refs = normalized_payload.get("refs")
        references = normalized_payload.get("references")

        if isinstance(refs, list) and "references" not in normalized_payload:
            normalized_payload["references"] = refs

        if isinstance(references, list) and "refs" not in normalized_payload:
            normalized_payload["refs"] = references

        return normalized_payload

    def _normalize_string_list(self, value: List[Any]) -> List[str]:
        normalized_items: List[str] = []
        for item in value:
            if isinstance(item, str):
                normalized_item = item.strip()
                if normalized_item:
                    normalized_items.append(normalized_item)
        return normalized_items

    def _coerce_int(self, value: Any) -> Optional[int]:
        if isinstance(value, bool):
            return None

        if isinstance(value, int):
            return value

        if isinstance(value, float):
            return int(value)

        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return None

            try:
                return int(float(trimmed))
            except ValueError:
                return None

        return None

    def _coerce_float(self, value: Any) -> Optional[float]:
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            trimmed = value.strip()
            if not trimmed:
                return None

            try:
                return float(trimmed)
            except ValueError:
                return None

        return None

    def _is_active_shot(self, shot: Dict[str, Any]) -> bool:
        status = shot.get("status")
        if isinstance(status, str) and status.strip().lower() in {"deleted", "inactive", "archived"}:
            return False
        active_flag = shot.get("active")
        if active_flag is False:
            return False
        metadata = shot.get("metadata")
        if isinstance(metadata, dict) and metadata.get("active") is False:
            return False
        return True

    def _is_object(self, value: Any) -> bool:
        return isinstance(value, dict)

    def _ensure_object_or_none(self, value: Any, field: str) -> Optional[Dict[str, Any]]:
        if value is None:
            return None
        if not self._is_object(value):
            raise StorageImportError("INVALID_IMPORT_PAYLOAD", f"{field} must be an object or null", 400)
        entity_id = value.get("id")
        if entity_id is not None and (not isinstance(entity_id, str) or not entity_id.strip()):
            raise StorageImportError("INVALID_IMPORT_PAYLOAD", f"{field} has invalid id", 400)
        return value

    def _ensure_array_of_objects(self, value: Any, field: str) -> List[Dict[str, Any]]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise StorageImportError("INVALID_IMPORT_PAYLOAD", f"{field} must be an array of objects", 400)
        for item in value:
            if not self._is_object(item):
                raise StorageImportError("INVALID_IMPORT_PAYLOAD", f"{field} must be an array of objects", 400)
            item_id = item.get("id")
            if item_id is not None and (not isinstance(item_id, str) or not item_id.strip()):
                raise StorageImportError("INVALID_IMPORT_PAYLOAD", f"{field} contains an item with invalid id", 400)
        return value

    def _assert_no_duplicate_ids(self, items: List[Dict[str, Any]], field: str) -> None:
        seen = set()
        for item in items:
            item_id = self._entity_id(item)
            if not item_id:
                continue
            if item_id in seen:
                raise StorageImportError("DUPLICATE_IDS_IN_PAYLOAD", f'Duplicate id "{item_id}" found in {field}', 400)
            seen.add(item_id)

    def _assert_no_append_collisions(
        self,
        existing: List[Dict[str, Any]],
        incoming: List[Dict[str, Any]],
        field: str,
    ) -> None:
        existing_ids = {self._entity_id(item) for item in existing if self._entity_id(item)}
        for item in incoming:
            item_id = self._entity_id(item)
            if not item_id:
                continue
            if item_id in existing_ids:
                raise StorageImportError(
                    "ID_COLLISION_WITH_EXISTING_DATA",
                    f'Id collision in {field}: "{item_id}" already exists',
                    409,
                )

    def _entity_id(self, value: Dict[str, Any]) -> Optional[str]:
        entity_id = value.get("id")
        if not isinstance(entity_id, str):
            return None
        normalized = entity_id.strip()
        return normalized if normalized else None

    def _get_store(self, backend: str):
        if backend == "sqlite":
            return SQLiteShotsStore(self.sqlite_file)
        return JsonShotsStore(self.json_file)

    def _reset_backend_data(self, backend: str) -> None:
        if backend == "sqlite":
            self.sqlite_file.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.sqlite_file) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS shots (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        prompt TEXT,
                        raw_prompt TEXT,
                        negative_prompt TEXT,
                        camera_preset TEXT,
                        nominal_ratio TEXT,
                        scene_id TEXT,
                        sequence_id TEXT,
                        status TEXT,
                        tags TEXT NOT NULL,
                        "references" TEXT NOT NULL,
                        layers TEXT NOT NULL,
                        render_inputs TEXT NOT NULL,
                        structured_prompt TEXT NOT NULL,
                        metadata TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute("DELETE FROM shots")
                conn.commit()
        else:
            self.json_file.parent.mkdir(parents=True, exist_ok=True)
            self.json_file.write_text("[]\n", encoding="utf-8")

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _shot(
        self,
        title: str,
        prompt: str,
        status: str,
        scene_id: str,
        sequence_id: str,
        camera_preset: str,
        nominal_ratio: str,
        tags: List[str],
    ) -> Dict[str, Any]:
        now = self._now_iso()
        return {
            "id": str(uuid4()),
            "title": title,
            "prompt": prompt,
            "raw_prompt": None,
            "negative_prompt": None,
            "camera_preset": camera_preset,
            "nominal_ratio": nominal_ratio,
            "scene_id": scene_id,
            "sequence_id": sequence_id,
            "status": status,
            "tags": tags,
            "references": [],
            "layers": [],
            "render_inputs": {},
            "structured_prompt": {},
            "metadata": {
                "seeded": True,
            },
            "updated_at": now,
            "created_at": now,
        }

    def _build_demo_shots(self) -> List[Dict[str, Any]]:
        return [
            self._shot(
                title="Plano 1 - Apertura",
                prompt="Exterior amanecer, carretera vacía, niebla suave, tono cinematográfico realista",
                status="draft",
                scene_id="scene_001",
                sequence_id="seq_001",
                camera_preset="wide_establishing",
                nominal_ratio="2.39:1",
                tags=["demo", "apertura", "exterior"],
            ),
            self._shot(
                title="Plano 2 - Interior cocina",
                prompt="Interior cocina, luz cálida lateral, personaje junto a la ventana, detalle atmosférico",
                status="draft",
                scene_id="scene_002",
                sequence_id="seq_001",
                camera_preset="medium",
                nominal_ratio="1.85:1",
                tags=["demo", "interior", "drama"],
            ),
            self._shot(
                title="Plano 3 - Contraplano",
                prompt="Contraplano interior, personaje escucha en silencio, luz de tarde, profundidad de campo suave",
                status="ready",
                scene_id="scene_002",
                sequence_id="seq_001",
                camera_preset="close_up",
                nominal_ratio="1.85:1",
                tags=["demo", "contraplano", "dialogo"],
            ),
        ]

    def update_active_storage_project(self, backend: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Project payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        state["project"] = deepcopy(payload)
        self._normalize_entity_id(state["project"])
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "project": state["project"]}

    def create_active_storage_sequence(self, backend: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Sequence payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        sequence = deepcopy(payload)
        self._normalize_entity_id(sequence)
        if not sequence.get("id"):
            sequence["id"] = f"seq_{str(uuid4())[:8]}"
        if any(self._entity_id(s) == sequence["id"] for s in state["sequences"]):
            raise StorageImportError("ID_COLLISION", f"Sequence with id {sequence['id']} already exists", 409)
        state["sequences"].append(sequence)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "sequence": sequence}

    def update_active_storage_sequence(self, backend: str, sequence_id: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Sequence payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        sequence_id = sequence_id.strip()
        found = False
        for i, seq in enumerate(state["sequences"]):
            if self._entity_id(seq) == sequence_id:
                updated_seq = {**seq, **payload, "id": sequence_id}
                state["sequences"][i] = updated_seq
                found = True
                break
        if not found:
            raise StorageImportError("SEQUENCE_NOT_FOUND", f"Sequence {sequence_id} not found", 404)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "sequence": state["sequences"][i]}

    def delete_active_storage_sequence(self, backend: str, sequence_id: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        sequence_id = sequence_id.strip()
        before = len(state["sequences"])
        state["sequences"] = [s for s in state["sequences"] if self._entity_id(s) != sequence_id]
        if len(state["sequences"]) == before:
            raise StorageImportError("SEQUENCE_NOT_FOUND", f"Sequence {sequence_id} not found", 404)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "deleted": sequence_id}

    def create_active_storage_scene(self, backend: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Scene payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        scene = deepcopy(payload)
        self._normalize_entity_id(scene)
        if not scene.get("id"):
            scene["id"] = f"scene_{str(uuid4())[:10]}"
        if any(self._entity_id(s) == scene["id"] for s in state["scenes"]):
            raise StorageImportError("ID_COLLISION", f"Scene with id {scene['id']} already exists", 409)
        state["scenes"].append(scene)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "scene": scene}

    def update_active_storage_scene(self, backend: str, scene_id: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Scene payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        scene_id = scene_id.strip()
        found = False
        for i, scene in enumerate(state["scenes"]):
            if self._entity_id(scene) == scene_id:
                updated_scene = {**scene, **payload, "id": scene_id}
                state["scenes"][i] = updated_scene
                found = True
                break
        if not found:
            raise StorageImportError("SCENE_NOT_FOUND", f"Scene {scene_id} not found", 404)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "scene": state["scenes"][i]}

    def delete_active_storage_scene(self, backend: str, scene_id: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        scene_id = scene_id.strip()
        before = len(state["scenes"])
        state["scenes"] = [s for s in state["scenes"] if self._entity_id(s) != scene_id]
        if len(state["scenes"]) == before:
            raise StorageImportError("SCENE_NOT_FOUND", f"Scene {scene_id} not found", 404)

        state["shots"] = [
            shot
            for shot in state["shots"]
            if not (isinstance(shot.get("scene_id"), str) and shot.get("scene_id").strip() == scene_id)
        ]

        self._persist_active_storage_state(backend, state)
        return {"ok": True, "deleted": scene_id}

    def create_active_storage_shot(self, backend: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Shot payload must be an object", 400)
        state = self._load_active_storage_state(backend)
        normalized_payload = self._normalize_shot_payload_aliases(deepcopy(payload))
        shot = self._normalize_shot(normalized_payload)
        if any(self._entity_id(s) == shot["id"] for s in state["shots"]):
            raise StorageImportError("ID_COLLISION", f"Shot with id {shot['id']} already exists", 409)
        state["shots"].append(shot)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "shot": shot}

    def update_active_storage_shot(self, backend: str, shot_id: str, payload: Any) -> Dict[str, Any]:
        backend = backend.strip().lower()
        if not self._is_object(payload):
            raise StorageImportError("INVALID_PAYLOAD", "Shot payload must be an object", 400)
        normalized_payload = self._normalize_shot_payload_aliases(deepcopy(payload))
        state = self._load_active_storage_state(backend)
        shot_id = shot_id.strip()
        found = False
        for i, shot in enumerate(state["shots"]):
            if self._entity_id(shot) == shot_id:
                merged = {**shot, **normalized_payload, "id": shot_id}
                updated_shot = self._normalize_shot(merged)
                state["shots"][i] = updated_shot
                found = True
                break
        if not found:
            raise StorageImportError("SHOT_NOT_FOUND", f"Shot {shot_id} not found", 404)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "shot": state["shots"][i]}

    def delete_active_storage_shot(self, backend: str, shot_id: str) -> Dict[str, Any]:
        backend = backend.strip().lower()
        state = self._load_active_storage_state(backend)
        shot_id = shot_id.strip()
        before = len(state["shots"])
        state["shots"] = [s for s in state["shots"] if self._entity_id(s) != shot_id]
        if len(state["shots"]) == before:
            raise StorageImportError("SHOT_NOT_FOUND", f"Shot {shot_id} not found", 404)
        self._persist_active_storage_state(backend, state)
        return {"ok": True, "deleted": shot_id}
