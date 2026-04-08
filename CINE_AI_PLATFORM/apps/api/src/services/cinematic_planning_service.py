from __future__ import annotations

from typing import Any, Dict, List, Optional


class CinematicPlanningService:
    _BEAT_TYPES = (
        "dialogue",
        "action",
        "exposition",
        "reaction",
        "insert",
        "transition",
    )

    _COVERAGE_TYPES = (
        "establishing",
        "wide",
        "medium",
        "close_up",
        "two_shot",
        "over_shoulder",
        "insert",
        "reaction",
        "detail",
    )

    def plan_beats(
        self,
        scene_breakdowns: List[Dict[str, Any]],
        fallback_beats: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        if not scene_breakdowns:
            return fallback_beats or []

        planned_beats: List[Dict[str, Any]] = []
        global_index = 1

        for breakdown in scene_breakdowns:
            if not isinstance(breakdown, dict):
                continue

            scene_id = str(breakdown.get("scene_id") or "").strip()
            characters_present = breakdown.get("characters_present", [])
            speaking_characters = breakdown.get("speaking_characters", [])
            key_actions = breakdown.get("key_actions", [])
            props_detected = breakdown.get("props_detected", [])
            moving_elements = breakdown.get("moving_elements", [])
            semi_moving_elements = breakdown.get("semi_moving_elements", [])
            action_blocks = [
                str(item)
                for item in breakdown.get("key_actions", [])
                if isinstance(item, str) and str(item).strip()
            ]
            dialogue_blocks = [
                item
                for item in breakdown.get("speaking_characters", [])
                if isinstance(item, str) and str(item).strip()
            ]

            is_new_location = self._is_new_location(breakdown, planned_beats)
            is_dialogue_scene = len(speaking_characters) >= 2
            is_action_scene = len(key_actions) >= 1
            has_relevant_props = len(props_detected) >= 1
            has_movement = len(moving_elements) >= 1
            has_semi_movement = len(semi_moving_elements) >= 1

            if is_new_location and not is_action_scene:
                planned_beats.append(
                    self._make_beat(
                        scene_id=scene_id,
                        index=global_index,
                        beat_type="exposition",
                        shot_intent="establishing",
                        summary="Establecer espacio y localizaci\u00f3n",
                        text=f"Plano de establecimiento de {breakdown.get('location', 'la escena')}",
                        motivation="Orientar al espectador en el espacio de la escena",
                    )
                )
                global_index += 1

            if is_dialogue_scene:
                planned_beats.extend(
                    self._plan_dialogue_coverage(
                        scene_id=scene_id,
                        index=global_index,
                        speaking_characters=speaking_characters,
                        characters_present=characters_present,
                        has_relevant_props=has_relevant_props,
                        props_detected=props_detected,
                    )
                )
                global_index += len(planned_beats) - global_index + 1

            if is_action_scene:
                if is_new_location:
                    planned_beats.append(
                        self._make_beat(
                            scene_id=scene_id,
                            index=global_index,
                            beat_type="action",
                            shot_intent="wide",
                            summary="Orientaci\u00f3n espacial de la acci\u00f3n",
                            text="Plano amplio para orientar la acci\u00f3n en el espacio",
                            motivation="Claridad espacial antes de entrar en detalle de la acci\u00f3n",
                        )
                    )
                    global_index += 1

                for action_text in key_actions:
                    has_movement_in_action = any(
                        term.lower() in action_text.lower() for term in moving_elements
                    )
                    planned_beats.append(
                        self._make_beat(
                            scene_id=scene_id,
                            index=global_index,
                            beat_type="action",
                            shot_intent="medium" if has_movement_in_action else "close_up",
                            summary=action_text[:80],
                            text=action_text,
                            motivation="Cubrir la acci\u00f3n principal con claridad" if has_movement_in_action else "Enfatizar detalle de la acci\u00f3n",
                        )
                    )
                    global_index += 1

            if has_relevant_props and not is_dialogue_scene:
                for prop in props_detected[:2]:
                    planned_beats.append(
                        self._make_beat(
                            scene_id=scene_id,
                            index=global_index,
                            beat_type="insert",
                            shot_intent="detail",
                            summary=f"Detalle de {prop}",
                            text=f"Plano de apoyo para destacar {prop}",
                            motivation=f"Enfatizar {prop} como elemento narrativo relevante",
                        )
                    )
                    global_index += 1

            if has_semi_movement and not is_dialogue_scene:
                for element in semi_moving_elements[:2]:
                    planned_beats.append(
                        self._make_beat(
                            scene_id=scene_id,
                            index=global_index,
                            beat_type="reaction",
                            shot_intent="close_up",
                            summary=f"Apoyo de {element}",
                            text=f"Plano de apoyo para {element}",
                            motivation=f"Mostrar cambio de estado o detalle de {element}",
                        )
                    )
                    global_index += 1

            if not planned_beats or planned_beats[-1].get("scene_id") != scene_id:
                if not any(b.get("scene_id") == scene_id for b in planned_beats):
                    planned_beats.append(
                        self._make_beat(
                            scene_id=scene_id,
                            index=global_index,
                            beat_type="exposition",
                            shot_intent="medium",
                            summary=breakdown.get("heading", "Escena"),
                            text=breakdown.get("heading", ""),
                            motivation="Presentar la escena de forma neutra",
                        )
                    )
                    global_index += 1

        return planned_beats if planned_beats else (fallback_beats or [])

    def _plan_dialogue_coverage(
        self,
        *,
        scene_id: str,
        index: int,
        speaking_characters: List[str],
        characters_present: List[str],
        has_relevant_props: bool,
        props_detected: List[str],
    ) -> List[Dict[str, Any]]:
        beats: List[Dict[str, Any]] = []
        current_index = index

        beats.append(
            self._make_beat(
                scene_id=scene_id,
                index=current_index,
                beat_type="dialogue",
                shot_intent="two_shot",
                summary="Plano de conjunto para el di\u00e1logo",
                text=f"{' y '.join(speaking_characters[:2])} en di\u00e1logo",
                motivation="Establecer la relaci\u00f3n espacial entre los interlocutores",
            )
        )
        current_index += 1

        for character in speaking_characters[:3]:
            beats.append(
                self._make_beat(
                    scene_id=scene_id,
                    index=current_index,
                    beat_type="dialogue",
                    shot_intent="over_shoulder",
                    summary=f"Plano de {character}",
                    text=f"{character} habla",
                    motivation=f"Cubrir la intervenci\u00f3n de {character}",
                )
            )
            current_index += 1

        if len(speaking_characters) >= 2:
            beats.append(
                self._make_beat(
                    scene_id=scene_id,
                    index=current_index,
                    beat_type="reaction",
                    shot_intent="reaction",
                    summary="Reacci\u00f3n del interlocutor",
                    text="Plano de reacci\u00f3n",
                    motivation="Mostrar respuesta emocional o gestual",
                )
            )
            current_index += 1

        if has_relevant_props:
            for prop in props_detected[:1]:
                beats.append(
                    self._make_beat(
                        scene_id=scene_id,
                        index=current_index,
                        beat_type="insert",
                        shot_intent="detail",
                        summary=f"Detalle de {prop} en di\u00e1logo",
                        text=f"Plano de apoyo de {prop}",
                        motivation=f"Vincular {prop} al intercambio dram\u00e1tico",
                    )
                )
                current_index += 1

        return beats

    def _make_beat(
        self,
        *,
        scene_id: str,
        index: int,
        beat_type: str,
        shot_intent: str,
        summary: str,
        text: str,
        motivation: str,
    ) -> Dict[str, Any]:
        return {
            "beat_id": f"{scene_id}_plan_{index:03d}",
            "index": index,
            "summary": summary.strip()[:120],
            "text": text.strip()[:200],
            "intent": self._map_intent(beat_type),
            "beat_type": beat_type,
            "shot_intent": shot_intent,
            "motivation": motivation.strip()[:160],
        }

    def _map_intent(self, beat_type: str) -> str:
        mapping = {
            "dialogue": "dialogue",
            "action": "action",
            "exposition": "setup",
            "reaction": "emotion",
            "insert": "progression",
            "transition": "progression",
        }
        return mapping.get(beat_type, "progression")

    def _is_new_location(
        self,
        breakdown: Dict[str, Any],
        existing_beats: List[Dict[str, Any]],
    ) -> bool:
        location = breakdown.get("location")
        if not location or not isinstance(location, str) or not location.strip():
            return False

        normalized = location.strip().lower()
        for beat in existing_beats:
            if not isinstance(beat, dict):
                continue
            existing_location = beat.get("location")
            if existing_location and isinstance(existing_location, str):
                if existing_location.strip().lower() == normalized:
                    return False
        return True
