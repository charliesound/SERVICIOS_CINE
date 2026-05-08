from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.cid_script_to_prompt_schema import CinematicIntent, PromptSpec  # noqa: E402
from services.cid_script_scene_parser_service import cid_script_scene_parser_service  # noqa: E402
from services.cinematic_intent_service import cinematic_intent_service  # noqa: E402
from services.cid_script_to_prompt_pipeline_service import run_script_to_prompt_pipeline  # noqa: E402
from services.prompt_construction_service import prompt_construction_service  # noqa: E402
from services.semantic_prompt_validation_service import semantic_prompt_validation_service  # noqa: E402


SAMPLE_SCRIPT = """1 INT. SALA DE REUNIONES. NOCHE.
Una directora revisa un storyboard sobre una mesa llena de notas. El productor espera una decision.
DIRECTORA
Necesito ver si esta escena respira.
PRODUCTOR
Entonces generemos otra version."""


def test_parser_detects_meeting_room_scene() -> None:
    sequences, scenes, warnings = cid_script_scene_parser_service.parse_script(SAMPLE_SCRIPT)
    assert not warnings or "regex_scene_detection_failed_using_fallback" not in warnings
    assert sequences
    assert scenes
    scene = scenes[0]
    assert scene.heading.startswith("1 INT. SALA DE REUNIONES")
    assert scene.int_ext == "INT"
    assert scene.time_of_day == "NOCHE"


def test_cinematic_intent_has_no_critical_empty_fields() -> None:
    _sequences, scenes, _warnings = cid_script_scene_parser_service.parse_script(SAMPLE_SCRIPT)
    scene = scenes[0]
    intent = cinematic_intent_service.build_intent(scene, "storyboard_frame", continuity_anchors=scene.visual_anchors)
    assert intent.subject
    assert intent.action
    assert intent.environment
    assert intent.lighting
    assert intent.composition
    assert intent.directorial_intent is not None
    assert intent.director_lens_id
    assert intent.montage_intent is not None
    assert intent.editorial_beats
    assert intent.shot_editorial_purpose is not None


def test_prompt_construction_contains_subject_action_environment() -> None:
    intent = CinematicIntent(
        intent_id="intent_scene_001_storyboard_frame",
        scene_id="scene_001",
        output_type="storyboard_frame",
        subject="storyboard panels for the scene",
        action="mapping the scene into readable shot panels with camera logic",
        environment="int sala de reuniones at noche",
        dramatic_intent="support a moment of evaluation and narrative decision",
        framing="multi-panel previs layout",
        shot_size="wide board view",
        camera_angle="slight overhead",
        lens="35mm",
        lighting="clear editorial tabletop lighting with readable documents",
        color_palette="charcoal, amber and soft white",
        composition="horizontal multi-panel layout with clear continuity flow",
        movement=None,
        mood="contained tension",
        director_lens_id="adaptive_auteur_fusion",
        directorial_intent=None,
        continuity_anchors=["location:sala de reuniones"],
        required_elements=["multiple panels", "camera marks"],
        forbidden_elements=["single hero frame"],
    )
    prompt = prompt_construction_service.build_prompt_spec(intent)
    positive = prompt.positive_prompt.lower()
    assert intent.subject.lower() in positive
    assert intent.action.lower() in positive
    assert intent.environment.lower() in positive


def test_semantic_prompt_validation_blocks_generic_prompt() -> None:
    intent = CinematicIntent(
        intent_id="intent_scene_001_storyboard_frame",
        scene_id="scene_001",
        output_type="storyboard_frame",
        subject="storyboard panels for the scene",
        action="mapping the scene into readable shot panels with camera logic",
        environment="int sala de reuniones at noche",
        dramatic_intent="support a moment of evaluation and narrative decision",
        framing="multi-panel previs layout",
        shot_size="wide board view",
        camera_angle="slight overhead",
        lens="35mm",
        lighting="clear editorial tabletop lighting with readable documents",
        color_palette="charcoal, amber and soft white",
        composition="horizontal multi-panel layout with clear continuity flow",
        movement=None,
        mood="contained tension",
        director_lens_id="adaptive_auteur_fusion",
        directorial_intent=None,
        continuity_anchors=["location:sala de reuniones"],
        required_elements=["multiple panels", "camera marks"],
        forbidden_elements=["single hero frame"],
    )
    prompt = PromptSpec(
        prompt_id="prompt_scene_001_storyboard_frame",
        scene_id="scene_001",
        output_type="storyboard_frame",
        positive_prompt="cinematic image, beautiful shot, dramatic scene",
        negative_prompt="",
        model_hint="flux_or_sdxl",
        width=1536,
        height=864,
        seed_hint=None,
        continuity_anchors=[],
        semantic_anchors=[],
        validation_status="pending",
        validation_errors=[],
    )
    result = semantic_prompt_validation_service.validate(prompt, intent)
    assert result.is_valid is False
    assert result.score < 0.6
    assert result.ambiguous_terms


def test_pipeline_returns_completed_status() -> None:
    response = asyncio.run(
        run_script_to_prompt_pipeline(
            script_text=SAMPLE_SCRIPT,
            output_type="storyboard_frame",
            max_scenes=5,
            scene_numbers=None,
            style_preset="premium_cinematic_saas",
            use_llm=False,
        )
    )
    assert response.status == "completed"
    assert response.scenes
    assert response.intents
    assert response.prompts
    assert response.intents[0].directorial_intent is not None
    assert response.intents[0].montage_intent is not None
    assert response.intents[0].editorial_beats
    assert response.prompts[0].editorial_purpose is not None
    assert "in the style of" not in response.prompts[0].positive_prompt.lower()
    assert "mise en scene:" in response.prompts[0].positive_prompt.lower()
    assert "blocking:" in response.prompts[0].positive_prompt.lower()
    assert "editorial function:" in response.prompts[0].positive_prompt.lower()
    assert "cut reason:" in response.prompts[0].positive_prompt.lower()


def test_semantic_validator_penalizes_missing_editorial_function() -> None:
    intent = CinematicIntent(
        intent_id="intent_scene_001_storyboard_frame",
        scene_id="scene_001",
        output_type="storyboard_frame",
        subject="storyboard panels for the scene",
        action="mapping the scene into readable shot panels with camera logic",
        environment="int sala de reuniones at noche",
        dramatic_intent="support a moment of evaluation and narrative decision",
        framing="multi-panel previs layout",
        shot_size="wide board view",
        camera_angle="slight overhead",
        lens="35mm",
        lighting="clear editorial tabletop lighting with readable documents",
        color_palette="charcoal, amber and soft white",
        composition="horizontal multi-panel layout with clear continuity flow",
        movement=None,
        mood="contained tension",
        director_lens_id="adaptive_auteur_fusion",
        directorial_intent=None,
        montage_intent=None,
        editorial_beats=[],
        shot_editorial_purpose=None,
        continuity_anchors=["location:sala de reuniones"],
        required_elements=["multiple panels", "camera marks"],
        forbidden_elements=["single hero frame"],
    )
    prompt = PromptSpec(
        prompt_id="prompt_scene_001_storyboard_frame",
        scene_id="scene_001",
        output_type="storyboard_frame",
        positive_prompt="subject: storyboard panels for the scene, action: mapping the scene into readable shot panels with camera logic, environment: int sala de reuniones at noche",
        negative_prompt="generic sci-fi interface",
        model_hint="flux_or_sdxl",
        width=1536,
        height=864,
        seed_hint=None,
        continuity_anchors=["location:sala de reuniones"],
        semantic_anchors=["subject:storyboard panels for the scene", "action:mapping", "environment:int sala de reuniones at noche"],
        editorial_purpose=None,
        montage_intent=None,
        validation_status="pending",
        validation_errors=[],
    )
    result = semantic_prompt_validation_service.validate(prompt, intent)
    assert result.is_valid is False
    assert "editorial_purpose_missing" in result.errors or "editorial_function_not_grounded" in result.errors
