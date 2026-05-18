from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from services.cinematography_prompt_reference_service import cinematography_prompt_reference_service


REFERENCE_FILES = {
    "maestro_rules": "comfyui_maestro_pro_juan_carlos.md",
    "wan22_template": "wan22_prompt_template.md",
    "wan22_t2v_director": "wan22_t2v_prompt_director.md",
    "wan22_template_numbered": "01_wan22_prompt_template.md",
    "camera_motion_dictionary": "camera_motion_dictionary.md",
    "camera_motion_dictionary_numbered": "02_camera_motion_dictionary.md",
    "negative_prompt_library": "negative_prompt_library.md",
    "negative_prompt_library_numbered": "03_negative_prompt_library.md",
    "eval_suite": "04_eval_suite.md",
    "loader": "prompt_reference_loader.md",
}


class StoryboardPromptReferenceService:
    def __init__(self, reference_dir: Optional[Path] = None) -> None:
        self.reference_dir = reference_dir or Path(__file__).resolve().parents[2] / "directivas" / "prompt_references"

    def load_prompt_references(self) -> dict[str, Any]:
        references: dict[str, dict[str, str]] = {}
        missing_files: list[str] = []
        for key, filename in REFERENCE_FILES.items():
            file_path = self.reference_dir / filename
            if file_path.is_file():
                references[key] = {
                    "path": str(file_path),
                    "content": file_path.read_text(encoding="utf-8"),
                }
            else:
                missing_files.append(filename)
        return {
            "reference_dir": str(self.reference_dir),
            "references": references,
            "missing_files": missing_files,
            "negative_library": self._parse_negative_prompt_library(
                references.get("negative_prompt_library", {}).get("content", "")
                or references.get("negative_prompt_library_numbered", {}).get("content", "")
            ),
        }

    def load_wan22_prompt_director_reference(self) -> dict[str, Any]:
        loaded = self.load_prompt_references()
        director_reference = loaded["references"].get("wan22_t2v_director")
        template_reference = loaded["references"].get("wan22_template_numbered") or loaded["references"].get("wan22_template")
        camera_reference = loaded["references"].get("camera_motion_dictionary_numbered") or loaded["references"].get("camera_motion_dictionary")
        eval_reference = loaded["references"].get("eval_suite")
        return {
            "director": director_reference,
            "template": template_reference,
            "camera": camera_reference,
            "eval_suite": eval_reference,
            "missing_files": loaded["missing_files"],
        }

    def build_storyboard_positive_prompt(
        self,
        *,
        shot_type: str,
        main_character: str,
        action: str,
        location: str,
        time_of_day: str,
        emotional_intent: str,
        camera_motion: str,
        lighting_style: str,
        lens_style: str,
        background_details: str,
        continuity_constraints: list[str],
        style_preset: str,
        scene_heading: str,
        shot_objective: str,
        script_excerpt_used: str,
    ) -> str:
        parts = [
            "cinematic storyboard frame",
            shot_type,
            main_character,
            action,
            f"exact location: {location}",
            f"time and atmosphere: {time_of_day}, {emotional_intent}",
            f"camera: {camera_motion}",
            f"lighting: {lighting_style}",
            f"lens/look: {lens_style}",
            f"background details from script: {background_details}",
            f"scene heading: {scene_heading}",
            f"shot objective: {shot_objective}",
            f"script excerpt: {script_excerpt_used}" if script_excerpt_used else "",
            f"consistent visual style: {style_preset.replace('_', ' ')}",
            "continuity constraints: " + ", ".join(self._dedupe_text(continuity_constraints)) if continuity_constraints else "",
            "avoid elements not present in the script",
        ]
        return ". ".join(part for part in parts if part)

    def build_storyboard_negative_prompt(
        self,
        *,
        level: str = "strict",
        include_modules: Optional[list[str]] = None,
        base_negative: str | None = None,
    ) -> str:
        loaded = self.load_prompt_references()["negative_library"]
        level_key = f"{level.strip().lower()}_negative"
        prompt_parts = [loaded.get(level_key) or loaded.get("strict_negative") or ""]
        if base_negative:
            prompt_parts.insert(0, base_negative)
        modules = include_modules or ["jitter", "identity_drift", "hands", "text", "exposure"]
        for module in modules:
            module_key = f"module_{module.strip().lower()}"
            prompt_parts.append(loaded.get(module_key, ""))
        return ", ".join(self._dedupe_text(prompt_parts))

    def build_wan22_t2v_positive_prompt(
        self,
        *,
        main_character: str,
        action: str,
        location: str,
        time_of_day: str,
        emotional_intent: str,
        camera_motion: str,
        lighting_style: str,
        lens_style: str,
        background_details: str,
        continuity_constraints: list[str],
        shot_type: str = "MS",
        scene_heading: str = "",
        shot_objective: str = "",
        script_excerpt_used: str = "",
        model_family: str = "wan22",
        single_continuous_take: bool = True,
    ) -> str:
        limited_motion = self._limit_camera_motion(camera_motion)
        constraints = self._dedupe_text(
            continuity_constraints
            + ["stable identity", "consistent outfit", "no text", "no watermark"]
        )
        parts = [
            "cinematic storyboard frame",
            f"model family: {model_family}",
            shot_type,
            main_character,
            action,
            f"exact location: {location}",
            f"time and atmosphere: {time_of_day}, {emotional_intent}",
            f"camera: {limited_motion}",
            "single continuous take, no cuts" if single_continuous_take else "",
            f"lighting: {lighting_style}",
            f"lens/look: {lens_style}",
            f"background details from script: {background_details}",
            f"scene heading: {scene_heading}" if scene_heading else "",
            f"shot objective: {shot_objective}" if shot_objective else "",
            f"script excerpt: {script_excerpt_used}" if script_excerpt_used else "",
            "continuity constraints: " + ", ".join(constraints),
        ]
        return ". ".join(part for part in parts if part)

    def build_wan22_t2v_negative_prompt(
        self,
        *,
        strict: bool = False,
        include_modules: Optional[list[str]] = None,
        base_negative: str | None = None,
    ) -> str:
        level = "strict" if strict else "base"
        modules = include_modules or ["jitter", "identity_drift", "hands", "text", "exposure"]
        return self.build_storyboard_negative_prompt(
            level=level,
            include_modules=modules,
            base_negative=base_negative,
        )

    def build_wan22_t2v_prompt_package(
        self,
        *,
        main_character: str,
        character_continuity: Optional[list[str]] = None,
        action: str,
        location: str,
        time_of_day: str,
        emotional_intent: str,
        camera_motion: str,
        lighting_style: str,
        lens_style: str,
        background_details: str,
        continuity_constraints: list[str],
        visual_constraints: list[str],
        shot_type: str = "MS",
        scene_heading: str = "",
        shot_objective: str = "",
        script_excerpt_used: str = "",
        model_family: str = "wan22",
        strict_negative: bool = False,
        diagnostic_rules_applied: Optional[list[str]] = None,
        shot_plan: Optional[dict[str, Any]] = None,
        single_continuous_take: bool = True,
    ) -> dict[str, Any]:
        positive_prompt = self.build_wan22_t2v_positive_prompt(
            main_character=main_character,
            action=action,
            location=location,
            time_of_day=time_of_day,
            emotional_intent=emotional_intent,
            camera_motion=camera_motion,
            lighting_style=lighting_style,
            lens_style=lens_style,
            background_details=background_details,
            continuity_constraints=continuity_constraints,
            shot_type=shot_type,
            scene_heading=scene_heading,
            shot_objective=shot_objective,
            script_excerpt_used=script_excerpt_used,
            model_family=model_family,
            single_continuous_take=single_continuous_take,
        )
        negative_prompt = self.build_wan22_t2v_negative_prompt(strict=strict_negative)
        metadata = self.build_shot_prompt_metadata(
            script_excerpt_used=script_excerpt_used,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            character_continuity=character_continuity or [main_character],
            location_continuity={"location": location, "time_of_day": time_of_day},
            camera_motion=self._limit_camera_motion(camera_motion),
            lighting_style=lighting_style,
            lens_style=lens_style,
            visual_constraints=visual_constraints,
            visual_continuity={
                "anchors": self._dedupe_text([location, time_of_day, background_details]),
                "continuous_take": single_continuous_take,
            },
            scene_heading=scene_heading,
            emotional_intent=emotional_intent,
            shot_objective=shot_objective,
            prompt_model_family=model_family,
            consistency_checklist=self._dedupe_text([
                "1 subject principal",
                "1 action principal",
                "1 localizacion",
                "1 momento del dia",
                "1-2 movimientos de camara maximo",
                "stable identity",
                "consistent outfit",
                "no text",
                "no watermark",
            ]),
            shot_plan=shot_plan or {},
            diagnostic_rules_applied=diagnostic_rules_applied or ["wan22_t2v_prompt_director"],
            shot_type=shot_type,
        )
        return {
            "prompt_model_family": model_family,
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "metadata": metadata,
        }

    def build_shot_prompt_metadata(
        self,
        *,
        script_excerpt_used: str,
        positive_prompt: str,
        negative_prompt: str,
        character_continuity: list[str],
        location_continuity: dict[str, Any],
        camera_motion: str,
        lighting_style: str,
        lens_style: str,
        visual_constraints: list[str],
        visual_continuity: dict[str, Any],
        scene_heading: str,
        emotional_intent: str,
        shot_objective: str,
        prompt_model_family: str = "wan22",
        consistency_checklist: Optional[list[str]] = None,
        shot_plan: Optional[dict[str, Any]] = None,
        diagnostic_rules_applied: Optional[list[str]] = None,
        cinematography_reference_sources: Optional[list[str]] = None,
        shot_type: str = "",
        framing: str = "",
        camera_angle: str = "",
        lens_suggestion: str = "",
        color_palette: str = "",
        color_grading: str = "",
        atmosphere: str = "",
        composition_notes: str = "",
        model_specific_guidance: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        loaded = self.load_prompt_references()
        cinematography_loaded = cinematography_prompt_reference_service.load_cinematography_prompt_references()
        prompt_reference_sources = [
            value["path"]
            for value in loaded["references"].values()
        ]
        resolved_cinematography_sources = cinematography_reference_sources or [
            value["path"]
            for value in cinematography_loaded["references"].values()
        ]
        return {
            "script_excerpt_used": script_excerpt_used,
            "prompt_model_family": prompt_model_family,
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "prompt_reference_sources": prompt_reference_sources,
            "character_continuity": character_continuity,
            "location_continuity": location_continuity,
            "camera_motion": camera_motion,
            "lighting_style": lighting_style,
            "lens_style": lens_style,
            "consistency_checklist": consistency_checklist or [],
            "shot_plan": shot_plan or {},
            "visual_constraints": visual_constraints,
            "visual_continuity": visual_continuity,
            "scene_heading": scene_heading,
            "emotional_intent": emotional_intent,
            "shot_objective": shot_objective,
            "diagnostic_rules_applied": diagnostic_rules_applied or [],
            "cinematography_reference_sources": resolved_cinematography_sources,
            "shot_type": shot_type,
            "framing": framing,
            "camera_angle": camera_angle,
            "lens_suggestion": lens_suggestion,
            "color_palette": color_palette,
            "color_grading": color_grading,
            "atmosphere": atmosphere,
            "composition_notes": composition_notes,
            "model_specific_guidance": model_specific_guidance or {},
        }

    def _parse_negative_prompt_library(self, content: str) -> dict[str, str]:
        parsed: dict[str, str] = {}
        for line in content.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            normalized_key = key.strip().lower()
            if normalized_key in {
                "base_negative",
                "light_negative",
                "strict_negative",
                "module_jitter",
                "module_identity_drift",
                "module_hands",
                "module_text",
                "module_exposure",
            }:
                parsed[normalized_key] = value.strip()
        return parsed

    def _dedupe_text(self, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for value in values:
            text = str(value or "").strip()
            if not text:
                continue
            key = text.lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned.append(text)
        return cleaned

    def _limit_camera_motion(self, camera_motion: str) -> str:
        chunks = [chunk.strip() for chunk in str(camera_motion or "").replace("/", ",").split(",") if chunk.strip()]
        if not chunks:
            return "locked frame"
        return ", ".join(chunks[:2])


storyboard_prompt_reference_service = StoryboardPromptReferenceService()


def load_prompt_references() -> dict[str, Any]:
    return storyboard_prompt_reference_service.load_prompt_references()


def load_wan22_prompt_director_reference() -> dict[str, Any]:
    return storyboard_prompt_reference_service.load_wan22_prompt_director_reference()


def build_storyboard_positive_prompt(**kwargs: Any) -> str:
    return storyboard_prompt_reference_service.build_storyboard_positive_prompt(**kwargs)


def build_storyboard_negative_prompt(**kwargs: Any) -> str:
    return storyboard_prompt_reference_service.build_storyboard_negative_prompt(**kwargs)


def build_wan22_t2v_positive_prompt(**kwargs: Any) -> str:
    return storyboard_prompt_reference_service.build_wan22_t2v_positive_prompt(**kwargs)


def build_wan22_t2v_negative_prompt(**kwargs: Any) -> str:
    return storyboard_prompt_reference_service.build_wan22_t2v_negative_prompt(**kwargs)


def build_wan22_t2v_prompt_package(**kwargs: Any) -> dict[str, Any]:
    return storyboard_prompt_reference_service.build_wan22_t2v_prompt_package(**kwargs)


def build_shot_prompt_metadata(**kwargs: Any) -> dict[str, Any]:
    return storyboard_prompt_reference_service.build_shot_prompt_metadata(**kwargs)
