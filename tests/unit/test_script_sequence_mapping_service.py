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

from schemas.cid_sequence_first_schema import ScriptSequenceMap  # noqa: E402
from services.cid_script_scene_parser_service import cid_script_scene_parser_service  # noqa: E402
from services.script_sequence_mapping_service import script_sequence_mapping_service  # noqa: E402

SCRIPT_TEXT = """1 INT. ESTUDIO - NOCHE
Un director revisa el storyboard con su equipo.
La atmósfera es tensa pero creativa.

2 EXT. CALLE - DIA
El equipo sale a filmar una escena nocturna.
El director da indicaciones al camarógrafo.

3 INT. SALA DE MONTAJE - NOCHE
El equipo revisa el metraje.
Discuten los cortes.

4 INT. ESTUDIO - DIA
Reunión final.
El director aprueba el montaje."""


def _parse_scenes():
    _, scenes, _ = cid_script_scene_parser_service.parse_script(SCRIPT_TEXT)
    return scenes


def test_build_sequence_map_returns_map() -> None:
    scenes = _parse_scenes()
    result = script_sequence_mapping_service.build_sequence_map(scenes, SCRIPT_TEXT)
    assert isinstance(result, ScriptSequenceMap)


def test_sequence_map_entries_have_script_excerpt() -> None:
    scenes = _parse_scenes()
    result = script_sequence_mapping_service.build_sequence_map(scenes, SCRIPT_TEXT)
    for entry in result.sequences:
        assert entry.script_excerpt


def test_sequence_map_detects_characters() -> None:
    scenes = _parse_scenes()
    result = script_sequence_mapping_service.build_sequence_map(scenes, SCRIPT_TEXT)
    for entry in result.sequences:
        assert isinstance(entry.characters, list)


def test_entry_recommended_for_storyboard_based_on_dramatic_function() -> None:
    scenes = _parse_scenes()
    result = script_sequence_mapping_service.build_sequence_map(scenes, SCRIPT_TEXT)
    for entry in result.sequences:
        if entry.dramatic_function in ("exposition", "climax", "resolution", "conflict_escalation", "rising_tension", "turning_point"):
            assert entry.recommended_for_storyboard is True


def test_entry_suggested_shot_count_is_positive() -> None:
    scenes = _parse_scenes()
    result = script_sequence_mapping_service.build_sequence_map(scenes, SCRIPT_TEXT)
    for entry in result.sequences:
        assert entry.suggested_shot_count > 0


def test_empty_scenes_returns_empty_map() -> None:
    result = script_sequence_mapping_service.build_sequence_map([])
    assert isinstance(result, ScriptSequenceMap)
    assert len(result.sequences) == 0
