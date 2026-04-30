"""
Shooting plan coverage service.
Detects what still needs to be shot.
"""

from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.change_governance import PlannedShot, ShootingPlan, ShootingPlanItem
from models.postproduction import Take
from models.report import ScriptNote, DirectorNote


async def get_shot_coverage(
    db: AsyncSession,
    project_id: str,
    approved_plan_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get coverage report - what's been shot vs what's planned.
    """
    shots = await db.execute(
        select(PlannedShot).where(
            PlannedShot.project_id == project_id,
            PlannedShot.status.in_(["approved", "shot"]),
        )
    )
    approved_shots = list(shots.scalars().all())
    
    essential_shots = [s for s in approved_shots if s.priority == "essential"]
    recommended_shots = [s for s in approved_shots if s.priority == "recommended"]
    optional_shots = [s for s in approved_shots if s.priority == "optional"]
    
    result_shot = await db.execute(
        select(Take).where(Take.project_id == project_id)
    )
    takes = list(result_shot.scalars().all())
    
    result_notes = await db.execute(
        select(ScriptNote).where(
            ScriptNote.project_id == project_id,
            ScriptNote.note_type.in_(["shot", "covered"]),
        )
    )
    shot_notes = list(result_notes.scalars().all())
    
    result_director_notes = await db.execute(
        select(DirectorNote).where(
            DirectorNote.project_id == project_id,
        )
    )
    director_notes = list(result_director_notes.scalars().all())
    
    all_shot_ids = set()
    for take in takes:
        if hasattr(take, 'planned_shot_id') and take.planned_shot_id:
            all_shot_ids.add(take.planned_shot_id)
        all_shot_ids.add(getattr(take, 'planned_shot_id', None))
    
    for note in shot_notes:
        if hasattr(note, 'scene_number') and note.scene_number:
            matching = [s for s in approved_shots if s.scene_number == note.scene_number]
            for m in matching:
                all_shot_ids.add(m.id)
    
    shot_evidence = set()
    for s in all_shot_ids:
        if s:
            shot_evidence.add(s)
    
    essential_done = [s for s in essential_shots if s.id in shot_evidence]
    essential_missing = [s for s in essential_shots if s.id not in shot_evidence]
    
    recommended_done = [s for s in recommended_shots if s.id in shot_evidence]
    recommended_done = [s for s in recommended_shots if s.id not in shot_evidence]
    
    optional_done = [s for s in optional_shots if s.id in shot_evidence]
    optional_missing = [s for s in optional_shots if s.id not in shot_evidence]
    
    needs_pickup = []
    for shot in essential_done + recommended_done:
        has_ng_take = any(
            t.status == "NG" for t in takes 
            if getattr(t, 'planned_shot_id', None) == shot.id
        )
        if has_ng_take:
            needs_pickup.append(shot)
    
    pickup_from_notes = []
    for note in shot_notes:
        if hasattr(note, 'needs_pickup') and note.needs_pickup:
            matching = [s for s in approved_shots if s.scene_number == note.scene_number]
            pickup_from_notes.extend(matching[:1])
    
    pickups_needed = list({s.id: s for s in pickup_from_notes + needs_pickup}.values())
    
    return {
        "planned_shots_count": len(approved_shots),
        "essential_count": len(essential_shots),
        "recommended_count": len(recommended_shots),
        "optional_count": len(optional_shots),
        
        "shot_count": len(set(all_shot_ids)),
        "essential_shot": len(essential_done),
        "recommended_shot": len(recommended_done),
        "optional_shot": len(optional_done),
        
        "missing_essential": len(essential_missing),
        "missing_recommended": len(recommended_done),
        "missing_optional": len(optional_missing),
        
        "missing_shots": [
            {"id": s.id, "sequence": s.sequence_number, "shot": s.shot_number, "priority": s.priority}
            for s in essential_missing
        ],
        "pickups_needed": [
            {"id": s.id, "sequence": s.sequence_number, "shot": s.shot_number}
            for s in pickups_needed
        ],
        "warnings": _generate_warnings(essential_missing, pickups_needed),
    }


def _generate_warnings(missing_shots: List[PlannedShot], pickups: List[PlannedShot]) -> List[str]:
    """Generate warning messages."""
    warnings = []
    
    if len(missing_shots) > 0:
        warnings.append(
            f"{len(missing_shots)} shots esenciales aún no rodados"
        )
    
    essential_sequences = set(s.sequence_number for s in missing_shots if s.priority == "essential")
    if len(essential_sequences) > 3:
        warnings.append(
            f"Faltan escenas enteras de {len(essential_sequences)} secuencias"
        )
    
    if len(pickups) > 0:
        warnings.append(f"{len(pickups)} pickup(s) necesario(s)")
    
    night_missing = [
        s for s in missing_shots if s.day_night == "night"
    ]
    if night_missing:
        warnings.append(
            f"{len(night_missing)} escena(s) nocturna(s) sin rodar"
        )
    
    ext_missing = [s for s in missing_shots if s.location and s.location.startswith("EXT")]
    if ext_missing:
        warnings.append(
            f"{len(ext_missing)} escena(s) exteriores sin rodar"
        )
    
    return warnings


async def get_scene_coverage(
    db: AsyncSession,
    project_id: str,
) -> Dict[str, Any]:
    """Get coverage by scene."""
    result = await db.execute(
        select(PlannedShot).where(PlannedShot.project_id == project_id)
    )
    shots = list(result.scalars().all())
    
    scene_data: Dict[int, Dict[str, Any]] = {}
    
    for shot in shots:
        if shot.scene_number not in scene_data:
            scene_data[shot.scene_number] = {
                "sequence": shot.sequence_number,
                "scene": shot.scene_number,
                "location": shot.location,
                "day_night": shot.day_night,
                "total": 0,
                "approved": 0,
                "shot": 0,
                "missing": 0,
            }
        
        scene_data[shot.scene_number]["total"] += 1
        
        if shot.status == "approved":
            scene_data[shot.scene_number]["approved"] += 1
        elif shot.status == "shot":
            scene_data[shot.scene_number]["shot"] += 1
        elif shot.status in ["proposed", "not_shot"]:
            scene_data[shot.scene_number]["missing"] += 1
    
    return scene_data


async def get_pickup_recommendations(
    db: AsyncSession,
    project_id: str,
) -> List[Dict[str, Any]]:
    """Get recommendations for pickup shoots."""
    coverage = await get_shot_coverage(db, project_id)
    
    recommendations = []
    
    for pickup in coverage.get("pickups_needed", []):
        recommendations.append({
            "shot_id": pickup["id"],
            "sequence": pickup["sequence"],
            "shot": pickup["shot"],
            "reason": "Marked NG or incomplete",
            "priority": "high",
        })
    
    for missing in coverage.get("missing_shots", [])[:5]:
        if missing["priority"] == "essential":
            recommendations.append({
                "shot_id": missing["id"],
                "sequence": missing["sequence"],
                "shot": missing["shot"],
                "reason": "Essential shot not yet shot",
                "priority": "high",
            })
    
    return recommendations