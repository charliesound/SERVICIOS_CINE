from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.production import ProductionBreakdown


EXPORT_VERSION = "1.0"
EXPORT_SOURCE = "cid_breakdown"


def _dict_or_empty(data: Any) -> dict:
    return data if isinstance(data, dict) else {}


def _list_or_empty(data: Any) -> list:
    return data if isinstance(data, list) else []


def _parse_breakdown(breakdown: ProductionBreakdown) -> dict[str, Any]:
    if not breakdown or not breakdown.breakdown_json:
        return {}
    try:
        return json.loads(breakdown.breakdown_json)
    except (json.JSONDecodeError, TypeError):
        return {}


class BreakdownExportService:
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

        if not breakdown:
            # Si no hay breakdown, devolvemos dictionary vacío pero válido para avisar.
            return {"_project_exists": True, "has_breakdown": False}

        breakdown_data = _parse_breakdown(breakdown)
        if not breakdown_data:
            return {"_project_exists": True, "has_breakdown": False}

        scenes = _list_or_empty(breakdown_data.get("scenes"))
        breakdowns = _list_or_empty(breakdown_data.get("breakdowns"))
        department_bd = _dict_or_empty(breakdown_data.get("department_breakdown"))
        metadata = _dict_or_empty(breakdown_data.get("metadata"))
        structured_payload = _dict_or_empty(breakdown_data.get("structured_payload"))

        characters: set[str] = set()
        locations: set[str] = set()
        props: set[str] = set()
        wardrobe: set[str] = set()
        makeup_hair: set[str] = set()
        vehicles: set[str] = set()
        animals: set[str] = set()
        weapons: set[str] = set()
        sfx_vfx: set[str] = set()
        sound: set[str] = set()
        production_notes: list[str] = []
        risks: list[str] = []
        difficulty: str = "medium"

        # Extraer datos de breakdowns detallados si existen
        for bd in breakdowns:
            chars = bd.get("characters") or []
            for c in chars:
                characters.add(c)
                
            locs = bd.get("locations_detected") or []
            if not locs and bd.get("location"):
                locs = [bd.get("location")]
            for loc in locs:
                locations.add(loc)

            prps = bd.get("props_detected") or bd.get("props") or []
            for p in prps:
                props.add(p)

            # Si existieran otros campos en breakdown actual o futuro:
            for item in bd.get("wardrobe") or []: wardrobe.add(item)
            for item in bd.get("makeup_hair") or []: makeup_hair.add(item)
            for item in bd.get("vehicles") or []: vehicles.add(item)
            for item in bd.get("animals") or []: animals.add(item)
            for item in bd.get("weapons") or []: weapons.add(item)
            for item in bd.get("sfx_vfx") or bd.get("sfx") or bd.get("vfx") or []: sfx_vfx.add(item)
            for item in bd.get("sound") or []: sound.add(item)
            for r in bd.get("risks") or []: risks.append(r)

        # De departments también podemos sacar cosas
        depts = department_bd.get("departments", {})
        for dept_name, dept_data in depts.items():
            if "notes" in dept_data:
                production_notes.append(f"{dept_name.capitalize()}: {dept_data['notes']}")

        warnings: list[str] = []
        if not scenes:
            warnings.append("no_scenes_found")
        if not department_bd:
            warnings.append("no_department_breakdown_found")

        payload: dict[str, Any] = {
            "_project_exists": True,
            "has_breakdown": True,
            "export_version": EXPORT_VERSION,
            "source": EXPORT_SOURCE,
            "project_id": project_id,
            "project_name": project.name if project else "",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "warnings": warnings,
            "scenes": scenes,
            "breakdowns": breakdowns,
            "departments": department_bd,
            "locations": sorted(list(locations)),
            "characters": sorted(list(characters)),
            "props": sorted(list(props)),
            "wardrobe": sorted(list(wardrobe)) if wardrobe else None,
            "makeup_hair": sorted(list(makeup_hair)) if makeup_hair else None,
            "vehicles": sorted(list(vehicles)) if vehicles else None,
            "animals": sorted(list(animals)) if animals else None,
            "weapons": sorted(list(weapons)) if weapons else None,
            "sfx_vfx": sorted(list(sfx_vfx)) if sfx_vfx else None,
            "sound": sorted(list(sound)) if sound else None,
            "production_notes": production_notes if production_notes else None,
            "risks": risks if risks else None,
            "difficulty": depts.get("postproduccion", {}).get("complexity", "medium"),
            "raw_breakdown_json": breakdown_data,
        }

        # Filtrar valores None
        payload = {k: v for k, v in payload.items() if v is not None}

        return payload

    def to_markdown(self, payload: dict[str, Any]) -> str:
        lines: list[str] = []
        name = payload.get("project_name") or payload.get("project_id") or "Untitled"
        lines.append(f"# CID Breakdown — {name}")
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

        lines.append("## Summary")
        lines.append(f"- **Difficulty**: {payload.get('difficulty', 'unknown').capitalize()}")
        lines.append("")

        if payload.get("production_notes"):
            lines.append("## Production Notes")
            for note in payload["production_notes"]:
                lines.append(f"- {note}")
            lines.append("")

        if payload.get("risks"):
            lines.append("## Risks")
            for risk in payload["risks"]:
                lines.append(f"- {risk}")
            lines.append("")

        def _add_section(title: str, items: list[str]):
            if items:
                lines.append(f"## {title} ({len(items)})")
                for item in items:
                    lines.append(f"- {item}")
                lines.append("")

        _add_section("Characters", payload.get("characters", []))
        _add_section("Locations", payload.get("locations", []))
        _add_section("Props & Atrezzo", payload.get("props", []))
        _add_section("Wardrobe", payload.get("wardrobe", []))
        _add_section("Makeup & Hair", payload.get("makeup_hair", []))
        _add_section("Vehicles", payload.get("vehicles", []))
        _add_section("Animals", payload.get("animals", []))
        _add_section("Weapons", payload.get("weapons", []))
        _add_section("SFX / VFX", payload.get("sfx_vfx", []))
        _add_section("Sound", payload.get("sound", []))

        department_bd = payload.get("departments", {})
        if department_bd:
            lines.append("## Departments")
            depts = department_bd.get("departments", {})
            if depts:
                for dept_name, dept_data in depts.items():
                    notes = dept_data.get("notes", "")
                    lines.append(f"### {dept_name.capitalize()}")
                    lines.append(f"{notes}")
                    for k, v in dept_data.items():
                        if k != "notes":
                            lines.append(f"- **{k}**: {v}")
                    lines.append("")
            else:
                lines.append(f"{json.dumps(department_bd, indent=2, ensure_ascii=False)}")
                lines.append("")

        breakdowns = payload.get("breakdowns", [])
        if breakdowns:
            lines.append(f"## Scene Breakdowns ({len(breakdowns)})")
            for bd in breakdowns:
                heading = bd.get("heading") or bd.get("scene_id") or ""
                lines.append(f"### {heading}")
                lines.append(f"- **Int/Ext**: {bd.get('int_ext', '')}")
                lines.append(f"- **Location**: {bd.get('location', '')}")
                lines.append(f"- **Time**: {bd.get('time_of_day', '')}")
                chars = bd.get("characters", [])
                if chars:
                    lines.append(f"- **Characters**: {', '.join(chars)}")
                props = bd.get("props_detected", []) or bd.get("props", [])
                if props:
                    lines.append(f"- **Props**: {', '.join(props)}")
                complexity = bd.get("complexity_flags", [])
                if complexity:
                    lines.append(f"- **Complexity**: {', '.join(complexity)}")
                lines.append("")

        return "\n".join(lines)

    def to_csv(self, payload: dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Generar CSV a partir de la lista de breakdowns
        writer.writerow([
            "Scene ID", "Heading", "Int/Ext", "Location", "Time of Day", 
            "Characters", "Props", "Complexity Flags", "Dialogue Lines", "Action Lines"
        ])

        breakdowns = payload.get("breakdowns", [])
        for bd in breakdowns:
            writer.writerow([
                bd.get("scene_id", ""),
                bd.get("heading", ""),
                bd.get("int_ext", ""),
                bd.get("location", ""),
                bd.get("time_of_day", ""),
                ", ".join(bd.get("characters", [])),
                ", ".join(bd.get("props_detected", []) or bd.get("props", [])),
                ", ".join(bd.get("complexity_flags", [])),
                bd.get("dialogue_count", 0),
                bd.get("action_lines", 0)
            ])

        return output.getvalue()


breakdown_export_service = BreakdownExportService()
