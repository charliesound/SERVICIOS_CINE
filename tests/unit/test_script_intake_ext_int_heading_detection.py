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

from services.script_intake_service import script_intake_service  # noqa: E402


THREE_SCENE_FRAGMENT = """59 EXT/INT. PARKING/COCHE. DÍA.
60 INT. PASILLO HOTEL. DÍA.
61 INT. HABITACIÓN HOTEL. DÍA.
"""


def test_script_intake_detects_three_numbered_scenes_with_ext_int() -> None:
    scenes = script_intake_service.parse_script(THREE_SCENE_FRAGMENT)
    assert len(scenes) == 3
    assert [int(scene.get("scene_number") or 0) for scene in scenes] == [59, 60, 61]
    assert str(scenes[0].get("heading") or "").startswith("59 EXT/INT")
    assert str(scenes[0].get("int_ext") or "") == "INT/EXT"
