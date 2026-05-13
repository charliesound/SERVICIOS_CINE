"""
Active Solutions Registry for CID.

Allows ComfySearch-found workflows and n8n-orchestrated pipelines
to be registered, activated, and executed as named solutions within CID.

A "solution" pairs:
  - a semantic need (e.g. "contraplano dramático SDXL")
  - a ComfyUI workflow JSON (found by ComfySearch)
  - a backend instance (still, video, dubbing, lab)
  - optional n8n workflow URL for orchestration
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory store (migrate to DB later)
_solutions: dict[str, dict] = {}
_solutions_file = "data/solutions_registry.json"

def _solution_id_from_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_")


def _normalize_solution(solution: dict) -> dict:
    """Backfill fields required by API responses for old registry entries."""
    normalized = dict(solution)
    now = datetime.now(timezone.utc).isoformat()

    name = normalized.get("name", "")
    normalized.setdefault("id", _solution_id_from_name(name) if name else "")
    normalized.setdefault("workflow_id", "")
    normalized.setdefault("backend", "still")
    normalized.setdefault("workflow_path", "")
    normalized.setdefault("description", "")
    normalized.setdefault("tags", [])
    normalized.setdefault("n8n_workflow_url", "")
    normalized.setdefault("is_active", True)
    normalized.setdefault("created_by", "system")
    normalized.setdefault("created_at", now)
    normalized.setdefault("updated_at", normalized.get("created_at", now))
    normalized.setdefault("execution_count", 0)
    normalized.setdefault("last_executed_at", None)

    return normalized



def _load():
    global _solutions
    try:
        with open(_solutions_file, "r") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            _solutions = {
                sid: _normalize_solution(sol)
                for sid, sol in raw.items()
                if isinstance(sol, dict)
            }
        else:
            _solutions = {}
    except (FileNotFoundError, json.JSONDecodeError):
        _solutions = {}


def _save():
    import os
    os.makedirs(os.path.dirname(_solutions_file) or ".", exist_ok=True)
    with open(_solutions_file, "w") as f:
        json.dump(_solutions, f, indent=2, ensure_ascii=False)


def register_solution(
    name: str,
    workflow_id: str,
    backend: str,
    workflow_path: str = "",
    description: str = "",
    tags: list[str] = None,
    n8n_workflow_url: str = "",
    created_by: str = "system",
) -> dict:
    _load()
    solution_id = _solution_id_from_name(name)

    solution = {
        "id": solution_id,
        "name": name,
        "workflow_id": workflow_id,
        "backend": backend,
        "workflow_path": workflow_path,
        "description": description,
        "tags": tags or [],
        "n8n_workflow_url": n8n_workflow_url,
        "is_active": True,
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "execution_count": 0,
    }
    _solutions[solution_id] = solution
    _save()
    logger.info("Solución activa registrada: %s (backend=%s)", name, backend)
    return solution


def get_solution(solution_id: str) -> Optional[dict]:
    _load()
    return _solutions.get(solution_id)


def list_solutions(backend: str = None, tag: str = None) -> list[dict]:
    _load()
    results = []
    for sol in _solutions.values():
        if backend and sol.get("backend") != backend:
            continue
        if tag and tag not in sol.get("tags", []):
            continue
        results.append(sol)
    return sorted(results, key=lambda x: x.get("name", ""))


def deactivate_solution(solution_id: str) -> bool:
    _load()
    if solution_id not in _solutions:
        return False
    _solutions[solution_id]["is_active"] = False
    _solutions[solution_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save()
    return True


def record_execution(solution_id: str):
    _load()
    if solution_id in _solutions:
        _solutions[solution_id]["execution_count"] = _solutions[solution_id].get("execution_count", 0) + 1
        _solutions[solution_id]["last_executed_at"] = datetime.now(timezone.utc).isoformat()
        _save()


# ── Seed default solutions from ComfySearch ───────────────────────────────────

DEFAULT_SOLUTIONS = [
    {
        "name": "Storyboard Cinematográfico SDXL",
        "workflow_id": "",
        "backend": "still",
        "description": "Generación de frames de storyboard en formato panorámico con SDXL",
        "tags": ["storyboard", "sdxl", "cine", "previsualizacion"],
    },
    {
        "name": "Doblaje TTS Español",
        "workflow_id": "dubbing_tts_es_es",
        "backend": "dubbing",
        "description": "Texto a voz en español para doblaje asistido",
        "tags": ["dubbing", "tts", "audio", "espanol"],
    },
    {
        "name": "Clonación de Voz Autorizada",
        "workflow_id": "dubbing_voice_clone_single",
        "backend": "dubbing",
        "description": "Clonación de voz desde audio de referencia con control legal",
        "tags": ["dubbing", "voice_clone", "audio", "legal"],
    },
    {
        "name": "LipSync Wav2Lip",
        "workflow_id": "",
        "backend": "dubbing",
        "description": "Sincronización labial mediante Wav2Lip sobre ComfyUI",
        "tags": ["dubbing", "lipsync", "video", "wav2lip"],
    },
    {
        "name": "Traducción y Doblaje Automático",
        "workflow_id": "dubbing_translate_stt_tts",
        "backend": "dubbing",
        "description": "Pipeline completo: transcribir, traducir y sintetizar voz",
        "tags": ["dubbing", "traduccion", "tts", "stt", "completo"],
    },
    {
        "name": "Video WAN Image-to-Video",
        "workflow_id": "video_wan",
        "backend": "video",
        "description": "Generación de vídeo cinematográfico desde imagen con WAN",
        "tags": ["video", "wan", "i2v", "cine"],
    },
    {
        "name": "Upscale 4K con Deinterlace",
        "workflow_id": "upscale_delivery",
        "backend": "lab",
        "description": "Restauración y upscaling de material legacy a 4K",
        "tags": ["restauracion", "upscale", "4k", "deinterlace"],
    },
]


def seed_defaults():
    _load()
    for sol in DEFAULT_SOLUTIONS:
        sid = _solution_id_from_name(sol["name"])
        if sid not in _solutions:
            sol["id"] = sid
            sol["is_active"] = True
            sol["created_at"] = datetime.now(timezone.utc).isoformat()
            sol["updated_at"] = datetime.now(timezone.utc).isoformat()
            sol["execution_count"] = 0
            sol["created_by"] = "system"
            _solutions[sid] = sol
    for sid, existing in list(_solutions.items()):
        _solutions[sid] = _normalize_solution(existing)

    _save()
    logger.info("Sembradas %d soluciones activas por defecto", len(DEFAULT_SOLUTIONS))
