import json
import mimetypes
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.review import Review, ReviewComment
from models.storage import MediaAsset, StorageSource
from models.storyboard import StoryboardShot
from schemas.auth_schema import TenantContext
from schemas.presentation_schema import (
    PresentationCommentItem,
    PresentationFilmstripResponse,
    PresentationProjectSummary,
    PresentationSequenceItem,
    PresentationShotItem,
    PresentationSummary,
)


class PresentationNotFoundError(ValueError):
    pass


class PresentationForbiddenError(ValueError):
    pass


class PresentationPreviewUnavailableError(ValueError):
    pass


class PresentationService:
    DEFAULT_SEQUENCE_ID = "no_sequence"

    async def build_filmstrip(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> PresentationFilmstripResponse:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        editable_shots = await self._list_storyboard_shots(db, project_id=project_id, tenant=tenant)
        assets = await self._list_project_assets(db, project_id=project_id, tenant=tenant)
        comments = await self._list_project_comments(db, project_id=project_id, tenant=tenant)

        if editable_shots:
            return await self._build_storyboard_filmstrip(
                project=project,
                project_id=project_id,
                editable_shots=editable_shots,
                assets=assets,
                comments=comments,
            )

        sequences: dict[str, list[PresentationShotItem]] = {}
        orphan_assets: list[PresentationShotItem] = []

        for asset in assets:
            metadata = self._decode_metadata(asset.metadata_json)
            sequence_id = str(metadata.get("sequence_id") or "").strip()
            effective_sequence_id = sequence_id or self.DEFAULT_SEQUENCE_ID
            shot = self._build_shot_item(asset, project_id=project_id, metadata=metadata)
            if effective_sequence_id != self.DEFAULT_SEQUENCE_ID:
                sequences.setdefault(effective_sequence_id, []).append(shot)
            else:
                orphan_assets.append(shot)

        sequence_items: list[PresentationSequenceItem] = []
        for sequence_id in sorted(sequences.keys()):
            shots = sorted(sequences[sequence_id], key=self._shot_sort_key)
            visual_modes = sorted({shot.visual_mode for shot in shots if shot.visual_mode})
            sequence_items.append(
                PresentationSequenceItem(
                    sequence_id=sequence_id,
                    title=f"Sequence {sequence_id}",
                    visual_modes=visual_modes,
                    shots=shots,
                )
            )

        review_comments = [
            PresentationCommentItem(
                id=str(comment.id),
                review_id=str(comment.review_id),
                author_name=comment.author_name,
                body=str(comment.body),
                created_at=comment.created_at,
            )
            for comment in comments
        ]

        summary = PresentationSummary(
            sequences_count=len(sequence_items),
            shots_count=len(assets),
            orphan_assets_count=len(orphan_assets),
            comments_count=len(review_comments),
            source_assets_count=len(assets),
        )

        return PresentationFilmstripResponse(
            project=PresentationProjectSummary(
                id=str(project.id),
                organization_id=str(project.organization_id),
                name=str(project.name),
                description=project.description,
                status=str(project.status),
            ),
            summary=summary,
            sequences=sequence_items,
            orphan_assets=sorted(orphan_assets, key=self._shot_sort_key),
            review_comments=review_comments,
            generated_at=datetime.now(timezone.utc),
        )

    async def _build_storyboard_filmstrip(
        self,
        *,
        project: Project,
        project_id: str,
        editable_shots: list[StoryboardShot],
        assets: list[MediaAsset],
        comments: list[ReviewComment],
    ) -> PresentationFilmstripResponse:
        assets_by_id = {str(asset.id): asset for asset in assets}
        sequences: dict[str, list[PresentationShotItem]] = {}
        orphan_assets: list[PresentationShotItem] = []

        sorted_shots = sorted(
            editable_shots,
            key=lambda shot: (
                shot.sequence_id or "",
                int(shot.sequence_order),
                shot.created_at.isoformat() if shot.created_at else "",
                str(shot.id),
            ),
        )
        for shot in sorted_shots:
            dto_shot = self._build_storyboard_shot_item(
                shot,
                project_id=project_id,
                asset=assets_by_id.get(str(shot.asset_id)) if shot.asset_id else None,
            )
            sequence_id = self._optional_text(shot.sequence_id)
            if sequence_id:
                sequences.setdefault(sequence_id, []).append(dto_shot)
            else:
                orphan_assets.append(dto_shot)

        sequence_items: list[PresentationSequenceItem] = []
        for sequence_id in sorted(sequences.keys()):
            shots = sorted(sequences[sequence_id], key=self._shot_sort_key)
            visual_modes = sorted({shot.visual_mode for shot in shots if shot.visual_mode})
            sequence_items.append(
                PresentationSequenceItem(
                    sequence_id=sequence_id,
                    title=f"Sequence {sequence_id}",
                    visual_modes=visual_modes,
                    shots=shots,
                )
            )

        review_comments = [
            PresentationCommentItem(
                id=str(comment.id),
                review_id=str(comment.review_id),
                author_name=comment.author_name,
                body=str(comment.body),
                created_at=comment.created_at,
            )
            for comment in comments
        ]

        linked_assets_count = sum(1 for shot in editable_shots if shot.asset_id)
        summary = PresentationSummary(
            sequences_count=len(sequence_items),
            shots_count=len(editable_shots),
            orphan_assets_count=len(orphan_assets),
            comments_count=len(review_comments),
            source_assets_count=linked_assets_count,
        )

        return PresentationFilmstripResponse(
            project=PresentationProjectSummary(
                id=str(project.id),
                organization_id=str(project.organization_id),
                name=str(project.name),
                description=project.description,
                status=str(project.status),
            ),
            summary=summary,
            sequences=sequence_items,
            orphan_assets=sorted(orphan_assets, key=self._shot_sort_key),
            review_comments=review_comments,
            generated_at=datetime.now(timezone.utc),
        )

    async def get_asset_preview_payload(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        asset_id: str,
        tenant: TenantContext,
    ) -> dict:
        project = await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)
        asset = await self._get_asset_for_project(db, project_id=project_id, asset_id=asset_id)

        if str(asset.organization_id) != str(project.organization_id):
            raise PresentationForbiddenError("Asset does not belong to the requested project tenant")
        if not tenant.is_global_admin and str(asset.organization_id) != str(tenant.organization_id):
            raise PresentationForbiddenError("Asset not accessible for tenant")

        metadata = self._decode_metadata(asset.metadata_json)
        resolved = self._resolve_asset_preview_source(asset, metadata)
        kind = resolved["kind"]
        if kind == "file":
            file_path = Path(str(resolved["value"]))
            await self._validate_asset_file_path(db, asset, file_path)
            media_type = getattr(asset, "mime_type", None) or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            return {
                "kind": "file",
                "path": str(file_path),
                "media_type": media_type,
                "filename": str(asset.file_name),
            }

        if kind == "json":
            return {
                "kind": "json",
                "payload": resolved["value"],
                "filename": str(asset.file_name),
            }

        raise PresentationPreviewUnavailableError("Asset preview is not available for this asset")

    async def build_pdf_render_payload(
        self,
        db: AsyncSession,
        *,
        payload: PresentationFilmstripResponse,
        tenant: TenantContext,
    ) -> dict:
        project_id = str(payload.project.id)
        await self._get_project_for_tenant(db, project_id=project_id, tenant=tenant)

        render_payload = payload.model_dump(mode="json")
        for collection_name in ("sequences", "orphan_assets"):
            collection = render_payload.get(collection_name, [])
            if collection_name == "sequences":
                for sequence in collection:
                    for shot in sequence.get("shots", []):
                        await self._attach_pdf_asset_fields(
                            db,
                            project_id=project_id,
                            shot=shot,
                            tenant=tenant,
                        )
            else:
                for shot in collection:
                    await self._attach_pdf_asset_fields(
                        db,
                        project_id=project_id,
                        shot=shot,
                        tenant=tenant,
                    )
        return render_payload

    def build_delivery_manifest(
        self,
        payload: PresentationFilmstripResponse,
        *,
        source_endpoint: str,
        pdf_file_name: str,
        pdf_mime_type: str = "application/pdf",
        format_version: str = "presentation_manifest.v1",
    ) -> dict:
        ordered_asset_ids: list[str] = []
        sequence_ids: list[str] = []
        for sequence in payload.sequences:
            sequence_ids.append(sequence.sequence_id)
            for shot in sequence.shots:
                ordered_asset_ids.append(shot.asset_id)
        for shot in payload.orphan_assets:
            ordered_asset_ids.append(shot.asset_id)

        return {
            "project_id": str(payload.project.id),
            "organization_id": str(payload.project.organization_id),
            "project_name": payload.project.name,
            "generated_at": payload.generated_at.isoformat(),
            "sequences_count": payload.summary.sequences_count,
            "shots_count": payload.summary.shots_count,
            "orphan_assets_count": payload.summary.orphan_assets_count,
            "comments_count": payload.summary.comments_count,
            "sequence_ids": sequence_ids,
            "asset_ids": ordered_asset_ids,
            "format_version": format_version,
            "source_endpoint": source_endpoint,
            "pdf_file_name": pdf_file_name,
            "pdf_mime_type": pdf_mime_type,
        }

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
            raise PresentationNotFoundError("Project not found")
        if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
            raise PresentationForbiddenError("Project not accessible for tenant")
        return project

    async def _get_asset_for_project(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        asset_id: str,
    ) -> MediaAsset:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == asset_id,
                MediaAsset.project_id == project_id,
            )
        )
        asset = result.scalar_one_or_none()
        if asset is None:
            raise PresentationNotFoundError("Asset not found")
        return asset

    async def _list_project_assets(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> list[MediaAsset]:
        query = select(MediaAsset).where(MediaAsset.project_id == project_id)
        if not tenant.is_global_admin:
            query = query.where(MediaAsset.organization_id == tenant.organization_id)
        query = query.order_by(MediaAsset.created_at.asc(), MediaAsset.id.asc())
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _list_project_comments(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> list[ReviewComment]:
        query = (
            select(ReviewComment)
            .join(Review, Review.id == ReviewComment.review_id)
            .where(Review.project_id == project_id)
            .order_by(ReviewComment.created_at.asc(), ReviewComment.id.asc())
        )
        if not tenant.is_global_admin:
            query = query.where(ReviewComment.organization_id == tenant.organization_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _list_storyboard_shots(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        tenant: TenantContext,
    ) -> list[StoryboardShot]:
        query = select(StoryboardShot).where(StoryboardShot.project_id == project_id)
        if not tenant.is_global_admin:
            query = query.where(StoryboardShot.organization_id == tenant.organization_id)
        query = query.order_by(
            StoryboardShot.sequence_id.asc(),
            StoryboardShot.sequence_order.asc(),
            StoryboardShot.created_at.asc(),
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def _attach_pdf_asset_fields(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        shot: dict,
        tenant: TenantContext,
    ) -> None:
        shot["pdf_thumbnail_url"] = None
        shot["pdf_has_embedded_image"] = False
        asset_type = str(shot.get("asset_type") or "").lower()
        asset_id = str(shot.get("asset_id") or "").strip()
        if not asset_id or asset_type != "image":
            return

        try:
            preview = await self.get_asset_preview_payload(
                db,
                project_id=project_id,
                asset_id=asset_id,
                tenant=tenant,
            )
        except ValueError:
            return

        if preview.get("kind") != "file":
            return

        media_type = str(preview.get("media_type") or "")
        if not media_type.startswith("image/"):
            return

        file_path = Path(str(preview["path"]))
        shot["pdf_thumbnail_url"] = file_path.resolve().as_uri()
        shot["pdf_has_embedded_image"] = True

    def _build_shot_item(
        self,
        asset: MediaAsset,
        *,
        project_id: str,
        metadata: dict | None = None,
    ) -> PresentationShotItem:
        metadata = metadata if metadata is not None else self._decode_metadata(asset.metadata_json)
        content_ref = getattr(asset, "content_ref", None)
        shot_order_raw = metadata.get("shot_order")
        shot_order = self._coerce_shot_order(shot_order_raw)
        prompt_summary = self._resolve_prompt_summary(asset, metadata)

        return PresentationShotItem(
            asset_id=str(asset.id),
            job_id=getattr(asset, "job_id", None),
            file_name=str(asset.file_name),
            asset_type=str(asset.asset_type),
            asset_source=getattr(asset, "asset_source", None),
            content_ref=content_ref,
            shot_order=shot_order,
            shot_type=self._optional_text(metadata.get("shot_type")),
            visual_mode=self._optional_text(metadata.get("visual_mode")),
            prompt_summary=prompt_summary,
            canonical_path_present=bool(getattr(asset, "canonical_path", None)),
            thumbnail_url=f"/api/projects/{project_id}/presentation/assets/{asset.id}/thumbnail",
            created_at=getattr(asset, "created_at", None),
        )

    def _build_storyboard_shot_item(
        self,
        shot: StoryboardShot,
        *,
        project_id: str,
        asset: MediaAsset | None,
    ) -> PresentationShotItem:
        asset_metadata = self._decode_metadata(asset.metadata_json) if asset is not None else {}
        file_name = str(asset.file_name) if asset is not None else f"Storyboard Shot {shot.sequence_order}"
        asset_type = str(asset.asset_type) if asset is not None else "manual"
        asset_source = getattr(asset, "asset_source", None) if asset is not None else "storyboard_editor"
        shot_type = self._optional_text(shot.shot_type) or self._optional_text(asset_metadata.get("shot_type"))
        visual_mode = self._optional_text(shot.visual_mode) or self._optional_text(asset_metadata.get("visual_mode"))
        prompt_summary = self._optional_text(shot.narrative_text)
        if not prompt_summary and asset is not None:
            prompt_summary = self._resolve_prompt_summary(asset, asset_metadata)
        if not prompt_summary:
            prompt_summary = f"Editable storyboard shot {shot.sequence_order}"

        return PresentationShotItem(
            asset_id=str(shot.asset_id or shot.id),
            job_id=getattr(asset, "job_id", None) if asset is not None else None,
            file_name=file_name,
            asset_type=asset_type,
            asset_source=asset_source,
            content_ref=getattr(asset, "content_ref", None) if asset is not None else None,
            shot_order=int(shot.sequence_order),
            shot_type=shot_type,
            visual_mode=visual_mode,
            prompt_summary=prompt_summary,
            canonical_path_present=bool(getattr(asset, "canonical_path", None)) if asset is not None else False,
            thumbnail_url=(
                f"/api/projects/{project_id}/presentation/assets/{asset.id}/thumbnail"
                if asset is not None
                else None
            ),
            created_at=shot.updated_at or shot.created_at,
        )

    def _decode_metadata(self, raw_metadata: str | None) -> dict:
        if not raw_metadata:
            return {}
        try:
            parsed = json.loads(raw_metadata)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _coerce_shot_order(self, value: object) -> int:
        try:
            if value is None or str(value).strip() == "":
                return 0
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _resolve_prompt_summary(self, asset: MediaAsset, metadata: dict) -> str | None:
        prompt_summary = self._optional_text(metadata.get("prompt_summary"))
        if prompt_summary:
            return prompt_summary
        prompt_summary = self._optional_text(metadata.get("prompt"))
        if prompt_summary:
            return prompt_summary[:240]
        sequence_id = self._optional_text(metadata.get("sequence_id"))
        if sequence_id:
            return f"Asset grouped in sequence {sequence_id}"
        return f"Indexed {asset.asset_type} asset {asset.file_name}"

    def _shot_sort_key(self, shot: PresentationShotItem) -> tuple[int, int, str, str]:
        created_at = shot.created_at.isoformat() if shot.created_at else ""
        has_explicit_shot_order = shot.shot_order > 0
        return (
            0 if has_explicit_shot_order else 1,
            shot.shot_order if has_explicit_shot_order else 0,
            created_at,
            shot.file_name,
        )

    def _resolve_asset_preview_source(self, asset: MediaAsset, metadata: dict) -> dict:
        file_candidates: list[str] = []
        canonical_path = self._optional_text(getattr(asset, "canonical_path", None))
        if canonical_path:
            file_candidates.append(canonical_path)

        metadata_candidates = [
            metadata.get("storage_path"),
            metadata.get("file_path"),
            metadata.get("canonical_path"),
            metadata.get("path"),
        ]
        for candidate in metadata_candidates:
            normalized = self._optional_text(candidate)
            if normalized:
                file_candidates.append(normalized)

        content_ref = self._optional_text(getattr(asset, "content_ref", None))
        if content_ref and content_ref.startswith("file://"):
            file_candidates.append(content_ref[7:])

        for candidate in file_candidates:
            path = Path(candidate)
            if path.is_file():
                return {"kind": "file", "value": str(path)}

        if metadata:
            return {"kind": "json", "value": metadata}

        raise PresentationPreviewUnavailableError("Asset has no resolvable preview source")

    async def _validate_asset_file_path(
        self,
        db: AsyncSession,
        asset: MediaAsset,
        file_path: Path,
    ) -> None:
        resolved_file = file_path.resolve(strict=True)
        storage_source_id = getattr(asset, "storage_source_id", None)
        if storage_source_id:
            result = await db.execute(
                select(StorageSource).where(StorageSource.id == storage_source_id)
            )
            storage_source = result.scalar_one_or_none()
            if storage_source is None:
                raise PresentationPreviewUnavailableError("Storage source not found for asset preview")
            storage_root = Path(str(storage_source.mount_path)).resolve(strict=True)
            if storage_root not in resolved_file.parents and resolved_file != storage_root:
                raise PresentationForbiddenError("Asset file path is outside the authorized storage root")


presentation_service = PresentationService()
