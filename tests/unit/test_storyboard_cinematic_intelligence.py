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


class TestStoryboardGenerateRequestSchema:
    def test_new_fields_defaults(self) -> None:
        from schemas.storyboard_schema import StoryboardGenerateRequest

        req = StoryboardGenerateRequest()
        assert req.director_lens_id is None
        assert req.montage_profile_id is None
        assert req.use_cinematic_intelligence is False
        assert req.use_montage_intelligence is False
        assert req.validate_prompts is False

    def test_new_fields_custom_values(self) -> None:
        from schemas.storyboard_schema import StoryboardGenerateRequest

        req = StoryboardGenerateRequest(
            director_lens_id="adaptive_auteur_fusion",
            montage_profile_id="adaptive_montage",
            use_cinematic_intelligence=True,
            use_montage_intelligence=True,
            validate_prompts=True,
        )
        assert req.director_lens_id == "adaptive_auteur_fusion"
        assert req.montage_profile_id == "adaptive_montage"
        assert req.use_cinematic_intelligence is True
        assert req.use_montage_intelligence is True
        assert req.validate_prompts is True


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
