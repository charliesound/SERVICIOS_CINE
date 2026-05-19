from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.script_intake_service import ScriptIntakeService  # noqa: E402


def test_sequence_traceability_preserves_real_scene_numbers() -> None:
    service = ScriptIntakeService()
    scenes = [
        {"scene_number": 59, "heading": "59 EXT/INT. PARKING/COCHE. DÍA.", "location": "PARKING/COCHE", "action_blocks": [], "characters_detected": []},
        {"scene_number": 60, "heading": "60 INT. PASILLO HOTEL. DÍA.", "location": "PASILLO HOTEL", "action_blocks": [], "characters_detected": []},
        {"scene_number": 61, "heading": "61 INT. HABITACIÓN HOTEL. DÍA.", "location": "HABITACIÓN HOTEL", "action_blocks": [], "characters_detected": []},
    ]

    sequences = service.build_sequence_blocks(scenes)
    assert len(sequences) == 1
    first = sequences[0]
    assert first["scene_numbers"] == [59, 60, 61]
    assert first["source_scene_start"] == 59
    assert first["source_scene_end"] == 61
    assert first["display_name"] == "Secuencia 1 — Escenas 59-61"
    assert first["sequence_id"] == "seq_001"
    for scene in scenes:
        assert scene["sequence_id"] == "seq_001"
        assert scene["sequence_order"] == 1
        assert scene["sequence_display_name"] == "Secuencia 1 — Escenas 59-61"


def test_nonconsecutive_scenes_can_share_sequence_by_dramatic_continuity() -> None:
    service = ScriptIntakeService()
    scenes = [
        {
            "scene_number": 59,
            "heading": "59 EXT. PARKING. DÍA.",
            "location": "PARKING/COCHE",
            "time_of_day": "DÍA",
            "dramatic_objective": "capture_escape",
            "action_blocks": ["amenaza y persecución"],
            "characters_detected": ["ANA", "LUIS"],
        },
        {
            "scene_number": 60,
            "heading": "60 INT. HOTEL. DÍA.",
            "location": "HABITACIÓN HOTEL",
            "time_of_day": "DÍA",
            "dramatic_objective": "cover_story",
            "action_blocks": ["calma táctica"],
            "characters_detected": ["MARTA"],
        },
        {
            "scene_number": 62,
            "heading": "62 EXT. PARKING. DÍA.",
            "location": "PARKING/COCHE",
            "time_of_day": "DÍA",
            "dramatic_objective": "capture_escape",
            "action_blocks": ["persigue y confronta"],
            "characters_detected": ["ANA", "LUIS"],
        },
    ]

    sequences = service.build_sequence_blocks(scenes)
    assert len(sequences) >= 2
    parking_sequence = next(seq for seq in sequences if 59 in seq["scene_numbers"])
    assert 62 in parking_sequence["scene_numbers"]
    assert parking_sequence["scene_numbers"] == [59, 62]


def test_consecutive_scenes_split_when_objective_conflict_changes() -> None:
    service = ScriptIntakeService()
    scenes = [
        {
            "scene_number": 10,
            "heading": "10 INT. OFICINA. NOCHE.",
            "location": "OFICINA",
            "time_of_day": "NOCHE",
            "dramatic_objective": "negotiate_contract",
            "action_blocks": ["negocia bajo tensión"],
            "characters_detected": ["ANA", "PEDRO"],
        },
        {
            "scene_number": 11,
            "heading": "11 INT. OFICINA. NOCHE.",
            "location": "OFICINA",
            "time_of_day": "NOCHE",
            "dramatic_objective": "hide_evidence",
            "action_blocks": ["oculta pruebas en silencio"],
            "characters_detected": ["MARTA"],
        },
    ]
    sequences = service.build_sequence_blocks(scenes)
    assert len(sequences) == 2
