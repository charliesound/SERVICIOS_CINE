from __future__ import annotations

from collections import defaultdict

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.storage import MediaAsset
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from schemas.shot_schema import (
    StoryboardShotBulkReorderRequest,
    StoryboardShotCreate,
    StoryboardShotUpdate,
)


class ShotService:
    async def list_project_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> list[StoryboardShot]:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        result = await db.execute(
            select(StoryboardShot)
            .where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == str(project.organization_id),
                StoryboardShot.is_active.is_(True),
            )
            .order_by(StoryboardShot.sequence_id.asc(), StoryboardShot.sequence_order.asc(), StoryboardShot.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_shot(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        payload: StoryboardShotCreate,
        tenant: TenantContext,
    ) -> StoryboardShot:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        sequence_id = self._normalize_optional_text(payload.sequence_id)
        asset = await self._validate_asset_binding(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            asset_id=payload.asset_id,
        )

        sequence_order = payload.sequence_order
        if sequence_order is None:
            sequence_order = await self._next_sequence_order(
                db,
                project_id=project_id,
                organization_id=str(project.organization_id),
                sequence_id=sequence_id,
            )

        shot = StoryboardShot(
            project_id=project_id,
            organization_id=str(project.organization_id),
            sequence_id=sequence_id,
            sequence_order=sequence_order,
            narrative_text=self._normalize_optional_text(payload.narrative_text),
            asset_id=str(asset.id) if asset is not None else None,
            shot_type=self._normalize_optional_text(payload.shot_type),
            visual_mode=self._normalize_optional_text(payload.visual_mode),
        )
        db.add(shot)
        await db.commit()
        await db.refresh(shot)
        return shot

    async def update_shot(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        shot_id: str,
        payload: StoryboardShotUpdate,
        tenant: TenantContext,
    ) -> StoryboardShot:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        shot = await self._get_storyboard_shot(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            shot_id=shot_id,
        )
        asset = await self._validate_asset_binding(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            asset_id=payload.asset_id,
        )

        if payload.sequence_id is not None:
            shot.sequence_id = self._normalize_optional_text(payload.sequence_id)
        if payload.sequence_order is not None:
            shot.sequence_order = payload.sequence_order
        if payload.narrative_text is not None:
            shot.narrative_text = self._normalize_optional_text(payload.narrative_text)
        if payload.asset_id is not None:
            shot.asset_id = str(asset.id) if asset is not None else None
        if payload.shot_type is not None:
            shot.shot_type = self._normalize_optional_text(payload.shot_type)
        if payload.visual_mode is not None:
            shot.visual_mode = self._normalize_optional_text(payload.visual_mode)

        await self._assert_no_duplicate_orders(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            overrides={shot.id: {"sequence_id": shot.sequence_id, "sequence_order": shot.sequence_order}},
        )
        await db.commit()
        await db.refresh(shot)
        return shot

    async def delete_shot(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        shot_id: str,
        tenant: TenantContext,
    ) -> None:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        shot = await self._get_storyboard_shot(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            shot_id=shot_id,
        )
        await db.delete(shot)
        await db.commit()

    async def bulk_reorder(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        payload: StoryboardShotBulkReorderRequest,
        tenant: TenantContext,
    ) -> list[StoryboardShot]:
        if not payload.shots:
            raise HTTPException(status_code=400, detail="shots must not be empty")

        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == str(project.organization_id),
                StoryboardShot.is_active.is_(True),
            )
        )
        shots = list(result.scalars().all())
        shot_map = {str(shot.id): shot for shot in shots}

        overrides: dict[str, dict[str, object]] = {}
        for item in payload.shots:
            shot = shot_map.get(item.shot_id)
            if shot is None:
                raise HTTPException(status_code=404, detail=f"Shot {item.shot_id} not found")
            overrides[item.shot_id] = {
                "sequence_id": self._normalize_optional_text(item.sequence_id)
                if item.sequence_id is not None
                else shot.sequence_id,
                "sequence_order": item.sequence_order,
            }

        await self._assert_no_duplicate_orders(
            db,
            project_id=project_id,
            organization_id=str(project.organization_id),
            overrides=overrides,
        )

        try:
            for shot_id, update in overrides.items():
                shot = shot_map[shot_id]
                shot.sequence_id = update["sequence_id"]
                shot.sequence_order = int(update["sequence_order"])
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        for shot in shots:
            await db.refresh(shot)
        return sorted(
            shots,
            key=lambda shot: (
                shot.sequence_id or "",
                shot.sequence_order,
                shot.created_at.isoformat() if shot.created_at else "",
            ),
        )

    async def _get_project_for_tenant(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> Project:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
            raise HTTPException(status_code=403, detail="Project not accessible for tenant")
        return project

    async def _get_storyboard_shot(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        shot_id: str,
    ) -> StoryboardShot:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.id == shot_id,
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
            )
        )
        shot = result.scalar_one_or_none()
        if shot is None:
            raise HTTPException(status_code=404, detail="Shot not found")
        return shot

    async def _validate_asset_binding(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        asset_id: str | None,
    ) -> MediaAsset | None:
        normalized_asset_id = self._normalize_optional_text(asset_id)
        if normalized_asset_id is None:
            return None

        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == normalized_asset_id,
                MediaAsset.project_id == project_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        asset = result.scalar_one_or_none()
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found for project")
        return asset

    async def _next_sequence_order(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        sequence_id: str | None,
    ) -> int:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
                StoryboardShot.sequence_id == sequence_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        existing = list(result.scalars().all())
        if not existing:
            return 1
        return max(int(shot.sequence_order) for shot in existing) + 1

    async def _assert_no_duplicate_orders(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        overrides: dict[str, dict[str, object]],
    ) -> None:
        result = await db.execute(
            select(StoryboardShot).where(
                StoryboardShot.project_id == project_id,
                StoryboardShot.organization_id == organization_id,
                StoryboardShot.is_active.is_(True),
            )
        )
        shots = list(result.scalars().all())
        grouped: dict[str, set[int]] = defaultdict(set)
        for shot in shots:
            override = overrides.get(str(shot.id), {})
            sequence_id = override.get("sequence_id", shot.sequence_id) or ""
            sequence_order = int(override.get("sequence_order", shot.sequence_order))
            if sequence_order in grouped[sequence_id]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Duplicate sequence_order {sequence_order} in sequence '{sequence_id or 'no_sequence'}'",
                )
            grouped[sequence_id].add(sequence_order)

    def _normalize_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


shot_service = ShotService()
