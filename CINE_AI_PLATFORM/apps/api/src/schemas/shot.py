from pydantic import BaseModel
from typing import Optional, List

class Shot(BaseModel):
    id: str
    scene_id: str
    type: str
    prompt: str
    negative_prompt: Optional[str] = None
    seed: int
    cfg: float
    steps: int
    workflow_key: str
    refs: List[str] = []
