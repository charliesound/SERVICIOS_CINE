from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None

class Project(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
