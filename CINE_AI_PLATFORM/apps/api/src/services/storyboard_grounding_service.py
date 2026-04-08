from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class StoryboardGroundingService:
    _INTENT_SUBJECTS = {
        "establishing": {"primary": "location", "secondary": "space", "focus": "environment"},
        "wide": {"primary": "action", "secondary": "characters", "focus": "spatial_orientation"},
        "medium": {"primary": "characters", "secondary": "action", "focus": "balanced_coverage"},
        "close_up": {"primary": "character_face", "secondary": "emotion", "focus": "emotional_detail"},
        "two_shot": {"primary": "two_characters", "secondary": "relationship", "focus": "spatial_relationship"},
        "over_shoulder": {"primary": "speaker", "secondary": "listener", "focus": "conversation_axis"},
        "insert": {"primary": "prop", "secondary": "detail", "focus": "object_dominance"},
        "reaction": {"primary": "character_face", "secondary": "emotion", "focus": "emotional_response"},
        "detail": {"primary": "prop", "secondary": "texture", "focus": "visual_detail"},
    }

    _COMPOSITION_HINTS = {
        "establishing": "wide composition, establish space and environment",
        "wide": "full body or action framing, clear spatial context",
        "medium": "waist-up framing, balanced character and environment",
        "close_up": "tight framing on face or key subject",
        "two_shot": "two characters in frame, clear spatial relationship",
        "over_shoulder": "over-shoulder perspective, speaker in focus",
        "insert": "tight framing on object, minimal background",
        "reaction": "tight framing on face, emphasize emotional response",
        "detail": "extreme close-up on visual detail or texture",
    }

    def ground_shot(
        self,
        *,
        shot_intent: Optional[str],
        beat_type: Optional[str],
        scene_breakdown: Optional[Dict[str, Any]],
        beat_text: str,
        characters: List[str],
        locations: List[str],
    ) -> Dict[str, Any]:
        intent = self._resolve_intent(shot_intent, beat_type)
        subjects = self._INTENT_SUBJECTS.get(intent, self._INTENT_SUBJECTS["medium"])

        primary_subjects = self._select_primary_subjects(intent, scene_breakdown, characters)
        secondary_subjects = self._select_secondary_subjects(intent, scene_breakdown, characters)
        location_anchor = self._select_location_anchor(intent, scene_breakdown, locations)
        prop_focus = self._select_prop_focus(intent, scene_breakdown, primary_subjects)
        action_focus = self._select_action_focus(intent, scene_breakdown, beat_text)
        emotional_focus = self._select_emotional_focus(intent, beat_type, characters)
        composition_hint = self._COMPOSITION_HINTS.get(intent, "balanced framing")
        grounding_notes = self._build_grounding_notes(intent, primary_subjects, location_anchor, prop_focus)

        return {
            "shot_intent": intent,
            "visual_focus": subjects.get("focus", "balanced"),
            "primary_subjects": primary_subjects,
            "secondary_subjects": secondary_subjects,
            "location_anchor": location_anchor,
            "prop_focus": prop_focus,
            "action_focus": action_focus,
            "emotional_focus": emotional_focus,
            "composition_hint": composition_hint,
            "grounding_notes": grounding_notes,
        }

    def enrich_prompt_base(self, prompt_base: str, grounding: Dict[str, Any]) -> str:
        enriched_parts = [prompt_base.strip()]

        composition = grounding.get("composition_hint")
        if composition and composition.strip():
            enriched_parts.append(composition.strip())

        location = grounding.get("location_anchor")
        if location and location.strip():
            enriched_parts.append(f"setting: {location.strip()}")

        primary = grounding.get("primary_subjects")
        if primary and primary.strip():
            enriched_parts.append(f"focus on: {primary.strip()}")

        prop = grounding.get("prop_focus")
        if prop and prop.strip():
            enriched_parts.append(f"featuring: {prop.strip()}")

        action = grounding.get("action_focus")
        if action and action.strip():
            enriched_parts.append(action.strip())

        return ", ".join(enriched_parts)

    def _resolve_intent(self, shot_intent: Optional[str], beat_type: Optional[str]) -> str:
        if shot_intent and shot_intent in self._INTENT_SUBJECTS:
            return shot_intent

        if beat_type == "dialogue":
            return "medium"
        if beat_type == "action":
            return "wide"
        if beat_type == "insert":
            return "insert"
        if beat_type == "reaction":
            return "reaction"

        return "medium"

    def _select_primary_subjects(
        self,
        intent: str,
        scene_breakdown: Optional[Dict[str, Any]],
        characters: List[str],
    ) -> str:
        if intent in ("close_up", "reaction"):
            speaking = self._get_speaking_characters(scene_breakdown)
            if speaking:
                return speaking[0]
            if characters:
                return characters[0]
            return "main subject"

        if intent == "two_shot":
            present = self._get_characters_present(scene_breakdown)
            selected = present[:2] if present else characters[:2]
            return " and ".join(selected) if selected else "two characters"

        if intent == "over_shoulder":
            speaking = self._get_speaking_characters(scene_breakdown)
            if speaking:
                return speaking[0]
            if characters:
                return characters[0]
            return "speaker"

        if intent in ("insert", "detail"):
            props = self._get_props_detected(scene_breakdown)
            if props:
                return props[0]
            return "key object"

        if intent == "establishing":
            location = self._get_location(scene_breakdown)
            return location or "environment"

        if intent == "wide":
            present = self._get_characters_present(scene_breakdown)
            if present:
                return present[0]
            if characters:
                return characters[0]
            return "scene subject"

        if characters:
            return characters[0]

        return "main subject"

    def _select_secondary_subjects(
        self,
        intent: str,
        scene_breakdown: Optional[Dict[str, Any]],
        characters: List[str],
    ) -> str:
        if intent == "two_shot":
            present = self._get_characters_present(scene_breakdown)
            selected = present[:2] if present else characters[:2]
            if len(selected) >= 2:
                return selected[1]
            return "second character"

        if intent == "over_shoulder":
            speaking = self._get_speaking_characters(scene_breakdown)
            if len(speaking) >= 2:
                return speaking[1]
            if len(characters) >= 2:
                return characters[1]
            return "listener"

        if intent in ("insert", "detail"):
            return "background context"

        if intent == "wide":
            action = self._get_key_actions(scene_breakdown)
            if action:
                return action[0][:60]
            return "action context"

        return ""

    def _select_location_anchor(
        self,
        intent: str,
        scene_breakdown: Optional[Dict[str, Any]],
        locations: List[str],
    ) -> Optional[str]:
        if intent == "establishing":
            location = self._get_location(scene_breakdown)
            return location

        if intent in ("wide", "medium", "two_shot"):
            location = self._get_location(scene_breakdown)
            return location

        if locations:
            return locations[0]

        return None

    def _select_prop_focus(
        self,
        intent: str,
        scene_breakdown: Optional[Dict[str, Any]],
        primary_subjects: str,
    ) -> Optional[str]:
        if intent in ("insert", "detail"):
            props = self._get_props_detected(scene_breakdown)
            if props:
                return props[0]

        if intent in ("wide", "medium"):
            visual = self._get_visual_elements(scene_breakdown)
            if visual:
                return visual[0]

        return None

    def _select_action_focus(
        self,
        intent: str,
        scene_breakdown: Optional[Dict[str, Any]],
        beat_text: str,
    ) -> Optional[str]:
        if intent in ("wide", "medium"):
            actions = self._get_key_actions(scene_breakdown)
            if actions:
                return actions[0][:80]

        moving = self._get_moving_elements(scene_breakdown)
        if moving and intent != "close_up":
            return f"movement: {moving[0]}"

        return None

    def _select_emotional_focus(
        self,
        intent: str,
        beat_type: Optional[str],
        characters: List[str],
    ) -> Optional[str]:
        if intent in ("close_up", "reaction"):
            if characters:
                return f"{characters[0]} emotional state"
            return "emotional detail"

        if beat_type == "reaction":
            if characters:
                return f"{characters[0]} reaction"
            return "character reaction"

        return None

    def _build_grounding_notes(
        self,
        intent: str,
        primary_subjects: str,
        location_anchor: Optional[str],
        prop_focus: Optional[str],
    ) -> List[str]:
        notes: List[str] = []

        if location_anchor:
            notes.append(f"location: {location_anchor}")

        if primary_subjects:
            notes.append(f"subject: {primary_subjects}")

        if prop_focus:
            notes.append(f"prop emphasis: {prop_focus}")

        if intent in ("insert", "detail"):
            notes.append("minimize background, isolate subject")

        if intent == "establishing":
            notes.append("open composition, show space clearly")

        return notes

    def _get_characters_present(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("characters_present", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_speaking_characters(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("speaking_characters", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_props_detected(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("props_detected", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_visual_elements(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("visual_elements", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_key_actions(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("key_actions", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_moving_elements(self, scene_breakdown: Optional[Dict[str, Any]]) -> List[str]:
        if not scene_breakdown:
            return []
        items = scene_breakdown.get("moving_elements", [])
        return [str(item) for item in items if isinstance(item, str) and str(item).strip()]

    def _get_location(self, scene_breakdown: Optional[Dict[str, Any]]) -> Optional[str]:
        if not scene_breakdown:
            return None
        location = scene_breakdown.get("location")
        if isinstance(location, str) and location.strip():
            return location.strip()
        return None
