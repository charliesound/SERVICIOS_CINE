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

from services.storyboard_prompt_reference_service import StoryboardPromptReferenceService  # noqa: E402


def test_load_prompt_references_from_default_directory() -> None:
    service = StoryboardPromptReferenceService()

    loaded = service.load_prompt_references()

    assert loaded["references"]
    assert "maestro_rules" in loaded["references"]
    assert "negative_prompt_library" in loaded["references"]
    assert "wan22_t2v_director" in loaded["references"]
    assert loaded["missing_files"] == []


def test_load_wan22_prompt_director_reference() -> None:
    service = StoryboardPromptReferenceService()

    loaded = service.load_wan22_prompt_director_reference()

    assert loaded["director"] is not None
    assert loaded["template"] is not None
    assert loaded["camera"] is not None


def test_load_prompt_references_tolerates_missing_files(tmp_path: Path) -> None:
    (tmp_path / "negative_prompt_library.md").write_text("STRICT_NEGATIVE: blurry, text, watermark\n", encoding="utf-8")
    service = StoryboardPromptReferenceService(reference_dir=tmp_path)

    loaded = service.load_prompt_references()

    assert loaded["references"]
    assert loaded["missing_files"]
    assert "comfyui_maestro_pro_juan_carlos.md" in loaded["missing_files"]


def test_build_storyboard_positive_prompt_contains_core_fields() -> None:
    service = StoryboardPromptReferenceService()

    positive = service.build_storyboard_positive_prompt(
        shot_type="MS",
        main_character="Marta",
        action="Marta entra en la casa abandonada con una linterna",
        location="casa abandonada",
        time_of_day="noche",
        emotional_intent="suspense oscuro",
        camera_motion="handheld subtle",
        lighting_style="low-key flashlight lighting",
        lens_style="50mm cinematic prime",
        background_details="pared desconchada, sombra larga, polvo en el aire",
        continuity_constraints=["stable identity", "consistent outfit"],
        style_preset="cinematic_realistic",
        scene_heading="INT. CASA ABANDONADA - NOCHE",
        shot_objective="explorar el pasillo",
        script_excerpt_used="Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
    )

    lowered = positive.lower()
    assert "marta" in lowered
    assert "casa abandonada" in lowered
    assert "noche" in lowered
    assert "linterna" in lowered
    assert "cinematic storyboard frame" in lowered


def test_build_storyboard_negative_prompt_contains_required_modules() -> None:
    service = StoryboardPromptReferenceService()

    negative = service.build_storyboard_negative_prompt(level="strict")

    lowered = negative.lower()
    assert "text" in lowered
    assert "watermark" in lowered
    assert "jitter" in lowered
    assert "deformed hands" in lowered


def test_build_wan22_t2v_positive_prompt_respects_structure_and_motion_limit() -> None:
    service = StoryboardPromptReferenceService()

    positive = service.build_wan22_t2v_positive_prompt(
        main_character="Marta",
        action="Marta entra en la casa abandonada con una linterna",
        location="casa abandonada",
        time_of_day="noche",
        emotional_intent="suspense oscuro",
        camera_motion="dolly in, pan left, tilt up",
        lighting_style="low-key flashlight lighting",
        lens_style="50mm cinematic prime",
        background_details="pared desconchada, sombra larga",
        continuity_constraints=["stable identity", "consistent outfit"],
        shot_type="MS",
        scene_heading="INT. CASA ABANDONADA - NOCHE",
        shot_objective="explorar el pasillo",
        script_excerpt_used="Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
        model_family="wan22",
    )

    lowered = positive.lower()
    assert "marta" in lowered
    assert "casa abandonada" in lowered
    assert "noche" in lowered
    assert "single continuous take" in lowered
    assert "dolly in, pan left" in lowered
    assert "tilt up" not in lowered


def test_build_wan22_t2v_negative_prompt_contains_required_modules() -> None:
    service = StoryboardPromptReferenceService()

    negative = service.build_wan22_t2v_negative_prompt(strict=False)

    lowered = negative.lower()
    assert "text" in lowered
    assert "watermark" in lowered
    assert "jitter" in lowered
    assert "deformed hands" in lowered


def test_build_wan22_t2v_prompt_package_supports_multiple_model_families() -> None:
    service = StoryboardPromptReferenceService()

    for model_family in ("wan22", "kandinsky5", "hunyuan"):
        package = service.build_wan22_t2v_prompt_package(
            main_character="Marta",
            action="Marta entra en la casa abandonada con una linterna",
            location="casa abandonada",
            time_of_day="noche",
            emotional_intent="suspense oscuro",
            camera_motion="handheld subtle",
            lighting_style="low-key flashlight lighting",
            lens_style="50mm cinematic prime",
            background_details="pared desconchada, sombra larga",
            continuity_constraints=["stable identity", "consistent outfit"],
            visual_constraints=["no text", "no watermark"],
            scene_heading="INT. CASA ABANDONADA - NOCHE",
            shot_objective="explorar el pasillo",
            script_excerpt_used="Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
            model_family=model_family,
        )

        assert package["metadata"]["prompt_model_family"] == model_family
        assert package["metadata"]["prompt_reference_sources"]


def test_build_shot_prompt_metadata_contains_positive_prompt_and_sources() -> None:
    service = StoryboardPromptReferenceService()

    metadata = service.build_shot_prompt_metadata(
        script_excerpt_used="Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
        positive_prompt="cinematic storyboard frame. Marta enters the abandoned house with a flashlight.",
        negative_prompt="text, watermark, jitter, deformed hands",
        character_continuity=["MARTA"],
        location_continuity={"location": "CASA ABANDONADA", "time_of_day": "NOCHE", "sequence_id": "seq_01"},
        camera_motion="handheld subtle",
        lighting_style="low-key flashlight lighting",
        lens_style="50mm cinematic prime",
        visual_constraints=["stable identity", "consistent outfit", "no text", "no watermark"],
        visual_continuity={"anchors": ["linterna", "sombra larga"], "continuity_phrase": "same location and props"},
        scene_heading="INT. CASA ABANDONADA - NOCHE",
        emotional_intent="suspense oscuro",
        shot_objective="explorar el pasillo",
    )

    assert metadata["positive_prompt"]
    assert metadata["prompt_reference_sources"]
    assert any(source.endswith("negative_prompt_library.md") for source in metadata["prompt_reference_sources"])
