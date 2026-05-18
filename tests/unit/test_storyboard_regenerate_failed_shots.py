from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from routes.storyboard_routes import (  # noqa: E402
    regenerate_failed_storyboard_sequence_shots,
    regenerate_storyboard_shot,
)
from schemas.storyboard_schema import (  # noqa: E402
    StoryboardFailedRegenerateRequest,
    StoryboardShotRegenerateRequest,
)
from services.storyboard_service import StoryboardService  # noqa: E402


def _shot(shot_id: str, score: float, suggested: str = "") -> SimpleNamespace:
    return SimpleNamespace(
        id=shot_id,
        metadata_json={
            "validation_score": score,
            "suggested_regeneration_prompt": suggested,
        },
    )


def test_failed_shots_from_candidates_respects_threshold() -> None:
    service = StoryboardService()
    candidates = [_shot("a", 65), _shot("b", 70), _shot("c", 45), _shot("d", 0.95)]
    failed = service._failed_shots_from_candidates(candidates, threshold=70)
    failed_ids = {str(item.id) for item in failed}
    assert failed_ids == {"a", "c"}


def test_resolve_regeneration_prompt_uses_suggested_prompt() -> None:
    service = StoryboardService()
    prompt = service._resolve_regeneration_prompt(
        {
            "suggested_regeneration_prompt": "STRICT SCRIPT ALIGNMENT: Marta with flashlight",
            "validation_failures": ["location"],
        }
    )
    assert "STRICT SCRIPT ALIGNMENT" in prompt
    assert "Marta" in prompt


def test_endpoint_regenerate_single_shot(monkeypatch) -> None:
    async def fake_regen(*args, **kwargs):
        return {
            "job_id": "regen-123",
            "project_id": "project-1",
            "sequence_id": "seq_01",
            "regenerated_shots": [
                {
                    "shot_id": "shot-new-1",
                    "source_shot_id": "shot-old-1",
                    "sequence_id": "seq_01",
                    "status": "queued",
                    "render_job_id": "render-1",
                    "reason": None,
                }
            ],
            "skipped_shots": [],
            "threshold": 70,
            "status": "completed",
        }

    monkeypatch.setattr("routes.storyboard_routes.storyboard_service.regenerate_storyboard_shot_from_validation", fake_regen)
    response = asyncio.run(
        regenerate_storyboard_shot(
            project_id="project-1",
            shot_id="shot-old-1",
            payload=StoryboardShotRegenerateRequest(threshold=70),
            db=object(),
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", role="owner", is_global_admin=False),
        )
    )
    assert response.job_id == "regen-123"
    assert response.regenerated_shots[0].source_shot_id == "shot-old-1"


def test_endpoint_regenerate_failed_sequence(monkeypatch) -> None:
    async def fake_regen_failed(*args, **kwargs):
        return {
            "job_id": "regen-999",
            "project_id": "project-1",
            "sequence_id": "seq_01",
            "regenerated_shots": [],
            "skipped_shots": [],
            "threshold": 70,
            "status": "completed",
        }

    monkeypatch.setattr("routes.storyboard_routes.storyboard_service.regenerate_failed_storyboard_shots", fake_regen_failed)
    response = asyncio.run(
        regenerate_failed_storyboard_sequence_shots(
            project_id="project-1",
            sequence_id="seq_001",
            payload=StoryboardFailedRegenerateRequest(threshold=70),
            db=object(),
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", role="owner", is_global_admin=False),
        )
    )
    assert response.job_id == "regen-999"
    assert response.sequence_id == "seq_01"


def test_regenerate_failed_sequence_returns_canonical_alias(monkeypatch) -> None:
    service = StoryboardService()

    async def fake_find_failed(*args, **kwargs):
        return "seq_01", []

    monkeypatch.setattr(service, "find_failed_storyboard_shots", fake_find_failed)
    result = asyncio.run(
        service.regenerate_failed_storyboard_shots(
            object(),
            project_id="project-1",
            sequence_id="seq_001",
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", role="owner", is_global_admin=False),
            threshold=70,
        )
    )
    assert result["sequence_id"] == "seq_01"
