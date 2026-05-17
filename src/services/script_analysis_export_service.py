from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.production import ProductionBreakdown
from services.script_synopsis_service import ScriptSynopsisService


EXPORT_VERSION = "1.0"
EXPORT_SOURCE = "cid_script_analysis_pro"


def _dict_or_empty(data: Any) -> dict:
    return data if isinstance(data, dict) else {}


def _list_or_empty(data: Any) -> list:
    return data if isinstance(data, list) else []


def _str_or_empty(data: Any) -> str:
    return str(data) if data else ""


def _parse_breakdown(breakdown: ProductionBreakdown) -> dict[str, Any]:
    if not breakdown or not breakdown.breakdown_json:
        return {}
    try:
        return json.loads(breakdown.breakdown_json)
    except (json.JSONDecodeError, TypeError):
        return {}


class ScriptAnalysisExportService:
    def __init__(self) -> None:
        self.synopsis_service = ScriptSynopsisService()

    async def build_export_payload(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> dict[str, Any] | None:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            return None

        result = await db.execute(
            select(ProductionBreakdown).where(
                ProductionBreakdown.project_id == project_id
            )
        )
        breakdown = result.scalar_one_or_none()
        breakdown_data = _parse_breakdown(breakdown)

        has_analysis = breakdown is not None and breakdown.status == "completed"
        has_script = bool(project.script_text)

        synopsis_result = None
        if has_script:
            synopsis_result = self.synopsis_service.analyze_script(
                project.script_text
            )
        synopsis = synopsis_result.synopsis if synopsis_result else None

        scenes = _list_or_empty(breakdown_data.get("scenes"))
        sequences_data = _list_or_empty(breakdown_data.get("sequences"))
        breakdowns = _list_or_empty(breakdown_data.get("breakdowns"))
        department_bd = _dict_or_empty(breakdown_data.get("department_breakdown"))
        metadata = _dict_or_empty(breakdown_data.get("metadata"))
        structured_payload = _dict_or_empty(
            breakdown_data.get("structured_payload")
        )
        summary = breakdown_data.get("summary") or department_bd

        characters: list[str] = []
        locations: list[str] = []
        if synopsis:
            characters = synopsis.main_characters
            locations = synopsis.main_locations
        if not characters:
            for scene in scenes:
                detected = scene.get("characters_detected") or scene.get("characters") or []
                characters.extend(d for d in detected if d not in characters)
        if not locations:
            for scene in scenes:
                loc = scene.get("location") or ""
                if loc and loc not in locations:
                    locations.append(loc)

        warnings: list[str] = []
        if synopsis_result:
            warnings.extend(synopsis_result.warnings)
        if not has_analysis:
            warnings.append("no_analysis_found")
        if not has_script:
            warnings.append("no_script_text")

        payload: dict[str, Any] = {
            "export_version": EXPORT_VERSION,
            "source": EXPORT_SOURCE,
            "project_id": project_id,
            "project_name": project.name if project else "",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "has_analysis": has_analysis,
            "has_script": has_script,
            "warnings": warnings,
        }

        if has_script:
            payload["script_text_length"] = len(project.script_text) if project.script_text else 0

        if synopsis:
            payload["logline"] = synopsis.logline
            payload["synopsis_short"] = synopsis.synopsis_short
            payload["synopsis_extended"] = synopsis.synopsis_extended
            payload["premise"] = synopsis.premise
            payload["theme"] = synopsis.theme
            payload["genre"] = synopsis.genre
            payload["tone"] = synopsis.tone
            payload["dramatic_structure"] = synopsis.dramatic_structure
            payload["production_notes"] = synopsis.production_notes
            payload["recommended_storyboard_sequences"] = (
                synopsis.recommended_storyboard_sequences
            )

        if breakdown_data:
            analysis_engine = breakdown_data.get("analysis_engine") or metadata.get("analysis_engine") or ""
            payload["analysis_engine"] = analysis_engine
            payload["analysis_summary"] = summary
            payload["tone_raw"] = _str_or_empty(breakdown_data.get("tone"))
            payload["llm_summary"] = _str_or_empty(
                breakdown_data.get("llm_summary")
            )
            payload["production_needs"] = _list_or_empty(
                breakdown_data.get("production_needs")
            )
            payload["storyboard_suggestions"] = _list_or_empty(
                breakdown_data.get("storyboard_suggestions")
            )

        if metadata:
            payload["metadata"] = metadata

        payload["characters"] = characters
        payload["locations"] = locations
        payload["scenes"] = scenes
        payload["sequences"] = sequences_data
        payload["breakdowns"] = breakdowns
        payload["department_breakdown"] = department_bd
        payload["structured_payload"] = structured_payload

        if breakdown:
            payload["analysis_created_at"] = (
                breakdown.created_at.isoformat()
                if breakdown.created_at
                else None
            )
            payload["analysis_updated_at"] = (
                breakdown.updated_at.isoformat()
                if breakdown.updated_at
                else None
            )

        return payload

    def to_markdown(self, payload: dict[str, Any]) -> str:
        lines: list[str] = []
        name = payload.get("project_name") or payload.get("project_id") or "Untitled"
        lines.append(f"# CID Script Analysis Pro — {name}")
        lines.append("")
        lines.append(f"> Generated: {payload.get('generated_at', '')}")
        lines.append(f"> Source: {payload.get('source', '')}")
        lines.append(f"> Version: {payload.get('export_version', '')}")
        lines.append("")

        warnings = payload.get("warnings", [])
        if warnings:
            lines.append("## Warnings")
            for w in warnings:
                lines.append(f"- {w}")
            lines.append("")

        if payload.get("logline"):
            lines.append("## Logline")
            lines.append("")
            lines.append(payload["logline"])
            lines.append("")

        if payload.get("synopsis_short"):
            lines.append("## Synopsis (short)")
            lines.append("")
            lines.append(payload["synopsis_short"])
            lines.append("")

        if payload.get("synopsis_extended"):
            lines.append("## Synopsis (extended)")
            lines.append("")
            lines.append(payload["synopsis_extended"])
            lines.append("")

        if payload.get("premise"):
            lines.append("## Premise")
            lines.append("")
            lines.append(payload["premise"])
            lines.append("")

        if payload.get("theme"):
            lines.append("## Theme")
            lines.append("")
            lines.append(payload["theme"])
            lines.append("")

        if payload.get("genre"):
            lines.append(f"**Genre**: {payload['genre']}")
            lines.append("")

        if payload.get("tone"):
            lines.append(f"**Tone**: {payload['tone']}")
            lines.append("")

        if payload.get("dramatic_structure"):
            lines.append("## Dramatic Structure")
            lines.append("")
            lines.append(payload["dramatic_structure"])
            lines.append("")

        characters = payload.get("characters", [])
        if characters:
            lines.append(f"## Characters ({len(characters)})")
            for c in characters:
                lines.append(f"- {c}")
            lines.append("")

        locations = payload.get("locations", [])
        if locations:
            lines.append(f"## Locations ({len(locations)})")
            for loc in locations:
                lines.append(f"- {loc}")
            lines.append("")

        scenes = payload.get("scenes", [])
        if scenes:
            lines.append(f"## Scenes ({len(scenes)})")
            for s in scenes:
                heading = s.get("heading") or s.get("name") or ""
                scene_num = s.get("scene_number") or ""
                lines.append(f"- **{scene_num}**: {heading}")
            lines.append("")

        sequences_data = payload.get("sequences", [])
        if sequences_data:
            lines.append(f"## Sequences ({len(sequences_data)})")
            for seq in sequences_data:
                title = seq.get("title") or seq.get("sequence_id") or ""
                summary = seq.get("summary") or ""
                lines.append(f"- **{title}**: {summary}")
            lines.append("")

        breakdowns = payload.get("breakdowns", [])
        if breakdowns:
            lines.append(f"## Scene Breakdowns ({len(breakdowns)})")
            for bd in breakdowns:
                heading = bd.get("heading") or bd.get("scene_id") or ""
                characters_detected = bd.get("characters", [])
                lines.append(f"- **{heading}**: {len(characters_detected)} characters")
            lines.append("")

        department_bd = payload.get("department_breakdown", {})
        if department_bd:
            lines.append("## Department Breakdown")
            depts = department_bd.get("departments", {})
            if depts:
                for dept_name, dept_data in depts.items():
                    notes = dept_data.get("notes", "")
                    lines.append(f"- **{dept_name}**: {notes}")
            else:
                lines.append(f"{json.dumps(department_bd, indent=2, ensure_ascii=False)}")
            lines.append("")

        if payload.get("production_notes"):
            lines.append("## Production Notes")
            for note in payload["production_notes"]:
                lines.append(f"- {note}")
            lines.append("")

        if payload.get("storyboard_suggestions"):
            lines.append("## Storyboard Suggestions")
            for s in payload["storyboard_suggestions"]:
                lines.append(f"- {s}")
            lines.append("")

        if payload.get("recommended_storyboard_sequences"):
            lines.append("## Recommended for Storyboard")
            for seq_id in payload["recommended_storyboard_sequences"]:
                lines.append(f"- {seq_id}")
            lines.append("")

        if payload.get("analysis_summary"):
            lines.append("## Analysis Summary")
            lines.append("")
            lines.append(
                json.dumps(
                    payload["analysis_summary"],
                    indent=2,
                    ensure_ascii=False,
                )
            )
            lines.append("")

        if payload.get("llm_summary"):
            lines.append("## LLM Summary")
            lines.append("")
            lines.append(payload["llm_summary"])
            lines.append("")

        if payload.get("metadata"):
            lines.append("## Metadata")
            lines.append("")
            lines.append(
                json.dumps(
                    payload["metadata"],
                    indent=2,
                    ensure_ascii=False,
                )
            )
            lines.append("")

        return "\n".join(lines)


script_analysis_export_service = ScriptAnalysisExportService()
