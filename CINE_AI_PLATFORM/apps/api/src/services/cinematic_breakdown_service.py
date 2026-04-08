from __future__ import annotations

import re
from typing import Any, Dict, List


class CinematicBreakdownService:
    _ACTION_TERMS = (
        "corre",
        "corren",
        "camina",
        "caminan",
        "entra",
        "entran",
        "sale",
        "salen",
        "mira",
        "miran",
        "abre",
        "abren",
        "cierra",
        "cierran",
        "recoge",
        "deja",
        "levanta",
        "saca",
        "guarda",
        "dispara",
        "golpea",
        "frena",
        "gira",
        "persigue",
        "huye",
        "enciende",
        "apaga",
        "cae",
        "caen",
    )
    _PROPS = {
        "arma": ("arma", "pistola", "revólver", "revolver", "cuchillo", "espada"),
        "maleta": ("maleta", "maletin", "maletín"),
        "telefono": ("telefono", "teléfono", "movil", "móvil", "celular"),
        "llave": ("llave", "llaves"),
        "vaso": ("vaso", "copa", "botella"),
        "libro": ("libro", "cuaderno"),
        "foto": ("foto", "fotografia", "fotografía", "retrato"),
        "carta": ("carta", "sobre", "nota"),
        "carpeta": ("carpeta", "archivo", "documento", "papeles"),
        "mochila": ("mochila", "bolso", "bolsa"),
        "pantalla": ("pantalla", "monitor", "televisor", "tablet"),
    }
    _VISUAL_ELEMENTS = {
        "puerta": ("puerta", "porton", "portón"),
        "ventana": ("ventana", "ventanal"),
        "mesa": ("mesa", "mostrador", "escritorio"),
        "silla": ("silla", "butaca", "taburete"),
        "coche": ("coche", "auto", "carro", "vehiculo", "vehículo", "camion", "camión"),
        "luz": ("luz", "lampara", "lámpara", "farol"),
        "cortina": ("cortina", "persiana"),
        "humo": ("humo", "niebla", "vapor"),
        "espejo": ("espejo",),
        "escalera": ("escalera", "escaleras"),
    }
    _MOVING_TERMS = (
        "corre",
        "camina",
        "entra",
        "sale",
        "salta",
        "persigue",
        "huye",
        "frena",
        "gira",
        "se mueve",
        "avanza",
        "retrocede",
    )
    _SEMI_MOVING_TERMS = (
        "abre",
        "cierra",
        "cae",
        "caen",
        "parpadea",
        "suena",
        "vibra",
        "enciende",
        "apaga",
        "humo",
        "cortina",
        "pantalla",
        "luz",
        "vaso",
        "telefono",
        "teléfono",
    )

    def build_scene_breakdowns(self, parsed_scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        breakdowns: List[Dict[str, Any]] = []

        for scene in parsed_scenes:
            if not isinstance(scene, dict):
                continue

            scene_id = self._clean_text(str(scene.get("scene_id") or ""))
            heading = self._clean_text(str(scene.get("heading") or ""))
            if not scene_id or not heading:
                continue

            action_blocks = [
                self._clean_text(str(item))
                for item in scene.get("action_blocks", [])
                if isinstance(item, str) and self._clean_text(str(item))
            ]
            dialogue_blocks = [
                item for item in scene.get("dialogue_blocks", [])
                if isinstance(item, dict)
                and self._clean_text(str(item.get("character") or ""))
                and self._clean_text(str(item.get("text") or ""))
            ]

            characters_present = self._extract_characters_present(scene, action_blocks, dialogue_blocks)
            speaking_characters = self._extract_speaking_characters(dialogue_blocks)
            key_actions = self._extract_key_actions(action_blocks)
            combined_scene_text = " ".join(
                action_blocks
                + [self._clean_text(str(item.get("text") or "")) for item in dialogue_blocks]
            )

            breakdowns.append(
                {
                    "scene_id": scene_id,
                    "heading": heading,
                    "location": self._clean_optional(scene.get("location")),
                    "time_of_day": self._clean_optional(scene.get("time_of_day")),
                    "characters_present": characters_present,
                    "speaking_characters": speaking_characters,
                    "key_actions": key_actions,
                    "props_detected": self._detect_keywords(combined_scene_text, self._PROPS, max_items=8),
                    "visual_elements": self._detect_keywords(combined_scene_text, self._VISUAL_ELEMENTS, max_items=8),
                    "moving_elements": self._extract_movement_candidates(action_blocks, self._MOVING_TERMS, max_items=6),
                    "semi_moving_elements": self._extract_movement_candidates(action_blocks, self._SEMI_MOVING_TERMS, max_items=6),
                }
            )

        return breakdowns

    def _extract_characters_present(
        self,
        scene: Dict[str, Any],
        action_blocks: List[str],
        dialogue_blocks: List[Dict[str, Any]],
    ) -> List[str]:
        characters: List[str] = []
        seen = set()

        for item in scene.get("characters_detected", []):
            normalized = self._normalize_name(str(item or ""))
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                characters.append(normalized)

        for item in dialogue_blocks:
            normalized = self._normalize_name(str(item.get("character") or ""))
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                characters.append(normalized)

        combined_actions = " ".join(action_blocks)
        for candidate in re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?\b", combined_actions):
            normalized = self._normalize_name(candidate)
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                characters.append(normalized)

        return characters[:8]

    def _extract_speaking_characters(self, dialogue_blocks: List[Dict[str, Any]]) -> List[str]:
        characters: List[str] = []
        seen = set()
        for item in dialogue_blocks:
            normalized = self._normalize_name(str(item.get("character") or ""))
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                characters.append(normalized)
        return characters[:8]

    def _extract_key_actions(self, action_blocks: List[str], max_items: int = 6) -> List[str]:
        actions: List[str] = []
        seen = set()

        for block in action_blocks:
            sentences = [
                self._clean_text(fragment)
                for fragment in re.split(r"(?<=[.!?])\s+", block)
                if self._clean_text(fragment)
            ]
            for sentence in sentences:
                lowered = sentence.lower()
                if not any(term in lowered for term in self._ACTION_TERMS):
                    continue
                key = lowered.strip()
                if key in seen:
                    continue
                seen.add(key)
                actions.append(sentence)
                if len(actions) >= max_items:
                    return actions

        if actions:
            return actions

        for block in action_blocks:
            normalized = self._clean_text(block)
            if not normalized:
                continue
            actions.append(normalized)
            if len(actions) >= max_items:
                break

        return actions

    def _detect_keywords(self, text: str, catalog: Dict[str, tuple[str, ...]], max_items: int) -> List[str]:
        normalized_text = self._clean_text(text).lower()
        if not normalized_text:
            return []

        detected: List[str] = []
        for label, aliases in catalog.items():
            if any(re.search(rf"\b{re.escape(alias.lower())}\b", normalized_text) for alias in aliases):
                detected.append(label)
            if len(detected) >= max_items:
                break

        return detected

    def _extract_movement_candidates(self, action_blocks: List[str], terms: tuple[str, ...], max_items: int) -> List[str]:
        candidates: List[str] = []
        seen = set()

        for block in action_blocks:
            sentences = [
                self._clean_text(fragment)
                for fragment in re.split(r"(?<=[.!?])\s+", block)
                if self._clean_text(fragment)
            ]
            for sentence in sentences:
                lowered = sentence.lower()
                if not any(term in lowered for term in terms):
                    continue
                key = lowered.strip()
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(sentence)
                if len(candidates) >= max_items:
                    return candidates

        return candidates

    def _normalize_name(self, value: str) -> str:
        cleaned = self._clean_text(value)
        if not cleaned:
            return ""
        return " ".join(part.capitalize() for part in cleaned.split())

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip())

    def _clean_optional(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = self._clean_text(value)
        return cleaned or None
