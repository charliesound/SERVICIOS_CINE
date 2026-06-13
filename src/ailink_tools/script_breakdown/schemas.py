"""Data schemas for Script-to-Production Breakdown demo."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import List


@dataclass
class Scene:
    scene_id: str
    number: int
    header: str
    location: str
    int_ext: str
    day_night: str
    characters: List[str]
    complexity: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Character:
    character_id: str
    name: str
    role: str
    scenes: List[int]
    age: str
    complexity: str
    notes: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Location:
    location_id: str
    name: str
    type: str
    int_ext: str
    scenes: List[int]
    permits: str
    complexity: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Risk:
    risk_id: str
    description: str
    impact: str
    probability: str
    mitigation: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BudgetItem:
    budget_id: str
    category: str
    low: int
    mid: int
    high: int
    confidence: str
    assumptions: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BreakdownResult:
    project: dict
    scenes: List[Scene]
    characters: List[Character]
    locations: List[Location]
    risks: List[Risk]
    viability: dict
    preliminary_budget: List[BudgetItem]
    recommendations: List[str]
    human_review_notes: List[str]
    metadata: dict

    def to_dict(self) -> dict:
        return {
            "project": self.project,
            "scenes": [s.to_dict() for s in self.scenes],
            "characters": [c.to_dict() for c in self.characters],
            "locations": [l.to_dict() for l in self.locations],
            "risks": [r.to_dict() for r in self.risks],
            "viability": self.viability,
            "preliminary_budget": [b.to_dict() for b in self.preliminary_budget],
            "recommendations": self.recommendations,
            "human_review_notes": self.human_review_notes,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
