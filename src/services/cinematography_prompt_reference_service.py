from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional


REFERENCE_FILES = {
    "kling_26": "kling_26_prompt_guide.md",
    "sora": "sora_prompt_guide.md",
    "openai_4o": "openai_4o_prompt_guide.md",
    "veo_31": "veo_31_prompt_guide.md",
    "adobe_firefly_video": "adobe_firefly_video_prompt_guide.md",
    "midjourney_style": "midjourney_style_guide.md",
}


class CinematographyPromptReferenceService:
    def __init__(self, reference_dir: Optional[Path] = None) -> None:
        self.reference_dir = reference_dir or Path(__file__).resolve().parents[2] / "directivas" / "cinematography_prompt_references"

    def load_cinematography_prompt_references(self) -> dict[str, Any]:
        references: dict[str, dict[str, str]] = {}
        missing_files: list[str] = []
        for key, filename in REFERENCE_FILES.items():
            path = self.reference_dir / filename
            if path.is_file():
                references[key] = {"path": str(path), "content": path.read_text(encoding="utf-8")}
            else:
                missing_files.append(filename)
        return {
            "reference_dir": str(self.reference_dir),
            "references": references,
            "missing_files": missing_files,
        }

    def extract_shot_type_vocabulary(self) -> list[str]:
        return self._extract_keywords(
            [
                "ECU", "CU", "MCU", "MS", "MLS", "WS", "EWS", "OTS", "POV",
                "insert shot", "establishing shot", "reaction shot",
            ]
        )

    def extract_camera_motion_vocabulary(self) -> list[str]:
        return self._extract_keywords(
            [
                "locked frame", "static", "dolly in", "dolly out", "tracking", "pan left", "pan right",
                "tilt up", "tilt down", "crane up", "crane down", "handheld", "push in", "orbit",
            ]
        )

    def extract_lighting_vocabulary(self) -> list[str]:
        return self._extract_keywords(
            [
                "low-key", "high-key", "soft light", "hard light", "motivated lighting",
                "rim light", "backlight", "practical lighting", "volumetric light", "golden hour",
            ]
        )

    def extract_lens_and_camera_vocabulary(self) -> list[str]:
        return self._extract_keywords(
            [
                "24mm", "35mm", "50mm", "85mm", "anamorphic", "spherical", "deep focus",
                "shallow depth of field", "rack focus", "prime lens",
            ]
        )

    def extract_color_grading_vocabulary(self) -> list[str]:
        return self._extract_keywords(
            [
                "teal and orange", "desaturated", "warm grade", "cool grade", "high contrast",
                "low contrast", "film grain", "bleach bypass", "cinematic grade",
            ]
        )

    def build_cinematography_guidance_for_script_scene(self, *, scene_heading: str, emotional_intent: str, location: str, time_of_day: str) -> dict[str, str]:
        tone = emotional_intent.lower()
        if any(token in tone for token in ("tension", "suspense", "oscuro", "thriller")):
            lighting = "low-key motivated practical lighting"
            color_palette = "cool shadows with restrained warm accents"
            atmosphere = "tense, contained, expectant"
        elif any(token in tone for token in ("romance", "nostalgia", "intim", "warm")):
            lighting = "soft warm key light"
            color_palette = "warm amber and soft neutrals"
            atmosphere = "intimate, emotional, human"
        else:
            lighting = "naturalistic cinematic lighting"
            color_palette = "balanced cinematic palette"
            atmosphere = "grounded narrative realism"
        return {
            "scene_heading": scene_heading,
            "location": location,
            "time_of_day": time_of_day,
            "lighting_style": lighting,
            "color_palette": color_palette,
            "atmosphere": atmosphere,
        }

    def build_visual_prompt_guidance_for_shot(self, *, shot_type: str, action: str, emotional_intent: str) -> dict[str, str]:
        shot_key = (shot_type or "MS").upper()
        framing = {
            "CU": "tight facial framing",
            "MS": "waist-up narrative framing",
            "WS": "wide environmental framing",
            "OTS": "over-the-shoulder relational framing",
            "POV": "subjective point-of-view framing",
        }.get(shot_key, "balanced narrative framing")
        angle = "eye-level"
        if shot_key in {"WS", "EWS"}:
            angle = "slightly low heroic perspective"
        if shot_key in {"CU", "ECU"}:
            angle = "subtle high-angle intimacy"
        motion = "locked frame"
        action_l = action.lower()
        if any(k in action_l for k in ("run", "chase", "walk", "follows", "entra", "avanza")):
            motion = "slow tracking move"
        if any(k in emotional_intent.lower() for k in ("tension", "suspense", "anxiety")):
            motion = "slow push-in"
        return {
            "shot_type": shot_key,
            "framing": framing,
            "camera_angle": angle,
            "camera_motion": motion,
            "composition": "clear foreground, readable midground, motivated background",
        }

    def build_model_specific_prompt_guidance(self, *, model_family: str, subject: str, action: str, environment: str, lighting: str, style: str) -> dict[str, Any]:
        family = (model_family or "wan22").strip().lower()
        templates = {
            "kling": "subject, action, environment, style, camera, emotion",
            "sora": "cinematic video, shot type, composition, atmosphere, style",
            "openai_4o": "subject, style, setting, lighting, emotion, composition",
            "veo": "subject, action, environment, lighting, camera, style",
            "firefly": "subject, action, environment/context, style/mood",
            "midjourney": "cinematic still, shot type, composition, camera, focal, dof, film look, lighting, color grading",
            "wan22": "script-faithful cinematic frame with continuity constraints",
        }
        resolved = "wan22"
        if "kling" in family:
            resolved = "kling"
        elif "sora" in family:
            resolved = "sora"
        elif "4o" in family or "openai" in family:
            resolved = "openai_4o"
        elif "veo" in family:
            resolved = "veo"
        elif "firefly" in family or "adobe" in family:
            resolved = "firefly"
        elif "midjourney" in family or "mj" in family:
            resolved = "midjourney"
        prompt = f"{subject}. {action}. {environment}. lighting: {lighting}. style: {style}."
        return {
            "model_prompt_family": resolved,
            "guidance_template": templates[resolved],
            "model_specific_prompt": prompt,
        }

    def _extract_keywords(self, canonical_terms: list[str]) -> list[str]:
        loaded = self.load_cinematography_prompt_references()
        corpus = "\n".join(item.get("content", "") for item in loaded["references"].values()).lower()
        found: list[str] = []
        seen: set[str] = set()
        for term in canonical_terms:
            normalized = term.lower()
            escaped = re.escape(normalized)
            if re.search(rf"\b{escaped}\b", corpus) or " " in normalized:
                key = normalized
                if key not in seen:
                    seen.add(key)
                    found.append(term)
        for term in canonical_terms:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                found.append(term)
        return found


cinematography_prompt_reference_service = CinematographyPromptReferenceService()


def load_cinematography_prompt_references() -> dict[str, Any]:
    return cinematography_prompt_reference_service.load_cinematography_prompt_references()
