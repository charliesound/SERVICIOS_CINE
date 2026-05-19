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
