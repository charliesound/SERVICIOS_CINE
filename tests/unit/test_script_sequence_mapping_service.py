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

MULTI_BLOCK_SCRIPT = """1 INT. OFICINA - NOCHE
Equipo revisa evidencias y define plan inicial.

2 INT. OFICINA - NOCHE
La discusión sigue sobre el mismo objetivo inmediato.

3 EXT. ALMACEN - MADRUGADA
CORTE A: operativo en nueva localización con riesgo alto.

4 EXT. ALMACEN - MADRUGADA
La acción continúa con tensión y persecución.

5 INT. TRIBUNAL - DIA
DÍAS DESPUÉS, presentan resultados y cambia el objetivo.
"""

THREE_SCENE_FRAGMENT = """59 EXT/INT. PARKING/COCHE. DÍA.
60 INT. PASILLO HOTEL. DÍA.
61 INT. HABITACIÓN HOTEL. DÍA.
"""


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


def test_multi_block_script_generates_multiple_sequences() -> None:
    _, scenes, _ = cid_script_scene_parser_service.parse_script(MULTI_BLOCK_SCRIPT)
    result = script_sequence_mapping_service.build_sequence_map(scenes, MULTI_BLOCK_SCRIPT)
    assert len(result.sequences) >= 3


def test_consecutive_coherent_scenes_are_grouped_together() -> None:
    _, scenes, _ = cid_script_scene_parser_service.parse_script(MULTI_BLOCK_SCRIPT)
    result = script_sequence_mapping_service.build_sequence_map(scenes, MULTI_BLOCK_SCRIPT)
    first = result.sequences[0]
    excerpt = first.script_excerpt.upper()
    assert "REVISA EVIDENCIAS" in excerpt
    assert "DISCUSIÓN SIGUE" in excerpt or "DISCUSION SIGUE" in excerpt


def test_strong_narrative_transition_creates_new_sequence() -> None:
    _, scenes, _ = cid_script_scene_parser_service.parse_script(MULTI_BLOCK_SCRIPT)
    result = script_sequence_mapping_service.build_sequence_map(scenes, MULTI_BLOCK_SCRIPT)
    excerpts = [entry.script_excerpt.upper() for entry in result.sequences]
    assert any("CORTE A" in excerpt for excerpt in excerpts)
    assert any("DÍAS DESPUÉS" in excerpt or "DIAS DESPUES" in excerpt for excerpt in excerpts)


def test_sequence_entry_has_optional_narrative_metadata() -> None:
    _, scenes, _ = cid_script_scene_parser_service.parse_script(MULTI_BLOCK_SCRIPT)
    result = script_sequence_mapping_service.build_sequence_map(scenes, MULTI_BLOCK_SCRIPT)
    entry = result.sequences[0]
    assert entry.sequence_title is not None
    assert entry.dramatic_purpose is not None
    assert entry.continuity_group is not None


def test_parser_detects_three_numbered_slugline_scenes_with_ext_int_and_slashes() -> None:
    _sequences, scenes, warnings = cid_script_scene_parser_service.parse_script(THREE_SCENE_FRAGMENT)
    assert not warnings or "regex_scene_detection_failed_using_fallback" not in warnings
    assert len(scenes) == 3
    numbers = [scene.scene_number for scene in scenes]
    assert numbers == [59, 60, 61]


def test_sequence_mapping_never_loses_detected_scenes_for_three_scene_fragment() -> None:
    _sequences, scenes, _warnings = cid_script_scene_parser_service.parse_script(THREE_SCENE_FRAGMENT)
    result = script_sequence_mapping_service.build_sequence_map(scenes, THREE_SCENE_FRAGMENT)
    assert len(scenes) == 3
    merged = "\n".join(entry.script_excerpt for entry in result.sequences).upper()
    assert "59 EXT/INT" in merged
    assert "60 INT." in merged
    assert "61 INT." in merged
