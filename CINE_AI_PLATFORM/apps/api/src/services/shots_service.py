from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime, timezone

from src.storage.json_shots_store import JsonShotsStore


class ShotsService:
    def __init__(self, store: JsonShotsStore):
        self.store = store

    def list_shots(self):
        return self.store.list_shots()

    def get_shot(self, shot_id: str):
        return self.store.get_shot(shot_id)

    def create_shot(self, payload: Dict[str, Any]):
        shot = self._build_shot(payload)
        return self.store.create_shot(shot)

    def replace_shot(self, shot_id: str, payload: Dict[str, Any]):
        current = self.store.get_shot(shot_id)
        if not current:
            return None
        shot = self._build_shot(payload, existing=current)
        return self.store.replace_shot(shot_id, shot)

    def patch_shot(self, shot_id: str, patch_data: Dict[str, Any]):
        current = self.store.get_shot(shot_id)
        if not current:
            return None
        shot = self._build_shot({**current, **patch_data}, existing=current)
        return self.store.replace_shot(shot_id, shot)

    def delete_shot(self, shot_id: str):
        return self.store.delete_shot(shot_id)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize_text(self, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str):
            return value.strip()
        return value

    def _build_shot(self, payload: Dict[str, Any], existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        base = dict(existing or {})
        shot = {**base, **payload}

        shot["id"] = shot.get("id") or str(uuid4())
        shot["title"] = self._normalize_text(shot.get("title"))
        shot["prompt"] = self._normalize_text(shot.get("prompt"))
        shot["raw_prompt"] = self._normalize_text(shot.get("raw_prompt"))
        shot["negative_prompt"] = self._normalize_text(shot.get("negative_prompt"))
        shot["camera_preset"] = self._normalize_text(shot.get("camera_preset"))
        shot["nominal_ratio"] = self._normalize_text(shot.get("nominal_ratio"))
        shot["scene_id"] = self._normalize_text(shot.get("scene_id"))
        shot["sequence_id"] = self._normalize_text(shot.get("sequence_id"))
        shot["status"] = self._normalize_text(shot.get("status"))

        shot["tags"] = shot.get("tags") if isinstance(shot.get("tags"), list) else []
        shot["references"] = shot.get("references") if isinstance(shot.get("references"), list) else []
        shot["layers"] = shot.get("layers") if isinstance(shot.get("layers"), list) else []
        shot["render_inputs"] = shot.get("render_inputs") if isinstance(shot.get("render_inputs"), dict) else {}
        shot["structured_prompt"] = shot.get("structured_prompt") if isinstance(shot.get("structured_prompt"), dict) else {}
        shot["metadata"] = shot.get("metadata") if isinstance(shot.get("metadata"), dict) else {}

        shot["updated_at"] = self._now_iso()
        if not existing:
            shot["created_at"] = shot["updated_at"]
        else:
            shot["created_at"] = existing.get("created_at", shot["updated_at"])

        return shot