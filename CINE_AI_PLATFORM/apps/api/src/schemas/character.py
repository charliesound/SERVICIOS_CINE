from pydantic import BaseModel
from typing import List

class Character(BaseModel):
    id: str
    project_id: str
    name: str
    seed_master: int
    reference_images: List[str] = []
