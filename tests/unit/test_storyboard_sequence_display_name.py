from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.storyboard_service import StoryboardService  # noqa: E402


def test_storyboard_sequence_display_name_uses_real_scene_range() -> None:
    service = StoryboardService()
    scenes = [
        {"scene_number": 59, "heading": "59 EXT/INT. PARKING/COCHE. DÍA.", "location": "PARKING/COCHE", "action_blocks": [], "characters_detected": []},
        {"scene_number": 60, "heading": "60 INT. PASILLO HOTEL. DÍA.", "location": "PASILLO HOTEL", "action_blocks": [], "characters_detected": []},
        {"scene_number": 61, "heading": "61 INT. HABITACIÓN HOTEL. DÍA.", "location": "HABITACIÓN HOTEL", "action_blocks": [], "characters_detected": []},
    ]
    seqs = service._build_sequences_from_scenes(scenes)
    assert len(seqs) == 1
    assert seqs[0].sequence_id == "seq_001"
    assert seqs[0].included_scenes == [59, 60, 61]
    assert seqs[0].title == "Secuencia 1 — Escenas 59, 60, 61"


def test_storyboard_display_name_nonconsecutive_not_shown_as_range() -> None:
    service = StoryboardService()
    scenes = [
        {"scene_number": 59, "heading": "59 EXT/INT. PARKING/COCHE. DÍA.", "location": "PARKING/COCHE", "action_blocks": [], "characters_detected": []},
        {"scene_number": 62, "heading": "62 EXT/INT. PARKING/COCHE. DÍA.", "location": "PARKING/COCHE", "action_blocks": [], "characters_detected": []},
    ]
    seqs = service._build_sequences_from_scenes(scenes)
    assert len(seqs) == 1
    assert seqs[0].title == "Secuencia 1 — Escenas 59, 62"
