from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.cid_script_intelligence_service import CIDScriptIntelligenceService  # noqa: E402


class _FakeResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class _FakeDb:
    def __init__(self, project, breakdown):
        self._values = [project, breakdown]

    async def execute(self, *_args, **_kwargs):
        if not self._values:
            return _FakeResult(None)
        return _FakeResult(self._values.pop(0))


@pytest.mark.asyncio
async def test_service_sanitizes_theory_text_and_keeps_sources(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="Escena con conflicto y acción")
    breakdown = SimpleNamespace(
        breakdown_json="""
        {
          "scenes": [{"scene_number": 1, "action_blocks": ["Amenaza directa"], "characters_detected": ["ANA"]}],
          "sequences": [{"sequence_id": "seq_01"}]
        }
        """,
    )
    fake_db = _FakeDb(project, breakdown)
    service = CIDScriptIntelligenceService()

    long_theory = "THEORY " * 200

    async def fake_context(*, topics=None):
        return {
            "summary": long_theory,
            "sources": [{"title": "Syd Field", "source_file": "x", "chunk_index": 1}],
            "fallback_used": False,
        }

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    result = await service.analyze_project(
        fake_db,
        project_id="proj-1",
        organization_id="org-1",
    )

    assert result["theory_sources_used"]
    full_text = " ".join(result["mckee"]["subtext_notes"]) + result["syd_field"]["act_structure"]
    assert "THEORY THEORY THEORY THEORY THEORY" not in full_text
    for value in result["scores"].values():
        assert 0 <= int(value) <= 100


@pytest.mark.asyncio
async def test_service_mentions_sequence_ids_when_scope_is_requested(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="Escena A\nEscena B")
    breakdown = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 1}, {"scene_number": 2}], "sequences": [{"sequence_id": "seq_01"}, {"sequence_id": "seq_02"}]}'
    )
    fake_db = _FakeDb(project, breakdown)
    service = CIDScriptIntelligenceService()

    async def fake_context(*, topics=None):
        return {"summary": "", "sources": [], "fallback_used": True}

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    result = await service.analyze_project(
        fake_db,
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["seq_02"],
    )
    assert "seq_02" in result["overall_diagnosis"]
