import re
import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.script_versioning import ScriptVersion, ScriptChangeReport, ProjectModuleStatus


class ScriptVersionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_initial_version(
        self,
        project_id: str,
        script_text: str,
        filename: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> ScriptVersion:
        content_hash = self.calculate_hash(script_text)
        
        result = await self.db.execute(
            select(func.max(ScriptVersion.version_number)).where(
                ScriptVersion.project_id == project_id
            )
        )
        max_version = result.scalar_one() or 0
        new_version = max_version + 1
        
        word_count = len(script_text.split())
        scene_count = self.count_scenes(script_text)
        
        version = ScriptVersion(
            project_id=project_id,
            organization_id=organization_id or "",
            version_number=new_version,
            title=f"Version {new_version}",
            source_filename=filename,
            script_text=script_text,
            content_hash=content_hash,
            word_count=word_count,
            scene_count=scene_count,
            status="active",
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        return version

    async def create_new_version(
        self,
        project_id: str,
        script_text: str,
        filename: Optional[str] = None,
        notes: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> Optional[ScriptVersion]:
        content_hash = self.calculate_hash(script_text)
        
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id,
                ScriptVersion.status == "active"
            )
        )
        current_active = result.scalar_one_or_none()
        
        if current_active and current_active.content_hash == content_hash:
            return None
        
        if current_active:
            current_active.status = "archived"
        
        result = await self.db.execute(
            select(func.max(ScriptVersion.version_number)).where(
                ScriptVersion.project_id == project_id
            )
        )
        max_version = result.scalar_one() or 0
        new_version = max_version + 1
        
        word_count = len(script_text.split())
        scene_count = self.count_scenes(script_text)
        
        version = ScriptVersion(
            project_id=project_id,
            organization_id=organization_id or "",
            version_number=new_version,
            title=f"Version {new_version}",
            source_filename=filename,
            script_text=script_text,
            content_hash=content_hash,
            word_count=word_count,
            scene_count=scene_count,
            status="active",
            notes=notes,
        )
        
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        
        return version

    async def get_active_version(self, project_id: str) -> Optional[ScriptVersion]:
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id,
                ScriptVersion.status == "active"
            )
        )
        return result.scalar_one_or_none()

    async def list_versions(self, project_id: str) -> list[ScriptVersion]:
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id
            ).order_by(ScriptVersion.version_number.desc())
        )
        return list(result.scalars().all())

    async def activate_version(
        self, project_id: str, version_id: str, project: Project
    ) -> Optional[ScriptVersion]:
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.id == version_id,
                ScriptVersion.project_id == project_id
            )
        )
        version = result.scalar_one_or_none()
        
        if not version:
            return None
        
        result = await self.db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id,
                ScriptVersion.status == "active"
            )
        )
        current_active = result.scalar_one_or_none()
        
        if current_active and current_active.id != version_id:
            current_active.status = "archived"
        
        version.status = "active"
        project.script_text = version.script_text
        
        await self.db.commit()
        await self.db.refresh(version)
        
        return version

    @staticmethod
    def calculate_hash(script_text: str) -> str:
        if not script_text:
            return ""
        return hashlib.sha256(script_text.encode('utf-8')).hexdigest()[:64]

    @staticmethod
    def count_scenes(script_text: str) -> int:
        if not script_text:
            return 0
        pattern = r'^(INT\.|EXT\.|INT/EXT\.|I/E\.?)'
        matches = re.findall(pattern, script_text, re.MULTILINE | re.IGNORECASE)
        return len(matches)

    async def update_module_status(
        self,
        project_id: str,
        organization_id: str,
        module_name: str,
        status: str,
        change_report_id: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> ProjectModuleStatus:
        result = await self.db.execute(
            select(ProjectModuleStatus).where(
                ProjectModuleStatus.project_id == project_id,
                ProjectModuleStatus.module_name == module_name
            )
        )
        module_status = result.scalar_one_or_none()
        
        if module_status:
            module_status.status = status
            module_status.affected_by_change_report_id = change_report_id
            module_status.summary = summary
            module_status.updated_at = datetime.now(timezone.utc)
        else:
            module_status = ProjectModuleStatus(
                project_id=project_id,
                organization_id=organization_id,
                module_name=module_name,
                status=status,
                affected_by_change_report_id=change_report_id,
                summary=summary,
            )
            self.db.add(module_status)
        
        await self.db.commit()
        await self.db.refresh(module_status)
        
        return module_status

    async def get_module_statuses(
        self, project_id: str
    ) -> list[ProjectModuleStatus]:
        result = await self.db.execute(
            select(ProjectModuleStatus).where(
                ProjectModuleStatus.project_id == project_id
            )
        )
        return list(result.scalars().all())


class ScriptChangeAnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def compare_versions(
        self,
        project_id: str,
        organization_id: str,
        from_version: ScriptVersion,
        to_version: ScriptVersion,
    ) -> ScriptChangeReport:
        from_text = from_version.script_text or ""
        to_text = to_version.script_text or ""
        
        from_scenes = self.extract_scenes(from_text)
        to_scenes = self.extract_scenes(to_text)
        
        from_characters = self.extract_characters(from_text)
        to_characters = self.extract_characters(to_text)
        
        from_locations = self.extract_locations(from_text)
        to_locations = self.extract_locations(to_text)
        
        added_scenes = [s for s in to_scenes if s not in from_scenes]
        removed_scenes = [s for s in from_scenes if s not in to_scenes]
        modified_scenes = self.find_modified_scenes(from_scenes, to_scenes)
        
        added_chars = [c for c in to_characters if c not in from_characters]
        removed_chars = [c for c in from_characters if c not in to_characters]
        
        prod_impact = self.analyze_production_impact(
            added_scenes, removed_scenes, modified_scenes, to_locations
        )
        budget_impact = self.analyze_budget_impact(prod_impact)
        storyboard_impact = self.analyze_storyboard_impact(modified_scenes)
        recommended = self.generate_recommended_actions(
            prod_impact, budget_impact, storyboard_impact
        )
        
        summary_parts = []
        if added_scenes:
            summary_parts.append(f"+{len(added_scenes)} scenes")
        if removed_scenes:
            summary_parts.append(f"-{len(removed_scenes)} scenes")
        if modified_scenes:
            summary_parts.append(f"~{len(modified_scenes)} modified")
        if added_chars:
            summary_parts.append(f"+{len(added_chars)} characters")
        
        summary = ", ".join(summary_parts) if summary_parts else "No significant changes"
        
        change_report = ScriptChangeReport(
            project_id=project_id,
            organization_id=organization_id,
            from_version_id=from_version.id,
            to_version_id=to_version.id,
            summary=summary,
            added_scenes_json=added_scenes,
            removed_scenes_json=removed_scenes,
            modified_scenes_json=modified_scenes,
            added_characters_json=added_chars,
            removed_characters_json=removed_chars,
            modified_locations_json=self.list_diff(from_locations, to_locations),
            production_impact_json=prod_impact,
            budget_impact_json=budget_impact,
            storyboard_impact_json=storyboard_impact,
            recommended_actions_json=recommended,
        )
        
        self.db.add(change_report)
        await self.db.commit()
        await self.db.refresh(change_report)
        
        return change_report

    def extract_scenes(self, text: str) -> list[dict]:
        if not text:
            return []
        
        scenes = []
        lines = text.split('\n')
        current_scene = None
        
        for line in lines:
            line = line.strip()
            if re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.?)', line, re.IGNORECASE):
                header = line
                location = ""
                time_of_day = ""
                
                if '-' in line:
                    parts = line.split('-')
                    header = parts[0].strip()
                    if len(parts) > 1:
                        location = parts[1].strip()
                    if len(parts) > 2:
                        time_of_day = parts[2].strip()
                else:
                    location = "Unknown"
                
                current_scene = {
                    "header": header,
                    "location": location,
                    "time_of_day": time_of_day,
                    "content": [],
                }
                scenes.append(current_scene)
            elif current_scene and line:
                current_scene["content"].append(line)
        
        return scenes

    def extract_characters(self, text: str) -> list[str]:
        if not text:
            return []
        
        names = set()
        pattern = r'\b([A-Z][A-Z]+)\b(?:\s+[A-Z][a-z]+)?(?:\s+[A-Z][a-z]+)?'
        for match in re.finditer(pattern, text):
            word = match.group(1)
            if len(word) >= 2 and word not in {'INT', 'EXT', 'THE', 'AND', 'FOR', 'WITH', 'HIS', 'HER', 'BUT', 'NOT', 'ALL', 'CAN', 'ONE', 'ARE', 'WAS', 'WERE'}:
                names.add(word)
        
        return sorted(list(names))

    def extract_locations(self, text: str) -> list[str]:
        if not text:
            return []
        
        locations = set()
        for line in text.split('\n'):
            line = line.strip()
            if re.match(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.?)', line, re.IGNORECASE):
                if '-' in line:
                    parts = line.split('-')
                    if len(parts) > 1:
                        loc = parts[1].strip()
                        if ' - ' in loc:
                            loc = loc.split(' - ')[0].strip()
                        if loc and loc != 'Unknown':
                            locations.add(loc)
        
        return sorted(list(locations))

    def list_diff(self, from_list: list, to_list: list) -> dict:
        from_set = set(from_list)
        to_set = set(to_list)
        
        return {
            "added": sorted(list(to_set - from_set)),
            "removed": sorted(list(from_set - to_set)),
        }

    def find_modified_scenes(self, from_scenes: list[dict], to_scenes: list[dict]) -> list[dict]:
        modifications = []
        
        from_headers = {s['header']: s for s in from_scenes}
        to_headers = {s['header']: s for s in to_scenes}
        
        common = set(from_headers.keys()) & set(to_headers.keys())
        
        for header in common:
            from_sc = from_headers[header]
            to_sc = to_headers[header]
            
            if from_sc['content'] != to_sc['content']:
                modifications.append({
                    "header": header,
                    "change": "dialogue" if from_sc['content'] and to_sc['content'] else "content",
                })
        
        return modifications

    def analyze_production_impact(
        self,
        added_scenes: list,
        removed_scenes: list,
        modified_scenes: list,
        locations: list,
    ) -> dict:
        analysis = {
            "complexity_change": 0,
            "night_exterior_count": 0,
            "day_exterior_count": 0,
            "new_locations": len(locations.get("added", [])),
            "action_scenes": len([s for s in added_scenes if 'ACTION' in str(s.get('content', [])).upper()]),
        }
        
        for scene in added_scenes:
            loc = scene.get('location', '').upper()
            tod = scene.get('time_of_day', '').upper()
            
            if 'NIGHT' in tod and ('EXT' in scene.get('header', '').upper() or 'EXT' in loc):
                analysis["night_exterior_count"] += 1
            if 'DAY' in tod and 'EXT' in scene.get('header', '').upper():
                analysis["day_exterior_count"] += 1
        
        for scene in modified_scenes:
            analysis["complexity_change"] += 1
        
        if removed_scenes:
            analysis["scenes_removed"] = len(removed_scenes)
        
        return analysis

    def analyze_budget_impact(self, prod_impact: dict) -> dict:
        impact = {
            "estimated_change": 0,
            "reason": [],
        }
        
        if prod_impact.get("night_exterior_count", 0) > 0:
            impact["reason"].append("Night exteriors require additional lighting")
            impact["estimated_change"] += prod_impact["night_exterior_count"] * 500
        
        if prod_impact.get("new_locations", 0) > 2:
            impact["reason"].append("Multiple new locations increase transport/logistics costs")
            impact["estimated_change"] += (prod_impact["new_locations"] - 2) * 300
        
        if prod_impact.get("action_scenes", 0) > 0:
            impact["reason"].append(f"{prod_impact['action_scenes']} action scenes may need stunt coordination")
            impact["estimated_change"] += prod_impact["action_scenes"] * 200
        
        return impact

    def analyze_storyboard_impact(self, modified_scenes: list[dict]) -> dict:
        return {
            "scenes_affected": len(modified_scenes),
            "sequence_regen_needed": len(modified_scenes) >= 3,
            "partial_update": 0 < len(modified_scenes) < 5,
        }

    def generate_recommended_actions(
        self,
        prod_impact: dict,
        budget_impact: dict,
        storyboard_impact: dict,
    ) -> list[dict]:
        actions = []
        
        if storyboard_impact.get("scenes_affected", 0) > 0:
            actions.append({
                "module": "storyboard",
                "action": "review_affected_scenes",
                "priority": "high" if storyboard_impact.get("sequence_regen_needed") else "medium",
                "reason": f"{storyboard_impact['scenes_affected']} scenes modified",
            })
        
        if budget_impact.get("estimated_change", 0) > 0:
            actions.append({
                "module": "budget",
                "action": "recalculate",
                "priority": "medium",
                "reason": "Production complexity changed",
            })
        
        if prod_impact.get("new_locations", 0) > 0:
            actions.append({
                "module": "producer_pack",
                "action": "update_locations",
                "priority": "medium",
                "reason": f"{prod_impact['new_locations']} new locations",
            })
        
        if not actions:
            actions.append({
                "module": "general",
                "action": "none",
                "priority": "low",
                "reason": "No significant impact",
            })
        
        return actions