from datetime import datetime
from typing import Any, Dict, Optional, Type

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ingest_document import DocumentAsset
from models.ingest_reports import CameraReport, DirectorNote, ScriptNote, SoundReport
from models.ingest_scan import MediaAsset
from services.document_understanding_service import get_owned_document
from services.ingest_scan_service import get_owned_asset
from services.storage_handshake_service import log_ingest_event, resolve_organization_id


ReportModel = (
    Type[CameraReport] | Type[SoundReport] | Type[ScriptNote] | Type[DirectorNote]
)

EVENT_TYPE_BY_MODEL: Dict[ReportModel, str] = {
    CameraReport: "camera_report",
    SoundReport: "sound_report",
    ScriptNote: "script_note",
    DirectorNote: "director_note",
}


async def resolve_report_context(
    db: AsyncSession,
    token_payload: Dict[str, Any],
    requested_organization_id: Optional[str],
    project_id: str,
    document_asset_id: Optional[str],
    media_asset_id: Optional[str],
    user_id: str,
) -> tuple[str, Optional[DocumentAsset], Optional[MediaAsset]]:
    organization_id = resolve_organization_id(
        token_payload,
        requested_organization_id,
        user_id,
    )
    document = None
    if document_asset_id:
        document = await get_owned_document(
            db, document_asset_id, organization_id, user_id
        )
        if document.project_id != project_id:
            raise HTTPException(
                status_code=400, detail="Document asset project mismatch"
            )
        organization_id = document.organization_id

    asset = None
    if media_asset_id:
        asset = await get_owned_asset(db, media_asset_id, organization_id, user_id)
        if asset.project_id != project_id:
            raise HTTPException(status_code=400, detail="Media asset project mismatch")
        organization_id = asset.organization_id

    return organization_id, document, asset


async def get_owned_report(
    db: AsyncSession,
    model: ReportModel,
    report_id: str,
    organization_id: Optional[str],
    user_id: str,
):
    filters = [model.id == report_id, model.created_by == user_id]
    if organization_id is not None:
        filters.append(model.organization_id == organization_id)
    result = await db.execute(select(model).where(and_(*filters)))
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


async def log_report_event(
    db: AsyncSession,
    model: ReportModel,
    report,
    action: str,
    user_id: str,
):
    report_type = EVENT_TYPE_BY_MODEL[model]
    await log_ingest_event(
        db=db,
        organization_id=report.organization_id,
        project_id=report.project_id,
        storage_source_id=None,
        event_type=f"{report_type}.{action}",
        payload={"report_id": report.id, "report_type": report_type},
        created_by=user_id,
    )


def apply_report_updates(report, payload) -> None:
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, field_name, value)
    report.updated_at = datetime.utcnow()
