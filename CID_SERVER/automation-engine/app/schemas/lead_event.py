from pydantic import BaseModel, EmailStr
from typing import Optional


class LeadPayload(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    message: str
    project_interest: Optional[str] = None
    source_channel: Optional[str] = None


class LeadEvent(BaseModel):
    event_type: str
    source: str
    payload: LeadPayload