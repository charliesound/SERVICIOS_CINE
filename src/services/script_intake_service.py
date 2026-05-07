from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project, ProjectJob
from models.production import ProductionBreakdown
from services.llm.llm_service import ScriptAnalysisLLMOutput, llm_service
from services.job_tracking_service import job_tracking_service
from services.script_document_classifier import SCENE_HEADING_RE


class ScriptIntakeService:
    _TIME_OF_DAY = (
        "DAY", "NIGHT", "MORNING", "EVENING", "AFTERNOON", "DAWN", "DUSK",
        "CONTINUOUS", "LATER", "MOMENTS LATER", "DIA", "NOCHE", "MANANA", "MAÑANA", "TARDE",
    )
    _PROPS_KEYWORDS = {
        "arma": ["pistola", "revólver", "cuchillo", "arma"],
        "transporte": ["coche", "auto", "camión", "tren", "avión", "barco"],
        "tecnología": ["teléfono", "móvil", "tablet", "ordenador", "computadora"],
        "objetos": ["maleta", "bolso", "libro", "carta", "foto", "documento"],
    }
    _LOCATION_KEYWORDS = ["casa", "oficina", "calle", "restaurante", "bar", "hotel", "hospital", "escuela", "aeropuerto"]

    def parse_script(self, script_text: str) -> list[dict[str, Any]]:
        if not script_text:
            return []

        lines = script_text.strip().split("\n")
        scenes = []
        current_scene = None
        action_buffer = []

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                if current_scene:
                    action_buffer.append(line)
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
                    "int_ext": heading["int_ext"],
                    "location": heading["location"],
                    "time_of_day": heading["time_of_day"],
                    "action_blocks": [],
                    "dialogue_blocks": [],
                    "characters_detected": [],
                }
                continue

            if current_scene is None:
                continue

            if self._is_character_cue(line):
                char_name = re.sub(r"^\(([^)]+)\).*$", r"\1", line).strip()
                current_scene["characters_detected"].append(char_name)
                current_scene["dialogue_blocks"].append({
                    "character": char_name,
                    "text": line[len(char_name) + 2:].strip() if len(char_name) + 2 < len(line) else ""
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
            r"^\s*(?:(?P<number>\d{1,4})[\.:\)-]?\s+)?(?P<int_ext>INT\.?|INTERIOR|EXT\.?|EXTERIOR|INT/EXT\.?|I/E\.?)\s+(?P<body>.+?)\s*$",
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

        int_ext_raw = (match.group("int_ext") or "INT").upper().rstrip(".")
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

        return {
            "scene_number": scene_number or 0,
            "heading": line,
            "int_ext": "INT/EXT" if "INT/EXT" in int_ext_raw or "I/E" in int_ext_raw else int_ext_raw,
            "location": location,
            "time_of_day": time_of_day,
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
    ) -> dict[str, Any]:
        characters = set()
        locations = set()
        props = set()
        ext_count = 0
        night_count = 0
        high_action_count = 0

        for bd in breakdowns:
            characters.update(bd.get("characters", []))
            locations.update(bd.get("locations_detected", []))
            props.update(bd.get("props_detected", []))
            if bd.get("int_ext") == "EXT":
                ext_count += 1
            if bd.get("time_of_day") in {"NIGHT", "NOCHE"}:
                night_count += 1
            if "high_action" in bd.get("complexity_flags", []):
                high_action_count += 1

        total_scenes = len(breakdowns)

        return {
            "summary": {
                "total_scenes": total_scenes,
                "total_characters": len(characters),
                "total_locations": len(locations),
                "ext_scenes": ext_count,
                "night_scenes": night_count,
            },
            "departments": {
                "direccion": {
                    "notes": f"Dirigir {total_scenes} escenas, {len(characters)} personajes",
                    "flags": [],
                },
                "produccion": {
                    "notes": f"Producir {total_scenes} escenas, {len(locations)} ubicaciones",
                    "flags": ["multiple_locations" if len(locations) > 3 else "single_location"],
                },
                "cast": {
                    "characters": list(characters),
                    "estimated_cast": len(characters),
                    "notes": f"{len(characters)} personajes requiere casting",
                },
                "localizaciones": {
                    "locations": list(locations),
                    "estimated_days": max(1, len(locations)),
                    "notes": f"{len(locations)} ubicaciones diferentes",
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

        sequence_blocks: list[dict[str, Any]] = []
        block_size = 3
        for index in range(0, len(scenes), block_size):
            chunk = scenes[index:index + block_size]
            sequence_number = len(sequence_blocks) + 1
            included_scene_numbers = [self._coerce_scene_number(scene) for scene in chunk]
            characters = sorted(
                {
                    character
                    for scene in chunk
                    for character in scene.get("characters_detected", [])
                    if character
                }
            )
            first_scene = chunk[0]
            title = first_scene.get("location") or first_scene.get("heading") or f"Sequence {sequence_number}"
            summary = "; ".join(
                scene.get("heading") or f"Scene {self._coerce_scene_number(scene)}"
                for scene in chunk
            )[:220]
            estimated_shots = max(1, sum(max(1, len(scene.get("action_blocks", [])[:3])) for scene in chunk))
            sequence_blocks.append(
                {
                    "sequence_id": f"seq_{sequence_number:02d}",
                    "sequence_number": sequence_number,
                    "title": title,
                    "summary": summary,
                    "included_scenes": included_scene_numbers,
                    "characters": characters,
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

    async def _run_llm_analysis_or_none(self, script_text: str) -> ScriptAnalysisLLMOutput | None:
        if not llm_service.is_enabled_for("script_analysis_provider"):
            return None
        try:
            return await llm_service.analyze_script(script_text)
        except Exception as exc:
            if llm_service.should_fallback(exc):
                return None
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
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=10, stage="Validando proyecto y documento", code="validating_project"
            )

        llm_output = await self._run_llm_analysis_or_none(script_text)
        scenes = [scene.model_dump() for scene in llm_output.scenes] if llm_output and llm_output.scenes else self.script_intake.parse_script(script_text)
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=35, stage="Clasificando documento y escenas", code="classifying_document"
            )

        breakdowns = self.script_intake.build_scene_breakdowns(scenes)
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=50, stage="Extrayendo escenas y desglose", code="extracting_scenes"
            )

        department_breakdown = self.script_intake.build_department_breakdown(breakdowns)
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=65, stage="Analizando desglose por departamentos", code="analyzing_breakdown"
            )

        document_payload = document_context or {}
        persisted_structured_payload = structured_payload or {}

        sequences = [sequence.model_dump() for sequence in llm_output.sequences] if llm_output and llm_output.sequences else self.script_intake.build_sequence_blocks(scenes)
        if job:
            await job_tracking_service.update_progress(
                db, job=job, percent=80, stage="Construyendo payload estructurado", code="building_structured_payload"
            )

        analysis_data = {
            "project_id": project_id,
            "organization_id": organization_id,
            "status": "completed",
            "document": document_payload,
            "structured_payload": persisted_structured_payload,
            "summary": department_breakdown,
            "tone": llm_output.tone if llm_output else "",
            "llm_summary": llm_output.summary if llm_output else "",
            "production_needs": llm_output.production_needs if llm_output else [],
            "storyboard_suggestions": llm_output.storyboard_suggestions if llm_output else [],
            "analysis_engine": "ollama" if llm_output else "heuristic",
            "scenes": scenes,
            "breakdowns": breakdowns,
            "department_breakdown": department_breakdown,
            "sequences": sequences,
            "metadata": {
                "total_scenes": len(scenes),
                "total_characters": department_breakdown["summary"]["total_characters"],
                "total_locations": department_breakdown["summary"]["total_locations"],
                "doc_type": document_payload.get("doc_type"),
                "confidence_score": document_payload.get("confidence_score"),
                "source_kind": document_payload.get("source_kind"),
                "analysis_engine": "ollama" if llm_output else "heuristic",
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
            status="completed",
        )

        if existing:
            existing.script_text = breakdown.script_text
            existing.breakdown_json = breakdown.breakdown_json
            existing.status = "completed"
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
            "status": "completed",
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
            "summary": breakdown_data.get("summary")
            or breakdown_data.get("department_breakdown", {}),
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
