from pydantic import BaseModel
from typing import Optional

class Scene(BaseModel):
    id: str
    project_id: str
    title: str
    dramatic_purpose: Optional[str] = None
