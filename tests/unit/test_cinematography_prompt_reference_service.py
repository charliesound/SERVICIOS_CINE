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

from services.cinematography_prompt_reference_service import CinematographyPromptReferenceService  # noqa: E402
from services.storyboard_service import StoryboardService  # noqa: E402


def test_load_all_reference_files_if_present() -> None:
    service = CinematographyPromptReferenceService()
    loaded = service.load_cinematography_prompt_references()
    assert "references" in loaded
    assert len(loaded["references"]) >= 6
    assert loaded["missing_files"] == []


def test_load_references_tolerates_missing_files(tmp_path: Path) -> None:
    (tmp_path / "sora_prompt_guide.md").write_text("Shot type, composition, atmosphere", encoding="utf-8")
    service = CinematographyPromptReferenceService(reference_dir=tmp_path)
    loaded = service.load_cinematography_prompt_references()
    assert loaded["references"]
    assert loaded["missing_files"]


def test_extract_lighting_vocabulary() -> None:
    service = CinematographyPromptReferenceService()
    lighting = [item.lower() for item in service.extract_lighting_vocabulary()]
    assert "low-key" in lighting
    assert "high-key" in lighting


def test_extract_camera_motion_vocabulary() -> None:
    service = CinematographyPromptReferenceService()
    motions = [item.lower() for item in service.extract_camera_motion_vocabulary()]
    assert "dolly in" in motions
    assert "tracking" in motions


def test_extract_shot_types() -> None:
    service = CinematographyPromptReferenceService()
    shots = [item.lower() for item in service.extract_shot_type_vocabulary()]
    assert "cu" in shots
    assert "ws" in shots


def test_build_cinematography_guidance_for_scene() -> None:
    service = CinematographyPromptReferenceService()
    guide = service.build_cinematography_guidance_for_script_scene(
        scene_heading="INT. CASA ABANDONADA - NOCHE",
        emotional_intent="suspense oscuro",
        location="CASA ABANDONADA",
        time_of_day="NOCHE",
    )
    assert guide["lighting_style"]
    assert guide["color_palette"]
    assert guide["atmosphere"]


def test_build_visual_prompt_guidance_for_shot() -> None:
    service = CinematographyPromptReferenceService()
    guide = service.build_visual_prompt_guidance_for_shot(
        shot_type="CU",
        action="Marta avanza por el pasillo",
        emotional_intent="suspense",
    )
    assert guide["camera_motion"]
    assert guide["framing"]
    assert guide["camera_angle"]


def test_storyboard_metadata_includes_cinematography_sources() -> None:
    scene = {
        "scene_number": 9,
        "heading": "INT. CASA ABANDONADA - NOCHE",
        "location": "CASA ABANDONADA",
        "time_of_day": "NOCHE",
        "action_blocks": ["Marta entra en la casa abandonada con una linterna."],
        "characters_detected": ["MARTA"],
    }
    service = StoryboardService()
    shot = service._enrich_storyboard_shot_payload(
        scene=scene,
        shot_payload={"shot_type": "MS", "description": "Marta avanza", "metadata_json": {}},
        sequence_for_scene=None,
        style_preset="cinematic_realistic",
        shot_order=1,
    )
    meta = shot["metadata_json"]
    assert meta.get("cinematography_reference_sources")
