from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class ScreenplayParserService:
    _SCENE_HEADING_RE = re.compile(
        r"^(INT\.?|EXT\.?|INT/EXT\.?|I/E\.?|INT\.\/EXT\.?)\s+.+$",
        re.IGNORECASE,
    )
    _TIME_OF_DAY_HINTS = (
        "DAY",
        "NIGHT",
        "MORNING",
        "EVENING",
        "AFTERNOON",
        "DAWN",
        "DUSK",
        "SUNSET",
        "SUNRISE",
        "DIA",
        "NOCHE",
        "MANANA",
        "MAÑANA",
        "TARDE",
        "AMANECER",
        "ATARDECER",
    )
    _TRANSITION_SUFFIXES = (
        " TO:",
        " OUT",
        " IN",
    )

    def parse_script(self, script_text: str) -> List[Dict[str, Any]]:
        normalized_script = self._normalize_text(script_text)
        if not normalized_script:
            return []

        lines = normalized_script.split("\n")
        scenes: List[Dict[str, Any]] = []
        current_scene: Optional[Dict[str, Any]] = None
        action_buffer: List[str] = []
        line_index = 0

        while line_index < len(lines):
            raw_line = lines[line_index]
            line = self._clean_line(raw_line)

            if not line:
                if current_scene is not None:
                    self._flush_action_buffer(current_scene, action_buffer)
                line_index += 1
                continue

            if self._is_scene_heading(line):
                if current_scene is not None:
                    self._flush_action_buffer(current_scene, action_buffer)
                    scenes.append(self._finalize_scene(current_scene))

                heading = self._normalize_heading(line)
                location, time_of_day = self._extract_heading_parts(heading)
                current_scene = {
                    "scene_id": f"scene_{len(scenes) + 1:03d}",
                    "heading": heading,
                    "location": location,
                    "time_of_day": time_of_day,
                    "action_blocks": [],
                    "dialogue_blocks": [],
                    "characters_detected": [],
                }
                line_index += 1
                continue

            if current_scene is None:
                line_index += 1
                continue

            if self._is_character_cue(line):
                self._flush_action_buffer(current_scene, action_buffer)
                dialogue_block, next_index = self._consume_dialogue_block(lines, line_index)
                if dialogue_block is not None:
                    current_scene["dialogue_blocks"].append(dialogue_block)
                    self._register_character(current_scene, dialogue_block["character"])
                    line_index = next_index
                    continue

            action_buffer.append(line)
            line_index += 1

        if current_scene is not None:
            self._flush_action_buffer(current_scene, action_buffer)
            scenes.append(self._finalize_scene(current_scene))

        return scenes

    def _consume_dialogue_block(self, lines: List[str], start_index: int) -> tuple[Optional[Dict[str, str]], int]:
        cue = self._normalize_character_cue(self._clean_line(lines[start_index]))
        dialogue_lines: List[str] = []
        line_index = start_index + 1

        while line_index < len(lines):
            current_line = self._clean_line(lines[line_index])
            if not current_line:
                if dialogue_lines:
                    line_index += 1
                    break
                line_index += 1
                continue

            if self._is_scene_heading(current_line) or self._is_character_cue(current_line):
                break

            dialogue_lines.append(current_line)
            line_index += 1

        if not dialogue_lines:
            return None, start_index + 1

        dialogue_text = " ".join(dialogue_lines).strip()
        if not dialogue_text:
            return None, line_index

        return {
            "character": cue,
            "text": dialogue_text,
        }, line_index

    def _flush_action_buffer(self, scene: Dict[str, Any], action_buffer: List[str]) -> None:
        if not action_buffer:
            return

        action_text = " ".join(action_buffer).strip()
        action_buffer.clear()
        if not action_text:
            return

        scene["action_blocks"].append(action_text)
        for character in self._extract_action_character_mentions(action_text):
            self._register_character(scene, character)

    def _extract_action_character_mentions(self, text: str) -> List[str]:
        mentions: List[str] = []
        seen = set()

        title_case = re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)?\b", text)
        uppercase = [token.title() for token in re.findall(r"\b[A-ZÁÉÍÓÚÑ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ]{2,})?\b", text)]

        for candidate in title_case + uppercase:
            normalized = self._normalize_character_cue(candidate)
            if not normalized:
                continue
            lowered = normalized.lower()
            if lowered in {"int", "ext", "dia", "noche", "day", "night"}:
                continue
            if lowered in seen:
                continue
            seen.add(lowered)
            mentions.append(normalized)

        return mentions[:8]

    def _register_character(self, scene: Dict[str, Any], character: str) -> None:
        normalized = self._normalize_character_cue(character)
        if not normalized:
            return

        existing = scene.get("characters_detected")
        if not isinstance(existing, list):
            existing = []
            scene["characters_detected"] = existing

        lowered_existing = {str(item).strip().lower() for item in existing if isinstance(item, str)}
        if normalized.lower() not in lowered_existing:
            existing.append(normalized)

    def _finalize_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "scene_id": scene["scene_id"],
            "heading": scene["heading"],
            "location": scene.get("location"),
            "time_of_day": scene.get("time_of_day"),
            "action_blocks": [str(item) for item in scene.get("action_blocks", []) if isinstance(item, str) and item.strip()],
            "dialogue_blocks": [
                {
                    "character": str(item.get("character") or "").strip(),
                    "text": str(item.get("text") or "").strip(),
                }
                for item in scene.get("dialogue_blocks", [])
                if isinstance(item, dict) and str(item.get("character") or "").strip() and str(item.get("text") or "").strip()
            ],
            "characters_detected": [
                str(item).strip()
                for item in scene.get("characters_detected", [])
                if isinstance(item, str) and str(item).strip()
            ],
        }

    def _extract_heading_parts(self, heading: str) -> tuple[Optional[str], Optional[str]]:
        without_prefix = re.sub(r"^(INT\.?|EXT\.?|INT/EXT\.?|I/E\.?|INT\.\/EXT\.?)\s+", "", heading, flags=re.IGNORECASE).strip()
        if not without_prefix:
            return None, None

        segments = [segment.strip(" -") for segment in re.split(r"\s+-\s+|\s+–\s+|\s+—\s+", without_prefix) if segment.strip(" -")]
        if not segments:
            return without_prefix or None, None

        time_of_day = None
        location_segments = segments[:]
        last_segment = segments[-1].upper()
        if any(hint in last_segment for hint in self._TIME_OF_DAY_HINTS):
            time_of_day = segments[-1].strip()
            location_segments = segments[:-1]

        location = " - ".join(location_segments).strip() or without_prefix
        return location or None, time_of_day

    def _is_scene_heading(self, line: str) -> bool:
        return bool(self._SCENE_HEADING_RE.match(line.strip()))

    def _is_character_cue(self, line: str) -> bool:
        cleaned = self._clean_line(line)
        if not cleaned:
            return False
        if self._is_scene_heading(cleaned):
            return False
        if len(cleaned) > 40:
            return False
        if any(cleaned.endswith(suffix) for suffix in self._TRANSITION_SUFFIXES):
            return False
        if cleaned.startswith("(") and cleaned.endswith(")"):
            return False

        letters = [char for char in cleaned if char.isalpha()]
        if not letters:
            return False

        uppercase_ratio = sum(1 for char in letters if char.isupper()) / len(letters)
        return uppercase_ratio >= 0.8

    def _normalize_heading(self, line: str) -> str:
        return self._clean_line(line).upper()

    def _normalize_character_cue(self, value: str) -> str:
        cleaned = self._clean_line(value)
        if not cleaned:
            return ""
        cleaned = re.sub(r"\s*\([^)]*\)\s*$", "", cleaned).strip()
        parts = [part.capitalize() for part in cleaned.split()]
        return " ".join(parts).strip()

    def _normalize_text(self, text: str) -> str:
        normalized = (text or "").replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.strip()
        return normalized

    def _clean_line(self, value: str) -> str:
        return re.sub(r"\s+", " ", (value or "").strip())
