from __future__ import annotations

import re
from typing import Any


class StoryboardImageScriptValidationService:
    SYNONYMS = {
        "casa abandonada": ["abandoned house", "derelict house"],
        "linterna": ["flashlight", "torch"],
        "suspense oscuro": ["dark suspense", "tense suspense"],
        "marta": ["marta"],
    }

    def build_validation_payload(
        self,
        *,
        script_excerpt_used: str,
        positive_prompt: str,
        scene_heading: str,
        shot_type: str,
        characters: list[str],
        location: str,
        visual_constraints: list[str],
        atmosphere: str = "",
    ) -> dict[str, Any]:
        key_object = self._extract_key_object(script_excerpt_used)
        action = self._extract_action(script_excerpt_used)
        main_character = (characters[0] if characters else "").strip()
        return {
            "script_excerpt_used": script_excerpt_used or "",
            "positive_prompt": positive_prompt or "",
            "scene_heading": scene_heading or "",
            "shot_type": (shot_type or "MS").upper(),
            "characters": characters or [],
            "location": location or "",
            "visual_constraints": visual_constraints or [],
            "expected_main_character": main_character,
            "expected_action": action,
            "expected_location": location or scene_heading,
            "expected_key_object": key_object,
            "expected_atmosphere": atmosphere or "cinematic",
            "expected_shot_type": (shot_type or "MS").upper(),
        }

    def validate_shot(
        self,
        *,
        validation_payload: dict[str, Any],
        observed_visual_text: str = "",
        minimum_score: float = 0.72,
    ) -> dict[str, Any]:
        expected = validation_payload
        reference_text = self._normalize_semantic_text(observed_visual_text or expected.get("positive_prompt") or "")
        script_text = self._normalize_semantic_text(str(expected.get("script_excerpt_used") or ""))

        char = self._contains(reference_text, expected.get("expected_main_character", ""))
        loc = self._contains(reference_text, expected.get("expected_location", ""))
        obj = self._contains(reference_text, expected.get("expected_key_object", ""))
        mood = self._contains(reference_text, expected.get("expected_atmosphere", ""))
        shot_type_match = self._contains(reference_text, expected.get("expected_shot_type", ""))

        # If reference text is too sparse, fallback to script/object grounding.
        if not obj and expected.get("expected_key_object"):
            obj = self._contains(script_text, expected.get("expected_key_object", "")) and self._contains(reference_text, expected.get("expected_key_object", ""))

        action = self._contains(reference_text, expected.get("expected_action", ""))

        component_scores = {
            "character_match": 1.0 if char else 0.0,
            "location_match": 1.0 if loc else 0.0,
            "object_match": 1.0 if obj else 0.0,
            "mood_match": 1.0 if mood else 0.0,
            "shot_type_match": 1.0 if shot_type_match else 0.0,
            "action_match": 1.0 if action else 0.0,
        }
        overall = round(sum(component_scores.values()) / len(component_scores), 3)

        missing: list[str] = []
        incorrect: list[str] = []
        if not char:
            missing.append("main_character")
        if not loc:
            missing.append("location")
        if not obj and expected.get("expected_key_object"):
            missing.append("key_object")
        if not mood and expected.get("expected_atmosphere"):
            missing.append("atmosphere")
        if not shot_type_match:
            missing.append("shot_type")
        if not action and expected.get("expected_action"):
            missing.append("action")

        if observed_visual_text:
            observed_lower = self._normalize_semantic_text(observed_visual_text)
            expected_location = self._normalize_semantic_text(str(expected.get("expected_location") or ""))
            if expected_location and expected_location not in observed_lower:
                incorrect.append("possible_wrong_location")

        needs_regen = overall < minimum_score
        regen_prompt = self.build_regeneration_prompt(validation_payload=validation_payload) if needs_regen else ""

        return {
            "overall_match_score": overall,
            "character_match": component_scores["character_match"],
            "location_match": component_scores["location_match"],
            "object_match": component_scores["object_match"],
            "mood_match": component_scores["mood_match"],
            "shot_type_match": component_scores["shot_type_match"],
            "missing_elements": missing,
            "incorrect_elements": incorrect,
            "regeneration_recommendation": "regenerate_with_stricter_constraints" if needs_regen else "keep_current_render",
            "suggested_regeneration_prompt": regen_prompt,
        }

    def build_regeneration_prompt(self, *, validation_payload: dict[str, Any]) -> str:
        expected_character = str(validation_payload.get("expected_main_character") or "main character").strip()
        expected_action = str(validation_payload.get("expected_action") or "script action").strip()
        expected_location = str(validation_payload.get("expected_location") or validation_payload.get("scene_heading") or "script location").strip()
        expected_object = str(validation_payload.get("expected_key_object") or "key prop from script").strip()
        expected_mood = str(validation_payload.get("expected_atmosphere") or "cinematic atmosphere").strip()
        expected_shot_type = str(validation_payload.get("expected_shot_type") or "MS").strip()
        base_prompt = str(validation_payload.get("positive_prompt") or "").strip()
        return (
            f"STRICT SCRIPT ALIGNMENT. {expected_shot_type} shot. Main character: {expected_character}. "
            f"Action: {expected_action}. Exact location: {expected_location}. "
            f"Key object must be visible: {expected_object}. Atmosphere: {expected_mood}. "
            f"Preserve script fidelity, no substitutions, no extra characters, no wrong props. "
            f"Base prompt: {base_prompt}"
        )

    def _extract_key_object(self, script_excerpt: str) -> str:
        lowered = (script_excerpt or "").lower()
        known_objects = [
            "linterna", "gun", "pistol", "knife", "telefono", "phone", "car", "coche", "mapa", "llave",
            "maleta", "documento", "mask", "mascara", "foto", "camera", "camara",
        ]
        for obj in known_objects:
            if re.search(rf"\b{re.escape(obj)}\b", lowered):
                return obj
        match = re.search(r"\bcon\s+([a-zA-Z0-9_\-]+)", lowered)
        if match:
            return match.group(1)
        return ""

    def _extract_action(self, script_excerpt: str) -> str:
        text = (script_excerpt or "").strip()
        if not text:
            return ""
        sentence = re.split(r"[\.!?]", text)[0].strip()
        return sentence[:140]

    def _contains(self, text: str, expected: str) -> bool:
        expected_clean = self._normalize_semantic_text(str(expected or "").strip())
        if not expected_clean:
            return True
        if expected_clean in text:
            return True
        tokens = [token for token in re.split(r"\W+", expected_clean) if len(token) > 2]
        if not tokens:
            return expected_clean in text
        hits = sum(1 for token in tokens if token in text)
        return hits >= max(1, min(2, len(tokens)))

    def _normalize_semantic_text(self, text: str) -> str:
        normalized = str(text or "").lower()
        for key, aliases in self.SYNONYMS.items():
            if key in normalized:
                continue
            for alias in aliases:
                if alias in normalized:
                    normalized = normalized.replace(alias, key)
        return normalized


storyboard_image_script_validation_service = StoryboardImageScriptValidationService()
