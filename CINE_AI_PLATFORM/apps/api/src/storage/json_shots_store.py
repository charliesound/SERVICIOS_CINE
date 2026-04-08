from pathlib import Path
from typing import Any, Dict, List, Optional
import json


class JsonShotsStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]\n", encoding="utf-8")

    def _load(self) -> List[Dict[str, Any]]:
        raw = self.file_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, list):
            raise RuntimeError("shots.json debe contener un array")
        return data

    def _save(self, shots: List[Dict[str, Any]]) -> None:
        self.file_path.write_text(
            json.dumps(shots, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def list_shots(self) -> List[Dict[str, Any]]:
        return self._load()

    def get_shot(self, shot_id: str) -> Optional[Dict[str, Any]]:
        shots = self._load()
        return next((s for s in shots if str(s.get("id")) == shot_id), None)

    def create_shot(self, shot: Dict[str, Any]) -> Dict[str, Any]:
        shots = self._load()
        shots.append(shot)
        self._save(shots)
        return shot

    def replace_shot(self, shot_id: str, shot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        shots = self._load()
        for index, current in enumerate(shots):
            if str(current.get("id")) == shot_id:
                shots[index] = shot
                self._save(shots)
                return shot
        return None

    def delete_shot(self, shot_id: str) -> bool:
        shots = self._load()
        new_shots = [s for s in shots if str(s.get("id")) != shot_id]
        if len(new_shots) == len(shots):
            return False
        self._save(new_shots)
        return True