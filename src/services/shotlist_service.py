"""
Shotlist and Shooting Plan services.
"""

import uuid
import re
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.change_governance import (
    PlannedShot,
    ShootingPlan,
    ShootingPlanItem,
    SHOT_STATUSES,
    SHOT_PRIORITIES,
    SHOT_TYPES,
)
from models.script_versioning import ScriptVersion
from models.storyboard import StoryboardShot


SCRIPT_HEADING_PATTERN = re.compile(
    r'^(INT\.|EXT\.|INT/EXT\.)\s+(.+?)\s*-\s*(DÍA|DIA|NOCHE|NIGHT|AM|PM)?\.?$',
    re.IGNORECASE
)
CHARACTER_PATTERN = re.compile(r'\b([A-Z][A-Z]+)\b')


def analyze_script_for_planned_shots(
    script_text: str,
    project_id: str,
    organization_id: str
) -> List[PlannedShot]:
    """Generate planned shots from script text."""
    if not script_text:
        return []
    
    lines = script_text.split('\n')
    shots = []
    current_sequence = 0
    current_scene = 0
    shot_counter = 0
    
    sequence_map: Dict[str, int] = {}
    scene_map: Dict[str, int] = {}
    
    active_version = None
    result = select(ScriptVersion).where(
        ScriptVersion.project_id == project_id,
        ScriptVersion.status == "active"
    )
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        heading_match = SCRIPT_HEADING_PATTERN.match(line)
        if heading_match:
            location = heading_match.group(2).strip()
            time_of_day = heading_match.group(3) or "DAY"
            day_night = "night" if time_of_day.upper() in ("NOCHE", "NIGHT", "PM") else "day"
            
            if location not in sequence_map:
                current_sequence += 1
                sequence_map[location] = current_sequence
            seq_num = sequence_map[location]
            
            if location not in scene_map:
                current_scene += 1
                scene_map[location] = current_scene
            scn_num = scene_map[location]
            
            shot_counter += 1
            
            characters = set()
            for char_line in lines:
                for match in CHARACTER_PATTERN.finditer(char_line):
                    char = match.group(1)
                    if len(char) > 1 and len(char) < 20:
                        characters.add(char)
            
            characters_json = list(characters)[:10]
            
            shot = PlannedShot(
                id=uuid.uuid4().hex,
                project_id=project_id,
                organization_id=organization_id,
                sequence_number=seq_num,
                scene_number=scn_num,
                shot_number=shot_counter,
                shot_code=f"{seq_num:02d}A",
                description=line[:200],
                shot_type="general",
                camera_movement=None,
                lens_suggestion=None,
                characters_json=characters_json,
                location=location[:100] if location else None,
                day_night=day_night,
                estimated_duration_seconds=10.0,
                priority="recommended",
                status="proposed",
                source_script_version_id=active_version,
                notes=None,
            )
            shots.append(shot)
            
            if len(shots) >= 50:
                break
    
    return shots


async def generate_planned_shots_from_project(
    db: AsyncSession,
    project_id: str,
    organization_id: str
) -> List[PlannedShot]:
    """Generate planned shots from project script."""
    from models.core import Project
    
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    script_text = None
    source_version_id = None
    
    if project and project.script_text:
        script_text = project.script_text
    
    if not script_text:
        result = await db.execute(
            select(ScriptVersion).where(
                ScriptVersion.project_id == project_id,
                ScriptVersion.status == "active"
            )
        )
        sv = result.scalars().first()
        if sv:
            script_text = sv.script_text
            source_version_id = sv.id
    
    shots = analyze_script_for_planned_shots(
        script_text or "",
        project_id,
        organization_id
    )
    
    for shot in shots:
        if source_version_id:
            shot.source_script_version_id = source_version_id
        db.add(shot)
    
    await db.commit()
    
    for shot in shots:
        await db.refresh(shot)
    
    return shots


async def get_planned_shots(
    db: AsyncSession,
    project_id: str,
    sequence_number: Optional[int] = None
) -> List[PlannedShot]:
    """Get planned shots for a project."""
    query = select(PlannedShot).where(PlannedShot.project_id == project_id)
    
    if sequence_number:
        query = query.where(PlannedShot.sequence_number == sequence_number)
    
    result = await db.execute(query.order_by(
        PlannedShot.sequence_number,
        PlannedShot.shot_number
    ))
    return list(result.scalars().all())


async def approve_planned_shot(
    db: AsyncSession,
    shot_id: str,
    user_id: str
) -> PlannedShot:
    """Approve a planned shot."""
    shot = await db.get(PlannedShot, shot_id)
    if not shot:
        raise ValueError(f"Shot {shot_id} not found")
    
    shot.status = "approved"
    shot.approved_by = user_id
    shot.approved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(shot)
    return shot


async def reject_planned_shot(
    db: AsyncSession,
    shot_id: str,
    user_id: str,
    notes: Optional[str] = None
) -> PlannedShot:
    """Reject a planned shot."""
    shot = await db.get(PlannedShot, shot_id)
    if not shot:
        raise ValueError(f"Shot {shot_id} not found")
    
    shot.status = "rejected"
    shot.notes = notes
    
    await db.commit()
    await db.refresh(shot)
    return shot


async def get_shot_coverage_summary(
    db: AsyncSession,
    project_id: str
) -> Dict[str, Any]:
    """Get shot coverage summary by status."""
    shots = await get_planned_shots(db, project_id)
    
    return {
        "total": len(shots),
        "proposed": sum(1 for s in shots if s.status == "proposed"),
        "approved": sum(1 for s in shots if s.status == "approved"),
        "rejected": sum(1 for s in shots if s.status == "rejected"),
        "shot": sum(1 for s in shots if s.status == "shot"),
        "pending_pickup": sum(1 for s in shots if s.status == "pending_pickup"),
        "not_shot": sum(1 for s in shots if s.status == "not_shot"),
    }


async def create_shooting_plan(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    title: str,
    created_by: Optional[str] = None
) -> ShootingPlan:
    """Create a new shooting plan."""
    plan = ShootingPlan(
        id=uuid.uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        title=title,
        status="draft",
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def add_shot_to_plan(
    db: AsyncSession,
    plan_id: str,
    shot_id: str,
    shooting_day: int
) -> ShootingPlanItem:
    """Add a planned shot to a shooting plan."""
    plan = await db.get(ShootingPlan, plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")
    
    shot = await db.get(PlannedShot, shot_id)
    if not shot:
        raise ValueError(f"Shot {shot_id} not found")
    
    item = ShootingPlanItem(
        id=uuid.uuid4().hex,
        shooting_plan_id=plan_id,
        project_id=shot.project_id,
        organization_id=shot.organization_id,
        shooting_day=shooting_day,
        sequence_number=shot.sequence_number,
        scene_number=shot.scene_number,
        shot_number=shot.shot_number,
        planned_shot_id=shot_id,
        location=shot.location,
        day_night=shot.day_night,
        characters_json=shot.characters_json,
        status="planned",
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_shooting_plans(
    db: AsyncSession,
    project_id: str
) -> List[ShootingPlan]:
    """Get shooting plans for a project."""
    result = await db.execute(
        select(ShootingPlan).where(
            ShootingPlan.project_id == project_id
        ).order_by(ShootingPlan.created_at.desc())
    )
    return list(result.scalars().all())


async def get_shooting_plan_items(
    db: AsyncSession,
    plan_id: str
) -> List[ShootingPlanItem]:
    """Get items for a shooting plan."""
    result = await db.execute(
        select(ShootingPlanItem).where(
            ShootingPlanItem.shooting_plan_id == plan_id
        ).order_by(
            ShootingPlanItem.shooting_day,
            ShootingPlanItem.sequence_number
        )
    )
    return list(result.scalars().all())


async def approve_shooting_plan(
    db: AsyncSession,
    plan_id: str,
    user_id: str
) -> ShootingPlan:
    """Approve a shooting plan."""
    plan = await db.get(ShootingPlan, plan_id)
    if not plan:
        raise ValueError(f"Plan {plan_id} not found")
    
    plan.status = "approved"
    plan.approved_by = user_id
    plan.approved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(plan)
    return plan