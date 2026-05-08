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

from schemas.cid_sequence_first_schema import FullScriptAnalysisResult  # noqa: E402
from services.cid_script_scene_parser_service import cid_script_scene_parser_service  # noqa: E402
from services.script_synopsis_service import script_synopsis_service  # noqa: E402

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


def test_analyze_script_returns_full_result() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert isinstance(result, FullScriptAnalysisResult)
    assert result.synopsis is not None
    assert result.sequence_map is not None


def test_analyze_empty_script_does_not_crash() -> None:
    result = script_synopsis_service.analyze_script("")
    assert isinstance(result, FullScriptAnalysisResult)
    assert result.warnings


def test_synopsis_has_logline_and_premise() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert result.synopsis.logline
    assert result.synopsis.premise


def test_synopsis_has_main_characters() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert isinstance(result.synopsis.main_characters, list)


def test_synopsis_has_main_locations() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert isinstance(result.synopsis.main_locations, list)
    assert len(result.synopsis.main_locations) > 0


def test_sequence_map_has_sequences() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert len(result.sequence_map.sequences) > 0


def test_sequence_map_has_recommended_priority() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    assert len(result.sequence_map.recommended_priority_order) > 0


def test_sequence_map_entries_have_required_fields() -> None:
    result = script_synopsis_service.analyze_script(SCRIPT_TEXT)
    for entry in result.sequence_map.sequences:
        assert entry.sequence_id
        assert entry.title
        assert entry.dramatic_function
