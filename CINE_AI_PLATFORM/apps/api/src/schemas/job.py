from pydantic import BaseModel
from typing import Optional

class Job(BaseModel):
    id: str
    shot_id: str
    status: str
    prompt_id: Optional[str] = None
    error: Optional[str] = None
