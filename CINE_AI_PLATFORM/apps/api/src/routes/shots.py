from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.schemas.shot import Shot

router = APIRouter(prefix="/shots", tags=["shots"])

shots_db = [
    {
        "id": "shot_001",
        "scene_id": "scene_001",
        "type": "close_up",
        "prompt": "Ana mira a Luis con tension contenida en la cocina",
        "negative_prompt": "blurry, low detail, bad anatomy",
        "seed": 111111,
        "cfg": 6.5,
        "steps": 30,
        "workflow_key": "master_shot",
        "refs": []
    },
    {
        "id": "shot_002",
        "scene_id": "scene_001",
        "type": "reverse_shot",
        "prompt": "Luis responde con mirada dura en contraplano",
        "negative_prompt": "blurry, low detail, bad anatomy",
        "seed": 111112,
        "cfg": 6.2,
        "steps": 30,
        "workflow_key": "reverse_shot",
        "refs": []
    },
    {
        "id": "shot_003",
        "scene_id": "scene_002",
        "type": "medium_close_up",
        "prompt": "Ana baja la mirada en silencio",
        "negative_prompt": "blurry, low detail, bad anatomy",
        "seed": 111113,
        "cfg": 6.0,
        "steps": 28,
        "workflow_key": "acting_variations",
        "refs": []
    },
    {
        "id": "shot_004",
        "scene_id": "scene_003",
        "type": "wide_shot",
        "prompt": "Marta entra al cafe en un plano general cinematografico",
        "negative_prompt": "blurry, low detail, bad anatomy",
        "seed": 222221,
        "cfg": 6.8,
        "steps": 32,
        "workflow_key": "location_establishing",
        "refs": []
    }
]

class ShotUpdate(BaseModel):
    type: str
    prompt: str
    negative_prompt: str | None = None
    seed: int
    cfg: float
    steps: int
    workflow_key: str
    refs: list[str] = []

@router.get("", response_model=list[Shot])
def list_shots():
    return shots_db

@router.get("/{shot_id}", response_model=Shot)
def get_shot(shot_id: str):
    for shot in shots_db:
        if shot["id"] == shot_id:
            return shot
    raise HTTPException(status_code=404, detail="Shot no encontrado")

@router.put("/{shot_id}", response_model=Shot)
def update_shot(shot_id: str, payload: ShotUpdate):
    for shot in shots_db:
        if shot["id"] == shot_id:
            shot["type"] = payload.type
            shot["prompt"] = payload.prompt
            shot["negative_prompt"] = payload.negative_prompt
            shot["seed"] = payload.seed
            shot["cfg"] = payload.cfg
            shot["steps"] = payload.steps
            shot["workflow_key"] = payload.workflow_key
            shot["refs"] = payload.refs
            return shot

    raise HTTPException(status_code=404, detail="Shot no encontrado")
