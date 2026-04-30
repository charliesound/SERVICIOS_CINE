from pydantic import BaseModel
from typing import Optional


class ScriptPayload(BaseModel):
    title: Optional[str] = None
    text: str
    goal: Optional[str] = None


class ScriptEvent(BaseModel):
    event_type: str
    source: str
    payload: ScriptPayload