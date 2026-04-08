from __future__ import annotations

from typing import Any, Dict, List, Optional


class ContinuityFormalService:
    _CONVERSATIONAL_INTENTS = ("two_shot", "over_shoulder", "reaction", "close_up")
    _CONVERSATIONAL_BEAT_TYPES = ("dialogue", "reaction")

    def assign_continuity(
        self,
        *,
        shot_intent: Optional[str],
        beat_type: Optional[str],
        characters: List[str],
        shot_index: int,
        previous_shots: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not self._is_conversational_shot(shot_intent, beat_type):
            return None

        if len(characters) < 1:
            return None

        primary_character = characters[0]
        counterpart = characters[1] if len(characters) > 1 else None

        axis_side = self._resolve_axis_side(shot_intent, shot_index, previous_shots)
        eyeline_direction = self._resolve_eyeline_direction(shot_intent, primary_character, counterpart)
        screen_position = self._resolve_screen_position(shot_intent, primary_character, shot_index)
        counterpart_anchor = self._resolve_counterpart_anchor(shot_intent, counterpart)

        return {
            "axis_side": axis_side,
            "eyeline_direction": eyeline_direction,
            "screen_position": screen_position,
            "counterpart_anchor": counterpart_anchor,
            "continuity_group": self._resolve_continuity_group(primary_character, counterpart),
        }

    def _is_conversational_shot(self, shot_intent: Optional[str], beat_type: Optional[str]) -> bool:
        if shot_intent and shot_intent in self._CONVERSATIONAL_INTENTS:
            return True
        if beat_type and beat_type in self._CONVERSATIONAL_BEAT_TYPES:
            return True
        return False

    def _resolve_axis_side(
        self,
        shot_intent: Optional[str],
        shot_index: int,
        previous_shots: List[Dict[str, Any]],
    ) -> str:
        for prev in reversed(previous_shots):
            if not isinstance(prev, dict):
                continue
            prev_continuity = prev.get("continuity_formal")
            if isinstance(prev_continuity, dict) and prev_continuity.get("axis_side"):
                return str(prev_continuity["axis_side"])

        if shot_intent == "two_shot":
            return "center"

        if shot_index % 2 == 1:
            return "left_of_axis"

        return "right_of_axis"

    def _resolve_eyeline_direction(
        self,
        shot_intent: Optional[str],
        primary_character: str,
        counterpart: Optional[str],
    ) -> str:
        if shot_intent == "two_shot":
            return "mutual"

        if shot_intent == "over_shoulder":
            return f"towards_{counterpart.lower().replace(' ', '_')}" if counterpart else "towards_offscreen"

        if shot_intent == "reaction":
            return f"towards_{counterpart.lower().replace(' ', '_')}" if counterpart else "towards_offscreen"

        if shot_intent == "close_up":
            return f"towards_{counterpart.lower().replace(' ', '_')}" if counterpart else "neutral"

        return "neutral"

    def _resolve_screen_position(
        self,
        shot_intent: Optional[str],
        primary_character: str,
        shot_index: int,
    ) -> str:
        if shot_intent == "two_shot":
            return "centered"

        if shot_intent == "over_shoulder":
            return "left_third" if shot_index % 2 == 1 else "right_third"

        if shot_intent == "reaction":
            return "right_third" if shot_index % 2 == 1 else "left_third"

        if shot_intent == "close_up":
            return "centered"

        return "centered"

    def _resolve_counterpart_anchor(
        self,
        shot_intent: Optional[str],
        counterpart: Optional[str],
    ) -> Optional[str]:
        if shot_intent in ("over_shoulder", "reaction"):
            return counterpart

        if shot_intent == "two_shot":
            return "both_characters"

        return None

    def _resolve_continuity_group(
        self,
        primary_character: str,
        counterpart: Optional[str],
    ) -> str:
        if counterpart:
            chars = sorted([primary_character.lower(), counterpart.lower()])
            return f"dialogue_{'_'.join(chars)}"
        return f"dialogue_{primary_character.lower()}"
