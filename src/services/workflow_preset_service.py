from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import yaml
from pathlib import Path

from .workflow_registry import workflow_registry, TaskCategory


@dataclass
class Preset:
    id: str
    name: str
    workflow_key: str
    description: str
    category: str
    backend: str
    inputs: Dict[str, Any]
    is_public: bool
    created_by: str
    created_at: datetime
    tags: List[str]


class WorkflowPresetService:
    _instance = None
    _presets: Dict[str, Preset] = {}
    _presets_dir: Path

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._presets_dir = Path(__file__).parent.parent / "config" / "presets"
        self._presets_dir.mkdir(exist_ok=True)
        self._load_presets()

    def _load_presets(self):
        for preset_file in self._presets_dir.glob("*.yml"):
            try:
                with open(preset_file, 'r') as f:
                    data = yaml.safe_load(f)
                    for key, preset_data in data.get("presets", {}).items():
                        preset = Preset(
                            id=key,
                            name=preset_data["name"],
                            workflow_key=preset_data["workflow_key"],
                            description=preset_data.get("description", ""),
                            category=preset_data.get("category", ""),
                            backend=preset_data.get("backend", ""),
                            inputs=preset_data.get("inputs", {}),
                            is_public=preset_data.get("public", True),
                            created_by=preset_data.get("created_by", "system"),
                            created_at=datetime.fromisoformat(preset_data.get("created_at", datetime.utcnow().isoformat())),
                            tags=preset_data.get("tags", [])
                        )
                        self._presets[key] = preset
            except Exception:
                pass

    def _save_preset(self, preset: Preset):
        preset_file = self._presets_dir / f"{preset.category}.yml"
        
        existing = {}
        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    existing = yaml.safe_load(f) or {}
            except Exception:
                existing = {}

        if "presets" not in existing:
            existing["presets"] = {}
        
        existing["presets"][preset.id] = {
            "name": preset.name,
            "workflow_key": preset.workflow_key,
            "description": preset.description,
            "category": preset.category,
            "backend": preset.backend,
            "inputs": preset.inputs,
            "public": preset.is_public,
            "created_by": preset.created_by,
            "created_at": preset.created_at.isoformat(),
            "tags": preset.tags
        }

        with open(preset_file, 'w') as f:
            yaml.dump(existing, f, default_flow_style=False)

    def create_preset(self, name: str, workflow_key: str, inputs: Dict[str, Any],
                     user_id: str, category: Optional[str] = None,
                     description: str = "", tags: Optional[List[str]] = None,
                     is_public: bool = False) -> Optional[Preset]:
        
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None

        preset_id = f"{user_id}_{name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        preset = Preset(
            id=preset_id,
            name=name,
            workflow_key=workflow_key,
            description=description,
            category=category or template.category.value,
            backend=template.backend,
            inputs=inputs,
            is_public=is_public,
            created_by=user_id,
            created_at=datetime.utcnow(),
            tags=tags or []
        )

        self._presets[preset_id] = preset
        self._save_preset(preset)

        return preset

    def get_preset(self, preset_id: str) -> Optional[Preset]:
        return self._presets.get(preset_id)

    def get_presets_by_workflow(self, workflow_key: str) -> List[Preset]:
        return [p for p in self._presets.values() if p.workflow_key == workflow_key]

    def get_presets_by_user(self, user_id: str) -> List[Preset]:
        return [p for p in self._presets.values() if p.created_by == user_id]

    def get_public_presets(self, category: Optional[str] = None) -> List[Preset]:
        presets = [p for p in self._presets.values() if p.is_public]
        if category:
            presets = [p for p in presets if p.category == category]
        return presets

    def list_presets(self, user_id: Optional[str] = None, include_public: bool = True,
                     category: Optional[str] = None) -> List[Dict[str, Any]]:
        result = []

        if include_public:
            result.extend([
                {
                    "id": p.id,
                    "name": p.name,
                    "workflow_key": p.workflow_key,
                    "description": p.description,
                    "category": p.category,
                    "backend": p.backend,
                    "tags": p.tags,
                    "is_public": p.is_public,
                    "created_by": p.created_by,
                    "created_at": p.created_at.isoformat()
                }
                for p in self._presets.values() if p.is_public
            ])

        if user_id:
            result.extend([
                {
                    "id": p.id,
                    "name": p.name,
                    "workflow_key": p.workflow_key,
                    "description": p.description,
                    "category": p.category,
                    "backend": p.backend,
                    "tags": p.tags,
                    "is_public": p.is_public,
                    "created_by": p.created_by,
                    "created_at": p.created_at.isoformat()
                }
                for p in self._presets.values() if p.created_by == user_id and not p.is_public
            ])

        if category:
            result = [p for p in result if p["category"] == category]

        return result

    def delete_preset(self, preset_id: str, user_id: str) -> bool:
        preset = self._presets.get(preset_id)
        if not preset:
            return False
        
        if preset.created_by != user_id:
            return False

        del self._presets[preset_id]
        return True


preset_service = WorkflowPresetService()
