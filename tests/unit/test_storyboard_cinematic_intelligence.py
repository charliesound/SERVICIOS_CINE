from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.cid_script_to_prompt_schema import ScriptScene  # noqa: E402
from services.storyboard_service import StoryboardService  # noqa: E402


SAMPLE_SCENE: dict = {
    "scene_number": 1,
    "heading": "INT. SALA DE REUNIONES. NOCHE",
    "location": "SALA DE REUNIONES",
    "time_of_day": "NOCHE",
    "action_blocks": [
        "Una directora revisa un storyboard sobre una mesa llena de notas.",
        "El productor espera una decision.",
    ],
    "characters_detected": ["DIRECTORA", "PRODUCTOR"],
    "props": ["storyboard", "notas", "mesa"],
    "dramatic_objective": "evaluar el ritmo narrativo",
    "conflict": "tension creativa vs presion de produccion",
    "emotional_tone": "tension contenida",
    "visual_anchors": ["storyboard", "mesa central"],
}

MINIMAL_SCENE: dict = {
    "scene_number": 5,
    "heading": "EXT. PLAZA. DIA",
    "action_blocks": ["Gente cruza la plaza. Un vendedor grita."],
}

EMPTY_SCENE: dict = {}

SCRIPT_FAITHFUL_SCENE: dict = {
    "scene_number": 9,
    "heading": "INT. CASA ABANDONADA - NOCHE",
    "location": "CASA ABANDONADA",
    "time_of_day": "NOCHE",
    "action_blocks": [
        "Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
        "La sombra de Marta tiembla sobre la pared mientras escucha un ruido fuera de cuadro.",
    ],
    "characters_detected": ["MARTA"],
    "props": ["linterna"],
    "visual_anchors": ["sombra larga", "pared desconchada"],
    "dramatic_objective": "avanzar con cautela hacia el origen del ruido",
    "emotional_tone": "suspense oscuro",
}


class TestSceneDictToScriptScene:
    def test_full_scene_dict(self) -> None:
        service = StoryboardService()
        script_scene = service._scene_dict_to_script_scene(SAMPLE_SCENE)
        assert isinstance(script_scene, ScriptScene)
        assert script_scene.scene_number == 1
        assert script_scene.int_ext == "INT"
        assert script_scene.location == "SALA DE REUNIONES"
        assert script_scene.time_of_day == "NOCHE"
        assert "DIRECTORA" in script_scene.characters
        assert script_scene.dramatic_objective == "evaluar el ritmo narrativo"

    def test_minimal_scene_dict(self) -> None:
        service = StoryboardService()
        script_scene = service._scene_dict_to_script_scene(MINIMAL_SCENE)
        assert isinstance(script_scene, ScriptScene)
        assert script_scene.scene_number == 5
        assert script_scene.int_ext == "EXT"
        assert script_scene.location is None
        assert script_scene.characters == []

    def test_empty_scene_dict(self) -> None:
        service = StoryboardService()
        script_scene = service._scene_dict_to_script_scene(EMPTY_SCENE)
        assert isinstance(script_scene, ScriptScene)
        assert script_scene.scene_number == 0
        assert script_scene.location is None


class TestBuildCinematicStoryboardShot:
    def test_default_params(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=3,
            style_preset="cinematic_realistic",
        )
        assert len(shots) == 3
        for shot in shots:
            assert "shot_type" in shot
            assert "description" in shot
            assert "positive_prompt" in shot
            assert "negative_prompt" in shot
            assert "metadata_json" in shot
            meta = shot["metadata_json"]
            assert "directorial_intent" in meta
            assert "montage_intent" in meta
            assert "shot_editorial_purpose" in meta
            assert "cinematic_intent_id" in meta
            assert "prompt_spec" in meta
            assert meta.get("director_lens_id") is not None

    def test_shots_per_scene(self) -> None:
        service = StoryboardService()
        for count in (1, 4, 6):
            shots = service._build_cinematic_storyboard_shot(
                SAMPLE_SCENE,
                shots_per_scene=count,
                style_preset="graphic_novel",
            )
            assert len(shots) == count, f"Expected {count} shots, got {len(shots)}"

    def test_with_validation_enabled(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=2,
            style_preset="cinematic_realistic",
            validate_prompts=True,
        )
        for shot in shots:
            meta = shot["metadata_json"]
            assert "validation" in meta
            assert meta["validation"] is not None
            assert "is_valid" in meta["validation"]

    def test_without_validation(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=2,
            style_preset="cinematic_realistic",
            validate_prompts=False,
        )
        for shot in shots:
            meta = shot["metadata_json"]
            assert meta.get("validation") is None

    def test_with_montage_intelligence(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=3,
            style_preset="cinematic_realistic",
            use_montage_intelligence=True,
        )
        for shot in shots:
            meta = shot["metadata_json"]
            shot_editorial = meta.get("shot_editorial_purpose")
            assert shot_editorial is not None
            if shot_editorial:
                assert "cut_reason" in shot_editorial
                assert "purpose" in shot_editorial

    def test_with_specific_director_lens(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=1,
            style_preset="cinematic_realistic",
            director_lens_id="epic_moral_landscape",
        )
        meta = shots[0]["metadata_json"]
        assert meta.get("director_lens_id") == "epic_moral_landscape"

    def test_with_specific_montage_profile(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=1,
            style_preset="cinematic_realistic",
            montage_profile_id="suspense_information_control",
        )
        meta = shots[0]["metadata_json"]
        montage = meta.get("montage_intent")
        assert montage is not None
        assert "editorial_function" in montage

    def test_forbidden_style_reference_not_in_prompt(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=1,
            style_preset="cinematic_realistic",
        )
        positive = shots[0]["positive_prompt"].lower()
        assert "in the style of" not in positive

    def test_minimal_scene_produces_valid_output(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            MINIMAL_SCENE,
            shots_per_scene=2,
            style_preset="moody_noir",
        )
        assert len(shots) == 2
        for shot in shots:
            assert shot["positive_prompt"]
            assert shot["negative_prompt"]

    def test_json_serializable(self) -> None:
        service = StoryboardService()
        shots = service._build_cinematic_storyboard_shot(
            SAMPLE_SCENE,
            shots_per_scene=2,
            style_preset="cinematic_realistic",
            validate_prompts=True,
        )
        dumped = json.dumps(shots, ensure_ascii=False, default=str)
        reloaded = json.loads(dumped)
        assert len(reloaded) == 2

    def test_script_faithful_metadata_contains_enriched_prompt_fields(self) -> None:
        service = StoryboardService()
        shot = service._enrich_storyboard_shot_payload(
            scene=SCRIPT_FAITHFUL_SCENE,
            shot_payload=service._build_cinematic_storyboard_shot(
                SCRIPT_FAITHFUL_SCENE,
                shots_per_scene=1,
                style_preset="cinematic_realistic",
            )[0],
            sequence_for_scene=None,
            style_preset="cinematic_realistic",
            shot_order=1,
        )

        meta = shot["metadata_json"]
        assert meta["script_excerpt_used"]
        assert meta["positive_prompt"]
        assert meta["negative_prompt"]
        assert meta["character_continuity"] == ["MARTA"]
        assert meta["location_continuity"]["location"] == "CASA ABANDONADA"
        assert meta["scene_heading"] == "INT. CASA ABANDONADA - NOCHE"
        assert meta["emotional_intent"]
        assert meta["shot_objective"]
        assert "validation_result" in meta
        assert "validation_score" in meta
        assert "suggested_regeneration_prompt" in meta

    def test_script_faithful_positive_prompt_mentions_core_story_elements(self) -> None:
        service = StoryboardService()
        shot = service._enrich_storyboard_shot_payload(
            scene=SCRIPT_FAITHFUL_SCENE,
            shot_payload={
                "shot_type": "MS",
                "description": "Marta avanza con la linterna por el pasillo de la casa abandonada.",
                "negative_prompt": "",
                "metadata_json": {},
            },
            sequence_for_scene=None,
            style_preset="cinematic_realistic",
            shot_order=1,
        )

        positive = shot["positive_prompt"].lower()
        assert "marta" in positive
        assert "linterna" in positive
        assert "casa abandonada" in positive
        assert "noche" in positive


class TestStoryboardGenerateRequestSchema:
    def test_new_fields_defaults(self) -> None:
        from schemas.storyboard_schema import StoryboardGenerateRequest

        req = StoryboardGenerateRequest()
        assert req.director_lens_id is None
        assert req.montage_profile_id is None
        assert req.use_cinematic_intelligence is False
        assert req.include_coverage_shots is True
        assert req.use_montage_intelligence is False
        assert req.validate_prompts is False

    def test_new_fields_custom_values(self) -> None:
        from schemas.storyboard_schema import StoryboardGenerateRequest

        req = StoryboardGenerateRequest(
            director_lens_id="adaptive_auteur_fusion",
            montage_profile_id="adaptive_montage",
            use_cinematic_intelligence=True,
            include_coverage_shots=False,
            use_montage_intelligence=True,
            validate_prompts=True,
        )
        assert req.director_lens_id == "adaptive_auteur_fusion"
        assert req.montage_profile_id == "adaptive_montage"
        assert req.use_cinematic_intelligence is True
        assert req.include_coverage_shots is False
        assert req.use_montage_intelligence is True
        assert req.validate_prompts is True


class TestCoveragePlan:
    def test_dialogue_scene_generates_reaction_and_look_coverage(self) -> None:
        service = StoryboardService()
        shots = service.build_cinematic_coverage_plan(
            scene=SAMPLE_SCENE,
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        roles = {shot.get("metadata_json", {}).get("shot_role") for shot in shots}
        assert "reaction" in roles
        assert "look" in roles

    def test_object_scene_generates_insert_shot(self) -> None:
        service = StoryboardService()
        scene = dict(SAMPLE_SCENE)
        scene["action_blocks"] = ["Abre la carpeta y muestra el documento firmado."]
        shots = service.build_cinematic_coverage_plan(
            scene=scene,
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        roles = {shot.get("metadata_json", {}).get("shot_role") for shot in shots}
        assert "insert" in roles

    def test_transition_scene_generates_transition_shot(self) -> None:
        service = StoryboardService()
        scene = {
            "scene_number": 4,
            "heading": "INT. PASILLO - DÍA",
            "location": "PASILLO",
            "action_blocks": ["Entra corriendo y sale hacia la puerta."],
        }
        shots = service.build_cinematic_coverage_plan(
            scene=scene,
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        roles = {shot.get("metadata_json", {}).get("shot_role") for shot in shots}
        assert "transition" in roles

    def test_every_coverage_shot_has_narrative_reason(self) -> None:
        service = StoryboardService()
        shots = service.build_cinematic_coverage_plan(
            scene=SAMPLE_SCENE,
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        assert shots
        for shot in shots:
            meta = shot.get("metadata_json") or {}
            assert meta.get("narrative_reason")
            assert meta.get("is_coverage_shot") is True
            assert meta.get("shot_role")

    def test_prompts_keep_hand_drawn_non_photoreal_language(self) -> None:
        service = StoryboardService()
        shots = service.build_cinematic_coverage_plan(
            scene=SAMPLE_SCENE,
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        assert shots
        for shot in shots:
            positive = str(shot.get("positive_prompt") or "").lower()
            negative = str(shot.get("negative_prompt") or "").lower()
            assert "hand-drawn" in positive or "monochrome" in positive
            assert "photograph" in negative or "realistic skin" in negative

    def test_no_generic_coverage_when_scene_has_no_narrative_signal(self) -> None:
        service = StoryboardService()
        shots = service.build_cinematic_coverage_plan(
            scene={"scene_number": 8, "heading": "INT. VACIO"},
            sequence_context=None,
            style_preset="hand_drawn_storyboard",
        )
        assert shots == []


class TestStoryboardShotMetadata:
    def test_metadata_field_in_model(self) -> None:
        from models.storyboard import StoryboardShot

        assert hasattr(StoryboardShot, "metadata_json")

    def test_metadata_field_in_response(self) -> None:
        from schemas.shot_schema import StoryboardShotResponse

        fields = StoryboardShotResponse.model_fields
        assert "metadata_json" in fields


class TestStoryboardServiceSignature:
    def test_generate_storyboard_accepts_new_params(self) -> None:
        import inspect

        sig = inspect.signature(StoryboardService.generate_storyboard)
        params = sig.parameters
        assert "director_lens_id" in params
        assert "montage_profile_id" in params
        assert "use_cinematic_intelligence" in params
        assert "use_montage_intelligence" in params
        assert "validate_prompts" in params


class TestStoryboardShotResponseMetadataJson:
    def test_metadata_json_from_dict(self) -> None:
        from schemas.shot_schema import StoryboardShotResponse

        data = {
            "id": "test-id",
            "project_id": "proj-id",
            "organization_id": "org-id",
            "sequence_order": 1,
            "version": 1,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "metadata_json": {"directorial_intent": {"lens": "test"}, "montage_intent": {}, "validation": None},
        }
        resp = StoryboardShotResponse(**data)
        assert isinstance(resp.metadata_json, dict)
        assert resp.metadata_json["directorial_intent"]["lens"] == "test"

    def test_metadata_json_from_string(self) -> None:
        from schemas.shot_schema import StoryboardShotResponse

        data = {
            "id": "test-id",
            "project_id": "proj-id",
            "organization_id": "org-id",
            "sequence_order": 1,
            "version": 1,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "metadata_json": json.dumps({"directorial_intent": {"lens": "test"}, "montage_intent": {}}),
        }
        resp = StoryboardShotResponse(**data)
        assert isinstance(resp.metadata_json, dict)
        assert resp.metadata_json["directorial_intent"]["lens"] == "test"

    def test_metadata_json_null(self) -> None:
        from schemas.shot_schema import StoryboardShotResponse

        data = {
            "id": "test-id",
            "project_id": "proj-id",
            "organization_id": "org-id",
            "sequence_order": 1,
            "version": 1,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "metadata_json": None,
        }
        resp = StoryboardShotResponse(**data)
        assert resp.metadata_json is None

    def test_metadata_json_empty_string(self) -> None:
        from schemas.shot_schema import StoryboardShotResponse

        data = {
            "id": "test-id",
            "project_id": "proj-id",
            "organization_id": "org-id",
            "sequence_order": 1,
            "version": 1,
            "is_active": True,
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-01T00:00:00",
            "metadata_json": "",
        }
        resp = StoryboardShotResponse(**data)
        assert resp.metadata_json == ""  # empty string passes through


class TestDirectorLensValidation:
    def test_valid_director_lens_id(self) -> None:
        from services.director_lens_service import director_lens_service

        profile = director_lens_service.get_profile("adaptive_auteur_fusion")
        assert profile is not None
        assert profile.lens_id == "adaptive_auteur_fusion"

    def test_invalid_director_lens_id_raises_value_error(self) -> None:
        from services.director_lens_service import director_lens_service

        try:
            director_lens_service.get_profile("non_existent_lens")
            assert False, "Expected ValueError"
        except ValueError as e:
            assert "Unknown director lens profile" in str(e)

    def test_all_known_lens_ids(self) -> None:
        from services.director_lens_service import director_lens_service

        profiles = director_lens_service.list_profiles()
        known_ids = {p.lens_id for p in profiles}
        expected = {
            "adaptive_auteur_fusion",
            "wonder_humanist_blocking",
            "suspense_geometric_control",
            "formal_symmetry_control",
            "melodrama_color_identity",
            "surreal_social_disruption",
            "epic_moral_landscape",
            "spiritual_time_pressure",
            "urban_moral_energy",
            "dream_identity_fragment",
        }
        assert known_ids == expected, f"Lens ID mismatch: {known_ids ^ expected}"


class TestMontageProfileValidation:
    def test_valid_montage_profile_ids(self) -> None:
        from services.montage_intelligence_service import montage_intelligence_service

        profiles = montage_intelligence_service.list_profiles()
        valid_ids = {p["profile_id"] for p in profiles}
        assert "adaptive_montage" in valid_ids
        assert "invisible_continuity_editing" in valid_ids

    def test_invalid_montage_profile_id_not_in_list(self) -> None:
        from services.montage_intelligence_service import montage_intelligence_service

        profiles = montage_intelligence_service.list_profiles()
        valid_ids = {p["profile_id"] for p in profiles}
        assert "non_existent_profile" not in valid_ids
        assert "" not in valid_ids
