from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postproduction import AssemblyCut, AssemblyCutItem, Take


class AssemblyService:
    async def generate_assembly(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:
        takes_result = await db.execute(
            select(Take)
            .where(Take.project_id == project_id, Take.is_recommended.is_(True))
            .order_by(Take.scene_number.asc(), Take.shot_number.asc(), Take.take_number.asc())
        )
        takes = list(takes_result.scalars().all())
        assembly = AssemblyCut(
            project_id=project_id,
            organization_id=organization_id,
            name=f"AssemblyCut {datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
            description="CID editorial MVP assembly cut",
            status="draft",
            source_scope="recommended_takes",
            source_version=1,
            metadata_json=json.dumps(
                {
                    "recommended_take_count": len(takes),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
            ),
            created_by=created_by,
        )
        db.add(assembly)
        await db.flush()

        timeline_cursor = 0
        for index, take in enumerate(takes):
            duration_frames = int(take.duration_frames or max(1, int((take.fps or 24.0) * 4)))
            item = AssemblyCutItem(
                assembly_cut_id=str(assembly.id),
                take_id=str(take.id),
                project_id=project_id,
                scene_number=take.scene_number,
                shot_number=take.shot_number,
                take_number=take.take_number,
                source_media_asset_id=take.camera_media_asset_id,
                audio_media_asset_id=take.sound_media_asset_id,
                start_tc=take.start_timecode,
                end_tc=take.end_timecode,
                timeline_in=timeline_cursor,
                timeline_out=timeline_cursor + duration_frames,
                duration_frames=duration_frames,
                fps=take.fps,
                recommended_reason=take.recommended_reason,
                order_index=index,
            )
            timeline_cursor += duration_frames
            db.add(item)
        await db.commit()
        return await self.get_latest_assembly(db, project_id=project_id)

    async def get_latest_assembly(self, db: AsyncSession, *, project_id: str) -> dict[str, Any]:
        result = await db.execute(
            select(AssemblyCut)
            .where(AssemblyCut.project_id == project_id)
            .order_by(AssemblyCut.created_at.desc(), AssemblyCut.id.desc())
        )
        assembly = result.scalars().first()
        if assembly is None:
            return {"assembly_cut": None, "items_created": 0}

        items_result = await db.execute(
            select(AssemblyCutItem)
            .where(AssemblyCutItem.assembly_cut_id == str(assembly.id))
            .order_by(AssemblyCutItem.order_index.asc())
        )
        items = list(items_result.scalars().all())
        metadata = {}
        try:
            metadata = json.loads(assembly.metadata_json or "{}")
        except Exception:
            metadata = {}
        return {
            "assembly_cut": {
                "id": str(assembly.id),
                "project_id": str(assembly.project_id),
                "organization_id": str(assembly.organization_id) if assembly.organization_id else None,
                "name": str(assembly.name),
                "description": assembly.description,
                "status": assembly.status,
                "source_scope": assembly.source_scope,
                "source_version": assembly.source_version,
                "metadata_json": metadata,
                "created_by": assembly.created_by,
                "created_at": assembly.created_at,
                "updated_at": assembly.updated_at,
                "items": [
                    {
                        "id": str(item.id),
                        "assembly_cut_id": str(item.assembly_cut_id),
                        "take_id": str(item.take_id) if item.take_id else None,
                        "project_id": str(item.project_id),
                        "scene_number": item.scene_number,
                        "shot_number": item.shot_number,
                        "take_number": item.take_number,
                        "source_media_asset_id": item.source_media_asset_id,
                        "audio_media_asset_id": item.audio_media_asset_id,
                        "start_tc": item.start_tc,
                        "end_tc": item.end_tc,
                        "timeline_in": item.timeline_in,
                        "timeline_out": item.timeline_out,
                        "duration_frames": item.duration_frames,
                        "fps": item.fps,
                        "recommended_reason": item.recommended_reason,
                        "order_index": item.order_index,
                        "created_at": item.created_at,
                    }
                    for item in items
                ],
            },
            "items_created": len(items),
        }


assembly_service = AssemblyService()
