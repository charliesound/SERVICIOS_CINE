from __future__ import annotations

import json
import logging
import re
import uuid
import unicodedata
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project, ProjectJob
from models.production import ProductionBreakdown
from services.llm.llm_service import ScriptAnalysisLLMOutput, llm_service
from services.job_tracking_service import job_tracking_service
from services.script_document_classifier import SCENE_HEADING_RE
from services.ollama_client_service import OllamaClientService


logger = logging.getLogger(__name__)


class ScriptIntakeService:
    _SEQUENCE_PREFIXES = {"SEC", "SECUENCIA", "SEQ"}
    _SCENE_PREFIXES = {"ESCENA"}
    _TIME_OF_DAY = (
        "DAY", "NIGHT", "MORNING", "EVENING", "AFTERNOON", "DAWN", "DUSK",
        "CONTINUOUS", "LATER", "MOMENTS LATER", "DIA", "DÍA", "NOCHE", "MANANA", "MAÑANA", "TARDE",
    )
    _PROPS_KEYWORDS = {
        "arma": ["pistola", "revólver", "cuchillo", "arma"],
        "transporte": ["coche", "auto", "camión", "tren", "avión", "barco"],
        "tecnología": ["teléfono", "móvil", "tablet", "ordenador", "computadora"],
        "objetos": ["maleta", "bolso", "libro", "carta", "foto", "documento"],
    }
    _LOCATION_KEYWORDS = ["casa", "oficina", "calle", "restaurante", "bar", "hotel", "hospital", "escuela", "aeropuerto"]

    def _normalize_location(self, value: str | None) -> str:
        raw = (value or "").lower()
        raw = re.sub(r"[^a-z0-9áéíóúñ/\s]", " ", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw

    def _strip_accents(self, value: str) -> str:
        return "".join(
            char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
        )

    def _location_summary_key(self, value: str | None) -> str:
        normalized = self._normalize_location(value)
        return self._strip_accents(normalized)

    def _summarize_locations(self, breakdowns: list[dict[str, Any]]) -> list[str]:
        canonical_locations: dict[str, str] = {}
        heading_keys: set[str] = set()

        for breakdown in breakdowns:
            heading_location = str(breakdown.get("location") or "").strip()
            heading_key = self._location_summary_key(heading_location)
            if heading_key:
                canonical_locations.setdefault(heading_key, heading_location)
                heading_keys.add(heading_key)

        for breakdown in breakdowns:
            detected_locations = [
                str(location).strip()
                for location in breakdown.get("locations_detected", [])
                if str(location).strip()
            ]

            for detected in detected_locations:
                detected_key = self._location_summary_key(detected)
                if not detected_key:
                    continue
                if detected_key in heading_keys:
                    continue
                if any(detected_key in heading_key for heading_key in heading_keys):
                    continue
                canonical_locations.setdefault(detected_key, detected)

        return sorted(canonical_locations.values())

    def _scene_markers(self, scene: dict[str, Any]) -> dict[str, Any]:
        action_text = " ".join(scene.get("action_blocks", [])).lower()
        objective = str(scene.get("dramatic_objective") or "").lower()
        conflict_markers = [
            marker
            for marker in ("conflicto", "discute", "amenaza", "crisis", "negocia", "tension", "tensión")
            if marker in action_text or marker in objective
        ]
        action_markers = [
            marker
            for marker in ("corre", "entra", "sale", "persigue", "escapa", "confronta", "golpea")
            if marker in action_text
        ]
        temporal_marker = str(scene.get("time_of_day") or "").strip().lower() or "unspecified"
        location_normalized = self._normalize_location(scene.get("location"))
        return {
            "location_normalized": location_normalized,
            "dramatic_objective": str(scene.get("dramatic_objective") or "").strip() or "advance_story_information",
            "conflict_markers": conflict_markers,
            "action_markers": action_markers,
            "temporal_marker": temporal_marker,
            "characters_detected": list(scene.get("characters_detected") or []),
        }

    def _sequence_affinity(self, scene: dict[str, Any], sequence_scenes: list[dict[str, Any]]) -> int:
        candidate = self._scene_markers(scene)
        last = self._scene_markers(sequence_scenes[-1])
        score = 0
        candidate_number = self._coerce_scene_number(scene)
        last_number = self._coerce_scene_number(sequence_scenes[-1])
        if candidate["location_normalized"] and candidate["location_normalized"] == last["location_normalized"]:
            score += 3
        elif candidate["location_normalized"] and last["location_normalized"] and candidate["location_normalized"] != last["location_normalized"]:
            score -= 2
        same_characters = set(candidate["characters_detected"]).intersection(last["characters_detected"])
        if same_characters:
            score += 2
        if candidate["temporal_marker"] == last["temporal_marker"]:
            score += 1
        if candidate["dramatic_objective"].lower() == str(last["dramatic_objective"]).lower():
            score += 3
        if set(candidate["conflict_markers"]).intersection(last["conflict_markers"]):
            score += 2
        if set(candidate["action_markers"]).intersection(last["action_markers"]):
            score += 1
        if candidate_number and last_number and abs(candidate_number - last_number) == 1:
            score += 2

        objective_changed = bool(candidate["dramatic_objective"] and last["dramatic_objective"] and candidate["dramatic_objective"].lower() != str(last["dramatic_objective"]).lower())
        if objective_changed and not same_characters:
            score -= 4
        if candidate["temporal_marker"] != last["temporal_marker"] and candidate["temporal_marker"] not in {"continuous", "continuo"}:
            score -= 2
        if objective_changed and not same_characters and not set(candidate["conflict_markers"]).intersection(last["conflict_markers"]):
            score -= 2
        return score

    def _has_strong_location_break(self, scene: dict[str, Any], sequence_scenes: list[dict[str, Any]]) -> bool:
        candidate = self._scene_markers(scene)
        last = self._scene_markers(sequence_scenes[-1])
        if not candidate["location_normalized"] or not last["location_normalized"]:
            return False
        if candidate["location_normalized"] == last["location_normalized"]:
            return False
        if candidate["temporal_marker"] != last["temporal_marker"]:
            return True
        # Hard cinematic cut between restaurant and parking-like chase blocks.
        pair = {candidate["location_normalized"], last["location_normalized"]}
        if any("restaurante" in loc for loc in pair) and any("parking" in loc or "coche" in loc for loc in pair):
            return True
        return False

    def _format_sequence_display_name(self, sequence_number: int, scene_numbers: list[int], location_hint: str | None) -> str:
        if not scene_numbers:
            return f"Secuencia {sequence_number}"
        sorted_numbers = sorted(scene_numbers)
        consecutive = all((b - a) == 1 for a, b in zip(sorted_numbers, sorted_numbers[1:]))
        if consecutive:
            scene_part = f"Escenas {sorted_numbers[0]}-{sorted_numbers[-1]}"
        else:
            scene_part = f"Escenas {', '.join(str(n) for n in sorted_numbers)}"
        if location_hint:
            return f"Secuencia {sequence_number} — {location_hint} — {scene_part}"
        return f"Secuencia {sequence_number} — {scene_part}"

    def parse_script(self, script_text: str) -> list[dict[str, Any]]:
        if not script_text:
            return []

        lines = script_text.strip().split("\n")
        scenes = []
        current_scene = None
        action_buffer = []
        current_character: str | None = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                if current_scene:
                    action_buffer.append(line)
                current_character = None
                continue

            heading = self._parse_scene_heading(line)
            if heading:
                if current_scene:
                    current_scene["action_blocks"] = action_buffer[:]
                    scenes.append(current_scene)
                    action_buffer = []

                current_scene = {
                    "scene_number": heading["scene_number"] or (len(scenes) + 1),
                    "scene_id": f"scene_{len(scenes) + 1:03d}",
                    "heading": heading["heading"],
                    "normalized_heading": heading["heading"],
                    "int_ext": heading["int_ext"],
                    "scene_type": heading["int_ext"],
                    "interior_exterior": heading["int_ext"],
                    "location": heading["location"],
                    "time_of_day": heading["time_of_day"],
                    "action_blocks": [],
                    "dialogue_blocks": [],
                    "characters_detected": [],
                    "source_sequence_number": heading.get("sequence_number"),
                    "source_sequence_label": heading.get("sequence_label"),
                }
                current_character = None
                continue

            if current_scene is None:
                continue

            if self._is_character_cue(line):
                char_name = line.strip()
                if char_name not in current_scene["characters_detected"]:
                    current_scene["characters_detected"].append(char_name)
                current_character = char_name
            elif current_character:
                current_scene["dialogue_blocks"].append({
                    "character": current_character,
                    "text": line,
                })
            else:
                action_buffer.append(line)

        if current_scene:
            current_scene["action_blocks"] = action_buffer[:]
            scenes.append(current_scene)

        return scenes

    def _is_character_cue(self, line: str) -> bool:
        return bool(re.match(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s\.']+$", line))

    def _parse_scene_heading(self, line: str) -> dict[str, Any] | None:
        if not SCENE_HEADING_RE.match(line):
            return None

        match = re.match(
            r"^\s*(?:(?P<number>\d{1,4})\s*[\.:\)-]?\s+)?(?:(?P<prefix>SEC(?:UENCIA)?|SEQ|ESCENA)\.?\s*(?P<prefix_number>\d{1,4})\s+)?(?P<int_ext>INT\.?\s*/\s*EXT\.?|EXT\.?\s*/\s*INT\.?|INT\.?|INTERIOR|EXT\.?|EXTERIOR|I/E\.?)\s+(?P<body>.+?)\s*$",
            line,
            re.IGNORECASE,
        )
        if not match:
            return None

        scene_number = 0
        number_group = match.group("number")
        if number_group:
            try:
                scene_number = int(number_group)
            except ValueError:
                scene_number = 0

        sequence_number = 0
        sequence_label: str | None = None
        prefix_group = (match.group("prefix") or "").strip().upper()
        prefix_number_group = match.group("prefix_number")
        if prefix_number_group:
            try:
                prefix_number = int(prefix_number_group)
            except ValueError:
                prefix_number = 0
            if prefix_group in self._SEQUENCE_PREFIXES:
                sequence_number = prefix_number
                sequence_label = f"Sec {prefix_number}"
                if scene_number == 0:
                    scene_number = prefix_number
            elif prefix_group in self._SCENE_PREFIXES and scene_number == 0:
                scene_number = prefix_number

        int_ext_raw = (match.group("int_ext") or "INT").upper().replace(" ", "").rstrip(".")
        body = (match.group("body") or "").strip()

        location = body.rstrip(" .-")
        time_of_day = "DAY"
        for tod in sorted(self._TIME_OF_DAY, key=len, reverse=True):
            tod_match = re.search(
                rf"(?:^|[\s\.-]){re.escape(tod)}\.?$",
                body,
                re.IGNORECASE,
            )
            if not tod_match:
                continue
            location = body[:tod_match.start()].rstrip(" .-") or body.rstrip(" .-")
            time_of_day = self._detect_time_of_day(tod)
            break

        normalized_int_ext = "INT/EXT" if ("INT/EXT" in int_ext_raw or "EXT/INT" in int_ext_raw or "I/E" in int_ext_raw) else int_ext_raw
        display_int_ext = f"{normalized_int_ext}." if normalized_int_ext in {"INT", "EXT"} else normalized_int_ext
        normalized_heading = f"{display_int_ext} {body}".strip()
        if number_group and not prefix_group:
            normalized_heading = line.strip()

        return {
            "scene_number": scene_number or 0,
            "heading": normalized_heading,
            "int_ext": normalized_int_ext,
            "location": location,
            "time_of_day": time_of_day,
            "sequence_number": sequence_number or None,
            "sequence_label": sequence_label,
        }

    def _detect_time_of_day(self, text: str) -> str:
        text_upper = text.upper()
        for tod in self._TIME_OF_DAY:
            if tod in text_upper:
                return tod
        return "DAY"

    def build_scene_breakdowns(self, scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        breakdowns = []
        for scene in scenes:
            action_text = " ".join(scene.get("action_blocks", []))
            dialogue_text = " ".join([d.get("text", "") for d in scene.get("dialogue_blocks", [])])
            combined = (action_text + " " + dialogue_text).lower()

            props = []
            for category, keywords in self._PROPS_KEYWORDS.items():
                for kw in keywords:
                    if kw in combined:
                        props.append(kw)

            locations = []
            for loc in self._LOCATION_KEYWORDS:
                if loc in combined:
                    locations.append(loc)
            heading_location = str(scene.get("location") or "").strip()
            if heading_location:
                locations.append(heading_location)

            complexity_flags = []
            if len(scene.get("characters_detected", [])) > 5:
                complexity_flags.append("high_cast")
            if len(scene.get("action_blocks", [])) > 10:
                complexity_flags.append("high_action")
            if scene.get("int_ext") == "EXT":
                complexity_flags.append("exterior")
            if any(kw in combined for kw in ["coche", "auto", "persigue", "accidente"]):
                complexity_flags.append("stunts_or_vehicle")

            breakdowns.append({
                "scene_id": scene.get("scene_id"),
                "heading": scene.get("heading"),
                "int_ext": scene.get("int_ext"),
                "scene_type": scene.get("scene_type") or scene.get("int_ext"),
                "location": scene.get("location"),
                "time_of_day": scene.get("time_of_day"),
                "characters": scene.get("characters_detected", []),
                "dialogue_count": len(scene.get("dialogue_blocks", [])),
                "action_lines": len(scene.get("action_blocks", [])),
                "props_detected": list(set(props)),
                "locations_detected": list(set(locations)),
                "complexity_flags": complexity_flags,
            })

        return breakdowns

    def build_department_breakdown(
        self,
        breakdowns: list[dict[str, Any]],
        total_sequences: int = 0,
    ) -> dict[str, Any]:
        characters = set()
        props = set()
        ext_count = 0
        int_count = 0
        night_count = 0
        high_action_count = 0
        summarized_locations = self._summarize_locations(breakdowns)

        for bd in breakdowns:
            characters.update(bd.get("characters", []))
            props.update(bd.get("props_detected", []))
            if bd.get("int_ext") == "EXT":
                ext_count += 1
            if bd.get("int_ext") == "INT":
                int_count += 1
            if bd.get("time_of_day") in {"NIGHT", "NOCHE"}:
                night_count += 1
            if "high_action" in bd.get("complexity_flags", []):
                high_action_count += 1

        total_scenes = len(breakdowns)

        return {
            "summary": {
                "total_scenes": total_scenes,
                "total_sequences": total_sequences,
                "total_characters": len(characters),
                "total_locations": len(summarized_locations),
                "int_scenes": int_count,
                "ext_scenes": ext_count,
                "night_scenes": night_count,
            },
            "departments": {
                "direccion": {
                    "notes": f"Dirigir {total_scenes} escenas, {len(characters)} personajes",
                    "flags": [],
                },
                "produccion": {
                    "notes": f"Producir {total_scenes} escenas, {len(summarized_locations)} ubicaciones",
                    "flags": ["multiple_locations" if len(summarized_locations) > 3 else "single_location"],
                },
                "cast": {
                    "characters": list(characters),
                    "estimated_cast": len(characters),
                    "notes": f"{len(characters)} personajes requiere casting",
                },
                "localizaciones": {
                    "locations": summarized_locations,
                    "estimated_days": max(1, len(summarized_locations)),
                    "notes": f"{len(summarized_locations)} ubicaciones diferentes",
                },
                "arte": {
                    "props": list(props),
                    "sets_required": len(props),
                    "notes": f"{len(props)} props a sourcing",
                },
                "vestuario": {
                    "estimated_costumes": len(characters),
                    "notes": f"{len(characters)} vestuario/personaje",
                },
                "camara": {
                    "exterior_ratio": round(ext_count / max(1, total_scenes), 2),
                    "notes": f"{ext_count} escenas externas",
                },
                "iluminacion": {
                    "night_ratio": round(night_count / max(1, total_scenes), 2),
                    "notes": f"{night_count} escenas nocturnas",
                },
                "sonido": {
                    "dialogue_scenes": sum(1 for b in breakdowns if b.get("dialogue_count", 0) > 0),
                    "notes": "Captura de diálogo en post",
                },
                "postproduccion": {
                    "estimated_hours": total_scenes * 2,
                    "complexity": "high" if high_action_count > 3 else "medium" if high_action_count > 0 else "standard",
                    "notes": f"Edición de {total_scenes} escenas",
                },
            },
        }

    def build_sequence_blocks(self, scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not scenes:
            return []

        working_scenes = sorted(
            list(scenes),
            key=lambda s: self._coerce_scene_number(s),
        )
        groups: list[list[dict[str, Any]]] = []
        for scene in working_scenes:
            explicit_sequence_number = self._coerce_source_sequence_number(scene)
            if not groups:
                groups.append([scene])
                continue
            if explicit_sequence_number:
                matching_group = next(
                    (
                        group for group in groups
                        if self._coerce_source_sequence_number(group[0]) == explicit_sequence_number
                    ),
                    None,
                )
                if matching_group is not None:
                    matching_group.append(scene)
                else:
                    groups.append([scene])
                continue
            best_index = -1
            best_score = -10
            for idx, group in enumerate(groups):
                affinity = self._sequence_affinity(scene, group)
                if affinity > best_score:
                    best_score = affinity
                    best_index = idx
            if best_index >= 0 and best_score >= 3 and not self._has_strong_location_break(scene, groups[best_index]):
                # prevent overly broad mixed-location groups unless links are explicit
                existing_locations = {
                    self._scene_markers(existing).get("location_normalized")
                    for existing in groups[best_index]
                    if self._scene_markers(existing).get("location_normalized")
                }
                incoming_location = self._scene_markers(scene).get("location_normalized")
                projected = set(existing_locations)
                if incoming_location:
                    projected.add(incoming_location)
                markers_incoming = self._scene_markers(scene)
                markers_last = self._scene_markers(groups[best_index][-1])
                has_causal_continuity = (
                    markers_incoming.get("dramatic_objective")
                    and markers_incoming.get("dramatic_objective") == markers_last.get("dramatic_objective")
                    and markers_incoming.get("temporal_marker") == markers_last.get("temporal_marker")
                    and bool(set(markers_incoming.get("characters_detected") or []).intersection(markers_last.get("characters_detected") or []))
                )
                incoming_number = self._coerce_scene_number(scene)
                last_number = self._coerce_scene_number(groups[best_index][-1])
                has_linear_continuity = (
                    incoming_number and last_number and abs(incoming_number - last_number) == 1
                    and markers_incoming.get("temporal_marker") == markers_last.get("temporal_marker")
                )
                if len(projected) <= 2 or (len(projected) <= 3 and (has_causal_continuity or has_linear_continuity)):
                    groups[best_index].append(scene)
                else:
                    groups.append([scene])
            else:
                groups.append([scene])

        sequence_blocks: list[dict[str, Any]] = []
        for chunk in groups:
            explicit_sequence_number = self._coerce_source_sequence_number(chunk[0])
            sequence_number = explicit_sequence_number or (len(sequence_blocks) + 1)
            included_scene_numbers = [self._coerce_scene_number(scene) for scene in chunk]
            scene_start = min(included_scene_numbers) if included_scene_numbers else 0
            scene_end = max(included_scene_numbers) if included_scene_numbers else 0
            characters = sorted(
                {
                    character
                    for scene in chunk
                    for character in scene.get("characters_detected", [])
                    if character
                }
            )
            first_scene = chunk[0]
            source_label = str(chunk[0].get("source_sequence_label") or f"Secuencia {sequence_number}")
            location_hint = str(first_scene.get("location") or "").strip() or None
            display_name = self._format_sequence_display_name(sequence_number, included_scene_numbers, location_hint)
            title = display_name
            summary = "; ".join(
                scene.get("heading") or f"Scene {self._coerce_scene_number(scene)}"
                for scene in chunk
            )[:220]
            sequence_id = f"seq_{sequence_number:03d}"
            location_groups = sorted({self._normalize_location(scene.get("location")) for scene in chunk if self._normalize_location(scene.get("location"))})
            continuity_groups = sorted({f"{self._normalize_location(scene.get('location'))}__{str(scene.get('time_of_day') or '').lower()}" for scene in chunk if self._normalize_location(scene.get("location"))})
            conflict_summary = ", ".join(sorted({marker for scene in chunk for marker in self._scene_markers(scene)["conflict_markers"]}))
            for scene in chunk:
                markers = self._scene_markers(scene)
                scene["sequence_id"] = sequence_id
                scene["sequence_order"] = sequence_number
                scene["sequence_display_name"] = display_name
                scene["location_normalized"] = markers["location_normalized"]
                scene["dramatic_objective"] = markers["dramatic_objective"]
                scene["conflict_markers"] = markers["conflict_markers"]
                scene["action_markers"] = markers["action_markers"]
                scene["temporal_marker"] = markers["temporal_marker"]
                scene["location_group"] = markers["location_normalized"]
                scene["continuity_group"] = f"{markers['location_normalized']}__{markers['temporal_marker']}"
                scene["related_scene_numbers"] = [number for number in included_scene_numbers if number != self._coerce_scene_number(scene)]
            estimated_shots = max(1, sum(max(1, len(scene.get("action_blocks", [])[:3])) for scene in chunk))
            sequence_blocks.append(
                {
                    "sequence_id": sequence_id,
                    "sequence_number": sequence_number,
                    "title": display_name,
                    "summary": summary,
                    "included_scenes": included_scene_numbers,
                    "scene_numbers": included_scene_numbers,
                    "scene_count": len(included_scene_numbers),
                    "source_sequence_label": source_label,
                    "source_scene_start": scene_start,
                    "source_scene_end": scene_end,
                    "display_name": display_name,
                    "characters": characters,
                    "location_groups": location_groups,
                    "continuity_groups": continuity_groups,
                    "dramatic_purpose": str(first_scene.get("dramatic_objective") or "advance_story_information"),
                    "conflict_summary": conflict_summary,
                    "location": first_scene.get("location"),
                    "emotional_arc": self._sequence_arc(chunk),
                    "estimated_duration": len(chunk) * 60,
                    "estimated_shots": estimated_shots,
                }
            )
        return sequence_blocks

    def _coerce_scene_number(self, scene: dict[str, Any]) -> int:
        value = scene.get("scene_number")
        if value is not None:
            try:
                return int(value)
            except Exception:
                pass
        scene_id = str(scene.get("scene_id") or "")
        match = re.search(r"(\d+)", scene_id)
        if match:
            return int(match.group(1))
        return 0

    def _coerce_source_sequence_number(self, scene: dict[str, Any]) -> int:
        value = scene.get("source_sequence_number")
        if value is not None:
            try:
                return int(value)
            except Exception:
                return 0
        return 0

    def _sequence_arc(self, scenes: list[dict[str, Any]]) -> str:
        text = " ".join(" ".join(scene.get("action_blocks", [])) for scene in scenes).lower()
        if any(token in text for token in ("fight", "run", "chase", "crash", "scream")):
            return "escalation"
        if any(token in text for token in ("confess", "remember", "observe", "silence")):
            return "introspection"
        return "setup"


class AnalysisService:
    def __init__(self):
        self.script_intake = ScriptIntakeService()

    async def _run_llm_analysis_or_none(self, script_text: str) -> tuple[ScriptAnalysisLLMOutput | None, dict[str, Any]]:
        settings = llm_service._settings()
        requested_provider = str(settings.get("provider", "ollama")).strip().lower()
        requested_model = OllamaClientService.get_model_for_task("script_analysis", settings)
        trace = {
            "analysis_provider": requested_provider,
            "analysis_model": requested_model if requested_provider == "ollama" else None,
            "fallback_used": False,
            "fallback_reason": None,
        }
        if not llm_service.is_enabled_for("script_analysis_provider"):
            trace["fallback_used"] = True
            trace["fallback_reason"] = "provider_disabled_or_not_ollama"
            return None, trace
        try:
            return await llm_service.analyze_script(script_text), trace
        except Exception as exc:
            if llm_service.should_fallback(exc):
                trace["fallback_used"] = True
                trace["fallback_reason"] = f"ollama_error:{type(exc).__name__}"
                return None, trace
            raise

    async def run_analysis(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        script_text: str,
        document_context: dict[str, Any] | None = None,
        structured_payload: dict[str, Any] | None = None,
        job: Optional[ProjectJob] = None,
    ) -> dict[str, Any]:
        normalized_script = (script_text or "").strip()
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=10, stage="Validando proyecto y documento", code="validating_project"
            )

        llm_output, engine_trace = await self._run_llm_analysis_or_none(script_text)
        heuristic_scenes = self.script_intake.parse_script(script_text)
        llm_scenes = [scene.model_dump() for scene in llm_output.scenes] if llm_output and llm_output.scenes else []
        heuristic_has_explicit_sequences = any(scene.get("source_sequence_number") for scene in heuristic_scenes)
        scenes = llm_scenes or heuristic_scenes
        if heuristic_has_explicit_sequences and len(heuristic_scenes) >= len(llm_scenes):
            scenes = heuristic_scenes
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=35, stage="Clasificando documento y escenas", code="classifying_document"
            )

        document_payload = document_context or {}
        persisted_structured_payload = structured_payload or {}

        heuristic_sequences = self.script_intake.build_sequence_blocks(heuristic_scenes)
        sequences = [sequence.model_dump() for sequence in llm_output.sequences] if llm_output and llm_output.sequences else self.script_intake.build_sequence_blocks(scenes)
        if heuristic_sequences and heuristic_has_explicit_sequences and len(heuristic_sequences) >= len(sequences):
            sequences = heuristic_sequences

        breakdowns = self.script_intake.build_scene_breakdowns(scenes)
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=50, stage="Extrayendo escenas y desglose", code="extracting_scenes"
            )

        department_breakdown = self.script_intake.build_department_breakdown(
            breakdowns,
            total_sequences=len(sequences),
        )
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=65, stage="Analizando desglose por departamentos", code="analyzing_breakdown"
            )
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=80, stage="Construyendo payload estructurado", code="building_structured_payload"
            )

        warnings: list[str] = []
        analysis_status = "completed"
        analysis_engine = "ollama" if llm_output else "heuristic"
        if engine_trace.get("fallback_used") and not llm_output:
            analysis_engine = "heuristic"
        if not normalized_script:
            analysis_status = "basic_empty"
            warnings.append("Script vacio. No hay texto para analizar.")
        elif not scenes:
            analysis_status = "degraded"
            warnings.append("No se detectaron escenas. Revisa formato de encabezados o parser.")

        analysis_trace = {
            "analysis_engine": analysis_engine,
            "analysis_provider": engine_trace.get("analysis_provider"),
            "analysis_model": engine_trace.get("analysis_model") if llm_output else engine_trace.get("analysis_model"),
            "fallback_used": bool(engine_trace.get("fallback_used")),
            "fallback_reason": engine_trace.get("fallback_reason"),
        }

        logger.info(
            "script_analysis_engine project_id=%s requested_provider=%s engine=%s model=%s fallback_used=%s fallback_reason=%s",
            project_id,
            engine_trace.get("analysis_provider"),
            analysis_trace["analysis_engine"],
            analysis_trace.get("analysis_model"),
            analysis_trace["fallback_used"],
            analysis_trace.get("fallback_reason"),
        )

        analysis_data = {
            "project_id": project_id,
            "organization_id": organization_id,
            "status": analysis_status,
            "document": document_payload,
            "structured_payload": persisted_structured_payload,
            "summary": department_breakdown,
            "tone": llm_output.tone if llm_output else "",
            "llm_summary": llm_output.summary if llm_output else "",
            "production_needs": llm_output.production_needs if llm_output else [],
            "storyboard_suggestions": llm_output.storyboard_suggestions if llm_output else [],
            "analysis_engine": analysis_trace["analysis_engine"],
            **analysis_trace,
            "scenes": scenes,
            "breakdowns": breakdowns,
            "department_breakdown": department_breakdown,
            "sequences": sequences,
            "warnings": warnings,
            "metadata": {
                "total_scenes": len(scenes),
                "total_characters": department_breakdown["summary"]["total_characters"],
                "total_locations": department_breakdown["summary"]["total_locations"],
                "doc_type": document_payload.get("doc_type"),
                "confidence_score": document_payload.get("confidence_score"),
                "source_kind": document_payload.get("source_kind"),
                "analysis_engine": analysis_trace["analysis_engine"],
                "analysis_provider": analysis_trace["analysis_provider"],
                "analysis_model": analysis_trace["analysis_model"],
                "fallback_used": analysis_trace["fallback_used"],
                "fallback_reason": analysis_trace["fallback_reason"],
                "warning_count": len(warnings),
            },
        }

        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=90, stage="Persistiendo resultados", code="persisting_results"
            )

        result = await db.execute(
            select(ProductionBreakdown).where(
                ProductionBreakdown.project_id == project_id
            )
        )
        existing = result.scalar_one_or_none()

        breakdown_id = str(uuid.uuid4())
        breakdown = ProductionBreakdown(
            id=breakdown_id,
            project_id=project_id,
            organization_id=organization_id,
            script_text=script_text[:10000] if script_text else None,
            breakdown_json=json.dumps(analysis_data, ensure_ascii=False),
            status=analysis_status,
        )

        if existing:
            existing.script_text = breakdown.script_text
            existing.breakdown_json = breakdown.breakdown_json
            existing.status = analysis_status
            breakdown_id = existing.id
        else:
            db.add(breakdown)

        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=100, stage="Análisis completado", code="completed"
            )

        await db.commit()

        return {
            "breakdown_id": breakdown_id,
            "status": analysis_status,
            "project_id": project_id,
            "organization_id": organization_id,
            "document": document_payload,
            "structured_payload": persisted_structured_payload,
            "summary": department_breakdown,
            "scenes_count": len(scenes),
            "characters_count": department_breakdown["summary"]["total_characters"],
            "locations_count": department_breakdown["summary"]["total_locations"],
            "breakdowns": breakdowns[:10],
            "department_breakdown": department_breakdown,
            "warnings": warnings,
            **analysis_trace,
        }

    async def get_summary(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> dict[str, Any]:
        result = await db.execute(
            select(ProductionBreakdown).where(
                ProductionBreakdown.project_id == project_id
            )
        )
        breakdown = result.scalar_one_or_none()

        if not breakdown:
            return {"status": "not_found", "message": "No analysis found"}

        try:
            breakdown_data = json.loads(breakdown.breakdown_json) if breakdown.breakdown_json else {}
        except:
            breakdown_data = {}

        return {
            "status": breakdown.status,
            "project_id": breakdown_data.get("project_id") or project_id,
            "organization_id": breakdown_data.get("organization_id"),
            "document_id": breakdown_data.get("document", {}).get("document_id"),
            "doc_type": breakdown_data.get("document", {}).get("doc_type"),
            "confidence_score": breakdown_data.get("document", {}).get("confidence_score"),
            "source_kind": breakdown_data.get("document", {}).get("source_kind"),
            "scenes_count": breakdown_data.get("metadata", {}).get("total_scenes", 0),
            "characters_count": breakdown_data.get("metadata", {}).get("total_characters", 0),
            "locations_count": breakdown_data.get("metadata", {}).get("total_locations", 0),
            "analysis_engine": breakdown_data.get("analysis_engine") or breakdown_data.get("metadata", {}).get("analysis_engine"),
            "analysis_provider": breakdown_data.get("analysis_provider") or breakdown_data.get("metadata", {}).get("analysis_provider"),
            "analysis_model": breakdown_data.get("analysis_model") or breakdown_data.get("metadata", {}).get("analysis_model"),
            "fallback_used": breakdown_data.get("fallback_used") if "fallback_used" in breakdown_data else breakdown_data.get("metadata", {}).get("fallback_used"),
            "fallback_reason": breakdown_data.get("fallback_reason") or breakdown_data.get("metadata", {}).get("fallback_reason"),
            "summary": breakdown_data.get("summary")
            or breakdown_data.get("department_breakdown", {}),
            "warnings": breakdown_data.get("warnings", []),
            "structured_payload": breakdown_data.get("structured_payload", {}),
            "sequences_count": len(breakdown_data.get("sequences", [])),
            "generated_at": breakdown.created_at.isoformat() if breakdown.created_at else None,
            "updated_at": breakdown.updated_at.isoformat() if breakdown.updated_at else None,
        }

    async def get_scenes(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> list[dict[str, Any]]:
        result = await db.execute(
            select(ProductionBreakdown).where(
                ProductionBreakdown.project_id == project_id
            )
        )
        breakdown = result.scalar_one_or_none()

        if not breakdown:
            return []

        try:
            breakdown_data = json.loads(breakdown.breakdown_json) if breakdown.breakdown_json else {}
        except:
            breakdown_data = []

        return breakdown_data.get("breakdowns", [])

    async def get_departments(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> dict[str, Any]:
        result = await db.execute(
            select(ProductionBreakdown).where(
                ProductionBreakdown.project_id == project_id
            )
        )
        breakdown = result.scalar_one_or_none()

        if not breakdown:
            return {"error": "No breakdown found"}

        try:
            breakdown_data = json.loads(breakdown.breakdown_json) if breakdown.breakdown_json else {}
        except:
            return {"error": "Invalid breakdown data"}

        return breakdown_data.get("department_breakdown", {})


script_intake_service = ScriptIntakeService()
analysis_service = AnalysisService()
