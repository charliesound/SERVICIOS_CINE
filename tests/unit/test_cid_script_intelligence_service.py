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


@pytest.mark.asyncio
async def test_sequence_alias_seq_001_matches_seq_01_and_filters_scenes(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="Escenas")
    breakdown = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 1, "action_blocks": ["conflicto"]}, {"scene_number": 2}, {"scene_number": 3, "action_blocks": ["corre"]}, {"scene_number": 4}], "sequences": [{"sequence_id": "seq_001", "included_scenes": [1, 2]}, {"sequence_id": "seq_002", "included_scenes": [3, 4]}]}'
    )
    fake_db = _FakeDb(project, breakdown)
    service = CIDScriptIntelligenceService()

    async def fake_context(*, topics=None):
        return {"summary": "", "sources": [{"title": "McKee"}], "fallback_used": False}

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    result = await service.analyze_project(
        fake_db,
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["seq_01"],
    )

    assert "Escenas analizadas: 2" in result["overall_diagnosis"]
    assert "[1, 2]" in result["overall_diagnosis"]


@pytest.mark.asyncio
async def test_nonexistent_sequence_returns_zero_analysis_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="Escenas")
    breakdown = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 1}, {"scene_number": 2}], "sequences": [{"sequence_id": "seq_01", "included_scenes": [1, 2]}]}'
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
        sequence_ids=["seq_03"],
    )

    assert "Escenas analizadas: 0" in result["overall_diagnosis"]
    assert result["scores"]["conflict_strength"] == 0
    assert any("No hay material analizable" in item for item in result["storyboard_actionables"])


@pytest.mark.asyncio
async def test_existing_sequence_map_does_not_fallback_to_global_for_seq02_request(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="Escenas")
    breakdown = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 41}, {"scene_number": 42}, {"scene_number": 59}], "sequences": [{"sequence_id": "seq_001", "scene_numbers": [41, 42, 59]}]}'
    )
    service = CIDScriptIntelligenceService()

    async def fake_context(*, topics=None):
        return {"summary": "", "sources": [], "fallback_used": True}

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    result = await service.analyze_project(
        _FakeDb(project, breakdown),
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["seq_02"],
    )
    assert "Escenas analizadas: 0" in result["overall_diagnosis"]


@pytest.mark.asyncio
async def test_different_sequences_produce_different_filtered_counts(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_context(*, topics=None):
        return {"summary": "", "sources": [], "fallback_used": True}

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    project_a = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="texto")
    breakdown_a = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 1}, {"scene_number": 2}, {"scene_number": 3}], "sequences": [{"sequence_id": "seq_01", "included_scenes": [1, 2]}, {"sequence_id": "seq_02", "included_scenes": [3]}]}'
    )
    service = CIDScriptIntelligenceService()
    result_a = await service.analyze_project(
        _FakeDb(project_a, breakdown_a),
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["seq_01"],
    )

    project_b = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="texto")
    breakdown_b = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 1}, {"scene_number": 2}, {"scene_number": 3}], "sequences": [{"sequence_id": "seq_01", "included_scenes": [1, 2]}, {"sequence_id": "seq_02", "included_scenes": [3]}]}'
    )
    result_b = await service.analyze_project(
        _FakeDb(project_b, breakdown_b),
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["seq_02"],
    )

    assert "Escenas analizadas: 2" in result_a["overall_diagnosis"]
    assert "Escenas analizadas: 1" in result_b["overall_diagnosis"]


@pytest.mark.asyncio
async def test_script_intelligence_handles_nonconsecutive_scene_numbers_in_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    project = SimpleNamespace(id="proj-1", organization_id="org-1", script_text="texto")
    breakdown = SimpleNamespace(
        breakdown_json='{"scenes": [{"scene_number": 59, "action_blocks": ["amenaza"]}, {"scene_number": 60, "action_blocks": ["calma"]}, {"scene_number": 62, "action_blocks": ["confronta"]}], "sequences": [{"sequence_id": "seq_001", "display_name": "Secuencia 1 — Parking/Coche — Escenas 59, 62", "scene_numbers": [59, 62]}, {"sequence_id": "seq_002", "scene_numbers": [60]}]}'
    )
    service = CIDScriptIntelligenceService()

    async def fake_context(*, topics=None):
        return {"summary": "", "sources": [], "fallback_used": True}

    monkeypatch.setattr(
        "services.cid_script_intelligence_service.cid_screenwriting_theory_service.fetch_theory_context",
        fake_context,
    )

    result = await service.analyze_project(
        _FakeDb(project, breakdown),
        project_id="proj-1",
        organization_id="org-1",
        sequence_ids=["1"],
    )
    assert "Escenas analizadas: 2" in result["overall_diagnosis"]
    assert "[59, 62]" in result["overall_diagnosis"]
    assert "Parking/Coche" in result["overall_diagnosis"]
