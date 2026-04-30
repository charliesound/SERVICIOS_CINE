from pydantic import BaseModel
from typing import List, Optional


class LeadRoutingResult(BaseModel):
    ok: bool = True
    classification: str
    lead_type: str
    priority: str
    recommended_campaign: str
    recommended_target: str
    recommended_secondary_target: Optional[str] = None
    next_action: str
    notes: List[str]


RoutingResult = LeadRoutingResult


class ScriptRoutingResult(BaseModel):
    ok: bool = True
    content_type: str
    recommended_pipeline: str
    priority: str
    notes: List[str]