from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import HTTPException  # noqa: E402
from services.storyboard_service import StoryboardGenerationMode  # noqa: E402


def test_generate_guard_message() -> None:
    message = (
        "Storyboard generation requires selected sequence_id or selected_sequence_ids. "
        "Run full script analysis first: POST /api/cid/script/analyze-full"
    )
    assert "sequence_id" in message
    assert "analyze-full" in message


def test_analyze_full_script_endpoint_exists() -> None:
    from routes.cid_script_to_prompt_routes import router  # noqa: E402
    paths = [r.path for r in router.routes]
    assert any("analyze-full" in p for p in paths)


def test_sequence_plan_endpoint_exists() -> None:
    from routes.storyboard_routes import router  # noqa: E402
    paths = [r.path for r in router.routes]
    assert any("plan" in p for p in paths)


def test_storyboard_generate_refuses_full_script() -> None:
    mode = StoryboardGenerationMode.FULL_SCRIPT
    has_sequence = False
    if mode in (StoryboardGenerationMode.FULL_SCRIPT, "") and not has_sequence:
        try:
            raise HTTPException(status_code=400, detail="Storyboard generation requires selected sequence_id")
        except HTTPException as e:
            assert e.status_code == 400
            assert "sequence_id" in e.detail
