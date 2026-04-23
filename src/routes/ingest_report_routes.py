from typing import Optional, Type

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.ingest_reports import CameraReport, DirectorNote, ScriptNote, SoundReport
from routes.auth_routes import get_authenticated_user, get_token_payload
from schemas.ingest_report_schema import (
    CameraReportCreate,
    CameraReportListResponse,
    CameraReportResponse,
    CameraReportUpdate,
    DirectorNoteCreate,
    DirectorNoteListResponse,
    DirectorNoteResponse,
    DirectorNoteUpdate,
    ScriptNoteCreate,
    ScriptNoteListResponse,
    ScriptNoteResponse,
    ScriptNoteUpdate,
    SoundReportCreate,
    SoundReportListResponse,
    SoundReportResponse,
    SoundReportUpdate,
)
from services.ingest_report_service import (
    apply_report_updates,
    get_owned_report,
    log_report_event,
    resolve_report_context,
)
from services.storage_handshake_service import resolve_organization_id

router = APIRouter(prefix="/api/ingest", tags=["reports"])


async def _create_report(
    db: AsyncSession,
    token_payload: dict,
    user_id: str,
    payload,
    model: Type[CameraReport]
    | Type[SoundReport]
    | Type[ScriptNote]
    | Type[DirectorNote],
):
    organization_id, document, asset = await resolve_report_context(
        db,
        token_payload,
        payload.organization_id,
        payload.project_id,
        payload.document_asset_id,
        payload.media_asset_id,
        user_id,
    )
    data = payload.model_dump()
    data["organization_id"] = organization_id
    data["document_asset_id"] = document.id if document else payload.document_asset_id
    data["media_asset_id"] = asset.id if asset else payload.media_asset_id
    data["created_by"] = user_id
    report = model(**data)
    db.add(report)
    await db.flush()
    await log_report_event(db, model, report, "created", user_id)
    await db.refresh(report)
    return report


async def _list_reports(
    db: AsyncSession,
    token_payload: dict,
    user_id: str,
    model,
    project_id: Optional[str],
    shooting_day_id: Optional[str],
    scene_id: Optional[str],
    shot_id: Optional[str],
):
    organization_id = resolve_organization_id(
        token_payload, None, user_id, use_user_fallback=False
    )
    filters = [model.created_by == user_id]
    if organization_id is not None:
        filters.append(model.organization_id == organization_id)
    if project_id is not None:
        filters.append(model.project_id == project_id)
    if shooting_day_id is not None:
        filters.append(model.shooting_day_id == shooting_day_id)
    if scene_id is not None:
        filters.append(model.scene_id == scene_id)
    if shot_id is not None:
        filters.append(model.shot_id == shot_id)
    result = await db.execute(select(model).where(and_(*filters)))
    return result.scalars().all()


async def _get_report(
    db: AsyncSession, token_payload: dict, user_id: str, report_id: str, model
):
    organization_id = resolve_organization_id(
        token_payload, None, user_id, use_user_fallback=False
    )
    return await get_owned_report(db, model, report_id, organization_id, user_id)


async def _update_report(
    db: AsyncSession, token_payload: dict, user_id: str, report_id: str, payload, model
):
    report = await _get_report(db, token_payload, user_id, report_id, model)
    updates = payload.model_dump(exclude_unset=True)
    if "document_asset_id" in updates or "media_asset_id" in updates:
        await resolve_report_context(
            db,
            token_payload,
            report.organization_id,
            report.project_id,
            updates.get("document_asset_id"),
            updates.get("media_asset_id"),
            user_id,
        )
    apply_report_updates(report, payload)
    await log_report_event(db, model, report, "updated", user_id)
    await db.flush()
    await db.refresh(report)
    return report


@router.post("/camera-reports", response_model=CameraReportResponse)
async def create_camera_report(
    payload: CameraReportCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _create_report(db, token_payload, user.user_id, payload, CameraReport)


@router.get("/camera-reports", response_model=CameraReportListResponse)
async def list_camera_reports(
    project_id: Optional[str] = None,
    shooting_day_id: Optional[str] = None,
    scene_id: Optional[str] = None,
    shot_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    items = await _list_reports(
        db,
        token_payload,
        user.user_id,
        CameraReport,
        project_id,
        shooting_day_id,
        scene_id,
        shot_id,
    )
    return CameraReportListResponse(items=items)


@router.get("/camera-reports/{report_id}", response_model=CameraReportResponse)
async def get_camera_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _get_report(db, token_payload, user.user_id, report_id, CameraReport)


@router.patch("/camera-reports/{report_id}", response_model=CameraReportResponse)
async def update_camera_report(
    report_id: str,
    payload: CameraReportUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _update_report(
        db, token_payload, user.user_id, report_id, payload, CameraReport
    )


@router.post("/sound-reports", response_model=SoundReportResponse)
async def create_sound_report(
    payload: SoundReportCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _create_report(db, token_payload, user.user_id, payload, SoundReport)


@router.get("/sound-reports", response_model=SoundReportListResponse)
async def list_sound_reports(
    project_id: Optional[str] = None,
    shooting_day_id: Optional[str] = None,
    scene_id: Optional[str] = None,
    shot_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    items = await _list_reports(
        db,
        token_payload,
        user.user_id,
        SoundReport,
        project_id,
        shooting_day_id,
        scene_id,
        shot_id,
    )
    return SoundReportListResponse(items=items)


@router.get("/sound-reports/{report_id}", response_model=SoundReportResponse)
async def get_sound_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _get_report(db, token_payload, user.user_id, report_id, SoundReport)


@router.patch("/sound-reports/{report_id}", response_model=SoundReportResponse)
async def update_sound_report(
    report_id: str,
    payload: SoundReportUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _update_report(
        db, token_payload, user.user_id, report_id, payload, SoundReport
    )


@router.post("/script-notes", response_model=ScriptNoteResponse)
async def create_script_note(
    payload: ScriptNoteCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _create_report(db, token_payload, user.user_id, payload, ScriptNote)


@router.get("/script-notes", response_model=ScriptNoteListResponse)
async def list_script_notes(
    project_id: Optional[str] = None,
    shooting_day_id: Optional[str] = None,
    scene_id: Optional[str] = None,
    shot_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    items = await _list_reports(
        db,
        token_payload,
        user.user_id,
        ScriptNote,
        project_id,
        shooting_day_id,
        scene_id,
        shot_id,
    )
    return ScriptNoteListResponse(items=items)


@router.get("/script-notes/{report_id}", response_model=ScriptNoteResponse)
async def get_script_note(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _get_report(db, token_payload, user.user_id, report_id, ScriptNote)


@router.patch("/script-notes/{report_id}", response_model=ScriptNoteResponse)
async def update_script_note(
    report_id: str,
    payload: ScriptNoteUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _update_report(
        db, token_payload, user.user_id, report_id, payload, ScriptNote
    )


@router.post("/director-notes", response_model=DirectorNoteResponse)
async def create_director_note(
    payload: DirectorNoteCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _create_report(db, token_payload, user.user_id, payload, DirectorNote)


@router.get("/director-notes", response_model=DirectorNoteListResponse)
async def list_director_notes(
    project_id: Optional[str] = None,
    shooting_day_id: Optional[str] = None,
    scene_id: Optional[str] = None,
    shot_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    items = await _list_reports(
        db,
        token_payload,
        user.user_id,
        DirectorNote,
        project_id,
        shooting_day_id,
        scene_id,
        shot_id,
    )
    return DirectorNoteListResponse(items=items)


@router.get("/director-notes/{report_id}", response_model=DirectorNoteResponse)
async def get_director_note(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _get_report(db, token_payload, user.user_id, report_id, DirectorNote)


@router.patch("/director-notes/{report_id}", response_model=DirectorNoteResponse)
async def update_director_note(
    report_id: str,
    payload: DirectorNoteUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_authenticated_user),
    token_payload: dict = Depends(get_token_payload),
):
    return await _update_report(
        db, token_payload, user.user_id, report_id, payload, DirectorNote
    )
