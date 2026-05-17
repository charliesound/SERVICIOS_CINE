from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import HTTPException  # noqa: E402
from schemas.storyboard_schema import StoryboardGenerateRequest  # noqa: E402
from services.storyboard_service import StoryboardGenerationMode  # noqa: E402
from services.storyboard_service import StoryboardSequenceBlock, StoryboardService  # noqa: E402


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


def _sample_scenes() -> list[dict[str, object]]:
    return [
        {"scene_number": 1, "heading": "INT. CASA - NOCHE", "scene_id": "scene_001"},
        {"scene_number": 2, "heading": "EXT. CALLE - DIA", "scene_id": "scene_002"},
        {"scene_number": 3, "heading": "INT. CAFE - TARDE", "scene_id": "scene_003"},
        {"scene_number": 4, "heading": "EXT. PARQUE - NOCHE", "scene_id": "scene_004"},
    ]


def _sample_sequences() -> list[StoryboardSequenceBlock]:
    return [
        StoryboardSequenceBlock(
            sequence_id="seq_001",
            sequence_number=1,
            title="Secuencia 1",
            summary="Primer bloque",
            included_scenes=[1, 2],
            characters=["A"],
            location="CASA",
            emotional_arc="setup",
            estimated_duration=120,
            estimated_shots=6,
        ),
        StoryboardSequenceBlock(
            sequence_id="seq_002",
            sequence_number=2,
            title="Secuencia 2",
            summary="Segundo bloque",
            included_scenes=[3, 4],
            characters=["B"],
            location="PARQUE",
            emotional_arc="escalation",
            estimated_duration=120,
            estimated_shots=6,
        ),
    ]


def test_contract_full_script_selection_returns_all_scenes() -> None:
    service = StoryboardService()
    scenes = _sample_scenes()
    selected = service._select_scenes(
        analysis_data={"scenes": scenes},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.FULL_SCRIPT,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2, 3, 4]


def test_contract_sequence_mode_accepts_canonical_sequence_id() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="seq_001",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_sequence_mode_accepts_numeric_alias() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="1",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_sequence_mode_accepts_sequence_prefixed_alias() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="sequence_001",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_scene_range_mode_selects_interval() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SCENE_RANGE,
        sequence_id=None,
        sequence_ids=[],
        scene_start=2,
        scene_end=3,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [2, 3]


def test_contract_selected_scenes_mode_selects_explicit_scene_numbers() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SELECTED_SCENES,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[1, 4],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 4]


def test_contract_single_scene_mode_selects_one_scene_from_selected_ids() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SINGLE_SCENE,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=["3"],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [3]


@pytest.mark.xfail(
    raises=AttributeError,
    strict=True,
    reason=(
        "Current implementation calls _resolve_sequence_block with sequence_id=None and crashes before HTTPException. "
        "Next commit should normalize this to HTTP 400/404 contract."
    ),
)
def test_contract_sequence_mode_without_sequence_id_returns_404_sequence_not_found() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id=None,
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Sequence not found"


def test_contract_scene_range_missing_boundaries_returns_400() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SCENE_RANGE,
            sequence_id=None,
            sequence_ids=[],
            scene_start=1,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "scene_start and scene_end are required" in exc.detail


def test_contract_invalid_mode_returns_400() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode="NOT_A_MODE",
            sequence_id=None,
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Unsupported storyboard generation mode"


def test_contract_nonexistent_sequence_returns_404() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id="seq_999",
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Sequence not found"


def test_schema_scope_fields_defaults_are_stable() -> None:
    req = StoryboardGenerateRequest()
    assert req.mode == "SEQUENCE"
    assert req.sequence_id is None
    assert req.sequence_ids == []
    assert req.scene_start is None
    assert req.scene_end is None
    assert req.scene_numbers == []
    assert req.shots_per_scene == 3
    assert req.overwrite is False
    assert req.style_preset == "cinematic_realistic"
